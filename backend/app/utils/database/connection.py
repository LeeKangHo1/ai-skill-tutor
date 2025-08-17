# backend/app/utils/database/connection.py
# 데이터베이스 연결 관리 및 기본 쿼리 실행 함수들 v2.0

import logging
import time
import threading
from typing import Optional, List, Dict, Any, Union, Tuple, Callable
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
import pymysql

from ...config.db_config import (
    get_db_connection, 
    DatabaseConnectionError, 
    DatabaseQueryError, 
    DatabaseIntegrityError,
    db_config,
    connection_manager
)

# 로깅 설정
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    데이터베이스 연결 클래스 v2.0
    MySQL 연결의 생성, 관리, 해제 및 자동 재연결을 담당합니다.
    """

    def __init__(self, config=None):
        """데이터베이스 연결 초기화"""
        from ...config.db_config import db_config, init_db_config
        
        if config is None:
            if db_config is None:
                init_db_config()
            self.config = db_config
        else:
            self.config = config
        
        self.connection = None
        self._last_ping_time = 0
        self._ping_interval = 30  # 30초마다 ping
        self._connection_lock = threading.Lock()

    def connect(self) -> Connection:
        """
        데이터베이스 연결 생성 v2.0
        
        Returns:
            Connection: PyMySQL 연결 객체
            
        Raises:
            DatabaseConnectionError: 연결 실패 시
        """
        with self._connection_lock:
            try:
                if self.connection and self.connection.open:
                    # 주기적 ping으로 연결 상태 확인
                    current_time = time.time()
                    if current_time - self._last_ping_time > self._ping_interval:
                        if self._ping_connection():
                            self._last_ping_time = current_time
                            return self.connection
                        else:
                            logger.warning("기존 연결이 비정상 상태입니다. 재연결을 시도합니다.")
                            self._close_connection()
                    else:
                        return self.connection
                
                # 새 연결 생성 (재시도 로직 포함)
                self.connection = self._create_connection_with_retry()
                self._last_ping_time = time.time()
                logger.info("데이터베이스 연결이 생성되었습니다.")
                return self.connection
                
            except Exception as e:
                error_msg = f"데이터베이스 연결 실패: {e}"
                logger.error(error_msg)
                raise DatabaseConnectionError(error_msg, e)

    def _create_connection_with_retry(self) -> Connection:
        """재시도 로직이 포함된 연결 생성"""
        attempts = 0
        last_error = None
        
        while attempts < self.config.max_reconnect_attempts:
            try:
                connection = pymysql.connect(**self.config.get_connection_params())
                logger.debug(f"연결 생성 성공 (시도: {attempts + 1})")
                return connection
                
            except pymysql.Error as e:
                attempts += 1
                last_error = e
                logger.warning(f"연결 생성 시도 {attempts}/{self.config.max_reconnect_attempts} 실패: {e}")
                
                if attempts < self.config.max_reconnect_attempts:
                    time.sleep(self.config.reconnect_delay)
        
        raise DatabaseConnectionError(f"연결 생성 실패 (최대 시도 횟수 초과): {last_error}")

    def _ping_connection(self) -> bool:
        """연결 상태 ping 확인"""
        try:
            if not self.connection or not self.connection.open:
                return False
            
            self.connection.ping(reconnect=False)
            
            # 추가 헬스체크 (설정된 경우)
            if self.config.enable_health_check:
                with self.connection.cursor() as cursor:
                    cursor.execute(self.config.health_check_query)
                    cursor.fetchone()
            
            return True
            
        except Exception as e:
            logger.debug(f"연결 ping 실패: {e}")
            return False

    def _close_connection(self) -> None:
        """내부 연결 종료"""
        try:
            if self.connection and self.connection.open:
                self.connection.close()
        except Exception as e:
            logger.warning(f"연결 종료 중 오류: {e}")
        finally:
            self.connection = None

    def disconnect(self) -> None:
        """
        데이터베이스 연결 해제 v2.0
        """
        with self._connection_lock:
            try:
                self._close_connection()
                logger.info("데이터베이스 연결이 해제되었습니다.")
            except Exception as e:
                logger.warning(f"연결 해제 중 오류: {e}")

    def is_connected(self) -> bool:
        """
        연결 상태 확인 v2.0
        
        Returns:
            bool: 연결 상태 (True: 연결됨, False: 연결 안됨)
        """
        with self._connection_lock:
            return self._ping_connection()

    def reconnect(self) -> Connection:
        """
        연결 재시도 v2.0
        
        Returns:
            Connection: 재연결된 PyMySQL 연결 객체
            
        Raises:
            DatabaseConnectionError: 재연결 실패 시
        """
        logger.info("데이터베이스 재연결을 시도합니다.")
        self.disconnect()
        return self.connect()

    def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """
        자동 재연결이 포함된 작업 실행
        
        Args:
            operation: 실행할 함수
            *args, **kwargs: 함수 인자들
            
        Returns:
            Any: 작업 결과
            
        Raises:
            DatabaseConnectionError: 재연결 실패 시
            DatabaseQueryError: 쿼리 실행 실패 시
        """
        attempts = 0
        last_error = None
        
        while attempts < self.config.max_reconnect_attempts:
            try:
                # 연결 확인 및 생성
                connection = self.connect()
                
                # 작업 실행
                return operation(connection, *args, **kwargs)
                
            except (pymysql.OperationalError, pymysql.InterfaceError) as e:
                # 연결 관련 오류 - 재시도
                attempts += 1
                last_error = e
                logger.warning(f"연결 오류로 재시도 {attempts}/{self.config.max_reconnect_attempts}: {e}")
                
                # 연결 초기화
                self.disconnect()
                
                if attempts < self.config.max_reconnect_attempts:
                    time.sleep(self.config.reconnect_delay)
                
            except Exception as e:
                # 다른 오류는 즉시 발생
                logger.error(f"작업 실행 중 오류: {e}")
                raise
        
        raise DatabaseConnectionError(f"자동 재연결 실패 (최대 시도 횟수 초과): {last_error}")

# ================================
# 기본 쿼리 실행 함수들
# ================================

def execute_query_with_retry(
    query: str, 
    params: Optional[Union[Tuple, Dict, List]] = None,
    fetch_result: bool = False,
    max_retries: int = 3
) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]], int]]:
    """
    자동 재연결이 포함된 SQL 쿼리 실행 함수 v2.0
    
    Args:
        query (str): 실행할 SQL 쿼리
        params (Optional[Union[Tuple, Dict, List]]): 쿼리 파라미터
        fetch_result (bool): 결과를 반환할지 여부
        max_retries (int): 최대 재시도 횟수
    
    Returns:
        Optional[Union[Dict, List[Dict], int]]: 
        - SELECT 쿼리: 결과 딕셔너리 또는 리스트
        - INSERT/UPDATE/DELETE: 영향받은 행 수
        - None: fetch_result=False인 경우
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
        DatabaseIntegrityError: 무결성 제약 위반 시
    """
    def _execute_operation(connection: Connection) -> Any:
        with connection.cursor() as cursor:
            # 쿼리 실행
            affected_rows = cursor.execute(query, params)
            
            # 결과 반환이 필요한 경우
            if fetch_result:
                # SELECT 쿼리인지 확인
                query_type = query.strip().upper().split()[0]
                if query_type == 'SELECT':
                    results = cursor.fetchall()
                    logger.debug(f"쿼리 실행 완료: {len(results)}개 행 조회")
                    return results
                else:
                    logger.debug(f"쿼리 실행 완료: {affected_rows}개 행 영향")
                    return affected_rows
            else:
                logger.debug(f"쿼리 실행 완료: {affected_rows}개 행 영향")
                return affected_rows
    
    # 재시도 로직
    attempts = 0
    last_error = None
    
    while attempts < max_retries:
        try:
            with get_db_connection() as connection:
                return _execute_operation(connection)
                
        except pymysql.IntegrityError as e:
            # 무결성 오류는 재시도하지 않음
            error_msg = f"데이터베이스 무결성 오류: {e}"
            logger.error(error_msg)
            raise DatabaseIntegrityError(error_msg, original_error=e)
            
        except (pymysql.OperationalError, pymysql.InterfaceError) as e:
            # 연결 관련 오류 - 재시도
            attempts += 1
            last_error = e
            logger.warning(f"연결 오류로 쿼리 재시도 {attempts}/{max_retries}: {e}")
            
            if attempts < max_retries:
                time.sleep(1.0)  # 1초 대기
            
        except pymysql.Error as e:
            error_msg = f"데이터베이스 쿼리 실행 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, query=query, params=params, original_error=e)
            
        except Exception as e:
            error_msg = f"예상치 못한 쿼리 실행 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, query=query, params=params, original_error=e)
    
    # 최대 재시도 횟수 초과
    error_msg = f"쿼리 실행 실패 (최대 재시도 횟수 초과): {last_error}"
    logger.error(error_msg)
    raise DatabaseQueryError(error_msg, query=query, params=params, original_error=last_error)

def execute_query(
    query: str, 
    params: Optional[Union[Tuple, Dict, List]] = None,
    fetch_result: bool = False
) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]], int]]:
    """
    SQL 쿼리 실행 함수 (기존 호환성 유지)
    
    Args:
        query (str): 실행할 SQL 쿼리
        params (Optional[Union[Tuple, Dict, List]]): 쿼리 파라미터
        fetch_result (bool): 결과를 반환할지 여부
    
    Returns:
        Optional[Union[Dict, List[Dict], int]]: 쿼리 실행 결과
    """
    return execute_query_with_retry(query, params, fetch_result)

def fetch_one_with_retry(
    query: str, 
    params: Optional[Union[Tuple, Dict, List]] = None,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    자동 재연결이 포함된 단일 레코드 조회 함수 v2.0
    
    Args:
        query (str): SELECT 쿼리
        params (Optional[Union[Tuple, Dict, List]]): 쿼리 파라미터
        max_retries (int): 최대 재시도 횟수
    
    Returns:
        Optional[Dict[str, Any]]: 조회된 레코드 또는 None
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
    """
    def _fetch_operation(connection: Connection) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result:
                logger.debug("단일 레코드 조회 성공")
            else:
                logger.debug("조회된 레코드가 없습니다")
            
            return result
    
    # 재시도 로직
    attempts = 0
    last_error = None
    
    while attempts < max_retries:
        try:
            with get_db_connection() as connection:
                return _fetch_operation(connection)
                
        except (pymysql.OperationalError, pymysql.InterfaceError) as e:
            # 연결 관련 오류 - 재시도
            attempts += 1
            last_error = e
            logger.warning(f"연결 오류로 조회 재시도 {attempts}/{max_retries}: {e}")
            
            if attempts < max_retries:
                time.sleep(1.0)
                
        except pymysql.Error as e:
            error_msg = f"단일 레코드 조회 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, query=query, params=params, original_error=e)
            
        except Exception as e:
            error_msg = f"예상치 못한 단일 레코드 조회 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, query=query, params=params, original_error=e)
    
    # 최대 재시도 횟수 초과
    error_msg = f"단일 레코드 조회 실패 (최대 재시도 횟수 초과): {last_error}"
    logger.error(error_msg)
    raise DatabaseQueryError(error_msg, query=query, params=params, original_error=last_error)

