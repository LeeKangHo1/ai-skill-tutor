# backend/app/agents/learning_supervisor/learning_supervisor_agent.py
# v2.0 업데이트: 통합 응답 생성 구조, workflow_response 지원, 하이브리드 UX

from typing import Dict, Any
from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.analysis.intent_analysis_tools import user_intent_analysis_tool
from app.agents.learning_supervisor.response_generator import response_generator
from app.utils.common.chat_logger import chat_logger


class LearningSupervisor:
    """
    학습 감독 에이전트 - LangGraph 워크플로우의 시작점이자 끝점
    
    새로운 워크플로우:
    1. session_start → 바로 theory_educator (의도 분석 없음)
    2. theory_completed → 질문 받기 OR 퀴즈 진행 (의도 분석 필요)
    3. quiz_generated → 사용자 답변 대기 (UI 안내)
    4. quiz_answer_submitted → 평가 피드백 (의도 분석 없음)
    5. quiz_and_feedback_completed → 질문 받기 OR 새 세션 시작 (의도 분석 필요)
    
    주요 역할:
    1. 사용자 메시지 받아서 필요시 의도 분석
    2. 분석 결과를 State에 저장 (supervisor_router가 사용)
    3. 워크플로우 완료 후 response_generator를 통해 최종 응답 생성
    """
    
    def __init__(self):
        self.agent_name = "learning_supervisor"
    
    def process_user_input(self, state: TutorState) -> TutorState:
        """
        사용자 입력 처리 - 워크플로우 시작 단계
        
        Args:
            state: 사용자 메시지가 포함된 TutorState
            
        Returns:
            의도 분석 결과가 추가된 TutorState (필요한 경우만)
        """
        try:
            # 현재 세션 진행 단계 확인
            session_stage = state.get("session_progress_stage", "session_start")
            
            # 세션 시작인 경우 의도 분석 없이 바로 진행
            if session_stage == "session_start":
                return self._handle_session_start(state)
            
            # 이론 완료 후 또는 피드백 완료 후에는 의도 분석 우선 처리
            if session_stage in ["theory_completed", "quiz_and_feedback_completed"]:
                # 퀴즈 답변 제출인지 먼저 확인 (실제 퀴즈 문제가 있는 경우만)
                if self._is_quiz_answer_submission(state):
                    return self._handle_quiz_answer_submission(state)
                
                # 그 외의 경우는 의도 분석 수행
                return self._handle_with_intent_analysis(state)
            
            # 기타 상황은 기본 처리
            return self._handle_default_input(state)
            
        except Exception as e:
            print(f"LearningSupervisor 입력 처리 중 오류: {e}")
            return state
    
    def generate_final_response(self, state: TutorState) -> TutorState:
        """
        최종 응답 생성 - response_generator에 위임
        
        Args:
            state: 에이전트 대본이 포함된 TutorState
            
        Returns:
            최종 응답이 추가된 TutorState
        """
        try:
            # response_generator를 통해 응답 정제
            updated_state = response_generator.generate_final_response(state)
            
            # 최종 대화 로그 저장
            chat_logger.save_session_log(updated_state, session_complete=True)
            
            return updated_state
            
        except Exception as e:
            print(f"LearningSupervisor 응답 생성 중 오류: {e}")
            # 오류 시 기본 응답
            return self._generate_error_response(state)
    
    def _is_quiz_answer_submission(self, state: TutorState) -> bool:
        """
        퀴즈 답변 제출인지 확인
        
        Args:
            state: TutorState
            
        Returns:
            퀴즈 답변 제출 여부
        """
        # UI 모드가 quiz이고 사용자 답변이 있는 경우 (v2.0 필드명)
        ui_mode = state.get("ui_mode", "chat")
        user_answer = state.get("user_answer", "")  # current_question_answer → user_answer
        
        # 최근 대화에서 사용자 메시지 확인
        conversations = state.get("current_session_conversations", [])
        has_recent_user_message = False
        
        if conversations:
            last_conv = conversations[-1]
            if last_conv.get("message_type") == "user":
                has_recent_user_message = True
        
        # 퀴즈 모드이면서 실제 퀴즈 문제가 있고, 사용자 입력이 있는 경우만 퀴즈 답변으로 판단
        has_quiz_question = bool(state.get("quiz_content", "").strip())  # current_question_content → quiz_content
        
        return ui_mode == "quiz" and has_quiz_question and (user_answer or has_recent_user_message)
    
    def _handle_session_start(self, state: TutorState) -> TutorState:
        """
        세션 시작 처리 - 의도 분석 없이 바로 이론 설명으로 진행
        """
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(state, self.agent_name)
        
        # 세션 시작 메시지를 대화 기록에 추가 (사용자 메시지가 있다면)
        user_message = self._extract_user_message(state)
        if user_message:
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=user_message,
                message_type="user"
            )
        
        # 의도는 자동으로 next_step (이론 설명으로 진행)
        updated_state["user_intent"] = "next_step"
        
        # 대화 로그 저장
        chat_logger.save_session_log(updated_state, session_complete=False)
        
        return updated_state
    
    def _handle_quiz_answer_submission(self, state: TutorState) -> TutorState:
        """
        퀴즈 답변 제출 처리 - 의도 분석 없이 바로 평가로 진행
        """
        # 사용자 답변 추출 및 State에 저장
        user_answer = self._extract_user_answer(state)
        
        if not user_answer:
            return self._handle_no_answer(state)
        
        # State에 사용자 답변만 저장 (퀴즈 내용은 QuizGenerator가 이미 저장함)
        updated_state = state_manager.update_user_answer(state, user_answer)
        
        # 답변을 대화 기록에 추가
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name=self.agent_name,
            message=f"답변: {user_answer}",
            message_type="user"
        )
        
        # quiz_answer 의도로 설정 (evaluation_feedback_agent로 라우팅용)
        updated_state["user_intent"] = "quiz_answer"
        
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(updated_state, self.agent_name)
        
        # 퀴즈 답변 로그 저장
        chat_logger.save_session_log(updated_state, session_complete=False)
        
        return updated_state
    
    def _handle_with_intent_analysis(self, state: TutorState) -> TutorState:
        """
        의도 분석이 필요한 단계 처리 (theory_completed, quiz_and_feedback_completed)
        """
        print(f"[DEBUG] _handle_with_intent_analysis 시작")
        
        # State에서 사용자 메시지 추출
        user_message = self._extract_user_message(state)
        print(f"[DEBUG] 추출된 사용자 메시지: '{user_message}'")
        
        # 사용자 메시지가 없으면 입력 요청
        if not user_message:
            return self._handle_no_message_in_question_phase(state)
        
        # 사용자 의도 분석
        analyzed_intent = self._analyze_user_intent(state, user_message)
        print(f"[DEBUG] 분석된 사용자 의도: '{analyzed_intent}'")
        
        # 분석 결과를 State에 저장
        updated_state = state.copy()
        updated_state["user_intent"] = analyzed_intent
        print(f"[DEBUG] State에 user_intent 저장 완료: '{analyzed_intent}'")
        
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(updated_state, self.agent_name)
        
        # 사용자 메시지를 대화 기록에 추가
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name=self.agent_name,
            message=user_message,
            message_type="user"
        )
        
        # 대화 로그 저장
        chat_logger.save_session_log(updated_state, session_complete=False)
        
        print(f"[DEBUG] _handle_with_intent_analysis 완료, 반환할 user_intent: '{updated_state.get('user_intent')}'")
        return updated_state
    
    def _handle_default_input(self, state: TutorState) -> TutorState:
        """기본 입력 처리 (예상치 못한 상황)"""
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(state, self.agent_name)
        
        # 기본적으로 next_step으로 처리
        updated_state["user_intent"] = "next_step"
        
        return updated_state
    
    def _extract_user_message(self, state: TutorState) -> str:
        """State에서 사용자 메시지 추출"""
        # API 요청에서 전달된 메시지 또는 대화 기록의 마지막 사용자 메시지
        conversations = state.get("current_session_conversations", [])
        
        # 마지막 대화에서 사용자 메시지 찾기
        for conv in reversed(conversations):
            if conv.get("message_type") == "user":
                return conv.get("message", "")
        
        # 없으면 빈 문자열 반환
        return ""
    
    def _extract_user_answer(self, state: TutorState) -> str:
        """State에서 사용자 퀴즈 답변 추출 (v2.0 필드명)"""
        # 이미 State에 저장된 답변이 있으면 그것을 사용
        current_answer = state.get("user_answer", "")  # current_question_answer → user_answer
        if current_answer:
            return current_answer
        
        # 없으면 대화 기록에서 마지막 사용자 메시지를 답변으로 간주
        return self._extract_user_message(state)
    
    def _analyze_user_intent(self, state: TutorState, user_message: str) -> str:
        """사용자 의도 분석"""
        try:
            print(f"[DEBUG] 의도 분석 시작 - 메시지: '{user_message}', 단계: {state['session_progress_stage']}")
            
            intent_result = user_intent_analysis_tool(
                user_message=user_message,
                current_stage=state["session_progress_stage"],
                user_type=state["user_type"]
            )
            
            print(f"[DEBUG] 의도 분석 결과: {intent_result}")
            
            # 의도 분석 결과를 대화 기록에 시스템 메시지로 추가 (로깅용)
            # 여기는 intent_analyzer가 맞으므로 유지
            state_manager.add_conversation(
                state,
                agent_name="intent_analyzer",
                message=f"의도 분석: {intent_result['intent']} (신뢰도: {intent_result['confidence']:.2f}, 근거: {intent_result['reasoning']})",
                message_type="tool"
            )
            
            final_intent = intent_result.get("intent", "next_step")
            print(f"[DEBUG] 최종 의도: {final_intent}")
            
            return final_intent
            
        except Exception as e:
            print(f"의도 분석 중 오류: {e}")
            return "next_step"  # 기본값
    
    def _handle_no_message_in_question_phase(self, state: TutorState) -> TutorState:
        """질문 단계에서 사용자 메시지가 없는 경우 처리"""
        session_stage = state.get("session_progress_stage", "")
        
        # 단계별 안내 메시지
        if session_stage == "theory_completed":
            guide_message = "이론 설명이 완료되었습니다. 궁금한 점이 있으시면 질문해주세요. 퀴즈를 시작하려면 '다음 단계'라고 말씀해주세요."
        elif session_stage == "quiz_and_feedback_completed":
            guide_message = "퀴즈와 피드백이 완료되었습니다. 추가 질문이 있으시면 언제든 물어보세요. 다음 학습으로 넘어가려면 '다음'이라고 말씀해주세요."
        else:
            guide_message = "메시지를 입력해주세요."
        
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(state, self.agent_name)
        
        # 안내 메시지를 대화 기록에 추가
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name=self.agent_name,
            message=guide_message,
            message_type="system"
        )
        
        # 로그 저장
        chat_logger.save_session_log(updated_state, session_complete=False)
        
        return updated_state
    
    def _handle_no_answer(self, state: TutorState) -> TutorState:
        """퀴즈 답변이 없는 경우 처리"""
        # 답변 요청 메시지 생성
        request_message = "답변을 입력해주세요."
        
        updated_state = state_manager.add_conversation(
            state,
            agent_name=self.agent_name,
            message=request_message,
            message_type="system"
        )
        
        return updated_state
    
    def _generate_error_response(self, state: TutorState) -> TutorState:
        """오류 응답 생성"""
        error_message = "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요."
        
        # 임시로 theory_draft에 오류 메시지 저장
        updated_state = state_manager.update_agent_draft(state, "theory_educator", error_message)
        
        return updated_state