# backend/app/config/production.py
"""
운영 환경 설정
운영 서버에서 사용되는 설정들을 정의합니다.
"""

from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """운영 환경 설정 클래스"""
    
    # 운영 모드 설정
    DEBUG = False
    TESTING = False
    
    # 운영용 데이터베이스 설정
    MYSQL_DATABASE = 'ai_skill_tutor_prod'
    
    # 보안 강화 설정
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 로깅 레벨을 WARNING으로 설정
    LOG_LEVEL = 'WARNING'
    
    # 운영용 CORS 설정 (엄격하게)
    CORS_ORIGINS = ['https://yourdomain.com']
    
    # 운영용 ChromaDB 경로
    CHROMA_DB_PATH = '/var/lib/ai_skill_tutor/chroma_db'