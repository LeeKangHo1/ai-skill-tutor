# backend/app/config/base.py
"""
기본 설정 클래스
모든 환경에서 공통으로 사용되는 설정들을 정의합니다.
"""

import os
from datetime import timedelta


class BaseConfig:
    """기본 설정 클래스"""
    
    # 기본 Flask 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT 설정
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # 데이터베이스 설정
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'ai_skill_tutor')
    
    # SQLAlchemy 설정
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # CORS 설정
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']
    
    # 로깅 설정
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
    
    # AI 모델 설정
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # ChromaDB 설정
    CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', 'data/chroma_db')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """데이터베이스 연결 URI 생성"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"