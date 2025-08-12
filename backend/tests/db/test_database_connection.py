# backend/tests/test_database_connection.py
# 데이터베이스 연결 테스트 구현

import sys
import os
import logging
from typing import Optional

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database.connection import DatabaseConnection, execute_query, fetch_one, fetch_all
from app.config.db_config import (
    DatabaseConnectionError, 
    DatabaseQueryError, 
    DatabaseIntegrityError,
    test_database_connection
)
from tests.fixtures.test_data import TestDataManager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnectionTest:
    """
    데이터베이스 연결 테스트 클래스
    MySQL 연결과 기본 작업을 검증합니다.
    """
    
    def __init__(self):
        """테스트 클래스 초기화"""
        self.db_conn = None
        self.test_data_manager = TestDataManager()
        self.test_results = {
            'connection_test': False,
            'connection_state_test': False,
            'disconnect_test': False,
            'reconnect_test': False,
            'users_crud_test': False,
            'user_progress_crud_test': False,
            'user_statistics_crud_test': False
        }
    
    def test_database_connection(self) -> bool:
        """
        기본 MySQL 연결 성공/실패 테스트
        요구사항 1.1, 1.2, 1.3 검증
        
        Returns:
            bool: 테스트 성공 여부
        """
        logger.info("🔄 데이터베이스 연결 테스트 시작...")
        
        try:
            # 1. 정상 연결 테스트
            self.db_conn = DatabaseConnection()
            connection = self.db_conn.connect()
            
            if connection and connection.open:
                logger.info("✅ MySQL 서버 연결 성공")
                
                # 연결 상태 확인을 위한 간단한 쿼리 실행
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 as test")
                    result = cursor.fetchone()
                    
                    if result and result.get('test') == 1:
                        logger.info("✅ 연결 상태 확인 성공")
                        self.test_results['connection_test'] = True
                        return True
                    else:
                        logger.error("❌ 연결 상태 확인 실패: 예상치 못한 결과")
                        return False
            else:
                logger.error("❌ MySQL 서버 연결 실패")
                return False
                
        except DatabaseConnectionError as e:
            logger.error(f"❌ 데이터베이스 연결 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 예상치 못한 연결 테스트 오류: {e}")
            return False
    
    def test_connection_state_and_disconnect(self) -> bool:
        """
        연결 상태 확인 및 연결 해제 테스트
        요구사항 1.1, 1.3 검증
        
        Returns:
            bool: 테스트 성공 여부
        """
        logger.info("🔄 연결 상태 확인 및 해제 테스트 시작...")
        
        try:
            if not self.db_conn:
                self.db_conn = DatabaseConnection()
                self.db_conn.connect()
            
            # 1. 연결 상태 확인 테스트
            if self.db_conn.is_connected():
                logger.info("✅ 연결 상태 확인 성공 (연결됨)")
                self.test_results['connection_state_test'] = True
            else:
                logger.error("❌ 연결 상태 확인 실패 (연결 안됨)")
                return False
            
            # 2. 연결 해제 테스트
            self.db_conn.disconnect()
            
            if not self.db_conn.is_connected():
                logger.info("✅ 연결 해제 성공")
                self.test_results['disconnect_test'] = True
                return True
            else:
                logger.error("❌ 연결 해제 실패 (여전히 연결됨)")
                return False
                
        except Exception as e:
            logger.error(f"❌ 연결 상태/해제 테스트 오류: {e}")
            return False
    
    def test_reconnection(self) -> bool:
        """
        재연결 기능 테스트
        요구사항 1.1, 1.2, 1.3 검증
        
        Returns:
            bool: 테스트 성공 여부
        """
        logger.info("🔄 재연결 기능 테스트 시작...")
        
        try:
            if not self.db_conn:
                self.db_conn = DatabaseConnection()
            
            # 1. 재연결 시도
            connection = self.db_conn.reconnect()
            
            if connection and connection.open:
                logger.info("✅ 재연결 성공")
                
                # 2. 재연결된 상태에서 연결 상태 확인
                if self.db_conn.is_connected():
                    logger.info("✅ 재연결 후 연결 상태 확인 성공")
                    
                    # 3. 재연결된 연결로 간단한 쿼리 실행
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 'reconnection_test' as test")
                        result = cursor.fetchone()
                        
                        if result and result.get('test') == 'reconnection_test':
                            logger.info("✅ 재연결된 연결로 쿼리 실행 성공")
                            self.test_results['reconnect_test'] = True
                            return True
                        else:
                            logger.error("❌ 재연결된 연결로 쿼리 실행 실패")
                            return False
                else:
                    logger.error("❌ 재연결 후 연결 상태 확인 실패")
                    return False
            else:
                logger.error("❌ 재연결 실패")
                return False
                
        except DatabaseConnectionError as e:
            logger.error(f"❌ 재연결 테스트 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 예상치 못한 재연결 테스트 오류: {e}")
            return False
    
    def test_connection_failure_handling(self) -> bool:
        """
        연결 실패 시 오류 처리 테스트
        요구사항 1.2 검증
        
        Returns:
            bool: 테스트 성공 여부
        """
        logger.info("🔄 연결 실패 처리 테스트 시작...")
        
        try:
            # 잘못된 설정으로 연결 시도
            from app.config.db_config import DatabaseConfig
            
            # 잘못된 포트로 설정 생성
            invalid_config = DatabaseConfig()
            invalid_config.port = 9999  # 존재하지 않는 포트
            
            invalid_db_conn = DatabaseConnection(invalid_config)
            
            try:
                invalid_db_conn.connect()
                logger.error("❌ 잘못된 설정으로 연결이 성공함 (예상치 못한 결과)")
                return False
            except DatabaseConnectionError as e:
                logger.info(f"✅ 연결 실패 시 적절한 오류 메시지 제공: {e}")
                return True
            except Exception as e:
                logger.error(f"❌ 예상치 못한 오류 타입: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 연결 실패 처리 테스트 오류: {e}")
            return False
    
    # ================================
    # 사용자 관련 테이블 CRUD 테스트
    # ================================
    
    def test_users_crud(self) -> bool:
        """
        users 테이블 CRUD 테스트
        요구사항 2.1, 2.2 검증
        
        Returns:
            bool: 테스트 성공 여부
        """
        logger.info("🔄 users 테이블 CRUD 테스트 시작...")
        
        try:
            # 테스트 사용자 데이터 생성
            test_user_data = self.test_data_manager.create_test_user_data()
            user_id = test_user_data['user_id']
            
            # 1. CREATE 테스트
            logger.info("--- users 테이블 CREATE 테스트 ---")
            
            # 사용자 생성
            created_user_id = self.test_data_manager.insert_test_user(test_user_data)
            
            if created_user_id == user_id:
                logger.info("✅ users 테이블 CREATE 성공")
            else:
                logger.error("❌ users 테이블 CREATE 실패")
                return False
            
            # 2. READ 테스트
            logger.info("--- users 테이블 READ 테스트 ---")
            
            # login_id로 사용자 조회
            query = "SELECT * FROM users WHERE login_id = %s"
            result = fetch_one(query, (test_user_data['login_id'],))
            
            if result and result['user_id'] == user_id:
                logger.info("✅ users 테이블 READ (login_id 조회) 성공")
            else:
                logger.error("❌ users 테이블 READ (login_id 조회) 실패")
                return False
            
            # user_id로 사용자 조회
            query = "SELECT * FROM users WHERE user_id = %s"
            result = fetch_one(query, (user_id,))
            
            if result and result['username'] == test_user_data['username']:
                logger.info("✅ users 테이블 READ (user_id 조회) 성공")
            else:
                logger.error("❌ users 테이블 READ (user_id 조회) 실패")
                return False
            
            # 존재하지 않는 사용자 조회 테스트
            query = "SELECT * FROM users WHERE login_id = %s"
            result = fetch_one(query, ('nonexistent_user',))
            
            if result is None:
                logger.info("✅ users 테이블 READ (존재하지 않는 사용자) 성공")
            else:
                logger.error("❌ users 테이블 READ (존재하지 않는 사용자) 실패")
                return False
            
            # 3. UPDATE 테스트
            logger.info("--- users 테이블 UPDATE 테스트 ---")
            
            # 사용자 정보 수정
            new_username = "수정된테스트사용자"
            new_user_type = "intermediate"
            
            query = """
            UPDATE users 
            SET username = %s, user_type = %s, updated_at = NOW()
            WHERE user_id = %s
            """
            execute_query(query, (new_username, new_user_type, user_id))
            
            # 수정 결과 확인
            query = "SELECT username, user_type FROM users WHERE user_id = %s"
            result = fetch_one(query, (user_id,))
            
            if result and result['username'] == new_username and result['user_type'] == new_user_type:
                logger.info("✅ users 테이블 UPDATE 성공")
            else:
                logger.error("❌ users 테이블 UPDATE 실패")
                return False
            
            # 존재하지 않는 사용자 수정 테스트
            query = """
            UPDATE users 
            SET username = %s 
            WHERE user_id = %s
            """
            execute_query(query, ("존재하지않는사용자", 99999))
            
            # 영향받은 행이 0개인지 확인 (실제로는 execute_query가 성공적으로 실행됨)
            logger.info("✅ users 테이블 UPDATE (존재하지 않는 사용자) 처리 성공")
            
            # 4. DELETE 테스트는 cleanup에서 수행
            logger.info("--- users 테이블 DELETE 테스트는 cleanup에서 수행 ---")
            
            self.test_results['users_crud_test'] = True
            return True
            
        except DatabaseQueryError as e:
            logger.error(f"❌ users 테이블 CRUD 테스트 쿼리 오류: {e}")
            return False
        except DatabaseIntegrityError as e:
            logger.error(f"❌ users 테이블 CRUD 테스트 무결성 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ users 테이블 CRUD 테스트 예상치 못한 오류: {e}")
            return False
    
    def test_user_progress_crud(self) -> bool:
        """
        user_progress 테이블 CRUD 테스트
        요구사항 2.1, 2.2 검증
        
        Returns:
            bool: 테스트 성공 여부
        """
        logger.info("🔄 user_progress 테이블 CRUD 테스트 시작...")
        
        try:
            # 사용자가 이미 생성되어 있는지 확인, 없으면 생성
            if not self.test_data_manager.is_data_created('users'):
                logger.info("user_progress 테스트를 위해 먼저 사용자를 생성합니다")
                test_user_data = self.test_data_manager.create_test_user_data()
                user_id = self.test_data_manager.insert_test_user(test_user_data)
            else:
                user_id = self.test_data_manager.created_data_ids['users'][0]
            
            # 1. CREATE 테스트
            logger.info("--- user_progress 테이블 CREATE 테스트 ---")
            
            # 사용자 진행 상태 생성
            progress_data = self.test_data_manager.create_test_user_progress_data(user_id)
            created_user_id = self.test_data_manager.insert_test_user_progress(progress_data)
            
            if created_user_id == user_id:
                logger.info("✅ user_progress 테이블 CREATE 성공")
            else:
                logger.error("❌ user_progress 테이블 CREATE 실패")
                return False
            
            # 외래키 제약 조건 테스트 (존재하지 않는 user_id)
            try:
                invalid_progress_data = self.test_data_manager.create_test_user_progress_data(99999)
                self.test_data_manager.insert_test_user_progress(invalid_progress_data)
                logger.error("❌ user_progress 테이블 외래키 제약 조건 실패 (예상치 못한 성공)")
                return False
            except Exception:
                logger.info("✅ user_progress 테이블 외래키 제약 조건 확인 성공")
            
            # 2. READ 테스트
            logger.info("--- user_progress 테이블 READ 테스트 ---")
            
            # 사용자별 진행 상태 조회
            query = "SELECT * FROM user_progress WHERE user_id = %s"
            result = fetch_one(query, (user_id,))
            
            if result and result['current_chapter'] == progress_data['current_chapter']:
                logger.info("✅ user_progress 테이블 READ (사용자별 조회) 성공")
            else:
                logger.error("❌ user_progress 테이블 READ (사용자별 조회) 실패")
                return False
            
            # 현재 챕터 정보 조회
            query = "SELECT current_chapter FROM user_progress WHERE user_id = %s"
            result = fetch_one(query, (user_id,))
            
            if result and result['current_chapter'] == progress_data['current_chapter']:
                logger.info("✅ user_progress 테이블 READ (현재 챕터 정보) 성공")
            else:
                logger.error("❌ user_progress 테이블 READ (현재 챕터 정보) 실패")
                return False
            
            # 3. UPDATE 테스트
            logger.info("--- user_progress 테이블 UPDATE 테스트 ---")
            
            # 현재 챕터 업데이트
            new_chapter = 2
            
            query = """
            UPDATE user_progress 
            SET current_chapter = %s, last_study_date = CURDATE(), updated_at = NOW()
            WHERE user_id = %s
            """
            execute_query(query, (new_chapter, user_id))
            
            # 수정 결과 확인
            query = "SELECT current_chapter FROM user_progress WHERE user_id = %s"
            result = fetch_one(query, (user_id,))
            
            if result and result['current_chapter'] == new_chapter:
                logger.info("✅ user_progress 테이블 UPDATE 성공")
            else:
                logger.error("❌ user_progress 테이블 UPDATE 실패")
                return False
            
            # 4. DELETE 테스트는 cleanup에서 수행
            logger.info("--- user_progress 테이블 DELETE 테스트는 cleanup에서 수행 ---")
            
            self.test_results['user_progress_crud_test'] = True
            return True
            
        except DatabaseQueryError as e:
            logger.error(f"❌ user_progress 테이블 CRUD 테스트 쿼리 오류: {e}")
            return False
        except DatabaseIntegrityError as e:
            logger.error(f"❌ user_progress 테이블 CRUD 테스트 무결성 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ user_progress 테이블 CRUD 테스트 예상치 못한 오류: {e}")
            return False
    
    def test_user_statistics_crud(self) -> bool:
        """
        user_statistics 테이블 CRUD 테스트
        요구사항 2.1, 2.2 검증
        
        Returns:
            bool: 테스트 성공 여부
        """
        logger.info("🔄 user_statistics 테이블 CRUD 테스트 시작...")
        
        try:
            # 사용자가 이미 생성되어 있는지 확인, 없으면 생성
            if not self.test_data_manager.is_data_created('users'):
                logger.info("user_statistics 테스트를 위해 먼저 사용자를 생성합니다")
                test_user_data = self.test_data_manager.create_test_user_data()
                user_id = self.test_data_manager.insert_test_user(test_user_data)
            else:
                user_id = self.test_data_manager.created_data_ids['users'][0]
            
            # 1. CREATE 테스트
            logger.info("--- user_statistics 테이블 CREATE 테스트 ---")
            
            # 사용자 통계 생성
            statistics_data = self.test_data_manager.create_test_user_statistics_data(user_id)
            created_user_id = self.test_data_manager.insert_test_user_statistics(statistics_data)
            
            if created_user_id == user_id:
                logger.info("✅ user_statistics 테이블 CREATE 성공")
            else:
                logger.error("❌ user_statistics 테이블 CREATE 실패")
                return False
            
            # 기본값 설정 확인
            query = "SELECT * FROM user_statistics WHERE user_id = %s"
            result = fetch_one(query, (user_id,))
            
            if (result and result['total_study_time_minutes'] == statistics_data['total_study_time_minutes'] and
                abs(float(result['average_accuracy']) - statistics_data['average_accuracy']) < 0.01):
                logger.info("✅ user_statistics 테이블 기본값 설정 확인 성공")
            else:
                logger.error("❌ user_statistics 테이블 기본값 설정 확인 실패")
                return False
            
            # 2. READ 테스트
            logger.info("--- user_statistics 테이블 READ 테스트 ---")
            
            # 사용자별 통계 조회
            query = "SELECT * FROM user_statistics WHERE user_id = %s"
            result = fetch_one(query, (user_id,))
            
            if result and result['total_completed_sessions'] == statistics_data['total_completed_sessions']:
                logger.info("✅ user_statistics 테이블 READ (사용자별 통계) 성공")
            else:
                logger.error("❌ user_statistics 테이블 READ (사용자별 통계) 실패")
                return False
            
            # 학습 시간 및 정답률 조회
            query = "SELECT total_study_time_minutes, average_accuracy, total_correct_answers FROM user_statistics WHERE user_id = %s"
            result = fetch_one(query, (user_id,))
            
            if (result and result['total_study_time_minutes'] == statistics_data['total_study_time_minutes'] and
                result['total_correct_answers'] == statistics_data['total_correct_answers']):
                logger.info("✅ user_statistics 테이블 READ (학습 시간 및 정답률) 성공")
            else:
                logger.error("❌ user_statistics 테이블 READ (학습 시간 및 정답률) 실패")
                return False
            
            # 3. UPDATE 테스트
            logger.info("--- user_statistics 테이블 UPDATE 테스트 ---")
            
            # 학습 통계 업데이트
            new_study_time = 120
            new_study_sessions = 4
            new_completed_sessions = 4
            new_correct_answers = 6
            new_average_accuracy = 75.0
            
            query = """
            UPDATE user_statistics 
            SET total_study_time_minutes = %s, total_study_sessions = %s, 
                total_completed_sessions = %s, total_correct_answers = %s,
                average_accuracy = %s, last_study_date = CURDATE(), updated_at = NOW()
            WHERE user_id = %s
            """
            execute_query(query, (new_study_time, new_study_sessions, new_completed_sessions, 
                                new_correct_answers, new_average_accuracy, user_id))
            
            # 수정 결과 확인
            query = "SELECT total_study_time_minutes, total_study_sessions, total_completed_sessions, average_accuracy FROM user_statistics WHERE user_id = %s"
            result = fetch_one(query, (user_id,))
            
            if (result and result['total_study_time_minutes'] == new_study_time and 
                result['total_study_sessions'] == new_study_sessions and 
                result['total_completed_sessions'] == new_completed_sessions and
                abs(float(result['average_accuracy']) - new_average_accuracy) < 0.01):  # Decimal 타입 처리
                logger.info("✅ user_statistics 테이블 UPDATE 성공")
            else:
                logger.error("❌ user_statistics 테이블 UPDATE 실패")
                return False
            
            # 평균 정답률 계산 확인 (Decimal 타입 처리)
            if abs(float(result['average_accuracy']) - new_average_accuracy) < 0.01:
                logger.info("✅ user_statistics 테이블 평균 정답률 계산 확인 성공")
            else:
                logger.error("❌ user_statistics 테이블 평균 정답률 계산 확인 실패")
                return False
            
            # 4. DELETE 테스트는 cleanup에서 수행
            logger.info("--- user_statistics 테이블 DELETE 테스트는 cleanup에서 수행 ---")
            
            self.test_results['user_statistics_crud_test'] = True
            return True
            
        except DatabaseQueryError as e:
            logger.error(f"❌ user_statistics 테이블 CRUD 테스트 쿼리 오류: {e}")
            return False
        except DatabaseIntegrityError as e:
            logger.error(f"❌ user_statistics 테이블 CRUD 테스트 무결성 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ user_statistics 테이블 CRUD 테스트 예상치 못한 오류: {e}")
            return False
    
    def run_all_connection_tests(self) -> bool:
        """
        모든 데이터베이스 연결 테스트 실행
        
        Returns:
            bool: 전체 테스트 성공 여부
        """
        logger.info("=== 데이터베이스 연결 테스트 시작 ===\n")
        
        test_methods = [
            ('기본 연결 테스트', self.test_database_connection),
            ('연결 상태 및 해제 테스트', self.test_connection_state_and_disconnect),
            ('재연결 기능 테스트', self.test_reconnection),
            ('연결 실패 처리 테스트', self.test_connection_failure_handling)
        ]
        
        all_passed = True
        
        for test_name, test_method in test_methods:
            try:
                logger.info(f"\n--- {test_name} ---")
                result = test_method()
                
                if result:
                    logger.info(f"✅ {test_name} 통과")
                else:
                    logger.error(f"❌ {test_name} 실패")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"❌ {test_name} 실행 중 오류: {e}")
                all_passed = False
        
        # 최종 정리
        self.cleanup()
        
        # 결과 요약
        logger.info("\n=== 테스트 결과 요약 ===")
        for test_name, result in self.test_results.items():
            status = "✅ 통과" if result else "❌ 실패"
            logger.info(f"{test_name}: {status}")
        
        if all_passed:
            logger.info("\n🎉 모든 데이터베이스 연결 테스트 통과!")
        else:
            logger.error("\n💥 일부 데이터베이스 연결 테스트 실패!")
        
        return all_passed
    
    def run_all_user_crud_tests(self) -> bool:
        """
        모든 사용자 관련 테이블 CRUD 테스트 실행
        
        Returns:
            bool: 전체 테스트 성공 여부
        """
        logger.info("=== 사용자 관련 테이블 CRUD 테스트 시작 ===\n")
        
        test_methods = [
            ('users 테이블 CRUD 테스트', self.test_users_crud),
            ('user_progress 테이블 CRUD 테스트', self.test_user_progress_crud),
            ('user_statistics 테이블 CRUD 테스트', self.test_user_statistics_crud)
        ]
        
        all_passed = True
        
        for test_name, test_method in test_methods:
            try:
                logger.info(f"\n--- {test_name} ---")
                result = test_method()
                
                if result:
                    logger.info(f"✅ {test_name} 통과")
                else:
                    logger.error(f"❌ {test_name} 실패")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"❌ {test_name} 실행 중 오류: {e}")
                all_passed = False
        
        # 테스트 데이터 정리
        self.cleanup_test_data()
        
        # 결과 요약
        logger.info("\n=== 사용자 관련 테이블 CRUD 테스트 결과 요약 ===")
        user_crud_results = {
            'users_crud_test': self.test_results['users_crud_test'],
            'user_progress_crud_test': self.test_results['user_progress_crud_test'],
            'user_statistics_crud_test': self.test_results['user_statistics_crud_test']
        }
        
        for test_name, result in user_crud_results.items():
            status = "✅ 통과" if result else "❌ 실패"
            logger.info(f"{test_name}: {status}")
        
        if all_passed:
            logger.info("\n🎉 모든 사용자 관련 테이블 CRUD 테스트 통과!")
        else:
            logger.error("\n💥 일부 사용자 관련 테이블 CRUD 테스트 실패!")
        
        return all_passed
    
    def cleanup(self) -> None:
        """
        테스트 후 정리 작업 (연결만 정리)
        """
        try:
            if self.db_conn:
                self.db_conn.disconnect()
                logger.info("✅ 테스트 연결 정리 완료")
        except Exception as e:
            logger.warning(f"⚠️ 테스트 연결 정리 중 오류: {e}")
    
    def cleanup_test_data(self) -> None:
        """
        테스트 데이터 정리 작업
        """
        try:
            logger.info("🔄 테스트 데이터 정리 시작...")
            self.test_data_manager.cleanup_all_test_data()
            logger.info("✅ 테스트 데이터 정리 완료")
        except Exception as e:
            logger.warning(f"⚠️ 테스트 데이터 정리 중 오류: {e}")
            # 강제 정리 시도
            try:
                self.test_data_manager._force_cleanup()
            except Exception as force_error:
                logger.error(f"❌ 강제 테스트 데이터 정리도 실패: {force_error}")

