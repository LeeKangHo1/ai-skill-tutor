# backend/tests/0813/test_agents_sequential_execution.py

import sys
import os
import time
import json
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.agents.theory_educator.theory_educator_agent import TheoryEducator
from app.agents.quiz_generator.quiz_generator_agent import QuizGenerator
from app.core.langraph.state_manager import TutorState, state_manager


def create_test_state() -> TutorState:
    """테스트용 초기 State 생성"""
    from datetime import datetime
    return {
        # 기본 사용자 정보
        "user_id": 1001,
        "user_type": "beginner",
        
        # 학습 진행 상태
        "current_chapter": 1,
        "current_section": 1,
        "current_agent": "session_manager",
        
        # 학습 세션 진행 단계
        "session_progress_stage": "session_start",
        
        # UI 모드 제어
        "ui_mode": "chat",
        
        # 퀴즈 관련 정보
        "current_question_type": "multiple_choice",
        "current_question_number": 0,
        "current_question_content": "",
        "current_question_answer": "",
        "is_answer_correct": 0,
        "evaluation_feedback": "",
        "hint_usage_count": 0,
        
        # 에이전트 대본 저장
        "theory_draft": "",
        "quiz_draft": "",
        "feedback_draft": "",
        "qna_draft": "",
        
        # 라우팅 & 디버깅
        "previous_agent": "",
        
        # 학습 세션 제어
        "session_decision_result": "",
        "current_session_count": 0,
        "session_start_time": datetime.now(),
        
        # 대화 관리
        "current_session_conversations": [],
        "recent_sessions_summary": []
    }


def print_state_summary(state: TutorState, title: str):
    """State 주요 내용을 요약해서 출력"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    
    print(f"사용자 ID: {state.get('user_id', 'N/A')}")
    print(f"사용자 타입: {state.get('user_type', 'N/A')}")
    print(f"현재 챕터: {state.get('current_chapter', 'N/A')}")
    print(f"현재 섹션: {state.get('current_section', 'N/A')}")
    print(f"현재 에이전트: {state.get('current_agent', 'N/A')}")
    print(f"세션 카운트: {state.get('current_session_count', 'N/A')}")
    
    # 진행 상황
    progress_stage = state.get('session_progress_stage', 'N/A')
    print(f"진행 단계: {progress_stage}")
    print(f"UI 모드: {state.get('ui_mode', 'N/A')}")
    
    # 대본 상태
    theory_draft = state.get('theory_draft', '')
    quiz_draft = state.get('quiz_draft', '')
    feedback_draft = state.get('feedback_draft', '')
    qna_draft = state.get('qna_draft', '')
    
    print(f"\n이론 대본 길이: {len(theory_draft)} 문자")
    if theory_draft:
        print(f"이론 대본 미리보기: {theory_draft[:100]}...")
    
    print(f"퀴즈 대본 길이: {len(quiz_draft)} 문자")
    if quiz_draft:
        print(f"퀴즈 대본 미리보기: {quiz_draft[:100]}...")
    
    print(f"피드백 대본 길이: {len(feedback_draft)} 문자")
    print(f"QnA 대본 길이: {len(qna_draft)} 문자")
    
    # 대화 기록
    conversations = state.get('current_session_conversations', [])
    print(f"\n대화 기록 수: {len(conversations)}")
    for i, conv in enumerate(conversations[-3:], 1):  # 최근 3개만 표시
        print(f"  {i}. [{conv.get('agent_name', 'unknown')}] {conv.get('message', '')[:50]}...")


def test_sequential_execution():
    """두 에이전트 연속 실행 테스트"""
    print("AI 활용법 학습 튜터 - 에이전트 연속 실행 테스트")
    print("=" * 60)
    
    # 시작 시간 기록
    total_start_time = time.time()
    
    # 1. 초기 State 생성
    initial_state = create_test_state()
    print_state_summary(initial_state, "초기 State")
    
    # 2. TheoryEducator 실행
    print(f"\n{'*'*30} TheoryEducator 실행 {'*'*30}")
    theory_agent = TheoryEducator()
    
    theory_start_time = time.time()
    state_after_theory = theory_agent.process(initial_state)
    theory_end_time = time.time()
    theory_duration = theory_end_time - theory_start_time
    
    print(f"TheoryEducator 실행 시간: {theory_duration:.2f}초")
    print_state_summary(state_after_theory, "TheoryEducator 실행 후 State")
    
    # 3. QuizGenerator 실행
    print(f"\n{'*'*30} QuizGenerator 실행 {'*'*30}")
    quiz_agent = QuizGenerator()
    
    quiz_start_time = time.time()
    final_state = quiz_agent.process(state_after_theory)
    quiz_end_time = time.time()
    quiz_duration = quiz_end_time - quiz_start_time
    
    print(f"QuizGenerator 실행 시간: {quiz_duration:.2f}초")
    print_state_summary(final_state, "QuizGenerator 실행 후 최종 State")
    
    # 4. 전체 실행 시간 계산
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # 5. 실행 시간 요약
    print(f"\n{'='*60}")
    print("실행 시간 요약")
    print(f"{'='*60}")
    print(f"TheoryEducator 실행 시간: {theory_duration:.2f}초")
    print(f"QuizGenerator 실행 시간: {quiz_duration:.2f}초")
    print(f"총 실행 시간: {total_duration:.2f}초")
    print(f"에이전트 실행 시간 합계: {theory_duration + quiz_duration:.2f}초")
    print(f"오버헤드 시간: {total_duration - (theory_duration + quiz_duration):.2f}초")
    
    # 6. 최종 State 상세 정보
    print(f"\n{'='*60}")
    print("최종 State 상세 정보")
    print(f"{'='*60}")
    
    # JSON 형태로 전체 State 출력 (민감한 정보 제외)
    display_state = {
        "user_info": {
            "user_id": final_state.get('user_id'),
            "user_type": final_state.get('user_type')
        },
        "learning_progress": {
            "current_chapter": final_state.get('current_chapter'),
            "current_section": final_state.get('current_section'),
            "session_count": final_state.get('current_session_count'),
            "progress_steps": final_state.get('session_progress', [])
        },
        "content_status": {
            "theory_draft_length": len(final_state.get('theory_draft', '')),
            "quiz_draft_length": len(final_state.get('quiz_draft', '')),
            "conversation_count": len(final_state.get('conversation_history', []))
        }
    }
    
    print(json.dumps(display_state, indent=2, ensure_ascii=False))
    
    return final_state


if __name__ == "__main__":
    try:
        final_state = test_sequential_execution()
        print(f"\n{'='*60}")
        print("테스트 완료!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()