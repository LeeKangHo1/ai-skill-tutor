# backend/app/utils/database/__init__.py
"""
데이터베이스 유틸리티들
데이터베이스 연결, 쿼리 빌더, 트랜잭션 관리 기능을 제공합니다.
"""

# 클래스들
from .connection import DatabaseConnection
from .query_builder import QueryBuilder
from .transaction import TransactionManager

# 기본 쿼리 실행 함수들
from .connection import execute_query, fetch_one, fetch_all

# CRUD 헬퍼 함수들
from .query_builder import (
    insert_record, 
    update_record, 
    delete_record, 
    count_records, 
    record_exists
)

# 트랜잭션 실행 함수들
from .transaction import execute_transaction, execute_batch_insert

__all__ = [
    # 클래스들
    'DatabaseConnection', 
    'QueryBuilder', 
    'TransactionManager',
    
    # 기본 쿼리 실행 함수들
    'execute_query',
    'fetch_one', 
    'fetch_all',
    
    # CRUD 헬퍼 함수들
    'insert_record',
    'update_record',
    'delete_record',
    'count_records',
    'record_exists',
    
    # 트랜잭션 실행 함수들
    'execute_transaction',
    'execute_batch_insert'
]