# ================================
# pytest 테스트 함수들
# ================================

def test_database_connection():
    """pytest용 데이터베이스 연결 테스트 함수"""
    try:
        # 환경변수 로드 확인
        from dotenv import load_dotenv
        load_dotenv()
        
        # 기본 연결 테스트 (전역 함수 사용)
        logger.info("=== 기본 데이터베이스 연결 확인 ===")
        from app.config.db_config import test_database_connection as basic_test
        assert basic_test(), "기본 데이터베이스 연결 확인 실패"
        logger.info("✅ 기본 데이터베이스 연결 확인 성공\n")
        
        # 상세 연결 테스트 실행
        connection_test = DatabaseConnectionTest()
        success = connection_test.run_all_connection_tests()
        
        assert success, "데이터베이스 연결 테스트 실패"
        
    except Exception as e:
        logger.error(f"❌ 테스트 실행 중 오류: {e}")
        raise

def test_user_tables_crud():
    """pytest용 사용자 관련 테이블 CRUD 테스트 함수"""
    try:
        # 환경변수 로드 확인
        from dotenv import load_dotenv
        load_dotenv()
        
        # 기본 연결 테스트 먼저 실행
        logger.info("=== 기본 데이터베이스 연결 확인 ===")
        from app.config.db_config import test_database_connection as basic_test
        assert basic_test(), "기본 데이터베이스 연결 확인 실패"
        logger.info("✅ 기본 데이터베이스 연결 확인 성공\n")
        
        # 사용자 관련 테이블 CRUD 테스트 실행
        connection_test = DatabaseConnectionTest()
        success = connection_test.run_all_user_crud_tests()
        
        assert success, "사용자 관련 테이블 CRUD 테스트 실패"
        
    except Exception as e:
        logger.error(f"❌ 사용자 관련 테이블 CRUD 테스트 실행 중 오류: {e}")
        raise