def fetch_all_with_retry(
    query: str, 
    params: Optional[Union[Tuple, Dict, List]] = None,
    max_retries: int = 3
) -> List[Dict[str, Any]]:
    """
    자동 재연결이 포함된 다중 레코드 조회 함수 v2.0
    
    Args:
        query (str): SELECT 쿼리
        params (Optional[Union[Tuple, Dict, List]]): 쿼리 파라미터
        max_retries (int): 최대 재시도 횟수
    
    Returns:
        List[Dict[str, Any]]: 조회된 레코드 리스트
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
    """
    def _fetch_all_operation(connection: Connection) -> List[Dict[str, Any]]:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            logger.debug(f"다중 레코드 조회 성공: {len(results)}개 행")
            return results
    
    # 재시도 로직
    attempts = 0
    last_error = None
    
    while attempts < max_retries:
        try:
            with get_db_connection() as connection:
                return _fetch_all_operation(connection)
                
        except (pymysql.OperationalError, pymysql.InterfaceError) as e:
            # 연결 관련 오류 - 재시도
            attempts += 1
            last_error = e
            logger.warning(f"연결 오류로 조회 재시도 {attempts}/{max_retries}: {e}")
            
            if attempts < max_retries:
                time.sleep(1.0)
                
        except pymysql.Error as e:
            error_msg = f"다중 레코드 조회 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, query=query, params=params, original_error=e)
            
        except Exception as e:
            error_msg = f"예상치 못한 다중 레코드 조회 오류: {e}"
            logger.error(error_msg)
            raise DatabaseQueryError(error_msg, query=query, params=params, original_error=e)
    
    # 최대 재시도 횟수 초과
    error_msg = f"다중 레코드 조회 실패 (최대 재시도 횟수 초과): {last_error}"
    logger.error(error_msg)
    raise DatabaseQueryError(error_msg, query=query, params=params, original_error=last_error)

