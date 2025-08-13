# backend/app/agents/evaluation_feedback/evaluation_feedback_agent.py

import json
import logging
from typing import Dict, Any

from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.analysis.evaluation_tools import (
    evaluate_multiple_choice,
    determine_next_step,
    create_evaluation_summary,
    validate_quiz_data
)
from app.tools.analysis.feedback_tools_chatgpt import (
    evaluate_subjective_with_feedback,
    generate_multiple_choice_feedback,
    generate_simple_feedback
)


class EvaluationFeedbackAgent:
    """
    평가 및 피드백 에이전트
    - QuizGenerator 완료 후 자동 호출
    - 객관식/주관식 답변 채점 및 피드백 생성
    - 다음 단계 진행 여부 결정
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
            업데이트된 TutorState (feedback_draft 및 평가 결과 포함)
        """
        try:
            self.logger.info(f"[{self.agent_name}] 평가 및 피드백 생성 시작")
            
            # 1. 현재 상태 검증
            if not self._validate_state(state):
                return self._create_error_state(state, "State 검증 실패")
            
            # 2. 퀴즈 데이터 파싱
            quiz_data = self._parse_quiz_data(state["quiz_draft"])
            if not quiz_data:
                return self._create_error_state(state, "퀴즈 데이터 파싱 실패")
            
            # 3. 퀴즈 타입별 평가 처리
            quiz_type = state["current_question_type"]
            user_answer = state["current_question_answer"]
            
            if quiz_type == "multiple_choice":
                score, evaluation_detail = self._evaluate_multiple_choice(quiz_data, user_answer)
                # 객관식 ChatGPT 피드백 생성
                mc_feedback = generate_multiple_choice_feedback(
                    quiz_data, evaluation_detail, state["user_type"], next_step
                )
                evaluation_detail["chatgpt_feedback"] = mc_feedback
            elif quiz_type == "subjective":
                score, evaluation_detail = self._evaluate_subjective(quiz_data, user_answer, state["user_type"])
            else:
                return self._create_error_state(state, f"지원하지 않는 퀴즈 타입: {quiz_type}")
            
            # 4. 다음 단계 결정
            next_step = determine_next_step(score, quiz_type, state["current_session_count"])
            
            # 5. 피드백 텍스트 생성
            feedback_text = self._generate_feedback_text(evaluation_detail, quiz_type, state["user_type"], next_step)
            
            # 6. State 업데이트
            updated_state = self._update_state_with_results(
                state, score, evaluation_detail, next_step, feedback_text
            )
            
            self.logger.info(f"[{self.agent_name}] 평가 완료 - 점수: {score}, 다음단계: {next_step}")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"[{self.agent_name}] 오류 발생: {str(e)}")
            return self._create_error_state(state, str(e))
    
    def _validate_state(self, state: TutorState) -> bool:
        """State 유효성 검증"""
        required_fields = [
            "quiz_draft", "current_question_answer", "current_question_type",
            "user_type", "current_session_count"
        ]
        
        for field in required_fields:
            if field not in state or not state[field]:
                self.logger.error(f"필수 필드 누락 또는 비어있음: {field}")
                return False
        
        # 사용자 답변이 실제로 있는지 확인
        user_answer = state["current_question_answer"].strip()
        if not user_answer:
            self.logger.error("사용자 답변이 비어있습니다.")
            return False
        
        return True
    
    def _parse_quiz_data(self, quiz_draft: str) -> Dict[str, Any]:
        """퀴즈 대본에서 JSON 데이터 파싱"""
        try:
            # JSON 파싱
            draft_data = json.loads(quiz_draft)
            quiz_data = draft_data.get("quiz", {})
            
            if not quiz_data:
                self.logger.error("퀴즈 데이터가 비어있습니다.")
                return None
            
            # 퀴즈 데이터 유효성 검증
            quiz_type = quiz_data.get("type", "")
            if not validate_quiz_data(quiz_data, quiz_type):
                self.logger.error("퀴즈 데이터 유효성 검증 실패")
                return None
            
            self.logger.info("퀴즈 데이터 파싱 및 검증 완료")
            return quiz_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"퀴즈 데이터 파싱 중 오류: {str(e)}")
            return None
    
    def _evaluate_multiple_choice(self, quiz_data: Dict[str, Any], user_answer: str) -> tuple:
        """객관식 평가 처리"""
        self.logger.info("객관식 평가 시작")
        return evaluate_multiple_choice(quiz_data, user_answer)
    
    def _evaluate_subjective(self, quiz_data: Dict[str, Any], user_answer: str, user_type: str) -> tuple:
        """주관식 평가 처리"""
        self.logger.info("주관식 평가 시작 (ChatGPT 호출)")
        return evaluate_subjective_with_feedback(quiz_data, user_answer, user_type)
    
    def _generate_feedback_text(self, evaluation_detail: Dict[str, Any], quiz_type: str, user_type: str, next_step: str) -> str:
        """최종 피드백 텍스트 생성"""
        try:
            # 다음 단계 멘트 정의
            proceed_message = "훌륭합니다! 이 파트를 성공적으로 완료했어요. 다음 파트로 진행할까요?"
            retry_message = "한 번 더 복습을 하고 넘어갈까요?"
            
            if quiz_type == "multiple_choice":
                # 객관식: ChatGPT 피드백 + 다음 단계 멘트
                chatgpt_feedback = evaluation_detail.get("chatgpt_feedback", "")
                next_step_text = proceed_message if next_step == "proceed" else retry_message
                
                if chatgpt_feedback:
                    return f"{chatgpt_feedback}\n\n{next_step_text}"
                else:
                    # ChatGPT 피드백 실패 시 기본 피드백 사용
                    fallback_feedback = generate_simple_feedback(evaluation_detail, quiz_type, user_type, next_step)
                    return f"{fallback_feedback}\n\n{next_step_text}"
            
            elif quiz_type == "subjective":
                # 주관식: ChatGPT에서 생성된 상세 피드백 + 다음 단계 멘트
                detailed_feedback = evaluation_detail.get("detailed_feedback", "")
                score = evaluation_detail.get("score", 0)
                next_step_text = proceed_message if next_step == "proceed" else retry_message
                
                if detailed_feedback:
                    return f"📊 점수: {score}점\n\n{detailed_feedback}\n\n{next_step_text}"
                else:
                    # ChatGPT 피드백이 없는 경우 기본 피드백
                    fallback_feedback = generate_simple_feedback(evaluation_detail, quiz_type, user_type, next_step)
                    return f"{fallback_feedback}\n\n{next_step_text}"
            
            else:
                return f"평가가 완료되었습니다. 점수: {evaluation_detail.get('score', 0)}\n\n{proceed_message}"
                
        except Exception as e:
            self.logger.error(f"피드백 텍스트 생성 중 오류: {str(e)}")
            score = evaluation_detail.get('score', 0)
            next_step_text = "훌륭합니다! 이 파트를 성공적으로 완료했어요. 다음 파트로 진행할까요?" if next_step == "proceed" else "한 번 더 복습을 하고 넘어갈까요?"
            return f"평가가 완료되었습니다. 점수: {score}\n\n{next_step_text}"
    
    def _update_state_with_results(
        self, 
        state: TutorState, 
        score: int, 
        evaluation_detail: Dict[str, Any],
        next_step: str,
        feedback_text: str
    ) -> TutorState:
        """평가 결과로 State 업데이트"""
        
        # 1. 평가 결과 업데이트
        updated_state = state_manager.update_quiz_info(
            state,
            is_correct=score,
            feedback=feedback_text
        )
        
        # 2. 세션 결정 결과 설정
        updated_state["session_decision_result"] = next_step
        
        # 3. 피드백 대본 저장
        updated_state = state_manager.update_agent_draft(
            updated_state,
            self.agent_name,
            feedback_text
        )
        
        # 4. 세션 진행 단계 업데이트
        updated_state = state_manager.update_session_progress(
            updated_state,
            self.agent_name
        )
        
        # 5. UI 모드를 chat으로 변경 (피드백 표시용)
        updated_state = state_manager.update_ui_mode(
            updated_state,
            "chat"
        )
        
        # 6. 대화 기록 추가
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name=self.agent_name,
            message=f"평가 완료 - 점수: {score}, 결정: {next_step}",
            message_type="system"
        )
        
        # 7. 세션 카운트 업데이트 (retry인 경우에만)
        if next_step == "retry":
            updated_state["current_session_count"] += 1
            self.logger.info(f"세션 카운트 증가: {updated_state['current_session_count']}")
        
        return updated_state
    
    def _create_error_state(self, state: TutorState, error_message: str) -> TutorState:
        """오류 발생 시 기본 State 생성"""
        self.logger.error(f"오류 상태 생성: {error_message}")
        
        error_feedback = f"평가 중 문제가 발생했습니다: {error_message}\n\n괜찮습니다! 다음 단계로 진행해보세요."
        
        # 기본 평가 결과로 업데이트
        updated_state = state_manager.update_quiz_info(
            state,
            is_correct=50,  # 중간 점수
            feedback=error_feedback
        )
        
        # 오류 시에는 강제로 proceed
        updated_state["session_decision_result"] = "proceed"
        
        # 오류 피드백 대본 저장
        updated_state = state_manager.update_agent_draft(
            updated_state,
            self.agent_name,
            error_feedback
        )
        
        # 세션 진행 단계 업데이트
        updated_state = state_manager.update_session_progress(
            updated_state,
            self.agent_name
        )
        
        return updated_state
    
    def get_evaluation_summary(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 평가 결과 요약 반환 (외부에서 호출 가능)
        
        Args:
            state: 현재 TutorState
            
        Returns:
            평가 요약 딕셔너리
        """
        return {
            "score": state.get("is_answer_correct", 0),
            "quiz_type": state.get("current_question_type", "unknown"),
            "next_step": state.get("session_decision_result", "proceed"),
            "feedback": state.get("evaluation_feedback", ""),
            "session_count": state.get("current_session_count", 0)
        }