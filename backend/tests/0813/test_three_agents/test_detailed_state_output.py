# backend/tests/0813/test_three_agents/test_detailed_state_output.py
"""
세 에이전트 실행 후 TutorState 상세 내용 출력 테스트
"""

import sys
import os
from datetime import datetime
import json

# 백엔드 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app.agents.theory_educator.theory_educator_agent import TheoryEducator
from app.agents.quiz_generator.quiz_generator_agent import QuizGenerator
from app.agents.evaluation_feedback.evaluation_feedback_agent import EvaluationFeedbackAgent
from app.core.langraph.state_manager import TutorState


def print_separator(title):
    """구분선과 제목 출력"""
    print("\n" + "="*80)
    print(f" {title} ")
    print("="*80)


def print_state_field(field_name, value, max_length=500):
    """State 필드를 보기 좋게 출력"""
    print(f"\n📋 {field_name}:")
    if isinstance(value, str):
        if len(value) > max_length:
            print(f"   길이: {len(value)}자")
            print(f"   내용: {value[:max_length]}...")
            print(f"   [... {len(value) - max_length}자 더 있음]")
        else:
            print(f"   길이: {len(value)}자")
            print(f"   내용: {value}")
    elif isinstance(value, (int, float)):
        print(f"   값: {value}")
    elif isinstance(value, bool):
        print(f"   값: {value}")
    elif isinstance(value, list):
        print(f"   리스트 길이: {len(value)}")
        if value:
            print(f"   내용: {value}")
    elif isinstance(value, dict):
        print(f"   딕셔너리 키 개수: {len(value)}")
        print(f"   내용: {json.dumps(value, ensure_ascii=False, indent=2)}")
    else:
        print(f"   값: {value}")


