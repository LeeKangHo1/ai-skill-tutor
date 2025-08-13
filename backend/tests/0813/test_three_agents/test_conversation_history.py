# backend/tests/0813/test_three_agents/test_conversation_history.py
"""
세 에이전트 실행 후 current_session_conversations 상세 내용 출력 테스트
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


def print_conversation_header():
    """대화 기록 헤더 출력"""
    print("\n" + "🗨️" * 50)
    print("📋 SESSION CONVERSATIONS 상세 분석")
    print("🗨️" * 50)


def print_conversation_item(index, conversation, show_details=True):
    """개별 대화 항목을 보기 좋게 출력"""
    print(f"\n{'='*60}")
    print(f"💬 대화 #{index + 1}")
    print(f"{'='*60}")
    
    # 기본 정보
    print(f"🤖 에이전트: {conversation.get('agent_name', 'Unknown')}")
    print(f"📅 시간: {conversation.get('timestamp', 'Unknown')}")
    print(f"📝 메시지 타입: {conversation.get('message_type', 'Unknown')}")
    print(f"🎯 세션 단계: {conversation.get('session_stage', 'Unknown')}")
    
    # 메시지 내용
    message = conversation.get('message', '')
    print(f"\n💭 메시지 내용:")
    print(f"   길이: {len(message)}자")
    print(f"   내용: {message}")
    
    if show_details:
        # 추가 세부 정보가 있다면 출력
        for key, value in conversation.items():
            if key not in ['agent_name', 'timestamp', 'message_type', 'session_stage', 'message']:
                print(f"📌 {key}: {value}")


def analyze_conversation_patterns(conversations):
    """대화 패턴 분석"""
    print(f"\n{'🔍'*60}")
    print("📊 대화 패턴 분석")
    print(f"{'🔍'*60}")
    
    # 기본 통계
    total_conversations = len(conversations)
    print(f"📈 총 대화 수: {total_conversations}")
    
    if not conversations:
        print("❌ 대화 기록이 없습니다.")
        return
    
    # 에이전트별 분류
    agent_counts = {}
    message_types = {}
    session_stages = {}
    
    for conv in conversations:
        agent = conv.get('agent_name', 'Unknown')
        msg_type = conv.get('message_type', 'Unknown')
        stage = conv.get('session_stage', 'Unknown')
        
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
        message_types[msg_type] = message_types.get(msg_type, 0) + 1
        session_stages[stage] = session_stages.get(stage, 0) + 1
    
    print(f"\n🤖 에이전트별 대화 수:")
    for agent, count in agent_counts.items():
        print(f"   - {agent}: {count}개")
    
    print(f"\n📝 메시지 타입별 분포:")
    for msg_type, count in message_types.items():
        print(f"   - {msg_type}: {count}개")
    
    print(f"\n🎯 세션 단계별 분포:")
    for stage, count in session_stages.items():
        print(f"   - {stage}: {count}개")
    
    # 시간 순서 분석
    if conversations and 'timestamp' in conversations[0]:
        print(f"\n⏰ 시간 순서 분석:")
        first_time = conversations[0]['timestamp']
        last_time = conversations[-1]['timestamp']
        duration = last_time - first_time
        print(f"   - 첫 대화: {first_time.strftime('%H:%M:%S')}")
        print(f"   - 마지막 대화: {last_time.strftime('%H:%M:%S')}")
        print(f"   - 총 소요 시간: {duration.total_seconds():.2f}초")


def test_objective_conversation_history():
    """객관식 퀴즈 대화 기록 테스트"""
    print_conversation_header()
    print("🎯 테스트 시나리오: 객관식 퀴즈 (챕터 2 섹션 2)")
    
    # 에이전트 초기화
    theory_agent = TheoryEducator()
    quiz_agent = QuizGenerator()
    feedback_agent = EvaluationFeedbackAgent()
    
    # 초기 TutorState 설정
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
    
    try:
        # 1. 이론 에이전트 실행
        print("\n🔄 이론 에이전트 실행 중...")
        theory_state = theory_agent.process(initial_state)
        
        # 2. 퀴즈 생성 에이전트 실행
        print("🔄 퀴즈 생성 에이전트 실행 중...")
        theory_state['current_agent'] = 'quiz_generator'
        quiz_state = quiz_agent.process(theory_state)
        
        # 3. 사용자 답변 추가
        quiz_state['current_question_answer'] = 'B'  # 정답 시뮬레이션
        
        # 4. 평가 피드백 에이전트 실행
        print("🔄 평가 피드백 에이전트 실행 중...")
        quiz_state['current_agent'] = 'evaluation_feedback'
        final_state = feedback_agent.process(quiz_state)
        
        # 대화 기록 분석
        conversations = final_state.get('current_session_conversations', [])
        
        print(f"\n✅ 모든 에이전트 실행 완료!")
        print(f"📊 수집된 대화 기록: {len(conversations)}개")
        
        # 각 대화 항목 상세 출력
        for i, conversation in enumerate(conversations):
            print_conversation_item(i, conversation)
        
        # 패턴 분석
        analyze_conversation_patterns(conversations)
        
        return conversations
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_subjective_conversation_history():
    """주관식 퀴즈 대화 기록 테스트"""
    print_conversation_header()
    print("🎯 테스트 시나리오: 주관식 퀴즈 (챕터 5 섹션 3)")
    
    # 에이전트 초기화
    theory_agent = TheoryEducator()
    quiz_agent = QuizGenerator()
    feedback_agent = EvaluationFeedbackAgent()
    
    # 초기 TutorState 설정 (주관식)
    initial_state: TutorState = {
        'user_id': 2,
        'user_type': 'advanced',
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
    
    try:
        # 1. 이론 에이전트 실행
        print("\n🔄 이론 에이전트 실행 중...")
        theory_state = theory_agent.process(initial_state)
        
        # 2. 퀴즈 생성 에이전트 실행
        print("🔄 퀴즈 생성 에이전트 실행 중...")
        theory_state['current_agent'] = 'quiz_generator'
        quiz_state = quiz_agent.process(theory_state)
        
        # 3. 사용자 답변 추가 (주관식)
        user_answer = """
        AI에게 여름과 겨울의 날씨 차이에 대해 설명해 달라고 할 때, 
        다음과 같이 요청할 수 있습니다:
        
        "여름과 겨울의 날씨 차이를 리스트 형식으로 정리해 주세요.
        각 계절별로 다음 항목을 포함해 주세요:
        - 계절명
        - 평균 기온 범위
        - 주요 특징 (날씨, 옷차림, 활동 등)"
        
        이렇게 구체적으로 요청하면 원하는 형식의 답변을 받을 수 있습니다.
        """
        quiz_state['current_question_answer'] = user_answer.strip()
        
        # 4. 평가 피드백 에이전트 실행
        print("🔄 평가 피드백 에이전트 실행 중...")
        quiz_state['current_agent'] = 'evaluation_feedback'
        final_state = feedback_agent.process(quiz_state)
        
        # 대화 기록 분석
        conversations = final_state.get('current_session_conversations', [])
        
        print(f"\n✅ 모든 에이전트 실행 완료!")
        print(f"📊 수집된 대화 기록: {len(conversations)}개")
        
        # 각 대화 항목 상세 출력
        for i, conversation in enumerate(conversations):
            print_conversation_item(i, conversation)
        
        # 패턴 분석
        analyze_conversation_patterns(conversations)
        
        return conversations
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return []


def compare_conversation_histories(obj_conversations, subj_conversations):
    """객관식과 주관식 대화 기록 비교"""
    print(f"\n{'🔄'*60}")
    print("📊 객관식 vs 주관식 대화 기록 비교")
    print(f"{'🔄'*60}")
    
    print(f"\n📈 기본 통계:")
    print(f"   - 객관식 대화 수: {len(obj_conversations)}개")
    print(f"   - 주관식 대화 수: {len(subj_conversations)}개")
    
    if obj_conversations and subj_conversations:
        # 시간 비교
        obj_duration = obj_conversations[-1]['timestamp'] - obj_conversations[0]['timestamp']
        subj_duration = subj_conversations[-1]['timestamp'] - subj_conversations[0]['timestamp']
        
        print(f"\n⏰ 처리 시간 비교:")
        print(f"   - 객관식 소요 시간: {obj_duration.total_seconds():.2f}초")
        print(f"   - 주관식 소요 시간: {subj_duration.total_seconds():.2f}초")
        
        # 에이전트별 메시지 길이 비교
        print(f"\n📝 메시지 특성 비교:")
        for conversations, quiz_type in [(obj_conversations, "객관식"), (subj_conversations, "주관식")]:
            total_length = sum(len(conv.get('message', '')) for conv in conversations)
            avg_length = total_length / len(conversations) if conversations else 0
            print(f"   - {quiz_type} 평균 메시지 길이: {avg_length:.1f}자")


if __name__ == "__main__":
    print("🚀 세 에이전트 대화 기록 상세 분석 시작")
    
    # 객관식 테스트
    print("\n" + "🎯" * 30)
    print("객관식 퀴즈 대화 기록 분석")
    print("🎯" * 30)
    obj_conversations = test_objective_conversation_history()
    
    print("\n" + "📝" * 30)
    print("주관식 퀴즈 대화 기록 분석")
    print("📝" * 30)
    subj_conversations = test_subjective_conversation_history()
    
    # 비교 분석
    if obj_conversations and subj_conversations:
        compare_conversation_histories(obj_conversations, subj_conversations)
    
    print(f"\n{'🎉'*60}")
    print("모든 대화 기록 분석이 완료되었습니다!")
    print(f"{'🎉'*60}")