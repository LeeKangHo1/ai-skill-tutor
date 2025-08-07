# backend/app/config/__init__.py
# Flask 애플리케이션 설정 클래스

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """기본 설정 클래스"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    CORS_ORIGINS = ['http://localhost:5173']
    DEBUG = True

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    DEBUG = False
    LOG_LEVEL = 'DEBUG'
    CORS_ORIGINS = ['*']
    DATABASE_URL = 'sqlite:///:memory:'  # ✅ 테스트용 SQLite 메모리 DB 등

# 설정 딕셔너리
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,   # ✅ 추가
    'default': DevelopmentConfig
}
