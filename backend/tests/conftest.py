# backend/tests/conftest.py
# pytest 설정 및 공통 픽스처 파일

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# 백엔드 앱 경로를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Redis 모듈 모킹 (테스트 환경에서 Redis 없이 실행)
sys.modules['redis'] = MagicMock()

from app import create_app
from app.utils.database.connection import execute_query
from app.utils.database.transaction import execute_transaction

@pytest.fixture(scope='session')
def app():
    """테스트용 Flask 애플리케이션 인스턴스 생성"""
    # 테스트 환경 변수 설정
    test_env = {
        'FLASK_ENV': 'testing',
        'DB_HOST': 'localhost',
        'DB_PORT': '3306',
        'DB_NAME': 'ai_skill_tutor_test',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'JWT_SECRET_KEY': 'test_jwt_secret_key_for_testing_only',
        'JWT_ACCESS_TOKEN_EXPIRES': '3600',
        'JWT_REFRESH_TOKEN_EXPIRES': '2592000'
    }
    
    with patch.dict(os.environ, test_env):
        app = create_app('testing')
        app.config['TESTING'] = True
        
        with app.app_context():
            yield app

@pytest.fixture(scope='function')
def client(app):
    """테스트 클라이언트 생성"""
    return app.test_client()

@pytest.fixture(scope='function')
def clean_database():
    """각 테스트 전후 데이터베이스 정리"""
    # 테스트 전 정리
    cleanup_tables()
    
    yield
    
    # 테스트 후 정리
    cleanup_tables()

def cleanup_tables():
    """테스트용 테이블 데이터 정리"""
    try:
        # 외래키 제약 조건 임시 비활성화
        execute_query("SET FOREIGN_KEY_CHECKS = 0")
        
        # 테스트 관련 테이블 데이터 삭제
        tables_to_clean = [
            'user_tokens',
            'user_statistics', 
            'user_progress',
            'users'
        ]
        
        for table in tables_to_clean:
            execute_query(f"DELETE FROM {table} WHERE login_id LIKE 'test_%'")
        
        # 외래키 제약 조건 재활성화
        execute_query("SET FOREIGN_KEY_CHECKS = 1")
        
    except Exception as e:
        print(f"데이터베이스 정리 중 오류 발생: {e}")

@pytest.fixture
def sample_user_data():
    """테스트용 사용자 데이터"""
    return {
        'login_id': 'test_user_001',
        'email': 'test001@example.com',
        'password': 'TestPass123!',
        'name': '테스트사용자001',
        'phone': '010-1234-5678'
    }

@pytest.fixture
def sample_user_data_2():
    """테스트용 사용자 데이터 2"""
    return {
        'login_id': 'test_user_002',
        'email': 'test002@example.com',
        'password': 'TestPass456!',
        'name': '테스트사용자002',
        'phone': '010-9876-5432'
    }

@pytest.fixture
def invalid_user_data():
    """유효하지 않은 사용자 데이터"""
    return {
        'login_id': 'ab',  # 너무 짧음
        'email': 'invalid-email',  # 잘못된 이메일 형식
        'password': '123',  # 너무 약한 비밀번호
        'name': '',  # 빈 이름
        'phone': '123'  # 잘못된 전화번호 형식
    }

@pytest.fixture
def auth_headers():
    """인증 헤더 생성 헬퍼"""
    def _create_auth_headers(access_token):
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    return _create_auth_headers