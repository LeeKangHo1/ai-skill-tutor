# backend/app/core/langraph/managers/agent_manager.py
# 에이전트 전환 관리 전담 모듈

import copy
from typing import Dict, Any, Optional, List, Tuple

from ..state.state_definition import TutorState, VALID_VALUES


class AgentManager:
    """
    에이전트 전환 및 UI 모드 관리를 담당하는 클래스
    
    주요 기능:
    - 에이전트 전환 로직
    - UI 모드 제어 (chat/quiz)
    - 사용자 의도 분석 결과 처리
    - 워크플로우 응답 관리
    - 에이전트 상태 추적
    - 라우팅 히스토리 관리
    """
    
    def __init__(self):
        """AgentManager 초기화"""
        self.valid_agents = VALID_VALUES.get("agent_names", [])
        self.valid_ui_modes = VALID_VALUES.get("ui_mode", ["chat", "quiz"])
        self.valid_intents = VALID_VALUES.get("user_intent", ["next_step", "question", "quiz_answer"])
    
    def update_agent_transition(self, 
                              state: TutorState, 
                              new_agent: str) -> TutorState:
        """
        에이전트 전환 시 State 업데이트
        
        Args:
            state: 현재 State
            new_agent: 새로운 에이전트 이름
        
        Returns:
            에이전트가 전환된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 이전 에이전트 저장
        updated_state["previous_agent"] = state.get("current_agent", "")
        
        # 새 에이전트 설정
        updated_state["current_agent"] = new_agent
        
        return updated_state
    
    def update_ui_mode(self, 
                      state: TutorState, 
                      mode: str) -> TutorState:
        """
        UI 모드 업데이트
        
        Args:
            state: 현재 State
            mode: UI 모드 ("chat" or "quiz")
        
        Returns:
            UI 모드가 업데이트된 State
        """
        if mode not in self.valid_ui_modes:
            mode = "chat"  # 기본값으로 fallback
        
        updated_state = copy.deepcopy(state)
        updated_state["ui_mode"] = mode
        return updated_state
    
    def update_user_intent(self, 
                          state: TutorState, 
                          intent: str) -> TutorState:
        """
        사용자 의도 업데이트
        
        Args:
            state: 현재 State
            intent: 사용자 의도
        
        Returns:
            의도가 업데이트된 State
        """
        if intent not in self.valid_intents:
            intent = "next_step"  # 기본값으로 fallback
        
        updated_state = copy.deepcopy(state)
        updated_state["user_intent"] = intent
        return updated_state
    
    def update_workflow_response(self, 
                               state: TutorState, 
                               workflow_response: Dict[str, Any]) -> TutorState:
        """
        워크플로우 응답 업데이트
        
        Args:
            state: 현재 State
            workflow_response: 워크플로우 응답 데이터
        
        Returns:
            워크플로우 응답이 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state["workflow_response"] = workflow_response
        return updated_state
    
    def transition_to_quiz_mode(self, 
                              state: TutorState, 
                              target_agent: str = "quiz_generator") -> TutorState:
        """
        퀴즈 모드로 전환
        
        Args:
            state: 현재 State
            target_agent: 목표 에이전트 (기본값: quiz_generator)
        
        Returns:
            퀴즈 모드로 전환된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 에이전트 전환
        updated_state = self.update_agent_transition(updated_state, target_agent)
        
        # UI 모드를 퀴즈로 변경
        updated_state = self.update_ui_mode(updated_state, "quiz")
        
        # 사용자 의도를 퀴즈 답변으로 설정
        updated_state = self.update_user_intent(updated_state, "quiz_answer")
        
        return updated_state
    
    def transition_to_chat_mode(self, 
                              state: TutorState, 
                              target_agent: Optional[str] = None) -> TutorState:
        """
        채팅 모드로 전환
        
        Args:
            state: 현재 State
            target_agent: 목표 에이전트 (None이면 현재 유지)
        
        Returns:
            채팅 모드로 전환된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 에이전트 전환 (지정된 경우만)
        if target_agent:
            updated_state = self.update_agent_transition(updated_state, target_agent)
        
        # UI 모드를 채팅으로 변경
        updated_state = self.update_ui_mode(updated_state, "chat")
        
        # 사용자 의도를 다음 단계로 설정
        updated_state = self.update_user_intent(updated_state, "next_step")
        
        return updated_state
    
    def handle_intent_routing(self, 
                            state: TutorState, 
                            user_intent: str, 
                            session_stage: str) -> str:
        """
        의도 분석 결과에 따른 에이전트 라우팅 결정
        
        Args:
            state: 현재 State
            user_intent: 사용자 의도
            session_stage: 세션 진행 단계
        
        Returns:
            라우팅할 에이전트 이름
        """
        # 1. 퀴즈 답변 처리 (의도 분석 없이 바로 평가)
        if user_intent == "quiz_answer":
            return "evaluation_feedback_agent"
        
        # 2. 질문 답변 요청
        if user_intent == "question":
            return "qna_resolver"
        
        # 3. 세션 완료 처리 (평가 완료 후)
        if session_stage == "quiz_and_feedback_completed" and user_intent == "next_step":
            return "session_manager"
        
        # 4. 다음 단계 진행
        if user_intent == "next_step":
            if session_stage == "session_start":
                return "theory_educator"
            elif session_stage == "theory_completed":
                return "quiz_generator"
        
        # 5. 기본값 - 직접 응답 생성
        return "learning_supervisor"
    
    def get_agent_transition_history(self, state: TutorState) -> List[Dict[str, Any]]:
        """
        에이전트 전환 히스토리 추출
        
        Args:
            state: 현재 State
        
        Returns:
            에이전트 전환 히스토리
        """
        conversations = state.get("current_session_conversations", [])
        
        transitions = []
        previous_agent = None
        
        for conv in conversations:
            agent = conv.get("agent_name")
            timestamp = conv.get("timestamp")
            stage = conv.get("session_stage")
            
            if agent != previous_agent:
                transitions.append({
                    "from_agent": previous_agent,
                    "to_agent": agent,
                    "timestamp": timestamp,
                    "session_stage": stage
                })
                previous_agent = agent
        
        return transitions
    
    def validate_agent_transition(self, 
                                from_agent: str, 
                                to_agent: str, 
                                session_stage: str) -> bool:
        """
        에이전트 전환 유효성 검증
        
        Args:
            from_agent: 현재 에이전트
            to_agent: 목표 에이전트  
            session_stage: 세션 진행 단계
        
        Returns:
            전환 유효성 여부
        """
        # 유효한 에이전트인지 확인
        if to_agent not in self.valid_agents:
            return False
        
        # 단계별 허용되는 전환 규칙
        valid_transitions = {
            "session_start": [
                "theory_educator", "session_manager", "learning_supervisor"
            ],
            "theory_completed": [
                "quiz_generator", "qna_resolver", "learning_supervisor"
            ],
            "quiz_and_feedback_completed": [
                "session_manager", "qna_resolver", "learning_supervisor"
            ]
        }
        
        allowed_agents = valid_transitions.get(session_stage, [])
        return to_agent in allowed_agents
    
    def get_recommended_next_agent(self, 
                                 state: TutorState, 
                                 user_intent: str) -> str:
        """
        현재 상태와 의도에 따른 권장 다음 에이전트
        
        Args:
            state: 현재 State
            user_intent: 사용자 의도
        
        Returns:
            권장 에이전트 이름
        """
        session_stage = state.get("session_progress_stage", "session_start")
        current_agent = state.get("current_agent", "")
        
        # 라우팅 로직 적용
        recommended_agent = self.handle_intent_routing(state, user_intent, session_stage)
        
        # 현재 에이전트와 같다면 learning_supervisor로 기본 설정
        if recommended_agent == current_agent:
            recommended_agent = "learning_supervisor"
        
        return recommended_agent
    
    def create_agent_workflow_context(self, state: TutorState) -> Dict[str, Any]:
        """
        에이전트 워크플로우 실행을 위한 컨텍스트 생성
        
        Args:
            state: 현재 State
        
        Returns:
            워크플로우 컨텍스트
        """
        return {
            "current_agent": state.get("current_agent", ""),
            "previous_agent": state.get("previous_agent", ""),
            "user_intent": state.get("user_intent", "next_step"),
            "session_stage": state.get("session_progress_stage", "session_start"),
            "ui_mode": state.get("ui_mode", "chat"),
            "chapter": state.get("current_chapter", 1),
            "section": state.get("current_section", 1),
            "user_type": state.get("user_type", "beginner")
        }
    
    def update_agent_with_ui_mode(self, 
                                state: TutorState, 
                                agent: str) -> TutorState:
        """
        에이전트에 따른 적절한 UI 모드 자동 설정
        
        Args:
            state: 현재 State
            agent: 에이전트 이름
        
        Returns:
            에이전트와 UI 모드가 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 에이전트 전환
        updated_state = self.update_agent_transition(updated_state, agent)
        
        # 에이전트별 적절한 UI 모드 설정
        agent_ui_mapping = {
            "quiz_generator": "quiz",
            "theory_educator": "chat",
            "evaluation_feedback_agent": "chat",
            "qna_resolver": "chat",
            "session_manager": "chat",
            "learning_supervisor": "chat"
        }
        
        ui_mode = agent_ui_mapping.get(agent, "chat")
        updated_state = self.update_ui_mode(updated_state, ui_mode)
        
        return updated_state
    
    def get_agent_status(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 에이전트 상태 정보 반환
        
        Args:
            state: 현재 State
        
        Returns:
            에이전트 상태 정보
        """
        current_agent = state.get("current_agent", "")
        previous_agent = state.get("previous_agent", "")
        ui_mode = state.get("ui_mode", "chat")
        user_intent = state.get("user_intent", "next_step")
        session_stage = state.get("session_progress_stage", "session_start")
        
        return {
            "current_agent": current_agent,
            "previous_agent": previous_agent,
            "ui_mode": ui_mode,
            "user_intent": user_intent,
            "session_stage": session_stage,
            "is_quiz_mode": ui_mode == "quiz",
            "is_chat_mode": ui_mode == "chat",
            "can_transition_to_quiz": session_stage == "theory_completed",
            "can_complete_session": session_stage == "quiz_and_feedback_completed",
            "workflow_context": self.create_agent_workflow_context(state)
        }
    
    def reset_agent_state(self, 
                         state: TutorState, 
                         default_agent: str = "session_manager") -> TutorState:
        """
        에이전트 상태 초기화
        
        Args:
            state: 현재 State
            default_agent: 기본 에이전트
        
        Returns:
            에이전트 상태가 초기화된 State
        """
        updated_state = copy.deepcopy(state)
        
        updated_state.update({
            "current_agent": default_agent,
            "previous_agent": "",
            "ui_mode": "chat",
            "user_intent": "next_step",
            "workflow_response": {}
        })
        
        return updated_state
    
    def handle_agent_error(self, 
                          state: TutorState, 
                          error_agent: str, 
                          fallback_agent: str = "learning_supervisor") -> TutorState:
        """
        에이전트 오류 처리 및 폴백
        
        Args:
            state: 현재 State
            error_agent: 오류가 발생한 에이전트
            fallback_agent: 폴백 에이전트
        
        Returns:
            폴백 처리된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 폴백 에이전트로 전환
        updated_state = self.update_agent_transition(updated_state, fallback_agent)
        
        # 안전한 상태로 복귀
        updated_state = self.update_ui_mode(updated_state, "chat")
        updated_state = self.update_user_intent(updated_state, "next_step")
        
        # 오류 정보를 워크플로우 응답에 기록
        error_response = {
            "error": True,
            "error_agent": error_agent,
            "fallback_agent": fallback_agent,
            "message": f"{error_agent} 처리 중 오류가 발생하여 {fallback_agent}로 전환되었습니다."
        }
        updated_state = self.update_workflow_response(updated_state, error_response)
        
        return updated_state
    
    def get_agent_statistics(self, state: TutorState) -> Dict[str, Any]:
        """
        에이전트 사용 통계 생성
        
        Args:
            state: 현재 State
        
        Returns:
            에이전트 사용 통계
        """
        conversations = state.get("current_session_conversations", [])
        
        agent_usage = {}
        transition_count = 0
        previous_agent = None
        
        for conv in conversations:
            agent = conv.get("agent_name", "unknown")
            
            # 에이전트 사용 횟수 집계
            agent_usage[agent] = agent_usage.get(agent, 0) + 1
            
            # 전환 횟수 집계
            if previous_agent and previous_agent != agent:
                transition_count += 1
            previous_agent = agent
        
        return {
            "agent_usage": agent_usage,
            "total_transitions": transition_count,
            "unique_agents": len(agent_usage),
            "most_used_agent": max(agent_usage.items(), key=lambda x: x[1])[0] if agent_usage else None,
            "current_agent": state.get("current_agent", ""),
            "session_stage": state.get("session_progress_stage", "")
        }


# 전역 AgentManager 인스턴스
agent_manager = AgentManager()