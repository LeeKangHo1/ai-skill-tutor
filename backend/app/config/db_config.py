# backend/app/config/db_config.py
# 데이터베이스 연결 설정 및 관리 모듈 v2.0

import os
import pymysql
import logging
import time
import threading
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from queue import Queue, Empty
from dataclasses import dataclass
from enum import Enum

# 로깅 설정
logger = logging.getLogger(__name__)

class EnvironmentType(Enum):
    """환경 타입 열거형"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

# 커스텀 예외 클래스들
class DatabaseConnectionError(Exception):
    """데이터베이스 연결 오류"""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error

class DatabaseQueryError(Exception):
    """데이터베이스 쿼리 오류"""
    def __init__(self, message: str, query: str = None, params: tuple = None, original_error: Exception = None):
        super().__init__(message)
        self.query = query
        self.params = params
        self.original_error = original_error

class DatabaseIntegrityError(Exception):
    """데이터베이스 무결성 오류"""
    def __init__(self, message: str, constraint_name: str = None, original_error: Exception = None):
        super().__init__(message)
        self.constraint_name = constraint_name
        self.original_error = original_error

@dataclass
class ConnectionPoolConfig:
    """연결 풀 설정 클래스"""
    min_connections: int = 5
    max_connections: int = 20
    max_idle_time: int = 300  # 5분
    health_check_interval: int = 60  # 1분
    connection_retry_attempts: int = 3
    connection_retry_delay: float = 1.0

class DatabaseConfig:
    """데이터베이스 설정 클래스 v2.0"""
    
    def __init__(self, environment: Optional[str] = None):
        """환경변수에서 데이터베이스 설정 로드"""
        # 환경 설정
        self.environment = EnvironmentType(environment or os.getenv('FLASK_ENV', 'development'))
        
        # 기본 연결 설정
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.charset = os.getenv('DB_CHARSET', 'utf8mb4')
        
        # 기본 타임아웃 설정
        self.connect_timeout = int(os.getenv('DB_CONNECT_TIMEOUT', 10))
        self.read_timeout = int(os.getenv('DB_READ_TIMEOUT', 10))
        self.write_timeout = int(os.getenv('DB_WRITE_TIMEOUT', 10))
        
        # v2.0 연결 풀 설정 (환경별 최적화)
        self.pool_config = self._get_pool_config_by_environment()
        
        # v2.0 헬스체크 설정
        self.enable_health_check = os.getenv('DB_ENABLE_HEALTH_CHECK', 'true').lower() == 'true'
        self.health_check_query = os.getenv('DB_HEALTH_CHECK_QUERY', 'SELECT 1')
        
        # v2.0 자동 재연결 설정
        self.enable_auto_reconnect = os.getenv('DB_ENABLE_AUTO_RECONNECT', 'true').lower() == 'true'
        self.max_reconnect_attempts = int(os.getenv('DB_MAX_RECONNECT_ATTEMPTS', 3))
        self.reconnect_delay = float(os.getenv('DB_RECONNECT_DELAY', 1.0))
        
        # SSL 설정 (운영 환경용)
        self.ssl_disabled = os.getenv('DB_SSL_DISABLED', 'false').lower() == 'true'
        self.ssl_ca = os.getenv('DB_SSL_CA')
        self.ssl_cert = os.getenv('DB_SSL_CERT')
        self.ssl_key = os.getenv('DB_SSL_KEY')
        
        # 설정 검증
        self._validate_config()
    
    def _get_pool_config_by_environment(self) -> ConnectionPoolConfig:
        """환경별 연결 풀 설정 반환"""
        if self.environment == EnvironmentType.DEVELOPMENT:
            return ConnectionPoolConfig(
                min_connections=int(os.getenv('DB_MIN_CONNECTIONS', 2)),
                max_connections=int(os.getenv('DB_MAX_CONNECTIONS', 10)),
                max_idle_time=int(os.getenv('DB_MAX_IDLE_TIME', 600)),  # 10분
                health_check_interval=int(os.getenv('DB_HEALTH_CHECK_INTERVAL', 120)),  # 2분
                connection_retry_attempts=int(os.getenv('DB_RETRY_ATTEMPTS', 3)),
                connection_retry_delay=float(os.getenv('DB_RETRY_DELAY', 1.0))
            )
        elif self.environment == EnvironmentType.TESTING:
            return ConnectionPoolConfig(
                min_connections=int(os.getenv('DB_MIN_CONNECTIONS', 1)),
                max_connections=int(os.getenv('DB_MAX_CONNECTIONS', 5)),
                max_idle_time=int(os.getenv('DB_MAX_IDLE_TIME', 300)),  # 5분
                health_check_interval=int(os.getenv('DB_HEALTH_CHECK_INTERVAL', 60)),  # 1분
                connection_retry_attempts=int(os.getenv('DB_RETRY_ATTEMPTS', 2)),
                connection_retry_delay=float(os.getenv('DB_RETRY_DELAY', 0.5))
            )
        else:  # PRODUCTION
            return ConnectionPoolConfig(
                min_connections=int(os.getenv('DB_MIN_CONNECTIONS', 5)),
                max_connections=int(os.getenv('DB_MAX_CONNECTIONS', 20)),
                max_idle_time=int(os.getenv('DB_MAX_IDLE_TIME', 300)),  # 5분
                health_check_interval=int(os.getenv('DB_HEALTH_CHECK_INTERVAL', 30)),  # 30초
                connection_retry_attempts=int(os.getenv('DB_RETRY_ATTEMPTS', 5)),
                connection_retry_delay=float(os.getenv('DB_RETRY_DELAY', 2.0))
            )
    
    def _validate_config(self) -> None:
        """데이터베이스 설정 검증"""
        required_fields = ['database', 'user', 'password']
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        
        if missing_fields:
            raise ValueError(f"필수 데이터베이스 설정이 누락되었습니다: {', '.join(missing_fields)}")
    
    def get_connection_params(self) -> Dict[str, Any]:
        """PyMySQL 연결 파라미터 반환 v2.0"""
        params = {
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
            'autocommit': False,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'use_unicode': True
        }
        
        # SSL 설정 추가 (운영 환경)
        if not self.ssl_disabled and self.environment == EnvironmentType.PRODUCTION:
            ssl_config = {}
            if self.ssl_ca:
                ssl_config['ca'] = self.ssl_ca
            if self.ssl_cert:
                ssl_config['cert'] = self.ssl_cert
            if self.ssl_key:
                ssl_config['key'] = self.ssl_key
            
            if ssl_config:
                params['ssl'] = ssl_config
        
        return params

@dataclass
class PooledConnection:
    """풀링된 연결 정보"""
    connection: Connection
    created_at: float
    last_used_at: float
    is_healthy: bool = True

class DatabaseConnectionManager:
    """데이터베이스 연결 관리 클래스 v2.0"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool_config = config.pool_config
        
        # v2.0 연결 풀 (Queue 기반으로 스레드 안전성 보장)
        self._connection_pool: Queue[PooledConnection] = Queue(maxsize=self.pool_config.max_connections)
        self._active_connections: List[PooledConnection] = []
        self._pool_lock = threading.Lock()
        
        # v2.0 헬스체크 스레드
        self._health_check_thread = None
        self._health_check_running = False
        
        # 연결 통계
        self._total_connections_created = 0
        self._total_connections_closed = 0
        
        # 초기 연결 풀 생성
        self._initialize_pool()
        
        # 헬스체크 시작
        if self.config.enable_health_check:
            self._start_health_check()
    
    def _initialize_pool(self) -> None:
        """초기 연결 풀 생성"""
        logger.info(f"연결 풀 초기화 시작 (최소: {self.pool_config.min_connections}개)")
        
        for _ in range(self.pool_config.min_connections):
            try:
                connection = self._create_new_connection()
                pooled_conn = PooledConnection(
                    connection=connection,
                    created_at=time.time(),
                    last_used_at=time.time()
                )
                self._connection_pool.put(pooled_conn, block=False)
                logger.debug("초기 연결이 풀에 추가되었습니다.")
            except Exception as e:
                logger.warning(f"초기 연결 생성 실패: {e}")
        
        logger.info(f"연결 풀 초기화 완료 (현재: {self._connection_pool.qsize()}개)")
    
    def _create_new_connection(self) -> Connection:
        """새로운 데이터베이스 연결 생성"""
        attempts = 0
        last_error = None
        
        while attempts < self.pool_config.connection_retry_attempts:
            try:
                connection = pymysql.connect(**self.config.get_connection_params())
                self._total_connections_created += 1
                logger.debug(f"새로운 연결 생성 성공 (총 생성: {self._total_connections_created})")
                return connection
                
            except pymysql.Error as e:
                attempts += 1
                last_error = e
                logger.warning(f"연결 생성 시도 {attempts}/{self.pool_config.connection_retry_attempts} 실패: {e}")
                
                if attempts < self.pool_config.connection_retry_attempts:
                    time.sleep(self.pool_config.connection_retry_delay)
        
        raise DatabaseConnectionError(f"연결 생성 실패 (최대 시도 횟수 초과): {last_error}")
    
    def get_connection(self) -> Connection:
        """데이터베이스 연결 획득 v2.0"""
        try:
            # 풀에서 사용 가능한 연결 확인
            try:
                pooled_conn = self._connection_pool.get(block=False)
                
                # 연결 상태 확인
                if self._is_connection_healthy(pooled_conn.connection):
                    pooled_conn.last_used_at = time.time()
                    with self._pool_lock:
                        self._active_connections.append(pooled_conn)
                    logger.debug("풀에서 기존 연결 재사용")
                    return pooled_conn.connection
                else:
                    # 비정상 연결 제거
                    self._close_connection(pooled_conn.connection)
                    logger.debug("비정상 연결 제거됨")
                    
            except Empty:
                # 풀이 비어있음
                pass
            
            # 새 연결 생성 (최대 연결 수 확인)
            with self._pool_lock:
                total_connections = len(self._active_connections) + self._connection_pool.qsize()
                
                if total_connections >= self.pool_config.max_connections:
                    raise DatabaseConnectionError(f"최대 연결 수 초과 ({self.pool_config.max_connections})")
            
            # 새 연결 생성
            connection = self._create_new_connection()
            pooled_conn = PooledConnection(
                connection=connection,
                created_at=time.time(),
                last_used_at=time.time()
            )
            
            with self._pool_lock:
                self._active_connections.append(pooled_conn)
            
            logger.debug("새로운 연결 생성 및 할당")
            return connection
            
        except Exception as e:
            logger.error(f"연결 획득 실패: {e}")
            raise DatabaseConnectionError(f"데이터베이스 연결 획득 실패: {e}")
    
    def return_connection(self, connection: Connection) -> None:
        """연결을 풀로 반환 v2.0"""
        try:
            with self._pool_lock:
                # 활성 연결 목록에서 찾기
                pooled_conn = None
                for conn in self._active_connections:
                    if conn.connection == connection:
                        pooled_conn = conn
                        self._active_connections.remove(conn)
                        break
                
                if not pooled_conn:
                    logger.warning("반환하려는 연결이 활성 목록에 없습니다.")
                    self._close_connection(connection)
                    return
            
            # 연결 상태 확인 및 초기화
            try:
                if connection.open:
                    connection.rollback()  # 트랜잭션 롤백
                    
                    # 연결이 건강하고 풀에 공간이 있으면 반환
                    if (self._is_connection_healthy(connection) and 
                        self._connection_pool.qsize() < self.pool_config.max_connections):
                        
                        pooled_conn.last_used_at = time.time()
                        self._connection_pool.put(pooled_conn, block=False)
                        logger.debug("연결이 풀로 반환되었습니다.")
                        return
                
            except Exception as e:
                logger.warning(f"연결 반환 중 오류: {e}")
            
            # 연결 종료
            self._close_connection(connection)
            
        except Exception as e:
            logger.error(f"연결 반환 처리 중 오류: {e}")
            self._close_connection(connection)
    
    def _is_connection_healthy(self, connection: Connection) -> bool:
        """연결 상태 확인 v2.0"""
        try:
            if not connection or not connection.open:
                return False
            
            # 실제 연결 상태 확인
            connection.ping(reconnect=False)
            
            # 헬스체크 쿼리 실행
            if self.config.enable_health_check:
                with connection.cursor() as cursor:
                    cursor.execute(self.config.health_check_query)
                    cursor.fetchone()
            
            return True
            
        except Exception as e:
            logger.debug(f"연결 상태 확인 실패: {e}")
            return False
    
    def _close_connection(self, connection: Connection) -> None:
        """연결 종료 v2.0"""
        try:
            if connection and connection.open:
                connection.close()
                self._total_connections_closed += 1
                logger.debug(f"연결 종료 (총 종료: {self._total_connections_closed})")
        except Exception as e:
            logger.warning(f"연결 종료 중 오류: {e}")
    
    def _start_health_check(self) -> None:
        """헬스체크 스레드 시작"""
        if self._health_check_thread and self._health_check_thread.is_alive():
            return
        
        self._health_check_running = True
        self._health_check_thread = threading.Thread(target=self._health_check_worker, daemon=True)
        self._health_check_thread.start()
        logger.info("헬스체크 스레드가 시작되었습니다.")
    
    def _health_check_worker(self) -> None:
        """헬스체크 워커 스레드"""
        while self._health_check_running:
            try:
                time.sleep(self.pool_config.health_check_interval)
                self._perform_health_check()
            except Exception as e:
                logger.error(f"헬스체크 중 오류: {e}")
    
    def _perform_health_check(self) -> None:
        """헬스체크 수행"""
        current_time = time.time()
        unhealthy_connections = []
        
        # 풀의 연결들 확인
        temp_connections = []
        
        while not self._connection_pool.empty():
            try:
                pooled_conn = self._connection_pool.get(block=False)
                
                # 유휴 시간 확인
                idle_time = current_time - pooled_conn.last_used_at
                if idle_time > self.pool_config.max_idle_time:
                    unhealthy_connections.append(pooled_conn)
                    continue
                
                # 연결 상태 확인
                if self._is_connection_healthy(pooled_conn.connection):
                    temp_connections.append(pooled_conn)
                else:
                    unhealthy_connections.append(pooled_conn)
                    
            except Empty:
                break
        
        # 건강한 연결들 다시 풀에 추가
        for conn in temp_connections:
            try:
                self._connection_pool.put(conn, block=False)
            except:
                unhealthy_connections.append(conn)
        
        # 비정상 연결들 종료
        for conn in unhealthy_connections:
            self._close_connection(conn.connection)
        
        if unhealthy_connections:
            logger.info(f"헬스체크: {len(unhealthy_connections)}개 비정상 연결 제거")
        
        # 최소 연결 수 유지
        current_pool_size = self._connection_pool.qsize()
        if current_pool_size < self.pool_config.min_connections:
            needed = self.pool_config.min_connections - current_pool_size
            logger.info(f"최소 연결 수 유지: {needed}개 연결 추가")
            
            for _ in range(needed):
                try:
                    connection = self._create_new_connection()
                    pooled_conn = PooledConnection(
                        connection=connection,
                        created_at=time.time(),
                        last_used_at=time.time()
                    )
                    self._connection_pool.put(pooled_conn, block=False)
                except Exception as e:
                    logger.warning(f"최소 연결 수 유지 중 연결 생성 실패: {e}")
                    break
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """연결 풀 통계 반환"""
        with self._pool_lock:
            return {
                'pool_size': self._connection_pool.qsize(),
                'active_connections': len(self._active_connections),
                'total_created': self._total_connections_created,
                'total_closed': self._total_connections_closed,
                'max_connections': self.pool_config.max_connections,
                'min_connections': self.pool_config.min_connections
            }
    
    def close_all_connections(self) -> None:
        """모든 연결 종료 v2.0"""
        # 헬스체크 중지
        self._health_check_running = False
        if self._health_check_thread and self._health_check_thread.is_alive():
            self._health_check_thread.join(timeout=5)
        
        # 활성 연결들 종료
        with self._pool_lock:
            for pooled_conn in self._active_connections:
                self._close_connection(pooled_conn.connection)
            self._active_connections.clear()
        
        # 풀의 연결들 종료
        while not self._connection_pool.empty():
            try:
                pooled_conn = self._connection_pool.get(block=False)
                self._close_connection(pooled_conn.connection)
            except Empty:
                break
        
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
    """데이터베이스 연결 테스트 v2.0"""
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # 기본 연결 테스트
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                if not (result and result.get('test') == 1):
                    logger.error("데이터베이스 연결 테스트 실패: 예상치 못한 결과")
                    return False
                
                # 데이터베이스 버전 확인
                cursor.execute("SELECT VERSION() as version")
                version_result = cursor.fetchone()
                if version_result:
                    logger.info(f"데이터베이스 연결 테스트 성공 - MySQL 버전: {version_result.get('version')}")
                
                # 현재 데이터베이스 확인
                cursor.execute("SELECT DATABASE() as current_db")
                db_result = cursor.fetchone()
                if db_result:
                    logger.info(f"현재 데이터베이스: {db_result.get('current_db')}")
                
                return True
                
    except Exception as e:
        logger.error(f"데이터베이스 연결 테스트 실패: {e}")
        return False