def detailed_state_analysis():
    """상세한 State 분석 실행"""
    print_separator("세 에이전트 실행 및 TutorState 상세 분석")
    
    # 에이전트 초기화
    theory_agent = TheoryEducator()
    quiz_agent = QuizGenerator()
    feedback_agent = EvaluationFeedbackAgent()
    
    # 초기 TutorState 설정 (객관식)
    print_separator("1. 초기 TutorState 설정")
    initial_state: TutorState = {
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
    
    print(f"🎯 테스트 시나리오: 챕터 {initial_state['current_chapter']} 섹션 {initial_state['current_section']} (객관식)")
    print(f"👤 사용자: ID {initial_state['user_id']}, 유형 {initial_state['user_type']}")
    print(f"📅 시작 시간: {initial_state['session_start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 2단계: 이론 에이전트 실행
    print_separator("2. 이론 에이전트 (TheoryEducator) 실행")
    try:
        theory_state = theory_agent.process(initial_state)
        
        print("✅ 이론 에이전트 실행 완료")
        print_state_field("theory_draft", theory_state.get('theory_draft', ''))
        print_state_field("session_progress_stage", theory_state.get('session_progress_stage', ''))
        print_state_field("current_agent", theory_state.get('current_agent', ''))
        
    except Exception as e:
        print(f"❌ 이론 에이전트 실행 오류: {e}")
        return
    
    # 3단계: 퀴즈 생성 에이전트 실행
    print_separator("3. 퀴즈 생성 에이전트 (QuizGenerator) 실행")
    try:
        theory_state['current_agent'] = 'quiz_generator'
        quiz_state = quiz_agent.process(theory_state)
        
        print("✅ 퀴즈 생성 에이전트 실행 완료")
        print_state_field("quiz_draft", quiz_state.get('quiz_draft', ''))
        print_state_field("current_question_content", quiz_state.get('current_question_content', ''))
        print_state_field("current_question_type", quiz_state.get('current_question_type', ''))
        print_state_field("current_question_number", quiz_state.get('current_question_number', 0))
        
    except Exception as e:
        print(f"❌ 퀴즈 생성 에이전트 실행 오류: {e}")
        return
    
    # 4단계: 사용자 답변 시뮬레이션
    print_separator("4. 사용자 답변 시뮬레이션")
    quiz_state['current_question_answer'] = 'A'  # 임시 답변
    print(f"🙋‍♂️ 사용자 답변: {quiz_state['current_question_answer']}")
    
    # 5단계: 평가 피드백 에이전트 실행
    print_separator("5. 평가 피드백 에이전트 (EvaluationFeedbackAgent) 실행")
    try:
        quiz_state['current_agent'] = 'evaluation_feedback'
        final_state = feedback_agent.process(quiz_state)
        
        print("✅ 평가 피드백 에이전트 실행 완료")
        print_state_field("evaluation_feedback", final_state.get('evaluation_feedback', ''))
        print_state_field("feedback_draft", final_state.get('feedback_draft', ''))
        print_state_field("is_answer_correct", final_state.get('is_answer_correct', 0))
        print_state_field("session_decision_result", final_state.get('session_decision_result', ''))
        
    except Exception as e:
        print(f"❌ 평가 피드백 에이전트 실행 오류: {e}")
        return
    
    # 6단계: 최종 TutorState 전체 분석
    print_separator("6. 최종 TutorState 전체 분석")
    
    print("\n🔍 기본 정보:")
    print(f"   - user_id: {final_state['user_id']}")
    print(f"   - user_type: {final_state['user_type']}")
    print(f"   - current_chapter: {final_state['current_chapter']}")
    print(f"   - current_section: {final_state['current_section']}")
    print(f"   - current_session_count: {final_state['current_session_count']}")
    
    print("\n🎯 진행 상태:")
    print(f"   - current_agent: {final_state['current_agent']}")
    print(f"   - session_progress_stage: {final_state['session_progress_stage']}")
    print(f"   - ui_mode: {final_state['ui_mode']}")
    
    print("\n❓ 퀴즈 정보:")
    print(f"   - current_question_type: {final_state['current_question_type']}")
    print(f"   - current_question_number: {final_state['current_question_number']}")
    print(f"   - hint_usage_count: {final_state['hint_usage_count']}")
    
    print("\n💬 사용자 상호작용:")
    print_state_field("current_question_content", final_state.get('current_question_content', ''), 200)
    print_state_field("current_question_answer", final_state.get('current_question_answer', ''))
    
    print("\n📊 평가 결과:")
    print(f"   - is_answer_correct: {final_state['is_answer_correct']}")
    print(f"   - session_decision_result: {final_state['session_decision_result']}")
    
    print("\n📝 에이전트 생성 대본들:")
    print_state_field("theory_draft", final_state.get('theory_draft', ''), 300)
    print_state_field("quiz_draft", final_state.get('quiz_draft', ''), 300)
    print_state_field("feedback_draft", final_state.get('feedback_draft', ''), 300)
    print_state_field("evaluation_feedback", final_state.get('evaluation_feedback', ''), 300)
    
    print("\n💾 대화 기록:")
    print_state_field("current_session_conversations", final_state.get('current_session_conversations', []))
    
    print_separator("분석 완료")
    print("🎉 세 에이전트의 순차 실행이 성공적으로 완료되었습니다!")
    print(f"📈 총 처리된 데이터:")
    print(f"   - 이론 설명: {len(final_state.get('theory_draft', ''))}자")
    print(f"   - 퀴즈 대본: {len(final_state.get('quiz_draft', ''))}자") 
    print(f"   - 피드백 대본: {len(final_state.get('feedback_draft', ''))}자")
    print(f"   - 평가 피드백: {len(final_state.get('evaluation_feedback', ''))}자")


def detailed_subjective_analysis():
    """주관식 퀴즈 상세 분석"""
    print_separator("주관식 퀴즈 세 에이전트 실행 및 TutorState 상세 분석")
    
    # 에이전트 초기화
    theory_agent = TheoryEducator()
    quiz_agent = QuizGenerator()
    feedback_agent = EvaluationFeedbackAgent()
    
    # 초기 TutorState 설정 (주관식)
    print_separator("1. 초기 TutorState 설정 (주관식)")
    initial_state: TutorState = {
        'user_id': 2,
        'user_type': 'beginner',
        'current_chapter': 5,
        'current_section': 3,
        'current_agent': 'theory_educator',
        'session_progress_stage': 'session_start',
        'ui_mode': 'chat',
        'current_question_type': 'subjective',
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
    
    print(f"🎯 테스트 시나리오: 챕터 {initial_state['current_chapter']} 섹션 {initial_state['current_section']} (주관식)")
    print(f"👤 사용자: ID {initial_state['user_id']}, 유형 {initial_state['user_type']}")
    
    try:
        # 이론 에이전트 실행
        print_separator("2. 이론 에이전트 실행")
        theory_state = theory_agent.process(initial_state)
        print("✅ 이론 에이전트 실행 완료")
        print_state_field("theory_draft", theory_state.get('theory_draft', ''), 400)
        
        # 퀴즈 생성 에이전트 실행
        print_separator("3. 퀴즈 생성 에이전트 실행")
        theory_state['current_agent'] = 'quiz_generator'
        quiz_state = quiz_agent.process(theory_state)
        print("✅ 퀴즈 생성 에이전트 실행 완료")
        print_state_field("quiz_draft", quiz_state.get('quiz_draft', ''), 400)
        print_state_field("current_question_content", quiz_state.get('current_question_content', ''))
        
        # 사용자 답변 시뮬레이션 (주관식)
        print_separator("4. 사용자 답변 시뮬레이션 (주관식)")
        user_answer = """
        AI 프롬프트 엔지니어링에서 가장 중요한 것은 명확하고 구체적인 지시사항을 제공하는 것입니다.
        예를 들어, '글을 써줘'보다는 '마케팅 전문가의 관점에서 신제품 런칭을 위한 500자 내외의 보도자료를 작성해줘'와 같이
        역할, 목적, 분량을 명시하는 것이 효과적입니다. 또한 예시를 제공하거나 단계별로 작업을 나누어 요청하는 것도 좋은 방법입니다.
        """
        quiz_state['current_question_answer'] = user_answer.strip()
        print_state_field("사용자 답변", quiz_state['current_question_answer'])
        
        # 평가 피드백 에이전트 실행
        print_separator("5. 평가 피드백 에이전트 실행")
        quiz_state['current_agent'] = 'evaluation_feedback'
        final_state = feedback_agent.process(quiz_state)
        print("✅ 평가 피드백 에이전트 실행 완료")
        print_state_field("evaluation_feedback", final_state.get('evaluation_feedback', ''))
        print_state_field("feedback_draft", final_state.get('feedback_draft', ''))
        print_state_field("is_answer_correct (점수)", final_state.get('is_answer_correct', 0))
        print_state_field("session_decision_result", final_state.get('session_decision_result', ''))
        
        print_separator("주관식 분석 완료")
        print("🎉 주관식 퀴즈 처리가 성공적으로 완료되었습니다!")
        print(f"📊 최종 점수: {final_state.get('is_answer_correct', 0)}점")
        print(f"🚀 진행 결정: {final_state.get('session_decision_result', '')}")
        
    except Exception as e:
        print(f"❌ 주관식 분석 중 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 세 에이전트 TutorState 상세 분석 시작")
    
    # 객관식 분석
    detailed_state_analysis()
    
    print("\n" + "🔄"*40)
    print("다음: 주관식 분석")
    print("🔄"*40)
    
    # 주관식 분석
    detailed_subjective_analysis()
    
    print("\n" + "🎯"*40)
    print("모든 분석이 완료되었습니다!")
    print("🎯"*40)