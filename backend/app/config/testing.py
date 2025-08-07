# backend/app/config/testing.py
"""
테스트 환경 설정
테스트 실행 시에만 사용되는 설정들을 정의합니다.
"""

from .base import BaseConfig


class TestingConfig(BaseConfig):
    """테스트 환경 설정 클래스"""
    
    # 테스트 모드 활성화
    DEBUG = True
    TESTING = True
    
    # 테스트용 데이터베이스 설정
    MYSQL_DATABASE = 'ai_skill_tutor_test'
    
    # 테스트용 JWT 설정 (짧은 만료 시간)
    from datetime import timedelta
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    
    # 테스트용 로깅 설정
    LOG_LEVEL = 'ERROR'
    
    # 테스트용 ChromaDB 경로 (메모리 사용)
    CHROMA_DB_PATH = ':memory:'
    
    # 테스트 시 외부 API 호출 비활성화
    DISABLE_EXTERNAL_APIS = True