# backend/app/core/database/transaction.py
"""
⚠️ DEPRECATED - 이 모듈은 더 이상 사용되지 않습니다.
현재 프로젝트에서는 app.utils.database.transaction 모듈을 사용합니다.

트랜잭션 관리자 모듈
자동 롤백 및 커밋 컨텍스트 관리자를 제공합니다.

⚠️ 사용 중단됨: 2025-08-20
대체 모듈: app.utils.database.transaction
"""

import pymysql
from typing import Optional, Any, List, Dict
from contextlib import contextmanager
import logging
from .mysql_client import MySQLClient

logger = logging.getLogger(__name__)


class TransactionManager:
    """트랜잭션 관리자 클래스"""
    
    def __init__(self, mysql_client: Optional[MySQLClient] = None):
        """
        트랜잭션 관리자 초기화
        
        Args:
            mysql_client: MySQL 클라이언트 인스턴스
        """
        self.mysql_client = mysql_client or MySQLClient()
        self._connection = None
        self._cursor = None
    
    @contextmanager
    def transaction(self):
        """
        트랜잭션 컨텍스트 관리자
        자동으로 트랜잭션을 시작하고, 성공 시 커밋, 실패 시 롤백합니다.
        
        Yields:
            TransactionContext: 트랜잭션 컨텍스트 객체
        """
        connection = None
        cursor = None
        
        try:
            # 연결 생성 및 자동 커밋 비활성화
            connection = self.mysql_client.connect()
            connection.autocommit(False)
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            # 트랜잭션 시작
            connection.begin()
            logger.debug("트랜잭션이 시작되었습니다.")
            
            # 트랜잭션 컨텍스트 생성
            transaction_context = TransactionContext(connection, cursor)
            
            yield transaction_context
            
            # 성공 시 커밋
            connection.commit()
            logger.debug("트랜잭션이 커밋되었습니다.")
            
        except Exception as e:
            # 실패 시 롤백
            if connection:
                try:
                    connection.rollback()
                    logger.debug("트랜잭션이 롤백되었습니다.")
                except Exception as rollback_error:
                    logger.error(f"롤백 중 오류 발생: {rollback_error}")
            
            logger.error(f"트랜잭션 실행 중 오류 발생: {e}")
            raise
            
        finally:
            # 리소스 정리
            if cursor:
                cursor.close()
            if connection:
                connection.autocommit(True)  # 자동 커밋 복원
    
    @contextmanager
    def savepoint(self, savepoint_name: str):
        """
        세이브포인트 컨텍스트 관리자
        중첩된 트랜잭션을 위한 세이브포인트를 생성합니다.
        
        Args:
            savepoint_name: 세이브포인트 이름
            
        Yields:
            str: 세이브포인트 이름
        """
        connection = self.mysql_client.connect()
        cursor = connection.cursor()
        
        try:
            # 세이브포인트 생성
            cursor.execute(f"SAVEPOINT {savepoint_name}")
            logger.debug(f"세이브포인트 '{savepoint_name}'이 생성되었습니다.")
            
            yield savepoint_name
            
        except Exception as e:
            # 세이브포인트로 롤백
            try:
                cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                logger.debug(f"세이브포인트 '{savepoint_name}'으로 롤백되었습니다.")
            except Exception as rollback_error:
                logger.error(f"세이브포인트 롤백 중 오류 발생: {rollback_error}")
            
            logger.error(f"세이브포인트 실행 중 오류 발생: {e}")
            raise
            
        finally:
            # 세이브포인트 해제
            try:
                cursor.execute(f"RELEASE SAVEPOINT {savepoint_name}")
                logger.debug(f"세이브포인트 '{savepoint_name}'이 해제되었습니다.")
            except Exception as release_error:
                logger.warning(f"세이브포인트 해제 중 오류 발생: {release_error}")
            
            cursor.close()


