# backend/tests/test_learning_sessions_crud.py
# 학습 세션 관련 테이블 CRUD 테스트 구현

import sys
import os
import logging
from typing import Optional, Dict, Any

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

class LearningSessionsCrudTest:
    """
    학습 세션 관련 테이블 CRUD 테스트 클래스
    learning_sessions, session_conversations, session_quizzes 테이블을 검증합니다.
    """
    
    def __init__(self):
        """테스트 클래스 초기화"""
        self.db_conn = None
        self.test_data_manager = TestDataManager()
        self.test_results = {
            'learning_sessions_crud_test': False,
            'session_conversations_crud_test': False,
            'session_quizzes_crud_test': False
        }
        self.test_user_id = None
        self.test_session_id = None
    
    def setup_test_prerequisites(self) -> bool:
        """
        테스트 전제 조건 설정 (사용자 데이터 생성)
        
        Returns:
            bool: 설정 성공 여부
        """
        logger.info("🔄 테스트 전제 조건 설정 중...")
        
        try:
            # 데이터베이스 연결 확인
            self.db_conn = DatabaseConnection()
            connection = self.db_conn.connect()
            
            if not connection or not connection.open:
                logger.error("❌ 데이터베이스 연결 실패")
                return False
            
            # 기존 테스트 데이터 정리
            self.test_data_manager.cleanup_all_test_data()
            
            # 테스트 사용자 생성
            test_user_data = self.test_data_manager.create_test_user_data()
            self.test_user_id = self.test_data_manager.insert_test_user(test_user_data)
            
            logger.info(f"✅ 테스트 사용자 생성 완료 (user_id: {self.test_user_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 테스트 전제 조건 설정 실패: {e}")
            return False
    
    # ================================
    # learning_sessions 테이블 CRUD 테스트
    # ================================
    
    def test_learning_sessions_crud(self) -> bool:
        """
        learning_sessions 테이블 CRUD 테스트
        요구사항 3.1 검증
        
        Returns:
            bool: 테스트 성공 여부
        """
        logger.info("🔄 learning_sessions 테이블 CRUD 테스트 시작...")
        
        try:
            # 1. CREATE 테스트
            logger.info("--- learning_sessions 테이블 CREATE 테스트 ---")
            
            # 학습 세션 생성
            session_data = self.test_data_manager.create_test_session_data(self.test_user_id)
            created_session_id = self.test_data_manager.insert_test_session(session_data)
            self.test_session_id = created_session_id
            
            if created_session_id == session_data['session_id']:
                logger.info("✅ learning_sessions 테이블 CREATE 성공")
            else:
                logger.error("❌ learning_sessions 테이블 CREATE 실패")
                return False
            
            # 외래키 제약 조건 테스트 (존재하지 않는 user_id)
            try:
                invalid_session_data = self.test_data_manager.create_test_session_data(99999)
                self.test_data_manager.insert_test_session(invalid_session_data)
                logger.error("❌ learning_sessions 테이블 외래키 제약 조건 실패 (예상치 못한 성공)")
                return False
            except Exception:
                logger.info("✅ learning_sessions 테이블 외래키 제약 조건 확인 성공")
            
            # 세션 ID 중복 처리 테스트
            try:
                duplicate_session_data = session_data.copy()
                self.test_data_manager.insert_test_session(duplicate_session_data)
                logger.error("❌ learning_sessions 테이블 세션 ID 중복 처리 실패 (예상치 못한 성공)")
                return False
            except Exception:
                logger.info("✅ learning_sessions 테이블 세션 ID 중복 처리 확인 성공")
            
            # 2. READ 테스트
            logger.info("--- learning_sessions 테이블 READ 테스트 ---")
            
            # 세션 ID로 세션 조회
            query = "SELECT * FROM learning_sessions WHERE session_id = %s"
            result = fetch_one(query, (created_session_id,))
            
            if result and result['user_id'] == self.test_user_id:
                logger.info("✅ learning_sessions 테이블 READ (세션 ID 조회) 성공")
            else:
                logger.error("❌ learning_sessions 테이블 READ (세션 ID 조회) 실패")
                return False
            
            # 사용자별 세션 목록 조회
            query = "SELECT * FROM learning_sessions WHERE user_id = %s ORDER BY session_sequence"
            results = fetch_all(query, (self.test_user_id,))
            
            if results and len(results) >= 1 and results[0]['session_id'] == created_session_id:
                logger.info("✅ learning_sessions 테이블 READ (사용자별 세션 목록) 성공")
            else:
                logger.error("❌ learning_sessions 테이블 READ (사용자별 세션 목록) 실패")
                return False
            
            # 챕터별 세션 조회
            query = "SELECT * FROM learning_sessions WHERE user_id = %s AND chapter_number = %s"
            results = fetch_all(query, (self.test_user_id, session_data['chapter_number']))
            
            if results and len(results) >= 1:
                logger.info("✅ learning_sessions 테이블 READ (챕터별 세션) 성공")
            else:
                logger.error("❌ learning_sessions 테이블 READ (챕터별 세션) 실패")
                return False
            
            # 존재하지 않는 세션 조회 테스트
            query = "SELECT * FROM learning_sessions WHERE session_id = %s"
            result = fetch_one(query, ('nonexistent_session',))
            
            if result is None:
                logger.info("✅ learning_sessions 테이블 READ (존재하지 않는 세션) 성공")
            else:
                logger.error("❌ learning_sessions 테이블 READ (존재하지 않는 세션) 실패")
                return False
            
            # 3. UPDATE 테스트
            logger.info("--- learning_sessions 테이블 UPDATE 테스트 ---")
            
            # 세션 상태 업데이트 (session_decision_result)
            new_decision_result = "retry"
            new_study_duration = 45
            
            query = """
            UPDATE learning_sessions 
            SET session_decision_result = %s, study_duration_minutes = %s, 
                session_end_time = NOW()
            WHERE session_id = %s
            """
            execute_query(query, (new_decision_result, new_study_duration, created_session_id))
            
            # 수정 결과 확인
            query = "SELECT session_decision_result, study_duration_minutes FROM learning_sessions WHERE session_id = %s"
            result = fetch_one(query, (created_session_id,))
            
            if (result and result['session_decision_result'] == new_decision_result and 
                result['study_duration_minutes'] == new_study_duration):
                logger.info("✅ learning_sessions 테이블 UPDATE 성공")
            else:
                logger.error("❌ learning_sessions 테이블 UPDATE 실패")
                return False
            
            # 세션 종료 시간 업데이트 테스트
            from datetime import datetime
            
            query = """
            UPDATE learning_sessions 
            SET session_end_time = %s
            WHERE session_id = %s
            """
            new_end_time = datetime.now()
            execute_query(query, (new_end_time, created_session_id))
            
            # 수정 결과 확인
            query = "SELECT session_end_time FROM learning_sessions WHERE session_id = %s"
            result = fetch_one(query, (created_session_id,))
            
            if result and result['session_end_time'] is not None:
                logger.info("✅ learning_sessions 테이블 세션 종료 시간 UPDATE 성공")
            else:
                logger.error("❌ learning_sessions 테이블 세션 종료 시간 UPDATE 실패")
                return False
            
            # 4. DELETE 테스트는 cleanup에서 수행
            logger.info("--- learning_sessions 테이블 DELETE 테스트는 cleanup에서 수행 ---")
            
            self.test_results['learning_sessions_crud_test'] = True
            return True
            
        except DatabaseQueryError as e:
            logger.error(f"❌ learning_sessions 테이블 CRUD 테스트 쿼리 오류: {e}")
            return False
        except DatabaseIntegrityError as e:
            logger.error(f"❌ learning_sessions 테이블 CRUD 테스트 무결성 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ learning_sessions 테이블 CRUD 테스트 예상치 못한 오류: {e}")
            return False
    
    # ================================
    # session_conversations 테이블 CRUD 테스트
    # ================================
    
    def test_session_conversations_crud(self) -> bool:
        """
        session_conversations 테이블 CRUD 테스트
        요구사항 3.2 검증
        
        Returns:
            bool: 테스트 성공 여부
        """
        logger.info("🔄 session_conversations 테이블 CRUD 테스트 시작...")
        
        try:
            # 세션이 없으면 먼저 생성
            if not self.test_session_id:
                if not self.test_learning_sessions_crud():
                    logger.error("❌ 전제 조건인 learning_sessions 테스트 실패")
                    return False
            
            # 1. CREATE 테스트
            logger.info("--- session_conversations 테이블 CREATE 테스트 ---")
            
            # 대화 레코드 생성
            conversation_data = self.test_data_manager.create_test_conversation_data(self.test_session_id, 1)
            created_conversation_id = self.test_data_manager.insert_test_conversation(conversation_data)
            
            if created_conversation_id == f"{self.test_session_id}_1":
                logger.info("✅ session_conversations 테이블 CREATE 성공")
            else:
                logger.error("❌ session_conversations 테이블 CREATE 실패")
                return False
            
            # 외래키 제약 조건 테스트 (존재하지 않는 session_id)
            try:
                invalid_conversation_data = self.test_data_manager.create_test_conversation_data('nonexistent_session', 1)
                self.test_data_manager.insert_test_conversation(invalid_conversation_data)
                logger.error("❌ session_conversations 테이블 외래키 제약 조건 실패 (예상치 못한 성공)")
                return False
            except Exception:
                logger.info("✅ session_conversations 테이블 외래키 제약 조건 확인 성공")
            
            # 메시지 순서 관리 테스트 - 여러 메시지 생성
            conversation_data_2 = self.test_data_manager.create_test_conversation_data(self.test_session_id, 2)
            conversation_data_2['agent_name'] = 'theory_educator'
            conversation_data_2['message_content'] = '두 번째 테스트 메시지입니다.'
            created_conversation_id_2 = self.test_data_manager.insert_test_conversation(conversation_data_2)
            
            if created_conversation_id_2 == f"{self.test_session_id}_2":
                logger.info("✅ session_conversations 테이블 메시지 순서 관리 성공")
            else:
                logger.error("❌ session_conversations 테이블 메시지 순서 관리 실패")
                return False
            
            # 2. READ 테스트
            logger.info("--- session_conversations 테이블 READ 테스트 ---")
            
            # 세션별 대화 목록 조회
            query = "SELECT * FROM session_conversations WHERE session_id = %s ORDER BY message_sequence"
            results = fetch_all(query, (self.test_session_id,))
            
            if results and len(results) >= 2:
                logger.info("✅ session_conversations 테이블 READ (세션별 대화 목록) 성공")
            else:
                logger.error("❌ session_conversations 테이블 READ (세션별 대화 목록) 실패")
                return False
            
            # 메시지 순서별 조회
            query = "SELECT * FROM session_conversations WHERE session_id = %s AND message_sequence = %s"
            result = fetch_one(query, (self.test_session_id, 1))
            
            if result and result['message_content'] == conversation_data['message_content']:
                logger.info("✅ session_conversations 테이블 READ (메시지 순서별 조회) 성공")
            else:
                logger.error("❌ session_conversations 테이블 READ (메시지 순서별 조회) 실패")
                return False
            
            # 에이전트별 메시지 조회
            query = "SELECT * FROM session_conversations WHERE session_id = %s AND agent_name = %s"
            results = fetch_all(query, (self.test_session_id, 'learning_supervisor'))
            
            if results and len(results) >= 1:
                logger.info("✅ session_conversations 테이블 READ (에이전트별 메시지) 성공")
            else:
                logger.error("❌ session_conversations 테이블 READ (에이전트별 메시지) 실패")
                return False
            
            # 3. UPDATE 테스트
            logger.info("--- session_conversations 테이블 UPDATE 테스트 ---")
            
            # 메시지 내용 수정
            new_message_content = "수정된 테스트 메시지입니다."
            new_session_progress_stage = "quiz_generation"
            
            query = """
            UPDATE session_conversations 
            SET message_content = %s, session_progress_stage = %s
            WHERE session_id = %s AND message_sequence = %s
            """
            execute_query(query, (new_message_content, new_session_progress_stage, self.test_session_id, 1))
            
            # 수정 결과 확인
            query = "SELECT message_content, session_progress_stage FROM session_conversations WHERE session_id = %s AND message_sequence = %s"
            result = fetch_one(query, (self.test_session_id, 1))
            
            if (result and result['message_content'] == new_message_content and 
                result['session_progress_stage'] == new_session_progress_stage):
                logger.info("✅ session_conversations 테이블 UPDATE 성공")
            else:
                logger.error("❌ session_conversations 테이블 UPDATE 실패")
                return False
            
            # 세션 진행 단계 업데이트 테스트
            query = """
            UPDATE session_conversations 
            SET session_progress_stage = %s
            WHERE session_id = %s AND message_sequence = %s
            """
            execute_query(query, ('evaluation_feedback', self.test_session_id, 2))
            
            # 수정 결과 확인
            query = "SELECT session_progress_stage FROM session_conversations WHERE session_id = %s AND message_sequence = %s"
            result = fetch_one(query, (self.test_session_id, 2))
            
            if result and result['session_progress_stage'] == 'evaluation_feedback':
                logger.info("✅ session_conversations 테이블 세션 진행 단계 UPDATE 성공")
            else:
                logger.error("❌ session_conversations 테이블 세션 진행 단계 UPDATE 실패")
                return False
            
            # 4. DELETE 테스트는 cleanup에서 수행
            logger.info("--- session_conversations 테이블 DELETE 테스트는 cleanup에서 수행 ---")
            
            self.test_results['session_conversations_crud_test'] = True
            return True
            
        except DatabaseQueryError as e:
            logger.error(f"❌ session_conversations 테이블 CRUD 테스트 쿼리 오류: {e}")
            return False
        except DatabaseIntegrityError as e:
            logger.error(f"❌ session_conversations 테이블 CRUD 테스트 무결성 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ session_conversations 테이블 CRUD 테스트 예상치 못한 오류: {e}")
            return False
    
    # ================================
    # session_quizzes 테이블 CRUD 테스트
    # ================================
    
    def test_session_quizzes_crud(self) -> bool:
        """
        session_quizzes 테이블 CRUD 테스트
        요구사항 3.3 검증
        
        Returns:
            bool: 테스트 성공 여부
        """
        logger.info("🔄 session_quizzes 테이블 CRUD 테스트 시작...")
        
        try:
            # 세션이 없으면 먼저 생성
            if not self.test_session_id:
                if not self.test_learning_sessions_crud():
                    logger.error("❌ 전제 조건인 learning_sessions 테스트 실패")
                    return False
            
            # 1. CREATE 테스트
            logger.info("--- session_quizzes 테이블 CREATE 테스트 ---")
            
            # 퀴즈 레코드 생성
            quiz_data = self.test_data_manager.create_test_quiz_data(self.test_session_id, 1)
            created_quiz_id = self.test_data_manager.insert_test_quiz(quiz_data)
            
            if created_quiz_id == self.test_session_id:
                logger.info("✅ session_quizzes 테이블 CREATE 성공")
            else:
                logger.error("❌ session_quizzes 테이블 CREATE 실패")
                return False
            
            # 외래키 제약 조건 테스트 (존재하지 않는 session_id)
            try:
                invalid_quiz_data = self.test_data_manager.create_test_quiz_data('nonexistent_session', 1)
                self.test_data_manager.insert_test_quiz(invalid_quiz_data)
                logger.error("❌ session_quizzes 테이블 외래키 제약 조건 실패 (예상치 못한 성공)")
                return False
            except Exception:
                logger.info("✅ session_quizzes 테이블 외래키 제약 조건 확인 성공")
            
            # 각 세션당 하나의 퀴즈만 가능하므로 다른 세션 생성
            session_data_2 = self.test_data_manager.create_test_session_data(self.test_user_id, 2)
            test_session_id_2 = self.test_data_manager.insert_test_session(session_data_2)
            
            # 문제 유형별 데이터 삽입 테스트
            quiz_data_2 = self.test_data_manager.create_test_quiz_data(test_session_id_2, 1)
            quiz_data_2['question_type'] = 'true_false'
            quiz_data_2['question_content'] = 'AI는 인공지능의 줄임말입니다. (참/거짓)'
            quiz_data_2['user_answer'] = 'True'
            created_quiz_id_2 = self.test_data_manager.insert_test_quiz(quiz_data_2)
            
            if created_quiz_id_2 == test_session_id_2:
                logger.info("✅ session_quizzes 테이블 문제 유형별 데이터 삽입 성공")
            else:
                logger.error("❌ session_quizzes 테이블 문제 유형별 데이터 삽입 실패")
                return False
            
            # 2. READ 테스트
            logger.info("--- session_quizzes 테이블 READ 테스트 ---")
            
            # 세션별 퀴즈 조회
            query = "SELECT * FROM session_quizzes WHERE session_id = %s"
            result = fetch_one(query, (self.test_session_id,))
            
            if result:
                logger.info("✅ session_quizzes 테이블 READ (세션별 퀴즈) 성공")
            else:
                logger.error("❌ session_quizzes 테이블 READ (세션별 퀴즈) 실패")
                return False
            
            # 문제 유형별 조회
            query = "SELECT * FROM session_quizzes WHERE question_type = %s"
            results = fetch_all(query, ('multiple_choice',))
            
            if results and len(results) >= 1:
                logger.info("✅ session_quizzes 테이블 READ (문제 유형별 조회) 성공")
            else:
                logger.error("❌ session_quizzes 테이블 READ (문제 유형별 조회) 실패")
                return False
            
            # 정답률 통계 조회 (사용자별)
            query = """
            SELECT 
                COUNT(*) as total_questions,
                SUM(CASE WHEN is_answer_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
                AVG(CASE WHEN is_answer_correct = 1 THEN 100.0 ELSE 0.0 END) as accuracy_rate
            FROM session_quizzes sq
            JOIN learning_sessions ls ON sq.session_id = ls.session_id
            WHERE ls.user_id = %s
            """
            result = fetch_one(query, (self.test_user_id,))
            
            if result and result['total_questions'] >= 1:
                logger.info(f"✅ session_quizzes 테이블 READ (정답률 통계) 성공 - 정답률: {result['accuracy_rate']:.1f}%")
            else:
                logger.error("❌ session_quizzes 테이블 READ (정답률 통계) 실패")
                return False
            
            # 3. UPDATE 테스트
            logger.info("--- session_quizzes 테이블 UPDATE 테스트 ---")
            
            # 사용자 답변 업데이트
            new_user_answer = "B"
            new_is_answer_correct = 0
            new_evaluation_feedback = "아쉽게도 틀렸습니다. 다시 한번 생각해보세요."
            
            query = """
            UPDATE session_quizzes 
            SET user_answer = %s, is_answer_correct = %s, evaluation_feedback = %s
            WHERE session_id = %s
            """
            execute_query(query, (new_user_answer, new_is_answer_correct, new_evaluation_feedback, self.test_session_id))
            
            # 수정 결과 확인
            query = "SELECT user_answer, is_answer_correct, evaluation_feedback FROM session_quizzes WHERE session_id = %s"
            result = fetch_one(query, (self.test_session_id,))
            
            if (result and result['user_answer'] == new_user_answer and 
                result['is_answer_correct'] == new_is_answer_correct and 
                result['evaluation_feedback'] == new_evaluation_feedback):
                logger.info("✅ session_quizzes 테이블 사용자 답변 UPDATE 성공")
            else:
                logger.error("❌ session_quizzes 테이블 사용자 답변 UPDATE 실패")
                return False
            
            # 평가 결과 업데이트 테스트 (두 번째 세션의 퀴즈)
            new_evaluation_feedback_2 = "정답입니다! 잘 이해하고 계시네요."
            
            query = """
            UPDATE session_quizzes 
            SET evaluation_feedback = %s
            WHERE session_id = %s
            """
            execute_query(query, (new_evaluation_feedback_2, test_session_id_2))
            
            # 수정 결과 확인
            query = "SELECT evaluation_feedback FROM session_quizzes WHERE session_id = %s"
            result = fetch_one(query, (test_session_id_2,))
            
            if result and result['evaluation_feedback'] == new_evaluation_feedback_2:
                logger.info("✅ session_quizzes 테이블 평가 결과 UPDATE 성공")
            else:
                logger.error("❌ session_quizzes 테이블 평가 결과 UPDATE 실패")
                return False
            
            # 4. DELETE 테스트는 cleanup에서 수행
            logger.info("--- session_quizzes 테이블 DELETE 테스트는 cleanup에서 수행 ---")
            
            self.test_results['session_quizzes_crud_test'] = True
            return True
            
        except DatabaseQueryError as e:
            logger.error(f"❌ session_quizzes 테이블 CRUD 테스트 쿼리 오류: {e}")
            return False
        except DatabaseIntegrityError as e:
            logger.error(f"❌ session_quizzes 테이블 CRUD 테스트 무결성 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ session_quizzes 테이블 CRUD 테스트 예상치 못한 오류: {e}")
            return False
    
    # ================================
    # 통합 테스트 실행 메서드들
    # ================================
    
    def run_all_learning_sessions_crud_tests(self) -> bool:
        """
        모든 학습 세션 관련 테이블 CRUD 테스트 실행
        
        Returns:
            bool: 전체 테스트 성공 여부
        """
        logger.info("=== 학습 세션 관련 테이블 CRUD 테스트 시작 ===\n")
        
        # 전제 조건 설정
        if not self.setup_test_prerequisites():
            logger.error("❌ 테스트 전제 조건 설정 실패")
            return False
        
        test_methods = [
            ('learning_sessions 테이블 CRUD 테스트', self.test_learning_sessions_crud),
            ('session_conversations 테이블 CRUD 테스트', self.test_session_conversations_crud),
            ('session_quizzes 테이블 CRUD 테스트', self.test_session_quizzes_crud)
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
        logger.info("\n=== 학습 세션 관련 테이블 CRUD 테스트 결과 요약 ===")
        for test_name, result in self.test_results.items():
            status = "✅ 통과" if result else "❌ 실패"
            logger.info(f"{test_name}: {status}")
        
        if all_passed:
            logger.info("\n🎉 모든 학습 세션 관련 테이블 CRUD 테스트 통과!")
        else:
            logger.error("\n💥 일부 학습 세션 관련 테이블 CRUD 테스트 실패!")
        
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
            logger.info("🔄 학습 세션 관련 테스트 데이터 정리 시작...")
            self.test_data_manager.cleanup_all_test_data()
            logger.info("✅ 학습 세션 관련 테스트 데이터 정리 완료")
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

def test_learning_sessions_crud():
    """pytest용 학습 세션 관련 테이블 CRUD 테스트 함수"""
    try:
        # 환경변수 로드 확인
        from dotenv import load_dotenv
        load_dotenv()
        
        # 기본 연결 테스트 먼저 실행
        logger.info("=== 기본 데이터베이스 연결 확인 ===")
        from app.config.db_config import test_database_connection as basic_test
        assert basic_test(), "기본 데이터베이스 연결 확인 실패"
        logger.info("✅ 기본 데이터베이스 연결 확인 성공\n")
        
        # 학습 세션 관련 테이블 CRUD 테스트 실행
        sessions_test = LearningSessionsCrudTest()
        success = sessions_test.run_all_learning_sessions_crud_tests()
        
        assert success, "학습 세션 관련 테이블 CRUD 테스트 실패"
        
    except Exception as e:
        logger.error(f"❌ 학습 세션 관련 테이블 CRUD 테스트 실행 중 오류: {e}")
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
        sessions_test = LearningSessionsCrudTest()
        
        # 학습 세션 관련 테이블 CRUD 테스트 실행
        logger.info("\n" + "="*60)
        logger.info("학습 세션 관련 테이블 CRUD 테스트")
        logger.info("="*60)
        success = sessions_test.run_all_learning_sessions_crud_tests()
        
        # 전체 결과
        logger.info("\n" + "="*60)
        logger.info("전체 테스트 결과 요약")
        logger.info("="*60)
        logger.info(f"학습 세션 관련 테이블 CRUD 테스트: {'✅ 성공' if success else '❌ 실패'}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 테스트 실행 중 오류: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info("\n✅ 학습 세션 관련 테이블 CRUD 테스트 완료!")
        sys.exit(0)
    else:
        logger.error("\n❌ 학습 세션 관련 테이블 CRUD 테스트 실패!")
        sys.exit(1)