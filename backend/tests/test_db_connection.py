# backend/tests/test_db_connection.py
# 데이터베이스 연결 테스트 스크립트

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config.db_config import (
    DatabaseConfig, 
    DatabaseConnectionManager,
    DatabaseConnectionError,
    get_db_connection,
    test_database_connection,
    initialize_database,
    init_db_config
)

class TestDatabaseConnection(unittest.TestCase):
    """데이터베이스 연결 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 테스트용 환경변수 설정
        self.test_env = {
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_password',
            'DB_CHARSET': 'utf8mb4',
            'DB_MAX_CONNECTIONS': '5',
            'DB_CONNECT_TIMEOUT': '5'
        }
    
    @patch.dict(os.environ, {'DB_HOST': 'localhost', 'DB_PORT': '3306', 
                            'DB_NAME': 'test_db', 'DB_USER': 'test_user', 
                            'DB_PASSWORD': 'test_password'})
    def test_database_config_creation(self):
        """데이터베이스 설정 생성 테스트"""
        config = DatabaseConfig()
        
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 3306)
        self.assertEqual(config.database, 'test_db')
        self.assertEqual(config.user, 'test_user')
        self.assertEqual(config.password, 'test_password')
        self.assertEqual(config.charset, 'utf8mb4')
    
    @patch.dict(os.environ, {'DB_HOST': 'localhost'})
    def test_database_config_validation_failure(self):
        """데이터베이스 설정 검증 실패 테스트"""
        with self.assertRaises(ValueError) as context:
            DatabaseConfig()
        
        self.assertIn('필수 데이터베이스 설정이 누락되었습니다', str(context.exception))
    
    @patch('app.config.db_config.pymysql.connect')
    def test_connection_manager_get_connection_success(self, mock_connect):
        """연결 관리자 연결 획득 성공 테스트"""
        # Mock 연결 객체 설정
        mock_connection = MagicMock()
        mock_connection.open = True
        mock_connect.return_value = mock_connection
        
        # 테스트용 설정으로 연결 관리자 생성
        with patch.dict(os.environ, self.test_env):
            config = DatabaseConfig()
            manager = DatabaseConnectionManager(config)
            
            connection = manager.get_connection()
            
            self.assertIsNotNone(connection)
            mock_connect.assert_called_once()
    
    @patch('app.config.db_config.pymysql.connect')
    def test_connection_manager_get_connection_failure(self, mock_connect):
        """연결 관리자 연결 획득 실패 테스트"""
        # 연결 실패 시뮬레이션
        mock_connect.side_effect = Exception("Connection failed")
        
        with patch.dict(os.environ, self.test_env):
            config = DatabaseConfig()
            manager = DatabaseConnectionManager(config)
            
            with self.assertRaises(DatabaseConnectionError):
                manager.get_connection()
    
    @patch('app.config.db_config.get_db_connection')
    def test_database_connection_test_success(self, mock_get_connection):
        """데이터베이스 연결 테스트 성공"""
        # Mock 커서와 연결 설정
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'test': 1}
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_get_connection.return_value.__enter__.return_value = mock_connection
        
        result = test_database_connection()
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once_with("SELECT 1 as test")
    
    @patch('app.config.db_config.get_db_connection')
    def test_database_connection_test_failure(self, mock_get_connection):
        """데이터베이스 연결 테스트 실패"""
        # 연결 실패 시뮬레이션
        mock_get_connection.side_effect = Exception("Connection failed")
        
        result = test_database_connection()
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()