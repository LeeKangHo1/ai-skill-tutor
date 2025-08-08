# backend/tests/fixtures/test_data.py
# 테스트 데이터 정의 및 관리 모듈

from datetime import datetime, timedelta
from typing import Dict, Any, List

class TestDataManager:
    """
    테스트 데이터 생성 및 관리 클래스
    모든 테이블의 테스트 데이터 생성/삭제 기능을 제공합니다.
    """
    
    def __init__(self):
        """테스트 데이터 매니저 초기화"""
        # 테스트 데이터 ID 추적을 위한 딕셔너리
        self.created_data_ids = {
            'users': [],
            'user_progress': [],
            'user_statistics': [],
            'learning_sessions': [],
            'session_conversations': [],
            'session_quizzes': []
        }
    
    # ================================
    # 테스트 데이터 생성 메서드들
    # ================================
    
    def create_test_user_data(self, user_id: int = None) -> Dict[str, Any]:
        """
        테스트 사용자 데이터 생성
        
        Args:
            user_id (int, optional): 사용자 ID (지정하지 않으면 자동 생성)
            
        Returns:
            Dict[str, Any]: 생성된 사용자 데이터
        """
        if user_id is None:
            user_id = 999  # 기본 테스트 사용자 ID
            
        test_user_data = {
            "user_id": user_id,
            "login_id": f"test_user_{user_id:03d}",
            "username": f"테스트사용자{user_id}",
            "email": f"test{user_id}@example.com",
            "password_hash": "hashed_password_123_test",
            "user_type": "beginner",
            "diagnosis_completed": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 생성된 데이터 ID 추적
        self.created_data_ids['users'].append(user_id)
        
        return test_user_data
    
    def create_test_user_progress_data(self, user_id: int = 999) -> Dict[str, Any]:
        """
        테스트 사용자 진행 상태 데이터 생성
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 생성된 사용자 진행 상태 데이터
        """
        test_progress_data = {
            "user_id": user_id,
            "current_chapter": 1,
            "last_study_date": datetime.now().date(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 생성된 데이터 ID 추적
        self.created_data_ids['user_progress'].append(user_id)
        
        return test_progress_data
    
    def create_test_user_statistics_data(self, user_id: int = 999) -> Dict[str, Any]:
        """
        테스트 사용자 통계 데이터 생성
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 생성된 사용자 통계 데이터
        """
        test_statistics_data = {
            "user_id": user_id,
            "total_study_time_minutes": 30,
            "total_study_sessions": 1,
            "total_completed_sessions": 1,
            "total_correct_answers": 1,
            "average_accuracy": 85.5,
            "last_study_date": datetime.now().date(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 생성된 데이터 ID 추적
        self.created_data_ids['user_statistics'].append(user_id)
        
        return test_statistics_data
    
    def create_test_session_data(self, user_id: int = 999, session_sequence: int = 1) -> Dict[str, Any]:
        """
        테스트 학습 세션 데이터 생성
        
        Args:
            user_id (int): 사용자 ID
            session_sequence (int): 세션 순서
            
        Returns:
            Dict[str, Any]: 생성된 학습 세션 데이터
        """
        session_start_time = datetime.now() - timedelta(minutes=30)  # 30분 전 시작
        session_end_time = datetime.now()  # 현재 시간 종료
        
        session_id = f"user{user_id}_ch1_session{session_sequence:03d}_{session_start_time.strftime('%Y%m%d_%H%M%S')}"
        
        test_session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "chapter_number": 1,
            "session_sequence": session_sequence,
            "session_start_time": session_start_time,
            "session_end_time": session_end_time,
            "study_duration_minutes": 30,
            "session_decision_result": "proceed",
            "created_at": datetime.now()
        }
        
        # 생성된 데이터 ID 추적
        self.created_data_ids['learning_sessions'].append(session_id)
        
        return test_session_data
    
    def create_test_conversation_data(self, session_id: str, message_sequence: int = 1) -> Dict[str, Any]:
        """
        테스트 세션 대화 데이터 생성
        
        Args:
            session_id (str): 세션 ID
            message_sequence (int): 메시지 순서
            
        Returns:
            Dict[str, Any]: 생성된 세션 대화 데이터
        """
        test_conversation_data = {
            "session_id": session_id,
            "message_sequence": message_sequence,
            "agent_name": "learning_supervisor",
            "message_type": "system",
            "message_content": f"테스트 메시지 {message_sequence}번입니다.",
            "message_timestamp": datetime.now(),
            "session_progress_stage": "theory_explanation",
            "created_at": datetime.now()
        }
        
        # 생성된 데이터 ID 추적 (session_id와 message_sequence 조합)
        conversation_id = f"{session_id}_{message_sequence}"
        self.created_data_ids['session_conversations'].append(conversation_id)
        
        return test_conversation_data
    
    def create_test_quiz_data(self, session_id: str, question_number: int = 1) -> Dict[str, Any]:
        """
        테스트 세션 퀴즈 데이터 생성
        
        Args:
            session_id (str): 세션 ID
            question_number (int): 문제 번호
            
        Returns:
            Dict[str, Any]: 생성된 세션 퀴즈 데이터
        """
        test_quiz_data = {
            "session_id": session_id,
            "question_number": question_number,
            "question_type": "multiple_choice",
            "question_content": f"테스트 문제 {question_number}번입니다.",
            "user_answer": "A",
            "is_answer_correct": 1,
            "evaluation_feedback": "정답입니다! 잘 이해하셨네요.",
            "hint_usage_count": 0,
            "created_at": datetime.now()
        }
        
        # 생성된 데이터 ID 추적 (session_id 사용, 각 세션당 하나의 퀴즈)
        self.created_data_ids['session_quizzes'].append(session_id)
        
        return test_quiz_data
    
    # ================================
    # 데이터베이스 삽입 메서드들
    # ================================
    
    def insert_test_user(self, user_data: Dict[str, Any] = None) -> int:
        """
        테스트 사용자를 데이터베이스에 삽입
        
        Args:
            user_data (Dict[str, Any], optional): 사용자 데이터 (없으면 기본 데이터 생성)
            
        Returns:
            int: 삽입된 사용자 ID
        """
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        if user_data is None:
            user_data = self.create_test_user_data()
        
        query = """
        INSERT INTO users (user_id, login_id, username, email, password_hash, user_type, diagnosis_completed, created_at, updated_at)
        VALUES (%(user_id)s, %(login_id)s, %(username)s, %(email)s, %(password_hash)s, %(user_type)s, %(diagnosis_completed)s, %(created_at)s, %(updated_at)s)
        """
        
        execute_query(query, user_data)
        return user_data['user_id']
    
    def insert_test_user_progress(self, progress_data: Dict[str, Any] = None) -> int:
        """
        테스트 사용자 진행 상태를 데이터베이스에 삽입
        
        Args:
            progress_data (Dict[str, Any], optional): 진행 상태 데이터
            
        Returns:
            int: 사용자 ID
        """
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        if progress_data is None:
            progress_data = self.create_test_user_progress_data()
        
        query = """
        INSERT INTO user_progress (user_id, current_chapter, last_study_date, created_at, updated_at)
        VALUES (%(user_id)s, %(current_chapter)s, %(last_study_date)s, %(created_at)s, %(updated_at)s)
        """
        
        execute_query(query, progress_data)
        return progress_data['user_id']
    
    def insert_test_user_statistics(self, statistics_data: Dict[str, Any] = None) -> int:
        """
        테스트 사용자 통계를 데이터베이스에 삽입
        
        Args:
            statistics_data (Dict[str, Any], optional): 통계 데이터
            
        Returns:
            int: 사용자 ID
        """
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        if statistics_data is None:
            statistics_data = self.create_test_user_statistics_data()
        
        query = """
        INSERT INTO user_statistics (user_id, total_study_time_minutes, total_study_sessions, total_completed_sessions, total_correct_answers, average_accuracy, last_study_date, created_at, updated_at)
        VALUES (%(user_id)s, %(total_study_time_minutes)s, %(total_study_sessions)s, %(total_completed_sessions)s, %(total_correct_answers)s, %(average_accuracy)s, %(last_study_date)s, %(created_at)s, %(updated_at)s)
        """
        
        execute_query(query, statistics_data)
        return statistics_data['user_id']
    
    def insert_test_session(self, session_data: Dict[str, Any] = None) -> str:
        """
        테스트 학습 세션을 데이터베이스에 삽입
        
        Args:
            session_data (Dict[str, Any], optional): 세션 데이터
            
        Returns:
            str: 세션 ID
        """
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        if session_data is None:
            session_data = self.create_test_session_data()
        
        query = """
        INSERT INTO learning_sessions (session_id, user_id, chapter_number, session_sequence, session_start_time, session_end_time, study_duration_minutes, session_decision_result, created_at)
        VALUES (%(session_id)s, %(user_id)s, %(chapter_number)s, %(session_sequence)s, %(session_start_time)s, %(session_end_time)s, %(study_duration_minutes)s, %(session_decision_result)s, %(created_at)s)
        """
        
        execute_query(query, session_data)
        return session_data['session_id']
    
    def insert_test_conversation(self, conversation_data: Dict[str, Any] = None) -> str:
        """
        테스트 세션 대화를 데이터베이스에 삽입
        
        Args:
            conversation_data (Dict[str, Any], optional): 대화 데이터
            
        Returns:
            str: 대화 ID (session_id_message_sequence)
        """
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        if conversation_data is None:
            # 기본 세션이 없으면 생성
            if not self.created_data_ids['learning_sessions']:
                session_data = self.create_test_session_data()
                self.insert_test_session(session_data)
            
            session_id = self.created_data_ids['learning_sessions'][0]
            conversation_data = self.create_test_conversation_data(session_id)
        
        query = """
        INSERT INTO session_conversations (session_id, message_sequence, agent_name, message_type, message_content, message_timestamp, session_progress_stage, created_at)
        VALUES (%(session_id)s, %(message_sequence)s, %(agent_name)s, %(message_type)s, %(message_content)s, %(message_timestamp)s, %(session_progress_stage)s, %(created_at)s)
        """
        
        execute_query(query, conversation_data)
        return f"{conversation_data['session_id']}_{conversation_data['message_sequence']}"
    
    def insert_test_quiz(self, quiz_data: Dict[str, Any] = None) -> str:
        """
        테스트 세션 퀴즈를 데이터베이스에 삽입
        
        Args:
            quiz_data (Dict[str, Any], optional): 퀴즈 데이터
            
        Returns:
            str: 퀴즈 ID (session_id_quiz_sequence)
        """
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        if quiz_data is None:
            # 기본 세션이 없으면 생성
            if not self.created_data_ids['learning_sessions']:
                session_data = self.create_test_session_data()
                self.insert_test_session(session_data)
            
            session_id = self.created_data_ids['learning_sessions'][0]
            quiz_data = self.create_test_quiz_data(session_id)
        
        query = """
        INSERT INTO session_quizzes (session_id, question_number, question_type, question_content, user_answer, is_answer_correct, evaluation_feedback, hint_usage_count, created_at)
        VALUES (%(session_id)s, %(question_number)s, %(question_type)s, %(question_content)s, %(user_answer)s, %(is_answer_correct)s, %(evaluation_feedback)s, %(hint_usage_count)s, %(created_at)s)
        """
        
        execute_query(query, quiz_data)
        return quiz_data['session_id']
    
    def setup_complete_test_data(self) -> Dict[str, Any]:
        """
        완전한 테스트 데이터 세트 생성 (모든 테이블에 연관된 데이터)
        
        Returns:
            Dict[str, Any]: 생성된 데이터의 ID들
        """
        try:
            # 1. 사용자 생성
            user_data = self.create_test_user_data()
            user_id = self.insert_test_user(user_data)
            
            # 2. 사용자 진행 상태 생성
            progress_data = self.create_test_user_progress_data(user_id)
            self.insert_test_user_progress(progress_data)
            
            # 3. 사용자 통계 생성
            statistics_data = self.create_test_user_statistics_data(user_id)
            self.insert_test_user_statistics(statistics_data)
            
            # 4. 학습 세션 생성
            session_data = self.create_test_session_data(user_id)
            session_id = self.insert_test_session(session_data)
            
            # 5. 세션 대화 생성
            conversation_data = self.create_test_conversation_data(session_id)
            conversation_id = self.insert_test_conversation(conversation_data)
            
            # 6. 세션 퀴즈 생성
            quiz_data = self.create_test_quiz_data(session_id)
            quiz_id = self.insert_test_quiz(quiz_data)
            
            return {
                'user_id': user_id,
                'session_id': session_id,
                'conversation_id': conversation_id,
                'quiz_id': quiz_id
            }
            
        except Exception as e:
            # 실패 시 생성된 데이터 정리
            self.cleanup_all_test_data()
            raise Exception(f"완전한 테스트 데이터 생성 실패: {e}")

    # ================================
    # 테스트 데이터 삭제 메서드들
    # ================================
    
    def cleanup_test_conversations(self) -> None:
        """테스트 대화 데이터 정리"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        try:
            for conversation_id in self.created_data_ids['session_conversations']:
                # conversation_id 형식: session_id_message_sequence
                parts = conversation_id.rsplit('_', 1)  # 마지막 '_'로만 분리
                if len(parts) == 2:
                    session_id, message_sequence = parts
                    query = """
                    DELETE FROM session_conversations 
                    WHERE session_id = %s AND message_sequence = %s
                    """
                    execute_query(query, (session_id, int(message_sequence)))
            
            self.created_data_ids['session_conversations'].clear()
            
        except Exception as e:
            print(f"테스트 대화 데이터 정리 중 오류: {e}")
    
    def cleanup_test_quizzes(self) -> None:
        """테스트 퀴즈 데이터 정리"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        try:
            for session_id in self.created_data_ids['session_quizzes']:
                query = """
                DELETE FROM session_quizzes 
                WHERE session_id = %s
                """
                execute_query(query, (session_id,))
            
            self.created_data_ids['session_quizzes'].clear()
            
        except Exception as e:
            print(f"테스트 퀴즈 데이터 정리 중 오류: {e}")
    
    def cleanup_test_sessions(self) -> None:
        """테스트 세션 데이터 정리"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        try:
            for session_id in self.created_data_ids['learning_sessions']:
                query = "DELETE FROM learning_sessions WHERE session_id = %s"
                execute_query(query, (session_id,))
            
            self.created_data_ids['learning_sessions'].clear()
            
        except Exception as e:
            print(f"테스트 세션 데이터 정리 중 오류: {e}")
    
    def cleanup_test_user_statistics(self) -> None:
        """테스트 사용자 통계 데이터 정리"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        try:
            for user_id in self.created_data_ids['user_statistics']:
                query = "DELETE FROM user_statistics WHERE user_id = %s"
                execute_query(query, (user_id,))
            
            self.created_data_ids['user_statistics'].clear()
            
        except Exception as e:
            print(f"테스트 사용자 통계 데이터 정리 중 오류: {e}")
    
    def cleanup_test_user_progress(self) -> None:
        """테스트 사용자 진행 상태 데이터 정리"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        try:
            for user_id in self.created_data_ids['user_progress']:
                query = "DELETE FROM user_progress WHERE user_id = %s"
                execute_query(query, (user_id,))
            
            self.created_data_ids['user_progress'].clear()
            
        except Exception as e:
            print(f"테스트 사용자 진행 상태 데이터 정리 중 오류: {e}")
    
    def cleanup_test_users(self) -> None:
        """테스트 사용자 데이터 정리"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        try:
            for user_id in self.created_data_ids['users']:
                query = "DELETE FROM users WHERE user_id = %s"
                execute_query(query, (user_id,))
            
            self.created_data_ids['users'].clear()
            
        except Exception as e:
            print(f"테스트 사용자 데이터 정리 중 오류: {e}")
    
    def cleanup_all_test_data(self) -> None:
        """
        모든 테스트 데이터 정리
        의존성 순서를 고려하여 삭제합니다.
        """
        try:
            # 의존성 순서에 따른 삭제 (자식 → 부모 순서)
            self.cleanup_test_conversations()
            self.cleanup_test_quizzes()
            self.cleanup_test_sessions()
            self.cleanup_test_user_statistics()
            self.cleanup_test_user_progress()
            self.cleanup_test_users()
            
            print("✅ 모든 테스트 데이터 정리 완료")
            
        except Exception as e:
            print(f"❌ 테스트 데이터 정리 중 오류: {e}")
            # 강제 정리 시도
            self._force_cleanup()
    
    def _force_cleanup(self) -> None:
        """
        강제 테스트 데이터 정리
        일반 정리가 실패했을 때 사용합니다.
        """
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from app.utils.database.connection import execute_query
        
        try:
            # 테스트 데이터 패턴으로 강제 삭제
            force_cleanup_queries = [
                "DELETE FROM session_conversations WHERE session_id LIKE 'user999_%'",
                "DELETE FROM session_quizzes WHERE session_id LIKE 'user999_%'",
                "DELETE FROM learning_sessions WHERE session_id LIKE 'user999_%'",
                "DELETE FROM user_statistics WHERE user_id = 999",
                "DELETE FROM user_progress WHERE user_id = 999",
                "DELETE FROM users WHERE user_id = 999 OR login_id LIKE 'test_user_%'"
            ]
            
            for query in force_cleanup_queries:
                try:
                    execute_query(query)
                except Exception as e:
                    print(f"강제 정리 쿼리 실행 중 오류: {e}")
            
            # 추적 데이터 초기화
            for key in self.created_data_ids:
                self.created_data_ids[key].clear()
            
            print("⚠️ 강제 테스트 데이터 정리 완료")
            
        except Exception as e:
            print(f"❌ 강제 테스트 데이터 정리 실패: {e}")
    
    # ================================
    # 유틸리티 메서드들
    # ================================
    
    def get_created_data_summary(self) -> Dict[str, int]:
        """
        생성된 테스트 데이터 요약 정보 반환
        
        Returns:
            Dict[str, int]: 테이블별 생성된 데이터 개수
        """
        return {
            table: len(ids) for table, ids in self.created_data_ids.items()
        }
    
    def is_data_created(self, table_name: str) -> bool:
        """
        특정 테이블에 테스트 데이터가 생성되었는지 확인
        
        Args:
            table_name (str): 테이블 이름
            
        Returns:
            bool: 데이터 생성 여부
        """
        return len(self.created_data_ids.get(table_name, [])) > 0

# 전역 테스트 데이터 매니저 인스턴스
test_data_manager = TestDataManager()