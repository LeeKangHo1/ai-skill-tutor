# backend/app/core/database/mysql_client.py
"""
⚠️ DEPRECATED - 이 모듈은 더 이상 사용되지 않습니다.
현재 프로젝트에서는 app.config.db_config 모듈을 사용합니다.

MySQL 데이터베이스 클라이언트 모듈
데이터베이스 연결과 기본 작업을 관리합니다.

⚠️ 사용 중단됨: 2025-08-20
대체 모듈: app.config.db_config.DatabaseConnectionManager
"""

import pymysql
from typing import Optional, Dict, Any, List
import os
from contextlib import contextmanager

class MySQLClient:
    """MySQL 데이터베이스 클라이언트 클래스"""
    
    def __init__(self):
        """MySQL 클라이언트 초기화"""
        self.connection_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'ai_skill_tutor'),
            'charset': 'utf8mb4',
            'autocommit': True
        }
        self._connection = None
    
    def connect(self) -> pymysql.Connection:
        """
        데이터베이스에 연결합니다.
        
        Returns:
            pymysql.Connection: 데이터베이스 연결 객체
        """
        if not self._connection or not self._connection.open:
            self._connection = pymysql.connect(**self.connection_config)
        return self._connection
    
    def disconnect(self) -> None:
        """데이터베이스 연결을 종료합니다."""
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def get_cursor(self):
        """
        커서를 안전하게 사용할 수 있는 컨텍스트 매니저입니다.
        
        Yields:
            pymysql.cursors.Cursor: 데이터베이스 커서
        """
        connection = self.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            yield cursor
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        SELECT 쿼리를 실행하고 결과를 반환합니다.
        
        Args:
            query (str): 실행할 SQL 쿼리
            params (Optional[tuple]): 쿼리 파라미터
            
        Returns:
            List[Dict[str, Any]]: 쿼리 결과
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        INSERT, UPDATE, DELETE 쿼리를 실행합니다.
        
        Args:
            query (str): 실행할 SQL 쿼리
            params (Optional[tuple]): 쿼리 파라미터
            
        Returns:
            int: 영향받은 행의 수
        """
        with self.get_cursor() as cursor:
            return cursor.execute(query, params)
    
    def check_connection(self) -> bool:
        """
        데이터베이스 연결 상태를 확인합니다.
        
        Returns:
            bool: 연결 상태 (True: 연결됨, False: 연결 안됨)
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception:
            return False