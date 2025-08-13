# backend/tests/test_config.py
# 테스트 설정 파일

import os
import tempfile

class TestConfig:
    """테스트용 설정 클래스"""
    
    # 기본 Flask 설정
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-secret-key-for-testing-only'
    
    # 데이터베이스 설정 (테스트용)
    DB_HOST = os.getenv('TEST_DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('TEST_DB_PORT', '3306'))
    DB_NAME = os.getenv('TEST_DB_NAME', 'ai_skill_tutor_test')
    DB_USER = os.getenv('TEST_DB_USER', 'test_user')
    DB_PASSWORD = os.getenv('TEST_DB_PASSWORD', 'test_password')
    
    # JWT 설정 (테스트용)
    JWT_SECRET_KEY = 'test-jwt-secret-key-for-testing-only'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1시간
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30일
    
    # CORS 설정
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # 로깅 설정 (테스트 시 최소화)
    LOG_LEVEL = 'ERROR'
    LOG_TO_FILE = False
    
    # 기타 테스트 설정
    WTF_CSRF_ENABLED = False  # CSRF 보호 비활성화 (테스트용)
    PRESERVE_CONTEXT_ON_EXCEPTION = False