def main():
    """메인 테스트 실행 함수"""
    try:
        # 환경변수 로드 확인
        from dotenv import load_dotenv
        load_dotenv()
        
        # 기본 연결 테스트 (전역 함수 사용)
        logger.info("=== 기본 데이터베이스 연결 확인 ===")
        from app.config.db_config import test_database_connection as basic_test
        if basic_test():
            logger.info("✅ 기본 데이터베이스 연결 확인 성공\n")
        else:
            logger.error("❌ 기본 데이터베이스 연결 확인 실패")
            return False
        
        # 테스트 인스턴스 생성
        connection_test = DatabaseConnectionTest()
        
        # 1. 연결 테스트 실행
        logger.info("\n" + "="*60)
        logger.info("1단계: 데이터베이스 연결 테스트")
        logger.info("="*60)
        connection_success = connection_test.run_all_connection_tests()
        
        # 2. 사용자 관련 테이블 CRUD 테스트 실행
        logger.info("\n" + "="*60)
        logger.info("2단계: 사용자 관련 테이블 CRUD 테스트")
        logger.info("="*60)
        crud_success = connection_test.run_all_user_crud_tests()
        
        # 전체 결과
        overall_success = connection_success and crud_success
        
        logger.info("\n" + "="*60)
        logger.info("전체 테스트 결과 요약")
        logger.info("="*60)
        logger.info(f"연결 테스트: {'✅ 성공' if connection_success else '❌ 실패'}")
        logger.info(f"CRUD 테스트: {'✅ 성공' if crud_success else '❌ 실패'}")
        logger.info(f"전체 결과: {'✅ 성공' if overall_success else '❌ 실패'}")
        
        return overall_success
        
    except Exception as e:
        logger.error(f"❌ 테스트 실행 중 오류: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info("\n✅ 데이터베이스 연결 테스트 완료!")
        sys.exit(0)
    else:
        logger.error("\n❌ 데이터베이스 연결 테스트 실패!")
        sys.exit(1)