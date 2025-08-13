# backend/tests/0813/test_three_agents/test_state_validation.py
"""
State 객체 검증 및 데이터 흐름 테스트
"""

import sys
import os
import pytest
from pathlib import Path

# 백엔드 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app.core.langraph.state_manager import TutorState
from datetime import datetime


class TestStateValidation:
    """State 객체 검증 테스트 클래스"""
    
    def test_state_initialization(self):
        """TutorState 객체 초기화 테스트"""
        print("\n=== TutorState 객체 초기화 테스트 ===")
        
        # 기본 TutorState 생성
        state: TutorState = {
            'user_id': 1,
            'user_type': 'beginner',
            'current_chapter': 2,
            'current_section': 2,
            'current_agent': 'theory_educator',
            'session_progress_stage': 'session_start',
            'ui_mode': 'chat',
            'current_question_type': 'multiple_choice',
            'current_question_number': 0,
            'current_question_content': '',
            'current_question_answer': '',
            'is_answer_correct': 0,
            'evaluation_feedback': '',
            'hint_usage_count': 0,
            'theory_draft': '',
            'quiz_draft': '',
            'feedback_draft': '',
            'qna_draft': '',
            'previous_agent': '',
            'session_decision_result': '',
            'current_session_count': 1,
            'session_start_time': datetime.now(),
            'current_session_conversations': []
        }
        
        print(f"생성된 TutorState 주요 필드:")
        print(f"- user_id: {state['user_id']}")
        print(f"- user_type: {state['user_type']}")
        print(f"- current_chapter: {state['current_chapter']}")
        print(f"- current_section: {state['current_section']}")
        print(f"- current_question_type: {state['current_question_type']}")
        
        # 필수 필드 검증
        assert state['user_id'] == 1
        assert state['user_type'] == 'beginner'
        assert state['current_chapter'] == 2
        assert state['current_section'] == 2
        assert state['current_question_type'] == 'multiple_choice'
        assert state['current_session_count'] == 1  # 기본값
        
        print("✅ TutorState 초기화 테스트 통과")
    
    def test_tutor_state_field_validation(self):
        """TutorState 필드 검증 테스트"""
        print("\n=== TutorState 필드 검증 테스트 ===")
        
        # TutorState 생성 및 필드 업데이트
        state: TutorState = {
            'user_id': 1,
            'user_type': 'beginner',
            'current_chapter': 2,
            'current_section': 2,
            'current_agent': 'theory_educator',
            'session_progress_stage': 'session_start',
            'ui_mode': 'chat',
            'current_question_type': 'multiple_choice',
            'current_question_number': 0,
            'current_question_content': '',
            'current_question_answer': '',
            'is_answer_correct': 0,
            'evaluation_feedback': '',
            'hint_usage_count': 0,
            'theory_draft': '',
            'quiz_draft': '',
            'feedback_draft': '',
            'qna_draft': '',
            'previous_agent': '',
            'session_decision_result': '',
            'current_session_count': 1,
            'session_start_time': datetime.now(),
            'current_session_conversations': []
        }
        
        # 이론 내용 추가
        state['theory_draft'] = "이것은 테스트용 이론 설명입니다."
        state['session_progress_stage'] = 'theory_completed'
        
        print(f"이론 완료 후 State:")
        print(f"- theory_draft 길이: {len(state['theory_draft'])}")
        print(f"- session_progress_stage: {state['session_progress_stage']}")
        
        # 퀴즈 내용 추가
        state['quiz_draft'] = "이것은 테스트용 퀴즈입니다."
        state['current_question_content'] = "AI의 정의는 무엇인가요?"
        state['current_question_number'] = 1
        
        print(f"퀴즈 완료 후 State:")
        print(f"- quiz_draft 길이: {len(state['quiz_draft'])}")
        print(f"- current_question_content: {state['current_question_content']}")
        print(f"- current_question_number: {state['current_question_number']}")
        
        # 사용자 답변 및 평가 추가
        state['current_question_answer'] = "인공지능"
        state['is_answer_correct'] = 1  # 객관식 정답
        state['evaluation_feedback'] = "정답입니다!"
        state['session_decision_result'] = 'proceed'
        
        print(f"평가 완료 후 State:")
        print(f"- current_question_answer: {state['current_question_answer']}")
        print(f"- is_answer_correct: {state['is_answer_correct']}")
        print(f"- evaluation_feedback: {state['evaluation_feedback']}")
        print(f"- session_decision_result: {state['session_decision_result']}")
        
        # 검증
        assert state['theory_draft'] != ''
        assert state['quiz_draft'] != ''
        assert state['current_question_content'] != ''
        assert state['current_question_answer'] != ''
        assert state['is_answer_correct'] == 1
        assert state['session_decision_result'] == 'proceed'
        
        print("✅ TutorState 필드 검증 테스트 통과")


if __name__ == "__main__":
    # 개별 테스트 실행
    test_instance = TestStateValidation()
    
    print("State 검증 테스트 실행 중...")
    
    try:
        test_instance.test_state_initialization()
        test_instance.test_tutor_state_field_validation()
        
        print("\n" + "="*60)
        print("✅ 모든 State 검증 테스트가 성공적으로 완료되었습니다!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()