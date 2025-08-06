# backend/app/config/__init__.py
# Flask 애플리케이션 설정 클래스

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """기본 설정 클래스"""
    # 시크릿 키 설정 (JWT 토큰 생성 등에 사용)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # 데이터베이스 설정
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # CORS 설정
    CORS_ORIGINS = ['http://localhost:5173']  # Vue.js 개발 서버
    
    # 디버그 모드 (개발 환경에서만 True)
    DEBUG = True

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """운영 환경 설정 (추후 사용)"""
    DEBUG = False
    TESTING = False

# 설정 딕셔너리
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}