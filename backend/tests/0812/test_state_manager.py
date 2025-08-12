# backend/tests/test_state_manager.py

import pytest
import sys
import os
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.langraph.state_manager import StateManager, TutorState

class TestStateManager:
    """StateManager 기본 동작 테스트"""
    
    def test_state_manager_initialization(self):
        """StateManager 초기화 테스트"""
        state_manager = StateManager()
        assert state_manager is not None
        print("✅ StateManager 초기화 성공")
    
    def test_tutor_state_creation(self):
        """TutorState 생성 테스트"""
        state = TutorState(
            user_id=1,
            user_type="beginner",
            current_chapter=1,
            current_section=1,
            current_agent="theory_educator",
            session_progress_stage="session_start",
            ui_mode="chat",
            current_question_type="multiple_choice",
            current_question_number=1,
            current_question_content="",
            current_question_answer="",
            is_answer_correct=0,
            evaluation_feedback="",
            hint_usage_count=0,
            theory_draft="",
            quiz_draft="",
            feedback_draft="",
            qna_draft="",
            previous_agent="",
            session_decision_result="proceed",
            current_session_count=1,
            session_start_time=datetime.now(),
            current_session_conversations=[]
        )
        
        assert state["user_id"] == 1
        assert state["current_chapter"] == 1
        assert state["current_section"] == 1
        print("✅ TutorState 생성 성공")
    
    def test_state_manager_basic_operations(self):
        """StateManager 기본 연산 테스트"""
        state_manager = StateManager()
        
        # 초기 상태 생성
        initial_state = TutorState(
            user_id=1,
            user_type="beginner",
            current_chapter=1,
            current_section=1,
            current_agent="theory_educator",
            session_progress_stage="session_start",
            ui_mode="chat",
            current_question_type="multiple_choice",
            current_question_number=1,
            current_question_content="",
            current_question_answer="",
            is_answer_correct=0,
            evaluation_feedback="",
            hint_usage_count=0,
            theory_draft="",
            quiz_draft="",
            feedback_draft="",
            qna_draft="",
            previous_agent="",
            session_decision_result="proceed",
            current_session_count=1,
            session_start_time=datetime.now(),
            current_session_conversations=[]
        )
        
        # 상태 업데이트 테스트
        updated_state = state_manager.update_agent_transition(
            initial_state,
            "quiz_generator"
        )
        
        assert updated_state["current_agent"] == "quiz_generator"
        print("✅ StateManager 상태 업데이트 성공")

if __name__ == "__main__":
    test = TestStateManager()
    test.test_state_manager_initialization()
    test.test_tutor_state_creation()
    test.test_state_manager_basic_operations()
    print("🎉 StateManager 모든 테스트 통과!")