def fetch_one(
    query: str, 
    params: Optional[Union[Tuple, Dict, List]] = None
) -> Optional[Dict[str, Any]]:
    """
    단일 레코드 조회 함수 (기존 호환성 유지)
    
    Args:
        query (str): SELECT 쿼리
        params (Optional[Union[Tuple, Dict, List]]): 쿼리 파라미터
    
    Returns:
        Optional[Dict[str, Any]]: 조회된 레코드 또는 None
    """
    return fetch_one_with_retry(query, params)

def fetch_all(
    query: str, 
    params: Optional[Union[Tuple, Dict, List]] = None
) -> List[Dict[str, Any]]:
    """
    다중 레코드 조회 함수 (기존 호환성 유지)
    
    Args:
        query (str): SELECT 쿼리
        params (Optional[Union[Tuple, Dict, List]]): 쿼리 파라미터
    
    Returns:
        List[Dict[str, Any]]: 조회된 레코드 리스트
    """
    return fetch_all_with_retry(query, params)

# v2.0 추가 유틸리티 함수들

def execute_batch_queries(
    queries: List[Tuple[str, Optional[Union[Tuple, Dict, List]]]],
    use_transaction: bool = True
) -> List[Any]:
    """
    배치 쿼리 실행 함수
    
    Args:
        queries: (쿼리, 파라미터) 튜플 리스트
        use_transaction: 트랜잭션 사용 여부
    
    Returns:
        List[Any]: 각 쿼리의 실행 결과 리스트
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
    """
    results = []
    
    try:
        with get_db_connection() as connection:
            if not use_transaction:
                connection.autocommit(True)
            
            try:
                for query, params in queries:
                    with connection.cursor() as cursor:
                        affected_rows = cursor.execute(query, params)
                        
                        # SELECT 쿼리인지 확인
                        query_type = query.strip().upper().split()[0]
                        if query_type == 'SELECT':
                            result = cursor.fetchall()
                        else:
                            result = affected_rows
                        
                        results.append(result)
                
                if use_transaction:
                    connection.commit()
                    
                logger.info(f"배치 쿼리 실행 완료: {len(queries)}개 쿼리")
                return results
                
            except Exception as e:
                if use_transaction:
                    connection.rollback()
                raise
            finally:
                if not use_transaction:
                    connection.autocommit(False)
                    
    except Exception as e:
        error_msg = f"배치 쿼리 실행 오류: {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg, original_error=e)

def check_connection_health() -> Dict[str, Any]:
    """
    연결 상태 확인 함수
    
    Returns:
        Dict[str, Any]: 연결 상태 정보
    """
    health_info = {
        'is_healthy': False,
        'connection_test': False,
        'pool_stats': {},
        'error': None
    }
    
    try:
        # 기본 연결 테스트
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                
                if result and result.get('test') == 1:
                    health_info['connection_test'] = True
        
        # 연결 풀 통계
        if connection_manager:
            health_info['pool_stats'] = connection_manager.get_pool_stats()
        
        health_info['is_healthy'] = health_info['connection_test']
        logger.debug("연결 상태 확인 완료")
        
    except Exception as e:
        health_info['error'] = str(e)
        logger.warning(f"연결 상태 확인 실패: {e}")
    
    return health_info
