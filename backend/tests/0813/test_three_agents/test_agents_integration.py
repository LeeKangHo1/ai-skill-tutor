# backend/tests/0813/test_three_agents/test_agents_integration.py
"""
세 에이전트 통합 테스트: 이론 에이전트 → 퀴즈 생성 에이전트 → 피드백 에이전트 순차 실행
"""

import sys
import os
import pytest
from datetime import datetime
from typing import Dict, Any

# 백엔드 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app.agents.theory_educator.theory_educator_agent import TheoryEducator
from app.agents.quiz_generator.quiz_generator_agent import QuizGenerator
from app.agents.evaluation_feedback.evaluation_feedback_agent import EvaluationFeedbackAgent
from app.core.langraph.state_manager import TutorState


class TestThreeAgentsIntegration:
    """세 에이전트 통합 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 초기화"""
        self.theory_agent = TheoryEducator()
        self.quiz_agent = QuizGenerator()
        self.feedback_agent = EvaluationFeedbackAgent()
    
    def test_objective_quiz_flow_chapter2_section2(self):
        """객관식 퀴즈 플로우 테스트 - 챕터 2 섹션 2"""
        print("\n=== 객관식 퀴즈 플로우 테스트 시작 (챕터 2 섹션 2) ===")
        
        # 1단계: 초기 TutorState 설정
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
        
        print(f"초기 State: 챕터 {initial_state['current_chapter']} 섹션 {initial_state['current_section']}")
        
        # 2단계: 이론 에이전트 실행
        print("\n--- 1단계: 이론 에이전트 실행 ---")
        try:
            theory_state = self.theory_agent.process(initial_state)
            
            print(f"이론 설명 결과:")
            print(f"- theory_draft 길이: {len(theory_state.get('theory_draft', ''))}")
            print(f"- theory_draft 미리보기: {theory_state.get('theory_draft', '')[:200]}...")
            
            # 3단계: 퀴즈 생성 에이전트 실행
            print("\n--- 2단계: 퀴즈 생성 에이전트 실행 ---")
            theory_state['current_agent'] = 'quiz_generator'
            quiz_state = self.quiz_agent.process(theory_state)
            
            print(f"퀴즈 생성 결과:")
            print(f"- quiz_draft 길이: {len(quiz_state.get('quiz_draft', ''))}")
            print(f"- current_question_content: {quiz_state.get('current_question_content', '')}")
            print(f"- current_question_type: {quiz_state.get('current_question_type', '')}")
            
            # 4단계: 사용자 답변 시뮬레이션 (정답)
            print("\n--- 3단계: 사용자 답변 시뮬레이션 (정답) ---")
            quiz_state['current_question_answer'] = 'A'  # 임시 정답
            print(f"사용자 답변: {quiz_state['current_question_answer']}")
            
            # 5단계: 평가 피드백 에이전트 실행
            print("\n--- 4단계: 평가 피드백 에이전트 실행 ---")
            quiz_state['current_agent'] = 'evaluation_feedback'
            final_state = self.feedback_agent.process(quiz_state)
            
            print(f"평가 피드백 결과:")
            print(f"- is_answer_correct: {final_state.get('is_answer_correct')}")
            print(f"- evaluation_feedback 길이: {len(final_state.get('evaluation_feedback', ''))}")
            print(f"- feedback_draft 길이: {len(final_state.get('feedback_draft', ''))}")
            print(f"- session_decision_result: {final_state.get('session_decision_result')}")
            
            # 최종 State 확인
            print(f"\n=== 최종 State 확인 ===")
            print(f"- user_id: {final_state['user_id']}")
            print(f"- current_chapter: {final_state['current_chapter']}")
            print(f"- current_section: {final_state['current_section']}")
            print(f"- current_question_type: {final_state['current_question_type']}")
            print(f"- is_answer_correct: {final_state['is_answer_correct']}")
            print(f"- session_decision_result: {final_state['session_decision_result']}")
            
            # 검증
            assert final_state.get('theory_draft') is not None
            assert final_state.get('quiz_draft') is not None
            assert final_state.get('evaluation_feedback') is not None
            
            print("\n=== 객관식 퀴즈 플로우 테스트 완료 ===")
            
        except Exception as e:
            print(f"테스트 실행 중 오류: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def test_subjective_quiz_flow_chapter5_section3(self):
        """주관식 퀴즈 플로우 테스트 - 챕터 5 섹션 3"""
        print("\n=== 주관식 퀴즈 플로우 테스트 시작 (챕터 5 섹션 3) ===")
        
        # 1단계: 초기 TutorState 설정 (주관식)
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
        
        print(f"초기 State: 챕터 {initial_state['current_chapter']} 섹션 {initial_state['current_section']} (주관식)")
        
        # 2단계: 이론 에이전트 실행
        print("\n--- 1단계: 이론 에이전트 실행 ---")
        try:
            theory_state = self.theory_agent.process(initial_state)
            
            print(f"이론 설명 결과:")
            print(f"- theory_draft 길이: {len(theory_state.get('theory_draft', ''))}")
            print(f"- theory_draft 미리보기: {theory_state.get('theory_draft', '')[:200]}...")
            
            # 3단계: 퀴즈 생성 에이전트 실행
            print("\n--- 2단계: 퀴즈 생성 에이전트 실행 ---")
            theory_state['current_agent'] = 'quiz_generator'
            quiz_state = self.quiz_agent.process(theory_state)
            
            print(f"퀴즈 생성 결과:")
            print(f"- quiz_draft 길이: {len(quiz_state.get('quiz_draft', ''))}")
            print(f"- current_question_content: {quiz_state.get('current_question_content', '')}")
            print(f"- current_question_type: {quiz_state.get('current_question_type', '')}")
            
            # 4단계: 사용자 답변 시뮬레이션 (주관식 답변)
            print("\n--- 3단계: 사용자 답변 시뮬레이션 (주관식) ---")
            user_answer = """
            AI 프롬프트 엔지니어링에서 가장 중요한 것은 명확하고 구체적인 지시사항을 제공하는 것입니다.
            예를 들어, '글을 써줘'보다는 '마케팅 전문가의 관점에서 신제품 런칭을 위한 500자 내외의 보도자료를 작성해줘'와 같이
            역할, 목적, 분량을 명시하는 것이 효과적입니다. 또한 예시를 제공하거나 단계별로 작업을 나누어 요청하는 것도 좋은 방법입니다.
            """
            quiz_state['current_question_answer'] = user_answer.strip()
            print(f"사용자 답변: {quiz_state['current_question_answer'][:100]}...")
            
            # 5단계: 평가 피드백 에이전트 실행
            print("\n--- 4단계: 평가 피드백 에이전트 실행 ---")
            quiz_state['current_agent'] = 'evaluation_feedback'
            final_state = self.feedback_agent.process(quiz_state)
            
            print(f"평가 피드백 결과:")
            print(f"- is_answer_correct (점수): {final_state.get('is_answer_correct')}")
            print(f"- evaluation_feedback 길이: {len(final_state.get('evaluation_feedback', ''))}")
            print(f"- feedback_draft 길이: {len(final_state.get('feedback_draft', ''))}")
            print(f"- session_decision_result: {final_state.get('session_decision_result')}")
            
            # 최종 State 확인
            print(f"\n=== 최종 State 확인 ===")
            print(f"- user_id: {final_state['user_id']}")
            print(f"- current_chapter: {final_state['current_chapter']}")
            print(f"- current_section: {final_state['current_section']}")
            print(f"- current_question_type: {final_state['current_question_type']}")
            print(f"- is_answer_correct (점수): {final_state['is_answer_correct']}")
            print(f"- session_decision_result: {final_state['session_decision_result']}")
            
            # 검증
            assert final_state.get('theory_draft') is not None
            assert final_state.get('quiz_draft') is not None
            assert final_state.get('evaluation_feedback') is not None
            assert isinstance(final_state.get('is_answer_correct'), (int, float))
            assert 0 <= final_state.get('is_answer_correct') <= 100
            
            print("\n=== 주관식 퀴즈 플로우 테스트 완료 ===")
            
        except Exception as e:
            print(f"테스트 실행 중 오류: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def test_state_persistence_through_agents(self):
        """State 데이터 지속성 테스트"""
        print("\n=== State 데이터 지속성 테스트 시작 ===")
        
        # 초기 State 설정
        initial_state: TutorState = {
            'user_id': 999,
            'user_type': 'advanced',
            'current_chapter': 1,
            'current_section': 1,
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
            'current_session_count': 2,  # 재학습 상황
            'session_start_time': datetime.now(),
            'current_session_conversations': []
        }
        
        print(f"초기 State: 사용자 {initial_state['user_id']}, 챕터 {initial_state['current_chapter']}, 세션 {initial_state['current_session_count']}")
        
        try:
            # 각 에이전트 실행 후 State 변화 추적
            states_history = [initial_state.copy()]
            
            # 이론 에이전트
            theory_state = self.theory_agent.process(initial_state)
            states_history.append(theory_state.copy())
            
            # 퀴즈 생성 에이전트
            theory_state['current_agent'] = 'quiz_generator'
            quiz_state = self.quiz_agent.process(theory_state)
            states_history.append(quiz_state.copy())
            
            # 사용자 답변 추가
            quiz_state['current_question_answer'] = 'A'
            states_history.append(quiz_state.copy())
            
            # 평가 피드백 에이전트
            quiz_state['current_agent'] = 'evaluation_feedback'
            final_state = self.feedback_agent.process(quiz_state)
            states_history.append(final_state.copy())
            
            # State 변화 추적 출력
            print(f"\n--- State 변화 추적 ---")
            stage_names = ["초기", "이론 완료", "퀴즈 완료", "답변 추가", "피드백 완료"]
            for i, state in enumerate(states_history):
                print(f"{stage_names[i]} State:")
                print(f"  - user_id: {state['user_id']}")
                print(f"  - user_type: {state['user_type']}")
                print(f"  - current_chapter: {state['current_chapter']}")
                print(f"  - current_section: {state['current_section']}")
                print(f"  - current_session_count: {state['current_session_count']}")
                print(f"  - theory_draft 길이: {len(state.get('theory_draft', ''))}")
                print(f"  - quiz_draft 길이: {len(state.get('quiz_draft', ''))}")
                print(f"  - current_question_answer: {state.get('current_question_answer', '')}")
                print(f"  - is_answer_correct: {state.get('is_answer_correct', 0)}")
                print()
            
            # 검증: 초기 데이터가 최종까지 유지되는지 확인
            assert final_state['user_id'] == initial_state['user_id']
            assert final_state['user_type'] == initial_state['user_type']
            assert final_state['current_chapter'] == initial_state['current_chapter']
            assert final_state['current_section'] == initial_state['current_section']
            assert final_state['current_session_count'] == initial_state['current_session_count']
            
            print("=== State 데이터 지속성 테스트 완료 ===")
            
        except Exception as e:
            print(f"테스트 실행 중 오류: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    # 개별 테스트 실행을 위한 메인 함수
    def run_tests():
        test_instance = TestThreeAgentsIntegration()
        test_instance.setup_method()
        
        print("세 에이전트 통합 테스트 실행 중...")
        
        try:
            test_instance.test_objective_quiz_flow_chapter2_section2()
            test_instance.test_subjective_quiz_flow_chapter5_section3()
            test_instance.test_state_persistence_through_agents()
            print("\n모든 테스트가 성공적으로 완료되었습니다!")
        except Exception as e:
            print(f"\n테스트 실행 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    run_tests()