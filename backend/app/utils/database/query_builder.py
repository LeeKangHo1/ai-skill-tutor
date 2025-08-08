# backend/app/utils/database/query_builder.py
# 쿼리 빌더 및 CRUD 헬퍼 함수들

import logging
from typing import Optional, List, Dict, Any, Union, Tuple
import pymysql

from ...config.db_config import (
    get_db_connection, 
    DatabaseQueryError, 
    DatabaseIntegrityError
)

# 로깅 설정
logger = logging.getLogger(__name__)

class QueryBuilder:
    """
    쿼리 빌더 클래스
    동적으로 SQL 쿼리를 생성하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """쿼리 빌더 초기화"""
        self.query_parts = {
            'select': [],
            'from': '',
            'where': [],
            'join': [],
            'order_by': [],
            'group_by': [],
            'having': [],
            'limit': None,
            'offset': None
        }
        self.params = []
    
    def select(self, columns: Union[str, List[str]]) -> 'QueryBuilder':
        """
        SELECT 절 추가
        
        Args:
            columns: 선택할 컬럼들 (문자열 또는 리스트)
            
        Returns:
            QueryBuilder: 체이닝을 위한 자기 자신 반환
        """
        if isinstance(columns, str):
            self.query_parts['select'].append(columns)
        elif isinstance(columns, list):
            self.query_parts['select'].extend(columns)
        return self
    
    def from_table(self, table_name: str) -> 'QueryBuilder':
        """
        FROM 절 설정
        
        Args:
            table_name: 테이블 이름
            
        Returns:
            QueryBuilder: 체이닝을 위한 자기 자신 반환
        """
        self.query_parts['from'] = table_name
        return self
    
    def where(self, condition: str, params: Optional[Union[Tuple, List]] = None) -> 'QueryBuilder':
        """
        WHERE 절 추가
        
        Args:
            condition: WHERE 조건
            params: 조건에 사용될 파라미터들
            
        Returns:
            QueryBuilder: 체이닝을 위한 자기 자신 반환
        """
        self.query_parts['where'].append(condition)
        if params:
            if isinstance(params, (list, tuple)):
                self.params.extend(params)
            else:
                self.params.append(params)
        return self
    
    def join(self, table: str, condition: str, join_type: str = 'INNER') -> 'QueryBuilder':
        """
        JOIN 절 추가
        
        Args:
            table: 조인할 테이블
            condition: 조인 조건
            join_type: 조인 타입 (INNER, LEFT, RIGHT, FULL)
            
        Returns:
            QueryBuilder: 체이닝을 위한 자기 자신 반환
        """
        join_clause = f"{join_type} JOIN {table} ON {condition}"
        self.query_parts['join'].append(join_clause)
        return self
    
    def order_by(self, column: str, direction: str = 'ASC') -> 'QueryBuilder':
        """
        ORDER BY 절 추가
        
        Args:
            column: 정렬할 컬럼
            direction: 정렬 방향 (ASC, DESC)
            
        Returns:
            QueryBuilder: 체이닝을 위한 자기 자신 반환
        """
        order_clause = f"{column} {direction.upper()}"
        self.query_parts['order_by'].append(order_clause)
        return self
    
    def group_by(self, columns: Union[str, List[str]]) -> 'QueryBuilder':
        """
        GROUP BY 절 추가
        
        Args:
            columns: 그룹화할 컬럼들
            
        Returns:
            QueryBuilder: 체이닝을 위한 자기 자신 반환
        """
        if isinstance(columns, str):
            self.query_parts['group_by'].append(columns)
        elif isinstance(columns, list):
            self.query_parts['group_by'].extend(columns)
        return self
    
    def having(self, condition: str, params: Optional[Union[Tuple, List]] = None) -> 'QueryBuilder':
        """
        HAVING 절 추가
        
        Args:
            condition: HAVING 조건
            params: 조건에 사용될 파라미터들
            
        Returns:
            QueryBuilder: 체이닝을 위한 자기 자신 반환
        """
        self.query_parts['having'].append(condition)
        if params:
            if isinstance(params, (list, tuple)):
                self.params.extend(params)
            else:
                self.params.append(params)
        return self
    
    def limit(self, count: int, offset: Optional[int] = None) -> 'QueryBuilder':
        """
        LIMIT 절 추가
        
        Args:
            count: 제한할 행 수
            offset: 시작 위치 (선택사항)
            
        Returns:
            QueryBuilder: 체이닝을 위한 자기 자신 반환
        """
        self.query_parts['limit'] = count
        if offset is not None:
            self.query_parts['offset'] = offset
        return self
    
    def build(self) -> Tuple[str, List]:
        """
        최종 쿼리 생성
        
        Returns:
            Tuple[str, List]: (쿼리 문자열, 파라미터 리스트)
            
        Raises:
            ValueError: 필수 절이 누락된 경우
        """
        if not self.query_parts['select']:
            raise ValueError("SELECT 절이 필요합니다")
        if not self.query_parts['from']:
            raise ValueError("FROM 절이 필요합니다")
        
        # SELECT 절 구성
        select_clause = "SELECT " + ", ".join(self.query_parts['select'])
        
        # FROM 절 구성
        from_clause = f"FROM {self.query_parts['from']}"
        
        # 쿼리 부분들을 조합
        query_parts = [select_clause, from_clause]
        
        # JOIN 절 추가
        if self.query_parts['join']:
            query_parts.extend(self.query_parts['join'])
        
        # WHERE 절 추가
        if self.query_parts['where']:
            where_clause = "WHERE " + " AND ".join(self.query_parts['where'])
            query_parts.append(where_clause)
        
        # GROUP BY 절 추가
        if self.query_parts['group_by']:
            group_by_clause = "GROUP BY " + ", ".join(self.query_parts['group_by'])
            query_parts.append(group_by_clause)
        
        # HAVING 절 추가
        if self.query_parts['having']:
            having_clause = "HAVING " + " AND ".join(self.query_parts['having'])
            query_parts.append(having_clause)
        
        # ORDER BY 절 추가
        if self.query_parts['order_by']:
            order_by_clause = "ORDER BY " + ", ".join(self.query_parts['order_by'])
            query_parts.append(order_by_clause)
        
        # LIMIT 절 추가
        if self.query_parts['limit'] is not None:
            if self.query_parts['offset'] is not None:
                limit_clause = f"LIMIT {self.query_parts['offset']}, {self.query_parts['limit']}"
            else:
                limit_clause = f"LIMIT {self.query_parts['limit']}"
            query_parts.append(limit_clause)
        
        final_query = " ".join(query_parts)
        return final_query, self.params
    
    def reset(self) -> 'QueryBuilder':
        """
        쿼리 빌더 초기화
        
        Returns:
            QueryBuilder: 초기화된 자기 자신 반환
        """
        self.query_parts = {
            'select': [],
            'from': '',
            'where': [],
            'join': [],
            'order_by': [],
            'group_by': [],
            'having': [],
            'limit': None,
            'offset': None
        }
        self.params = []
        return self

# ================================
# CRUD 헬퍼 함수들
# ================================

def insert_record(
    table: str, 
    data: Dict[str, Any],
    return_id: bool = True
) -> Optional[int]:
    """
    레코드 삽입 함수
    
    Args:
        table (str): 테이블 명
        data (Dict[str, Any]): 삽입할 데이터
        return_id (bool): 삽입된 레코드의 ID 반환 여부
    
    Returns:
        Optional[int]: 삽입된 레코드의 ID (return_id=True인 경우)
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
        DatabaseIntegrityError: 무결성 제약 위반 시
    """
    if not data:
        raise ValueError("삽입할 데이터가 비어있습니다")
    
    try:
        # 쿼리 생성
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = tuple(data.values())
        
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                
                if return_id:
                    inserted_id = cursor.lastrowid
                    logger.debug(f"레코드 삽입 성공: {table} 테이블, ID: {inserted_id}")
                    return inserted_id
                else:
                    logger.debug(f"레코드 삽입 성공: {table} 테이블")
                    return None
                    
    except pymysql.IntegrityError as e:
        error_msg = f"레코드 삽입 무결성 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseIntegrityError(error_msg)
    except pymysql.Error as e:
        error_msg = f"레코드 삽입 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)
    except Exception as e:
        error_msg = f"예상치 못한 레코드 삽입 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)

def update_record(
    table: str, 
    data: Dict[str, Any], 
    where_clause: str, 
    where_params: Optional[Union[Tuple, List]] = None
) -> int:
    """
    레코드 업데이트 함수
    
    Args:
        table (str): 테이블 명
        data (Dict[str, Any]): 업데이트할 데이터
        where_clause (str): WHERE 조건절
        where_params (Optional[Union[Tuple, List]]): WHERE 조건 파라미터
    
    Returns:
        int: 업데이트된 행 수
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
        DatabaseIntegrityError: 무결성 제약 위반 시
    """
    if not data:
        raise ValueError("업데이트할 데이터가 비어있습니다")
    
    try:
        # 쿼리 생성
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        
        # 파라미터 결합
        params = list(data.values())
        if where_params:
            params.extend(where_params)
        
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                affected_rows = cursor.execute(query, params)
                logger.debug(f"레코드 업데이트 성공: {table} 테이블, {affected_rows}개 행 영향")
                return affected_rows
                
    except pymysql.IntegrityError as e:
        error_msg = f"레코드 업데이트 무결성 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseIntegrityError(error_msg)
    except pymysql.Error as e:
        error_msg = f"레코드 업데이트 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)
    except Exception as e:
        error_msg = f"예상치 못한 레코드 업데이트 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)

def delete_record(
    table: str, 
    where_clause: str, 
    where_params: Optional[Union[Tuple, List]] = None
) -> int:
    """
    레코드 삭제 함수
    
    Args:
        table (str): 테이블 명
        where_clause (str): WHERE 조건절
        where_params (Optional[Union[Tuple, List]]): WHERE 조건 파라미터
    
    Returns:
        int: 삭제된 행 수
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
    """
    try:
        query = f"DELETE FROM {table} WHERE {where_clause}"
        
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                affected_rows = cursor.execute(query, where_params)
                logger.debug(f"레코드 삭제 성공: {table} 테이블, {affected_rows}개 행 삭제")
                return affected_rows
                
    except pymysql.Error as e:
        error_msg = f"레코드 삭제 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)
    except Exception as e:
        error_msg = f"예상치 못한 레코드 삭제 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)

def count_records(
    table: str, 
    where_clause: Optional[str] = None, 
    where_params: Optional[Union[Tuple, List]] = None
) -> int:
    """
    레코드 개수 조회 함수
    
    Args:
        table (str): 테이블 명
        where_clause (Optional[str]): WHERE 조건절
        where_params (Optional[Union[Tuple, List]]): WHERE 조건 파라미터
    
    Returns:
        int: 레코드 개수
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
    """
    try:
        from .connection import fetch_one
        
        if where_clause:
            query = f"SELECT COUNT(*) as count FROM {table} WHERE {where_clause}"
        else:
            query = f"SELECT COUNT(*) as count FROM {table}"
        
        result = fetch_one(query, where_params)
        count = result['count'] if result else 0
        
        logger.debug(f"레코드 개수 조회 성공: {table} 테이블, {count}개")
        return count
        
    except Exception as e:
        error_msg = f"레코드 개수 조회 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)

def record_exists(
    table: str, 
    where_clause: str, 
    where_params: Optional[Union[Tuple, List]] = None
) -> bool:
    """
    레코드 존재 여부 확인 함수
    
    Args:
        table (str): 테이블 명
        where_clause (str): WHERE 조건절
        where_params (Optional[Union[Tuple, List]]): WHERE 조건 파라미터
    
    Returns:
        bool: 레코드 존재 여부
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
    """
    try:
        count = count_records(table, where_clause, where_params)
        exists = count > 0
        
        logger.debug(f"레코드 존재 여부 확인: {table} 테이블, 존재: {exists}")
        return exists
        
    except Exception as e:
        error_msg = f"레코드 존재 여부 확인 오류 ({table}): {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)