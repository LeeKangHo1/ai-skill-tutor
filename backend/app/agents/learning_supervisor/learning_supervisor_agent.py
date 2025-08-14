# backend/app/agents/learning_supervisor/learning_supervisor_agent.py

from typing import Dict, Any
from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.analysis.intent_analysis_tools import user_intent_analysis_tool
from app.utils.common.chat_logger import chat_logger


class LearningSupervisor:
    """
    학습 감독 에이전트 - LangGraph 워크플로우의 시작점이자 끝점
    
    새로운 워크플로우:
    1. session_start → 바로 theory_educator (의도 분석 없음)
    2. theory_completed → 질문 받기 OR 퀴즈 진행 (의도 분석 필요)
    3. quiz_and_feedback_completed → 질문 받기 OR 새 세션 시작 (의도 분석 필요)
    
    주요 역할:
    1. 사용자 메시지 받아서 필요시 의도 분석
    2. 분석 결과를 State에 저장 (supervisor_router가 사용)
    3. 워크플로우 완료 후 최종 응답을 사용자에게 반환
    """
    
    def __init__(self):
        pass
    
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
            
            # 이론 완료 후 또는 피드백 완료 후에는 의도 분석 필요
            if session_stage in ["theory_completed", "quiz_and_feedback_completed"]:
                return self._handle_with_intent_analysis(state)
            
            # 기타 상황은 기본 처리
            return self._handle_default_input(state)
            
        except Exception as e:
            print(f"LearningSupervisor 입력 처리 중 오류: {e}")
            return state
    
    def generate_final_response(self, state: TutorState) -> TutorState:
        """
        최종 응답 생성 - 워크플로우 완료 단계
        
        Args:
            state: response_generator 처리가 완료된 TutorState
            
        Returns:
            최종 응답이 추가된 TutorState
        """
        try:
            # response_generator에서 생성된 최종 응답 추출
            final_response = self._extract_final_response(state)
            
            if not final_response:
                # 응답이 없으면 기본 응답 생성
                final_response = self._generate_default_response(state)
            
            # 최종 응답을 대화 기록에 추가
            updated_state = state_manager.add_conversation(
                state,
                agent_name="learning_supervisor",
                message=final_response,
                message_type="system"
            )
            
            # UI 모드 업데이트 (필요한 경우)
            updated_state = self._update_ui_mode_if_needed(updated_state)
            
            # 최종 대화 로그 저장
            chat_logger.save_session_log(updated_state, session_complete=True)
            
            return updated_state
            
        except Exception as e:
            print(f"LearningSupervisor 응답 생성 중 오류: {e}")
            # 오류 시 기본 응답
            error_response = "죄송합니다. 처리 중 오류가 발생했습니다. 다시 시도해주세요."
            error_state = state_manager.add_conversation(
                state,
                agent_name="learning_supervisor",
                message=error_response,
                message_type="system"
            )
            return error_state
    
    def handle_quiz_answer(self, state: TutorState) -> TutorState:
        """
        퀴즈 답변 처리 - 별도 엔트리 포인트
        
        Args:
            state: 사용자 답변이 포함된 TutorState
            
        Returns:
            답변 처리가 완료된 TutorState
        """
        try:
            # 사용자 답변 추출
            user_answer = self._extract_user_answer(state)
            
            if not user_answer:
                return self._handle_no_answer(state)
            
            # State에 답변 저장
            updated_state = state_manager.update_quiz_info(state, user_answer=user_answer)
            
            # 답변을 대화 기록에 추가
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name="user",
                message=f"답변: {user_answer}",
                message_type="user"
            )
            
            # quiz_answer 의도로 설정 (evaluation_feedback_agent로 라우팅용)
            updated_state["user_intent"] = "quiz_answer"
            
            # 퀴즈 답변 로그 저장
            chat_logger.save_session_log(updated_state, session_complete=False)
            
            return updated_state
            
        except Exception as e:
            print(f"퀴즈 답변 처리 중 오류: {e}")
            return state
    
    def _handle_session_start(self, state: TutorState) -> TutorState:
        """
        세션 시작 처리 - 의도 분석 없이 바로 이론 설명으로 진행
        
        Args:
            state: TutorState
            
        Returns:
            처리된 TutorState
        """
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(state, "learning_supervisor")
        
        # 세션 시작 메시지를 대화 기록에 추가 (사용자 메시지가 있다면)
        user_message = self._extract_user_message(state)
        if user_message:
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name="user",
                message=user_message,
                message_type="user"
            )
        
        # 의도는 자동으로 next_step (이론 설명으로 진행)
        updated_state["user_intent"] = "next_step"
        
        # 대화 로그 저장
        chat_logger.save_session_log(updated_state, session_complete=False)
        
        return updated_state
    
    def _handle_with_intent_analysis(self, state: TutorState) -> TutorState:
        """
        의도 분석이 필요한 단계 처리 (theory_completed, quiz_and_feedback_completed)
        
        Args:
            state: TutorState
            
        Returns:
            의도 분석 결과가 포함된 TutorState
        """
        # State에서 사용자 메시지 추출
        user_message = self._extract_user_message(state)
        
        # 사용자 메시지가 없으면 입력 요청
        if not user_message:
            return self._handle_no_message_in_question_phase(state)
        
        # 사용자 의도 분석
        user_intent = self._analyze_user_intent(state, user_message)
        
        # 분석 결과를 State에 저장
        updated_state = state.copy()
        updated_state["user_intent"] = user_intent
        
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(updated_state, "learning_supervisor")
        
        # 사용자 메시지를 대화 기록에 추가
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name="user",
            message=user_message,
            message_type="user"
        )
        
        # 대화 로그 저장
        chat_logger.save_session_log(updated_state, session_complete=False)
        
        return updated_state
    
    def _handle_default_input(self, state: TutorState) -> TutorState:
        """
        기본 입력 처리 (예상치 못한 상황)
        
        Args:
            state: TutorState
            
        Returns:
            기본 처리된 TutorState
        """
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(state, "learning_supervisor")
        
        # 기본적으로 next_step으로 처리
        updated_state["user_intent"] = "next_step"
        
        return updated_state
    
    def _handle_no_message_in_question_phase(self, state: TutorState) -> TutorState:
        """
        질문 단계에서 사용자 메시지가 없는 경우 처리
        
        Args:
            state: TutorState
            
        Returns:
            적절한 안내 메시지가 포함된 TutorState
        """
        session_stage = state.get("session_progress_stage", "")
        
        # 단계별 안내 메시지
        if session_stage == "theory_completed":
            guide_message = "이론 설명이 완료되었습니다. 궁금한 점이 있으시면 질문해주세요. 퀴즈를 시작하려면 '다음 단계'라고 말씀해주세요."
        elif session_stage == "quiz_and_feedback_completed":
            guide_message = "퀴즈와 피드백이 완료되었습니다. 추가 질문이 있으시면 언제든 물어보세요. 다음 학습으로 넘어가려면 '다음'이라고 말씀해주세요."
        else:
            guide_message = "메시지를 입력해주세요."
        
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(state, "learning_supervisor")
        
        # 안내 메시지를 대화 기록에 추가
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name="learning_supervisor",
            message=guide_message,
            message_type="system"
        )
        
        # 로그 저장
        chat_logger.save_session_log(updated_state, session_complete=False)
        
        return updated_state
    
    def _extract_user_message(self, state: TutorState) -> str:
        """
        State에서 사용자 메시지 추출
        
        Args:
            state: TutorState
            
        Returns:
            사용자 메시지 문자열
        """
        # API 요청에서 전달된 메시지 또는 대화 기록의 마지막 사용자 메시지
        conversations = state.get("current_session_conversations", [])
        
        # 마지막 대화에서 사용자 메시지 찾기
        for conv in reversed(conversations):
            if conv.get("message_type") == "user":
                return conv.get("message", "")
        
        # 없으면 빈 문자열 반환
        return ""
    
    def _extract_user_answer(self, state: TutorState) -> str:
        """
        State에서 사용자 퀴즈 답변 추출
        
        Args:
            state: TutorState
            
        Returns:
            사용자 답변 문자열
        """
        # 이미 State에 저장된 답변이 있으면 그것을 사용
        current_answer = state.get("current_question_answer", "")
        if current_answer:
            return current_answer
        
        # 없으면 대화 기록에서 마지막 사용자 메시지를 답변으로 간주
        return self._extract_user_message(state)
    
    def _extract_final_response(self, state: TutorState) -> str:
        """
        response_generator에서 생성된 최종 응답 추출
        
        Args:
            state: TutorState
            
        Returns:
            최종 응답 문자열
        """
        # response_generator에서 생성된 응답은 보통 특정 draft 필드에 저장됨
        # 현재 에이전트에 따라 적절한 draft 필드에서 추출
        current_agent = state.get("current_agent", "")
        
        if "theory" in current_agent:
            return state.get("theory_draft", "")
        elif "quiz" in current_agent:
            return state.get("quiz_draft", "")
        elif "feedback" in current_agent:
            return state.get("feedback_draft", "")
        elif "qna" in current_agent:
            return state.get("qna_draft", "")
        
        # 기본적으로 모든 draft를 확인해서 가장 최근 내용 반환
        drafts = [
            state.get("theory_draft", ""),
            state.get("quiz_draft", ""),
            state.get("feedback_draft", ""),
            state.get("qna_draft", "")
        ]
        
        for draft in drafts:
            if draft and draft.strip():
                return draft
        
        return ""
    
    def _analyze_user_intent(self, state: TutorState, user_message: str) -> str:
        """
        사용자 의도 분석
        """
        try:
            intent_result = user_intent_analysis_tool(
                user_message=user_message,
                current_stage=state["session_progress_stage"],
                user_type=state["user_type"]
            )
            
            # 의도 분석 결과를 대화 기록에 시스템 메시지로 추가 (로깅용)
            state_manager.add_conversation(
                state,
                agent_name="intent_analyzer",
                message=f"의도 분석: {intent_result['intent']} (신뢰도: {intent_result['confidence']:.2f}, 근거: {intent_result['reasoning']})",
                message_type="tool"
            )
            
            return intent_result.get("intent", "next_step")
            
        except Exception as e:
            print(f"의도 분석 중 오류: {e}")
            return "next_step"  # 기본값
    
    def _handle_no_answer(self, state: TutorState) -> TutorState:
        """
        퀴즈 답변이 없는 경우 처리
        
        Args:
            state: TutorState
            
        Returns:
            기본 처리된 TutorState
        """
        # 답변 요청 메시지 생성
        request_message = "답변을 입력해주세요."
        
        updated_state = state_manager.add_conversation(
            state,
            agent_name="learning_supervisor",
            message=request_message,
            message_type="system"
        )
        
        return updated_state
    
    def _generate_default_response(self, state: TutorState) -> str:
        """
        기본 응답 생성
        
        Args:
            state: TutorState
            
        Returns:
            기본 응답 메시지
        """
        current_stage = state["session_progress_stage"]
        
        if current_stage == "session_start":
            return "안녕하세요! 학습을 시작하겠습니다."
        elif current_stage == "theory_completed":
            return "이론 학습이 완료되었습니다. 궁금한 점이 있으시면 질문해주세요. 퀴즈를 시작하려면 '다음 단계'라고 말씀해주세요."
        elif current_stage == "quiz_and_feedback_completed":
            return "퀴즈와 피드백이 완료되었습니다. 추가 질문이 있으시면 언제든 물어보세요. 다음 학습으로 넘어가려면 '다음'이라고 말씀해주세요."
        else:
            return "무엇을 도와드릴까요?"
    
    def _update_ui_mode_if_needed(self, state: TutorState) -> TutorState:
        """
        필요한 경우 UI 모드 업데이트
        
        Args:
            state: TutorState
            
        Returns:
            UI 모드가 업데이트된 TutorState
        """
        current_stage = state["session_progress_stage"]
        current_ui_mode = state.get("ui_mode", "chat")
        
        # 퀴즈 생성 후에는 quiz 모드로
        if "quiz" in state.get("quiz_draft", "") and current_ui_mode != "quiz":
            return state_manager.update_ui_mode(state, "quiz")
        
        # 피드백 완료 후에는 다시 chat 모드로
        if current_stage == "quiz_and_feedback_completed" and current_ui_mode != "chat":
            return state_manager.update_ui_mode(state, "chat")
        
        return state