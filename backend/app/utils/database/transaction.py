# backend/app/utils/database/transaction.py
# 트랜잭션 관리 및 복합 작업 실행 함수들

import logging
from typing import List, Dict, Any, Union, Tuple, Optional
import pymysql

from ...config.db_config import (
    get_db_connection, 
    DatabaseQueryError, 
    DatabaseIntegrityError
)

# 로깅 설정
logger = logging.getLogger(__name__)

class TransactionManager:
    """
    트랜잭션 관리 클래스
    데이터베이스 트랜잭션의 시작, 커밋, 롤백을 관리합니다.
    """
    
    def __init__(self, connection):
        """트랜잭션 관리자 초기화"""
        self.connection = connection
        self.in_transaction = False
        self.savepoints = []
    
    def begin(self) -> None:
        """
        트랜잭션 시작
        
        Raises:
            DatabaseQueryError: 트랜잭션 시작 실패 시
        """
        try:
            if self.in_transaction:
                logger.warning("이미 트랜잭션이 진행 중입니다.")
                return
            
            # MySQL에서는 autocommit을 False로 설정하면 트랜잭션이 시작됨
            self.connection.autocommit(False)
            self.in_transaction = True
            logger.debug("트랜잭션이 시작되었습니다.")
            
        except Exception as e:
            error_msg = f"트랜잭션 시작 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, original_error=e)
    
    def commit(self) -> None:
        """
        트랜잭션 커밋
        
        Raises:
            DatabaseQueryError: 커밋 실패 시
        """
        try:
            if not self.in_transaction:
                logger.warning("진행 중인 트랜잭션이 없습니다.")
                return
            
            self.connection.commit()
            self.in_transaction = False
            self.savepoints.clear()
            logger.debug("트랜잭션이 커밋되었습니다.")
            
        except Exception as e:
            error_msg = f"트랜잭션 커밋 오류: {e}"
            logger.error(error_msg)
            # 커밋 실패 시 롤백 시도
            try:
                self.rollback()
            except:
                pass
            raise DatabaseQueryError(error_msg, original_error=e)
    
    def rollback(self) -> None:
        """
        트랜잭션 롤백
        
        Raises:
            DatabaseQueryError: 롤백 실패 시
        """
        try:
            if not self.in_transaction:
                logger.warning("진행 중인 트랜잭션이 없습니다.")
                return
            
            self.connection.rollback()
            self.in_transaction = False
            self.savepoints.clear()
            logger.debug("트랜잭션이 롤백되었습니다.")
            
        except Exception as e:
            error_msg = f"트랜잭션 롤백 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, original_error=e)
    
    def savepoint(self, name: str) -> None:
        """
        세이브포인트 생성
        
        Args:
            name: 세이브포인트 이름
            
        Raises:
            DatabaseQueryError: 세이브포인트 생성 실패 시
        """
        try:
            if not self.in_transaction:
                raise ValueError("트랜잭션이 시작되지 않았습니다.")
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"SAVEPOINT {name}")
            
            self.savepoints.append(name)
            logger.debug(f"세이브포인트 '{name}'이 생성되었습니다.")
            
        except Exception as e:
            error_msg = f"세이브포인트 생성 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, original_error=e)
    
    def rollback_to_savepoint(self, name: str) -> None:
        """
        세이브포인트로 롤백
        
        Args:
            name: 롤백할 세이브포인트 이름
            
        Raises:
            DatabaseQueryError: 세이브포인트 롤백 실패 시
        """
        try:
            if name not in self.savepoints:
                raise ValueError(f"세이브포인트 '{name}'이 존재하지 않습니다.")
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")
            
            # 해당 세이브포인트 이후의 세이브포인트들 제거
            savepoint_index = self.savepoints.index(name)
            self.savepoints = self.savepoints[:savepoint_index + 1]
            
            logger.debug(f"세이브포인트 '{name}'으로 롤백되었습니다.")
            
        except Exception as e:
            error_msg = f"세이브포인트 롤백 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, original_error=e)
    
    def release_savepoint(self, name: str) -> None:
        """
        세이브포인트 해제
        
        Args:
            name: 해제할 세이브포인트 이름
            
        Raises:
            DatabaseQueryError: 세이브포인트 해제 실패 시
        """
        try:
            if name not in self.savepoints:
                raise ValueError(f"세이브포인트 '{name}'이 존재하지 않습니다.")
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"RELEASE SAVEPOINT {name}")
            
            self.savepoints.remove(name)
            logger.debug(f"세이브포인트 '{name}'이 해제되었습니다.")
            
        except Exception as e:
            error_msg = f"세이브포인트 해제 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, original_error=e)
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

# ================================
# 트랜잭션 실행 함수들
# ================================

