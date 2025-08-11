# backend/app/config/development.py
"""
개발 환경 설정
개발 시에만 사용되는 설정들을 정의합니다.
"""

from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """개발 환경 설정 클래스"""
    
    # 개발 모드 활성화
    DEBUG = True
    TESTING = False
    
    # 개발용 데이터베이스 설정
    MYSQL_DATABASE = 'ai_skill_tutor_dev'
    
    # 로깅 레벨을 DEBUG로 설정
    LOG_LEVEL = 'DEBUG'
    
    # 개발용 CORS 설정 (더 관대하게)
    CORS_ORIGINS = ['*']
    
    # 개발용 JWT 만료 시간 (더 길게)
    from datetime import timedelta
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # 개발용 ChromaDB 경로
    CHROMA_DB_PATH = 'data/chroma_db_dev'
    
    # 개발용 쿠키 설정 (HTTP에서도 동작하도록)
    COOKIE_SECURE = False