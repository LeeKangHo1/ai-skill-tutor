# backend/app/agents/evaluation_feedback/evaluation_feedback_agent.py
# v2.0 업데이트: State quiz 정보 직접 사용, update_evaluation_result 활용

import json
import logging
from typing import Dict, Any

from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.analysis.evaluation_tools import (
    evaluate_multiple_choice,
    determine_next_step,
    validate_quiz_data
)
from app.tools.content.feedback_tools_chatgpt import (
    evaluate_subjective_with_feedback,
    generate_multiple_choice_feedback,
    generate_simple_feedback
)


class EvaluationFeedbackAgent:
    """
    평가 및 피드백 에이전트 (v2.0)
    - QuizGenerator 완료 후 자동 호출
    - 객관식/주관식 답변 채점 및 피드백 생성
    - 다음 단계 진행 여부 결정
    - v2.0: State quiz 정보 직접 사용, update_evaluation_result 활용
    """
    
    def __init__(self):
        self.agent_name = "evaluation_feedback_agent"
        self.logger = logging.getLogger(__name__)
    
    def process(self, state: TutorState) -> TutorState:
        """
        평가 및 피드백 생성 메인 프로세스
        
        Args:
            state: 현재 TutorState
            
        Returns:
            업데이트된 TutorState (평가 결과 및 피드백 포함)
        """
        try:
            self.logger.info(f"[{self.agent_name}] 평가 및 피드백 생성 시작")
            
            # 1. 현재 상태 검증
            if not self._validate_state(state):
                return self._create_error_state(state, "State 검증 실패")
            
            # 2. State에서 퀴즈 데이터 직접 가져오기 (v2.0)
            quiz_data = self._get_quiz_data_from_state(state)
            if not quiz_data:
                return self._create_error_state(state, "State에서 퀴즈 데이터 추출 실패")
            
            # 3. 퀴즈 타입별 평가 및 피드백 생성 (v2.0 필드명)
            quiz_type = state["quiz_type"]  # current_question_type → quiz_type
            user_answer = state["user_answer"]  # current_question_answer → user_answer
            
            if quiz_type == "multiple_choice":
                score, feedback_text = self._process_multiple_choice(
                    quiz_data, user_answer, state["user_type"]
                )
            elif quiz_type == "subjective":
                score, feedback_text = self._process_subjective(
                    quiz_data, user_answer, state["user_type"]
                )
            else:
                return self._create_error_state(state, f"지원하지 않는 퀴즈 타입: {quiz_type}")
            
            # 4. 다음 단계 결정
            next_step = determine_next_step(score, quiz_type, state["current_session_count"])
            
            # 5. State 업데이트 (순수 피드백만 저장, 안내 멘트는 ResponseGenerator에서 처리)
            updated_state = self._update_state_with_results(
                state, score, feedback_text, next_step
            )
            
            self.logger.info(f"[{self.agent_name}] 평가 완료 - 점수: {score}, 다음단계: {next_step}")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"[{self.agent_name}] 오류 발생: {str(e)}")
            return self._create_error_state(state, str(e))
    
    def _validate_state(self, state: TutorState) -> bool:
        """State 유효성 검증 (v2.0 필드명 변경)"""
        required_fields = [
            "quiz_type", "quiz_content", "user_answer",  # v2.0 필드명
            "user_type", "current_session_count"
        ]
        
        for field in required_fields:
            if field not in state:
                self.logger.error(f"필수 필드 누락: {field}")
                return False
        
        # 사용자 답변이 실제로 있는지 확인
        user_answer = state["user_answer"].strip()
        if not user_answer:
            self.logger.error("사용자 답변이 비어있습니다.")
            return False
        
        # 퀴즈 내용이 있는지 확인
        quiz_content = state["quiz_content"].strip()
        if not quiz_content:
            self.logger.error("퀴즈 내용이 비어있습니다.")
            return False
        
        return True
    
    def _get_quiz_data_from_state(self, state: TutorState) -> Dict[str, Any]:
        """State에서 퀴즈 데이터 직접 추출 (v2.0 신규)"""
        try:
            quiz_type = state["quiz_type"]
            
            # State에서 퀴즈 정보 구성
            quiz_data = {
                "type": quiz_type,
                "question": state["quiz_content"],
                "hint": state.get("quiz_hint", "")
            }
            
            # 객관식 전용 필드
            if quiz_type == "multiple_choice":
                quiz_data.update({
                    "options": state.get("quiz_options", []),
                    "correct_answer": state.get("quiz_correct_answer", 1),
                    "explanation": state.get("quiz_explanation", "")
                })
            
            # 주관식 전용 필드
            elif quiz_type == "subjective":
                quiz_data.update({
                    "sample_answer": state.get("quiz_sample_answer", ""),
                    "evaluation_criteria": state.get("quiz_evaluation_criteria", [])
                })
            
            # 퀴즈 데이터 유효성 검증
            if not validate_quiz_data(quiz_data, quiz_type):
                self.logger.error("State 퀴즈 데이터 유효성 검증 실패")
                return None
            
            self.logger.info("State에서 퀴즈 데이터 추출 및 검증 완료")
            return quiz_data
            
        except Exception as e:
            self.logger.error(f"State 퀴즈 데이터 추출 중 오류: {str(e)}")
            return None
    
    def _process_multiple_choice(self, quiz_data: Dict[str, Any], user_answer: str, user_type: str) -> tuple:
        """객관식 평가 및 피드백 처리"""
        try:
            self.logger.info("객관식 평가 시작")
            
            # 1. 로컬 채점 (score: 0 또는 1, is_correct: bool, explanation: str)
            score, is_correct, explanation = evaluate_multiple_choice(quiz_data, user_answer)
            
            # 2. ChatGPT 피드백 생성
            feedback_text = generate_multiple_choice_feedback(
                quiz_data, user_answer, is_correct, user_type
            )
            
            return score, feedback_text
            
        except Exception as e:
            self.logger.error(f"객관식 처리 중 오류: {str(e)}")
            # 백업 피드백 생성
            fallback_feedback = generate_simple_feedback(
                "multiple_choice", 0, False, "처리 중 오류가 발생했습니다.", user_type
            )
            return 0, fallback_feedback
    
    def _process_subjective(self, quiz_data: Dict[str, Any], user_answer: str, user_type: str) -> tuple:
        """주관식 평가 및 피드백 처리"""
        try:
            self.logger.info("주관식 평가 시작 (ChatGPT 호출)")
            
            # ChatGPT 평가 및 피드백 생성
            score, feedback_text = evaluate_subjective_with_feedback(
                quiz_data, user_answer, user_type
            )
            
            return score, feedback_text
            
        except Exception as e:
            self.logger.error(f"주관식 처리 중 오류: {str(e)}")
            # 백업 피드백 생성
            fallback_feedback = generate_simple_feedback(
                "subjective", 50, None, "처리 중 오류가 발생했습니다.", user_type
            )
            return 50, fallback_feedback
    
    def _update_state_with_results(
        self, 
        state: TutorState, 
        score: int, 
        feedback_text: str,
        next_step: str
    ) -> TutorState:
        """평가 결과로 State 업데이트 (v2.0 update_evaluation_result 사용)"""
        
        # 1. 평가 결과 업데이트 (v2.0 전용 메서드 사용)
        quiz_type = state["quiz_type"]
        if quiz_type == "multiple_choice":
            is_correct = score >= 1  # 1점이면 정답
            updated_state = state_manager.update_evaluation_result(
                state,
                is_correct=is_correct,
                feedback=feedback_text
            )
        else:  # subjective
            # 주관식: 점수로 평가 (0-100 범위)
            updated_state = state_manager.update_evaluation_result(
                state,
                score=score,
                feedback=feedback_text
            )
        
        # 2. 세션 결정 결과 설정 (v2.0 필드명 변경)
        updated_state["retry_decision_result"] = next_step  # session_decision_result → retry_decision_result
        
        # 3. 피드백 대본 저장 (LearningSupervisor용) - 순수 피드백만
        updated_state = state_manager.update_agent_draft(
            updated_state,
            self.agent_name,
            feedback_text
        )
        
        # 4. 현재 에이전트 설정 (QuizGenerator와 동일)
        updated_state = state_manager.update_agent_transition(
            updated_state,
            self.agent_name
        )
        
        # 5. 세션 진행 단계 업데이트
        print(f"[DEBUG] EvaluationFeedbackAgent - 세션 진행 단계 업데이트 전: {updated_state.get('session_progress_stage')}")
        updated_state = state_manager.update_session_progress(
            updated_state,
            self.agent_name
        )
        print(f"[DEBUG] EvaluationFeedbackAgent - 세션 진행 단계 업데이트 후: {updated_state.get('session_progress_stage')}")
        
        # 6. UI 모드를 chat으로 변경 (피드백 표시용)
        updated_state = state_manager.update_ui_mode(
            updated_state,
            "chat"
        )
        
        # 7. 대화 기록 추가
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name=self.agent_name,
            message=f"평가 완료 - 점수: {score}, 결정: {next_step}",
            message_type="system"
        )
        
        return updated_state
    
    def _create_error_state(self, state: TutorState, error_message: str) -> TutorState:
        """오류 발생 시 기본 State 생성 (v2.0 update_evaluation_result 사용)"""
        self.logger.error(f"오류 상태 생성: {error_message}")
        
        error_feedback = f"평가 중 문제가 발생했습니다: {error_message}"
        
        # 기본 평가 결과로 업데이트 (v2.0 메서드 사용)
        quiz_type = state.get("quiz_type", "multiple_choice")
        if quiz_type == "multiple_choice":
            updated_state = state_manager.update_evaluation_result(
                state,
                is_correct=False,  # 오류 시 오답 처리
                feedback=error_feedback
            )
        else:  # subjective
            updated_state = state_manager.update_evaluation_result(
                state,
                score=50,  # 중간 점수
                feedback=error_feedback
            )
        
        # 오류 시에는 강제로 proceed (v2.0 필드명)
        updated_state["retry_decision_result"] = "proceed"  # session_decision_result → retry_decision_result
        
        # 오류 피드백 대본 저장
        updated_state = state_manager.update_agent_draft(
            updated_state,
            self.agent_name,
            error_feedback
        )
        
        # 현재 에이전트 설정 (오류 시에도 동일)
        updated_state = state_manager.update_agent_transition(
            updated_state,
            self.agent_name
        )
        
        # 세션 진행 단계 업데이트
        updated_state = state_manager.update_session_progress(
            updated_state,
            self.agent_name
        )
        
        # UI 모드를 chat으로 변경
        updated_state = state_manager.update_ui_mode(
            updated_state,
            "chat"
        )
        
        # 대화 기록 추가
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name=self.agent_name,
            message=f"오류 발생: {error_message}",
            message_type="system"
        )
        
        return updated_state
    
    def get_evaluation_summary(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 평가 결과 요약 반환 (v2.0 필드명 변경)
        
        Args:
            state: 현재 TutorState
            
        Returns:
            평가 요약 딕셔너리
        """
        quiz_type = state.get("quiz_type", "unknown")
        
        # 퀴즈 타입별 점수 계산
        if quiz_type == "multiple_choice":
            score = 100 if state.get("multiple_answer_correct", False) else 0
        else:  # subjective
            score = state.get("subjective_answer_score", 0)
        
        return {
            "score": score,
            "quiz_type": quiz_type,  # current_question_type → quiz_type
            "next_step": state.get("retry_decision_result", "proceed"),  # session_decision_result → retry_decision_result
            "feedback": state.get("evaluation_feedback", ""),
            "session_count": state.get("current_session_count", 0),
            "multiple_answer_correct": state.get("multiple_answer_correct", False),  # v2.0 신규
            "subjective_answer_score": state.get("subjective_answer_score", 0)  # v2.0 신규
        }