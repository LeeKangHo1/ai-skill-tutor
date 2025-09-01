# backend/app/agents/learning_supervisor/learning_supervisor_agent.py
# v2.0 업데이트: 통합 응답 생성 구조, workflow_response 지원, 하이브리드 UX

from typing import Dict, Any
from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.analysis.intent_analysis_tools import user_intent_analysis_tool
from app.agents.learning_supervisor.response_generator import response_generator
from app.utils.common.chat_logger import chat_logger
import uuid
import time


class LearningSupervisor:
    """
    학습 감독 에이전트 - LangGraph 워크플로우의 시작점이자 끝점
    
    새로운 워크플로우:
    1. session_start → 바로 theory_educator (의도 분석 없음)
    2. theory_completed → 질문 받기 OR 퀴즈 진행 (의도 분석 필요)
    3. quiz_answer → 바로 evaluation_feedback (의도 분석 없음)
    4. quiz_and_feedback_completed → 질문 받기 OR 새 세션 시작 (의도 분석 필요)
    
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
            user_intent = state.get("user_intent", "next_step")
            
            print(f"[DEBUG] LearningSupervisor.process_user_input 호출됨")
            print(f"[DEBUG] - session_stage: {session_stage}")
            print(f"[DEBUG] - 의도 분석 이전 남아있던 user_intent: {user_intent}")
            
            # 퀴즈 답변 처리 (theory_completed 상태에서 quiz_answer 의도인 경우)
            if session_stage == "theory_completed" and user_intent == "quiz_answer":
                print(f"[DEBUG] 퀴즈 답변 처리: stage={session_stage}, intent={user_intent}")
                return self._handle_predefined_intent(state)
            
            # 세션 시작인 경우 의도 분석 없이 바로 진행
            if session_stage == "session_start":
                return self._handle_session_start(state)
            
            # Complete 요청인 경우 의도 분석 건너뛰기 (retry_decision_result가 있으면 Complete 요청)
            retry_decision = state.get("retry_decision_result", "")
            if retry_decision and user_intent == "next_step":
                print(f"[DEBUG] Complete 요청 감지 (decision: {retry_decision}) - 의도 분석 건너뛰기")
                return self._handle_predefined_intent(state)
            
            # 이론 완료 후 또는 피드백 완료 후에는 의도 분석 수행
            if session_stage in ["theory_completed", "quiz_and_feedback_completed"]:
                print(f"[DEBUG] 의도 분석이 필요한 단계: {session_stage}")
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
            print(f"[DEBUG] LearningSupervisor.generate_final_response 호출됨")
            print(f"[DEBUG] - current_agent: {state.get('current_agent')}")
            print(f"[DEBUG] - session_progress_stage: {state.get('session_progress_stage')}")
            
            # response_generator를 통해 응답 정제
            updated_state = response_generator.generate_final_response(state)
            
            print(f"[DEBUG] ResponseGenerator 처리 완료")
            
            # 최종 대화 로그 저장
            chat_logger.save_session_log(updated_state, session_complete=True)
            
            return updated_state
            
        except Exception as e:
            print(f"LearningSupervisor 응답 생성 중 오류: {e}")
            # 오류 시 기본 응답
            return self._generate_error_response(state)
    
    def _handle_predefined_intent(self, state: TutorState) -> TutorState:
        """
        이미 설정된 의도 처리 (quiz_answer 등)
        
        Args:
            state: TutorState
            
        Returns:
            현재 에이전트 정보가 업데이트된 TutorState
        """
        user_intent = state.get("user_intent", "")
        print(f"[DEBUG] _handle_predefined_intent - 의도: '{user_intent}'")
        
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(state, self.agent_name)
        
        # 퀴즈 답변인 경우 사용자 답변을 대화 기록에 추가
        if user_intent == "quiz_answer":
            user_answer = state.get("user_answer", "")
            if user_answer:
                # 사용자 답변을 대화 기록에 추가 (중복 방지)
                conversations = updated_state.get("current_session_conversations", [])
                last_user_message = ""
                if conversations and conversations[-1].get("message_type") == "user":
                    last_user_message = conversations[-1].get("message", "")
                
                if last_user_message != user_answer:
                    updated_state = state_manager.add_conversation(
                        updated_state,
                        agent_name="user",
                        message=user_answer,
                        message_type="user"
                    )
                    print(f"[DEBUG] 대화 기록에 사용자 답변 추가: '{user_answer}'")
        
        # 대화 로그 저장
        chat_logger.save_session_log(updated_state, session_complete=False)
        
        return updated_state
    
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
        
        # === 🚀 NEW: question 의도에 대한 특별 처리 ===
        if analyzed_intent == "question":
            return self._handle_question_intent_for_streaming(state, user_message)
        
        # 분석 결과를 State에 저장 (기존 로직)
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
    
    # === 🚀 NEW METHOD: 질문 의도에 대한 스트리밍 준비 처리 ===
    def _handle_question_intent_for_streaming(self, state: TutorState, user_message: str) -> TutorState:
        """
        질문 의도 감지 시 스트리밍 준비 상태로 전환
        
        Args:
            state: 현재 TutorState
            user_message: 사용자 질문
            
        Returns:
            스트리밍 준비 상태로 설정된 TutorState
        """
        import uuid
        import time
        
        print(f"[DEBUG] _handle_question_intent_for_streaming 시작 - 질문: '{user_message}'")
        
        # 1. 임시 스트리밍 세션 ID 생성
        temp_session_id = str(uuid.uuid4())
        
        # 2. 스트리밍 세션 데이터 준비 (전역 임시 저장소에 저장)
        from app.routes.learning.session.qna_stream import streaming_sessions
        
        streaming_session_data = {
            "user_message": user_message,
            "context": {
                "chapter": state.get("current_chapter", 1),
                "section": state.get("current_section", 1),
                "session_stage": state.get("session_progress_stage", ""),
                "user_type": state.get("user_type", "beginner")
            },
            "expires_at": time.time() + 30,  # 30초 후 만료
            "original_state": state.copy()  # QnA Agent에서 State 관리할 때 사용
        }
        
        # 3. 전역 임시 저장소에 스트리밍 세션 저장
        streaming_sessions[temp_session_id] = streaming_session_data
        
        # 4. State 업데이트 (TutorState 구조 유지)
        updated_state = state.copy()
        updated_state["user_intent"] = "question_streaming"  # 특별한 의도로 설정
        
        # 5. 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(updated_state, self.agent_name)
        
        # # 6. 사용자 질문을 대화 기록에 추가
        # updated_state = state_manager.add_conversation(
        #     updated_state,
        #     agent_name="user",  # 사용자 메시지로 기록
        #     message=user_message,
        #     message_type="user"
        # )
        
        # 7. 스트리밍 준비 로그 추가
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name=self.agent_name,
            message=f"질문 의도 감지 - 스트리밍 세션 준비 (ID: {temp_session_id})",
            message_type="system"
        )
        
        # 8. 대화 로그 저장
        chat_logger.save_session_log(updated_state, session_complete=False)
        
        print(f"[DEBUG] 스트리밍 세션 준비 완료 - ID: {temp_session_id}")
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
    
    def _generate_error_response(self, state: TutorState) -> TutorState:
        """오류 응답 생성"""
        error_message = "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요."
        
        # 임시로 theory_draft에 오류 메시지 저장
        updated_state = state_manager.update_agent_draft(state, "theory_educator", error_message)
        
        return updated_state