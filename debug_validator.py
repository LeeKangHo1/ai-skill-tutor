# debug_validator.py
# State 검증기 디버깅 스크립트

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from backend.app.core.langraph.state.state_validator import StateValidator, StateValidationError

def debug_validation():
    """검증 실패 원인 디버깅"""
    validator = StateValidator()
    
    # 기본 State 생성
    base_state = {
        "user_id": 1,
        "user_type": "beginner",
        "current_chapter": 1,
        "current_section": 1,
        "current_session_count": 1,
        "session_progress_stage": "session_start",  # 유효한 값으로 수정
        "ui_mode": "chat",
        "quiz_type": "multiple_choice",
        "user_intent": "next_step",  # 유효한 값으로 수정
        "retry_decision_result": "proceed",
        "current_agent": "learning_supervisor",
        "subjective_answer_score": 0,
        "hint_usage_count": 0,
        "multiple_answer_correct": False,
        "quiz_content": "",
        "quiz_options": [],
        "quiz_correct_answer": None,
        "quiz_evaluation_criteria": [],
        "current_session_conversations": [],
        "recent_sessions_summary": [],
        "workflow_response": {},
        "session_start_time": datetime.now()
    }
    
    print("=== State 검증 디버깅 ===")
    
    # 검증 보고서 생성
    report = validator.get_validation_report(base_state)
    
    print(f"전체 유효성: {report['is_valid']}")
    print(f"수행된 검사: {report['checks_performed']}")
    
    if report['errors']:
        print("\n오류 목록:")
        for error in report['errors']:
            print(f"- {error['step']}: {error['message']}")
            if error.get('field'):
                print(f"  필드: {error['field']}, 값: {error['value']}")
    
    if report['warnings']:
        print("\n경고 목록:")
        for warning in report['warnings']:
            print(f"- {warning['step']}: {warning['message']}")

if __name__ == "__main__":
    debug_validation()