def test_database_health() -> Dict[str, Any]:
    """데이터베이스 상태 확인 v2.0"""
    health_info = {
        'connection_test': False,
        'pool_stats': {},
        'environment': None,
        'error': None
    }
    
    try:
        # 연결 테스트
        health_info['connection_test'] = test_database_connection()
        
        # 환경 정보
        if db_config:
            health_info['environment'] = db_config.environment.value
        
        # 연결 풀 통계
        if connection_manager:
            health_info['pool_stats'] = connection_manager.get_pool_stats()
        
        logger.info("데이터베이스 상태 확인 완료")
        
    except Exception as e:
        health_info['error'] = str(e)
        logger.error(f"데이터베이스 상태 확인 실패: {e}")
    
    return health_info

def initialize_database():
    """데이터베이스 초기화 v2.0"""
    try:
        logger.info("데이터베이스 초기화를 시작합니다...")
        
        # 설정 초기화
        init_db_config()
        
        # 연결 테스트
        if not test_database_connection():
            raise DatabaseConnectionError("데이터베이스 연결 테스트에 실패했습니다.")
        
        # 상태 확인
        health_info = test_database_health()
        logger.info(f"데이터베이스 환경: {health_info.get('environment')}")
        logger.info(f"연결 풀 상태: {health_info.get('pool_stats')}")
        
        logger.info("데이터베이스 초기화가 완료되었습니다.")
        return True
        
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        raise

def cleanup_database():
    """데이터베이스 정리 v2.0"""
    try:
        if connection_manager:
            # 연결 풀 통계 로깅
            stats = connection_manager.get_pool_stats()
            logger.info(f"정리 전 연결 풀 상태: {stats}")
            
            # 모든 연결 종료
            connection_manager.close_all_connections()
        
        logger.info("데이터베이스 정리가 완료되었습니다.")
    except Exception as e:
        logger.error(f"데이터베이스 정리 중 오류: {e}")

# 모듈 레벨에서 사용할 수 있는 모든 클래스와 함수들 v2.0
__all__ = [
    'EnvironmentType',
    'ConnectionPoolConfig',
    'DatabaseConfig',
    'DatabaseConnectionManager', 
    'DatabaseConnectionError',
    'DatabaseQueryError',
    'DatabaseIntegrityError',
    'get_db_connection',
    'test_database_connection',
    'test_database_health',
    'initialize_database',
    'cleanup_database',
    'init_db_config'
]