def execute_transaction(operations: List[Dict[str, Any]]) -> List[Any]:
    """
    트랜잭션 실행 함수 - 여러 작업을 하나의 트랜잭션으로 실행
    
    Args:
        operations (List[Dict[str, Any]]): 실행할 작업 리스트
            각 작업은 다음 형태: {
                'type': 'query'|'insert'|'update'|'delete',
                'query': str (type이 'query'인 경우),
                'table': str (type이 'insert'|'update'|'delete'인 경우),
                'data': Dict (type이 'insert'|'update'인 경우),
                'where_clause': str (type이 'update'|'delete'인 경우),
                'params': Optional[Union[Tuple, List]]
            }
    
    Returns:
        List[Any]: 각 작업의 결과 리스트
    
    Raises:
        DatabaseQueryError: 트랜잭션 실행 실패 시
    """
    if not operations:
        raise ValueError("실행할 작업이 없습니다")
    
    results = []
    
    try:
        with get_db_connection() as connection:
            # 트랜잭션 시작 (autocommit=False가 기본값)
            for operation in operations:
                op_type = operation.get('type')
                
                if op_type == 'query':
                    # 직접 쿼리 실행
                    query = operation['query']
                    params = operation.get('params')
                    
                    with connection.cursor() as cursor:
                        affected_rows = cursor.execute(query, params)
                        
                        # SELECT 쿼리인지 확인
                        if query.strip().upper().startswith('SELECT'):
                            result = cursor.fetchall()
                        else:
                            result = affected_rows
                        
                        results.append(result)
                
                elif op_type == 'insert':
                    # INSERT 작업
                    table = operation['table']
                    data = operation['data']
                    return_id = operation.get('return_id', True)
                    
                    columns = ', '.join(data.keys())
                    placeholders = ', '.join(['%s'] * len(data))
                    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                    values = tuple(data.values())
                    
                    with connection.cursor() as cursor:
                        cursor.execute(query, values)
                        result = cursor.lastrowid if return_id else cursor.rowcount
                        results.append(result)
                
                elif op_type == 'update':
                    # UPDATE 작업
                    table = operation['table']
                    data = operation['data']
                    where_clause = operation['where_clause']
                    where_params = operation.get('params', [])
                    
                    set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
                    query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
                    
                    params = list(data.values())
                    if where_params:
                        params.extend(where_params)
                    
                    with connection.cursor() as cursor:
                        affected_rows = cursor.execute(query, params)
                        results.append(affected_rows)
                
                elif op_type == 'delete':
                    # DELETE 작업
                    table = operation['table']
                    where_clause = operation['where_clause']
                    where_params = operation.get('params')
                    
                    query = f"DELETE FROM {table} WHERE {where_clause}"
                    
                    with connection.cursor() as cursor:
                        affected_rows = cursor.execute(query, where_params)
                        results.append(affected_rows)
                
                else:
                    raise ValueError(f"지원하지 않는 작업 타입: {op_type}")
            
            # 모든 작업이 성공하면 커밋 (컨텍스트 매니저에서 자동 처리)
            logger.info(f"트랜잭션 실행 성공: {len(operations)}개 작업 완료")
            return results
            
    except Exception as e:
        # 오류 발생 시 롤백 (컨텍스트 매니저에서 자동 처리)
        error_msg = f"트랜잭션 실행 오류: {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)

def execute_batch_insert(
    table: str, 
    data_list: List[Dict[str, Any]],
    batch_size: int = 100
) -> List[int]:
    """
    배치 삽입 함수 - 대량의 데이터를 효율적으로 삽입
    
    Args:
        table (str): 테이블 명
        data_list (List[Dict[str, Any]]): 삽입할 데이터 리스트
        batch_size (int): 배치 크기
    
    Returns:
        List[int]: 삽입된 레코드들의 ID 리스트
    
    Raises:
        DatabaseQueryError: 배치 삽입 실패 시
    """
    if not data_list:
        raise ValueError("삽입할 데이터가 없습니다")
    
    inserted_ids = []
    
    try:
        with get_db_connection() as connection:
            # 첫 번째 데이터로 컬럼 구조 확인
            first_data = data_list[0]
            columns = ', '.join(first_data.keys())
            placeholders = ', '.join(['%s'] * len(first_data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            # 배치 단위로 처리
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                
                with connection.cursor() as cursor:
                    for data in batch:
                        # 모든 데이터가 같은 컬럼 구조를 가지는지 확인
                        if set(data.keys()) != set(first_data.keys()):
                            raise ValueError("모든 데이터가 동일한 컬럼 구조를 가져야 합니다")
                        
                        values = tuple(data.values())
                        cursor.execute(query, values)
                        inserted_ids.append(cursor.lastrowid)
                
                logger.debug(f"배치 삽입 완료: {len(batch)}개 레코드")
            
            logger.info(f"배치 삽입 성공: {table} 테이블, 총 {len(data_list)}개 레코드")
            return inserted_ids
            
    except Exception as e:
        error_msg = f"배치 삽입 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)