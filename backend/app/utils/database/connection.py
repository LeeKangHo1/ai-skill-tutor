# backend/app/utils/database/connection.py
# 데이터베이스 연결 관리 및 기본 쿼리 실행 함수들

import logging
from typing import Optional, List, Dict, Any, Union, Tuple
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
import pymysql

from ...config.db_config import (
    get_db_connection, 
    DatabaseConnectionError, 
    DatabaseQueryError, 
    DatabaseIntegrityError
)

# 로깅 설정
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    데이터베이스 연결 클래스
    MySQL 연결의 생성, 관리, 해제를 담당합니다.
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

    def connect(self) -> Connection:
        """
        데이터베이스 연결 생성
        
        Returns:
            Connection: PyMySQL 연결 객체
            
        Raises:
            DatabaseConnectionError: 연결 실패 시
        """
        try:
            if self.connection and self.connection.open:
                return self.connection
                
            self.connection = pymysql.connect(**self.config.get_connection_params())
            logger.info("데이터베이스 연결이 생성되었습니다.")
            return self.connection
            
        except pymysql.Error as e:
            error_msg = f"데이터베이스 연결 실패: {e}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg, e)

    def disconnect(self) -> None:
        """
        데이터베이스 연결 해제
        """
        try:
            if self.connection and self.connection.open:
                self.connection.close()
                logger.info("데이터베이스 연결이 해제되었습니다.")
        except Exception as e:
            logger.warning(f"연결 해제 중 오류: {e}")
        finally:
            self.connection = None

    def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            bool: 연결 상태 (True: 연결됨, False: 연결 안됨)
        """
        try:
            if not self.connection or not self.connection.open:
                return False
            
            # 실제 연결 상태 확인
            self.connection.ping(reconnect=False)
            return True
        except:
            return False

    def reconnect(self) -> Connection:
        """
        연결 재시도
        
        Returns:
            Connection: 재연결된 PyMySQL 연결 객체
            
        Raises:
            DatabaseConnectionError: 재연결 실패 시
        """
        logger.info("데이터베이스 재연결을 시도합니다.")
        self.disconnect()
        return self.connect()

# ================================
# 기본 쿼리 실행 함수들
# ================================

def execute_query(
    query: str, 
    params: Optional[Union[Tuple, Dict, List]] = None,
    fetch_result: bool = False
) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]], int]]:
    """
    SQL 쿼리 실행 함수
    
    Args:
        query (str): 실행할 SQL 쿼리
        params (Optional[Union[Tuple, Dict, List]]): 쿼리 파라미터
        fetch_result (bool): 결과를 반환할지 여부
    
    Returns:
        Optional[Union[Dict, List[Dict], int]]: 
        - SELECT 쿼리: 결과 딕셔너리 또는 리스트
        - INSERT/UPDATE/DELETE: 영향받은 행 수
        - None: fetch_result=False인 경우
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
        DatabaseIntegrityError: 무결성 제약 위반 시
    """
    try:
        with get_db_connection() as connection:
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
                    
    except pymysql.IntegrityError as e:
        error_msg = f"데이터베이스 무결성 오류: {e}"
        logger.error(error_msg)
        raise DatabaseIntegrityError(error_msg)
    except pymysql.Error as e:
        error_msg = f"데이터베이스 쿼리 실행 오류: {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)
    except Exception as e:
        error_msg = f"예상치 못한 쿼리 실행 오류: {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)

def fetch_one(
    query: str, 
    params: Optional[Union[Tuple, Dict, List]] = None
) -> Optional[Dict[str, Any]]:
    """
    단일 레코드 조회 함수
    
    Args:
        query (str): SELECT 쿼리
        params (Optional[Union[Tuple, Dict, List]]): 쿼리 파라미터
    
    Returns:
        Optional[Dict[str, Any]]: 조회된 레코드 또는 None
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
    """
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                
                if result:
                    logger.debug("단일 레코드 조회 성공")
                else:
                    logger.debug("조회된 레코드가 없습니다")
                
                return result
                
    except pymysql.Error as e:
        error_msg = f"단일 레코드 조회 오류: {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)
    except Exception as e:
        error_msg = f"예상치 못한 단일 레코드 조회 오류: {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)

def fetch_all(
    query: str, 
    params: Optional[Union[Tuple, Dict, List]] = None
) -> List[Dict[str, Any]]:
    """
    다중 레코드 조회 함수
    
    Args:
        query (str): SELECT 쿼리
        params (Optional[Union[Tuple, Dict, List]]): 쿼리 파라미터
    
    Returns:
        List[Dict[str, Any]]: 조회된 레코드 리스트
    
    Raises:
        DatabaseQueryError: 쿼리 실행 실패 시
    """
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                logger.debug(f"다중 레코드 조회 성공: {len(results)}개 행")
                return results
                
    except pymysql.Error as e:
        error_msg = f"다중 레코드 조회 오류: {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)
    except Exception as e:
        error_msg = f"예상치 못한 다중 레코드 조회 오류: {e}"
        logger.error(error_msg)
        raise DatabaseQueryError(error_msg)