class TransactionContext:
    """트랜잭션 컨텍스트 클래스"""
    
    def __init__(self, connection: pymysql.Connection, cursor: pymysql.cursors.Cursor):
        """
        트랜잭션 컨텍스트 초기화
        
        Args:
            connection: 데이터베이스 연결 객체
            cursor: 데이터베이스 커서 객체
        """
        self.connection = connection
        self.cursor = cursor
    
    def execute(self, query: str, params: Optional[tuple] = None) -> int:
        """
        쿼리를 실행합니다.
        
        Args:
            query: 실행할 SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            int: 영향받은 행의 수
        """
        try:
            result = self.cursor.execute(query, params)
            logger.debug(f"쿼리 실행 완료: {query[:100]}...")
            return result
        except Exception as e:
            logger.error(f"쿼리 실행 실패: {e}")
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        여러 개의 파라미터로 쿼리를 일괄 실행합니다.
        
        Args:
            query: 실행할 SQL 쿼리
            params_list: 파라미터 리스트
            
        Returns:
            int: 영향받은 행의 수
        """
        try:
            result = self.cursor.executemany(query, params_list)
            logger.debug(f"일괄 쿼리 실행 완료: {len(params_list)}개 항목")
            return result
        except Exception as e:
            logger.error(f"일괄 쿼리 실행 실패: {e}")
            raise
    
    def fetch_one(self) -> Optional[Dict[str, Any]]:
        """
        단일 결과를 가져옵니다.
        
        Returns:
            Optional[Dict[str, Any]]: 쿼리 결과 또는 None
        """
        return self.cursor.fetchone()
    
    def fetch_all(self) -> List[Dict[str, Any]]:
        """
        모든 결과를 가져옵니다.
        
        Returns:
            List[Dict[str, Any]]: 쿼리 결과 리스트
        """
        return self.cursor.fetchall()
    
    def fetch_many(self, size: int) -> List[Dict[str, Any]]:
        """
        지정된 개수만큼 결과를 가져옵니다.
        
        Args:
            size: 가져올 결과 개수
            
        Returns:
            List[Dict[str, Any]]: 쿼리 결과 리스트
        """
        return self.cursor.fetchmany(size)
    
    def get_last_insert_id(self) -> int:
        """
        마지막으로 삽입된 AUTO_INCREMENT ID를 가져옵니다.
        
        Returns:
            int: 마지막 삽입 ID
        """
        return self.connection.insert_id()
    
    def get_row_count(self) -> int:
        """
        마지막 쿼리에서 영향받은 행의 수를 가져옵니다.
        
        Returns:
            int: 영향받은 행의 수
        """
        return self.cursor.rowcount


class BatchTransactionManager:
    """배치 트랜잭션 관리자 클래스"""
    
    def __init__(self, mysql_client: Optional[MySQLClient] = None, batch_size: int = 1000):
        """
        배치 트랜잭션 관리자 초기화
        
        Args:
            mysql_client: MySQL 클라이언트 인스턴스
            batch_size: 배치 크기
        """
        self.mysql_client = mysql_client or MySQLClient()
        self.batch_size = batch_size
        self.transaction_manager = TransactionManager(mysql_client)
    
    def execute_batch_insert(self, query: str, data_list: List[tuple]) -> int:
        """
        배치 INSERT를 실행합니다.
        
        Args:
            query: INSERT 쿼리
            data_list: 삽입할 데이터 리스트
            
        Returns:
            int: 총 삽입된 행의 수
        """
        total_inserted = 0
        
        # 데이터를 배치 크기로 분할
        for i in range(0, len(data_list), self.batch_size):
            batch_data = data_list[i:i + self.batch_size]
            
            with self.transaction_manager.transaction() as tx:
                inserted_count = tx.execute_many(query, batch_data)
                total_inserted += inserted_count
                
                logger.debug(f"배치 {i//self.batch_size + 1}: {inserted_count}개 행 삽입")
        
        logger.info(f"총 {total_inserted}개 행이 삽입되었습니다.")
        return total_inserted
    
    def execute_batch_update(self, query: str, data_list: List[tuple]) -> int:
        """
        배치 UPDATE를 실행합니다.
        
        Args:
            query: UPDATE 쿼리
            data_list: 업데이트할 데이터 리스트
            
        Returns:
            int: 총 업데이트된 행의 수
        """
        total_updated = 0
        
        # 데이터를 배치 크기로 분할
        for i in range(0, len(data_list), self.batch_size):
            batch_data = data_list[i:i + self.batch_size]
            
            with self.transaction_manager.transaction() as tx:
                updated_count = tx.execute_many(query, batch_data)
                total_updated += updated_count
                
                logger.debug(f"배치 {i//self.batch_size + 1}: {updated_count}개 행 업데이트")
        
        logger.info(f"총 {total_updated}개 행이 업데이트되었습니다.")
        return total_updated


# 편의 함수들
def with_transaction(mysql_client: Optional[MySQLClient] = None):
    """
    트랜잭션 데코레이터를 위한 팩토리 함수
    
    Args:
        mysql_client: MySQL 클라이언트 인스턴스
        
    Returns:
        function: 트랜잭션 데코레이터
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            transaction_manager = TransactionManager(mysql_client)
            with transaction_manager.transaction() as tx:
                return func(tx, *args, **kwargs)
        return wrapper
    return decorator


def execute_in_transaction(func, mysql_client: Optional[MySQLClient] = None, *args, **kwargs):
    """
    함수를 트랜잭션 내에서 실행합니다.
    
    Args:
        func: 실행할 함수 (첫 번째 인자로 TransactionContext를 받아야 함)
        mysql_client: MySQL 클라이언트 인스턴스
        *args: 함수에 전달할 위치 인자
        **kwargs: 함수에 전달할 키워드 인자
        
    Returns:
        Any: 함수의 반환값
    """
    transaction_manager = TransactionManager(mysql_client)
    with transaction_manager.transaction() as tx:
        return func(tx, *args, **kwargs)