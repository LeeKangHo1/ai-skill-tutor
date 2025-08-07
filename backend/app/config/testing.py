# backend/app/config/testing.py

class TestingConfig:
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    CORS_ORIGINS = '*'
    # 테스트용 더미 DB 연결 정보 (필요 시)
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'test_db'
