# backend/app/config/db_config.py
# 데이터베이스 연결 설정 및 관리 모듈

import os
import pymysql
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

# 로깅 설정
logger = logging.getLogger(__name__)

# 커스텀 예외 클래스들
class DatabaseConnectionError(Exception):
    """데이터베이스 연결 오류"""
    pass

class DatabaseQueryError(Exception):
    """데이터베이스 쿼리 오류"""
    pass

class DatabaseIntegrityError(Exception):
    """데이터베이스 무결성 오류"""
    pass

class DatabaseConfig:
    """데이터베이스 설정 클래스"""
    
    def __init__(self):
        """환경변수에서 데이터베이스 설정 로드"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.charset = os.getenv('DB_CHARSET', 'utf8mb4')
        
        # 연결 풀 설정
        self.max_connections = int(os.getenv('DB_MAX_CONNECTIONS', 10))
        self.connect_timeout = int(os.getenv('DB_CONNECT_TIMEOUT', 10))
        self.read_timeout = int(os.getenv('DB_READ_TIMEOUT', 10))
        self.write_timeout = int(os.getenv('DB_WRITE_TIMEOUT', 10))
        
        # 설정 검증
        self._validate_config()
    
    def _validate_config(self) -> None:
        """데이터베이스 설정 검증"""
        required_fields = ['database', 'user', 'password']
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        
        if missing_fields:
            raise ValueError(f"필수 데이터베이스 설정이 누락되었습니다: {', '.join(missing_fields)}")
    
    def get_connection_params(self) -> Dict[str, Any]:
        """PyMySQL 연결 파라미터 반환"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'charset': self.charset,
            'connect_timeout': self.connect_timeout,
            'read_timeout': self.read_timeout,
            'write_timeout': self.write_timeout,
            'cursorclass': DictCursor,
            'autocommit': False
        }

class DatabaseConnectionManager:
    """데이터베이스 연결 관리 클래스"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection_pool = []
        self._max_pool_size = config.max_connections
    
    def get_connection(self) -> Connection:
        """데이터베이스 연결 획득"""
        try:
            # 연결 풀에서 사용 가능한 연결 확인
            if self._connection_pool:
                connection = self._connection_pool.pop()
                if connection.open:
                    try:
                        # 실제 연결 상태 확인
                        connection.ping(reconnect=False)
                        return connection
                    except:
                        # 연결이 끊어진 경우 닫기
                        connection.close()
            
            # 새 연결 생성
            connection = pymysql.connect(**self.config.get_connection_params())
            logger.info("새로운 데이터베이스 연결이 생성되었습니다.")
            return connection
            
        except pymysql.Error as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise DatabaseConnectionError(f"데이터베이스 연결에 실패했습니다: {e}")
        except Exception as e:
            logger.error(f"예상치 못한 연결 오류: {e}")
            raise DatabaseConnectionError(f"데이터베이스 연결 중 오류가 발생했습니다: {e}")
    
    def return_connection(self, connection: Connection) -> None:
        """연결을 풀로 반환"""
        try:
            if connection and connection.open and len(self._connection_pool) < self._max_pool_size:
                # 트랜잭션 롤백 및 연결 상태 초기화
                connection.rollback()
                self._connection_pool.append(connection)
                logger.debug("연결이 풀로 반환되었습니다.")
            else:
                self.close_connection(connection)
        except Exception as e:
            logger.warning(f"연결 반환 중 오류: {e}")
            self.close_connection(connection)
    
    def close_connection(self, connection: Connection) -> None:
        """연결 종료"""
        try:
            if connection and connection.open:
                connection.close()
                logger.debug("데이터베이스 연결이 종료되었습니다.")
        except Exception as e:
            logger.warning(f"연결 종료 중 오류: {e}")
    
    def close_all_connections(self) -> None:
        """모든 연결 종료"""
        while self._connection_pool:
            connection = self._connection_pool.pop()
            self.close_connection(connection)
        logger.info("모든 데이터베이스 연결이 종료되었습니다.")

# 전역 인스턴스들
db_config = None
connection_manager = None

def init_db_config():
    """데이터베이스 설정 초기화"""
    global db_config, connection_manager
    if db_config is None:
        db_config = DatabaseConfig()
        connection_manager = DatabaseConnectionManager(db_config)

@contextmanager
def get_db_connection():
    """데이터베이스 연결 컨텍스트 매니저"""
    if connection_manager is None:
        init_db_config()
    
    connection = None
    try:
        connection = connection_manager.get_connection()
        yield connection
        # 성공 시 커밋
        connection.commit()
    except Exception as e:
        if connection:
            try:
                connection.rollback()
                logger.warning("트랜잭션이 롤백되었습니다.")
            except Exception as rollback_error:
                logger.error(f"롤백 중 오류: {rollback_error}")
        raise
    finally:
        if connection:
            connection_manager.return_connection(connection)

def test_database_connection() -> bool:
    """데이터베이스 연결 테스트"""
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                if result and result.get('test') == 1:
                    logger.info("데이터베이스 연결 테스트 성공")
                    return True
                else:
                    logger.error("데이터베이스 연결 테스트 실패: 예상치 못한 결과")
                    return False
    except Exception as e:
        logger.error(f"데이터베이스 연결 테스트 실패: {e}")
        return False

def initialize_database():
    """데이터베이스 초기화"""
    try:
        logger.info("데이터베이스 초기화를 시작합니다...")
        
        # 연결 테스트
        if not test_database_connection():
            raise DatabaseConnectionError("데이터베이스 연결 테스트에 실패했습니다.")
        
        logger.info("데이터베이스 초기화가 완료되었습니다.")
        return True
        
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        raise

def cleanup_database():
    """데이터베이스 정리"""
    try:
        if connection_manager:
            connection_manager.close_all_connections()
        logger.info("데이터베이스 정리가 완료되었습니다.")
    except Exception as e:
        logger.error(f"데이터베이스 정리 중 오류: {e}")

# 모듈 레벨에서 사용할 수 있는 모든 클래스와 함수들
__all__ = [
    'DatabaseConfig',
    'DatabaseConnectionManager', 
    'DatabaseConnectionError',
    'DatabaseQueryError',
    'DatabaseIntegrityError',
    'get_db_connection',
    'test_database_connection',
    'initialize_database',
    'cleanup_database',
    'init_db_config'
]