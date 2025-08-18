# backend/app/core/langraph/state_manager.py
# 통합 StateManager 래퍼 클래스 - 기존 코드 호환성 보장

import copy
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple

# State 정의 및 관리자들 import
from .state import (
    TutorState, 
    StateFactory, 
    StateValidator, 
    StateValidationError,
    state_factory, 
    state_validator
)

from .managers import (
    QuizManager,
    SessionManager, 
    ConversationManager,
    AgentManager,
    quiz_manager,
    session_manager,
    conversation_manager,
    agent_manager
)


class StateManager:
    """
    통합 StateManager 래퍼 클래스
    
    기존 StateManager API를 유지하면서 내부적으로는 분리된 관리자들을 사용
    점진적 마이그레이션을 지원하며 하위 호환성을 보장
    
    내부 구조:
    - StateFactory: State 생성 및 초기화
    - StateValidator: State 유효성 검증
    - QuizManager: 퀴즈 관련 기능
    - SessionManager: 세션 진행 관리
    - ConversationManager: 대화 관리
    - AgentManager: 에이전트 전환 관리
    """
    
    def __init__(self):
        """StateManager 초기화 - 모든 하위 관리자들 초기화"""
        # 팩토리 및 검증기
        self.factory = state_factory
        self.validator = state_validator
        
        # 도메인별 관리자들
        self.quiz = quiz_manager
        self.session = session_manager  
        self.conversation = conversation_manager
        self.agent = agent_manager
        
        # 기본 State 템플릿
        self._default_state = self.factory.get_default_state()
    
    # ==========================================
    # 기존 StateManager API 호환성 메서드들
    # ==========================================
    
    def _create_default_state(self) -> TutorState:
        """기본 State 템플릿 생성 (기존 API 호환성)"""
        return self.factory.get_default_state()
    
    def initialize_state(self, user_id: int, user_type: str, current_chapter: int = 1, current_section: int = 1) -> TutorState:
        """새로운 사용자 State 초기화 (기존 API 호환성)"""
        return self.factory.create_new_state(user_id, user_type, current_chapter, current_section)
    
    def update_section_progress(self, state: TutorState, next_section: int = None, next_chapter: int = None) -> TutorState:
        """섹션/챕터 진행 업데이트 (기존 API 호환성)"""
        return self.session.update_section_progress(state, next_section, next_chapter)
    
    def update_agent_transition(self, state: TutorState, new_agent: str) -> TutorState:
        """에이전트 전환 시 State 업데이트 (기존 API 호환성)"""
        return self.agent.update_agent_transition(state, new_agent)
    
    def update_session_progress(self, state: TutorState, completed_agent: str) -> TutorState:
        """세션 진행 단계 업데이트 (기존 API 호환성)"""
        return self.session.update_session_progress(state, completed_agent)
    
    def update_ui_mode(self, state: TutorState, mode: str) -> TutorState:
        """UI 모드 업데이트 (기존 API 호환성)"""
        return self.agent.update_ui_mode(state, mode)
    
    def update_quiz_info(self, state: TutorState, **kwargs) -> TutorState:
        """퀴즈 관련 정보 업데이트 (기존 API 호환성)"""
        return self.quiz.update_quiz_info(state, **kwargs)
    
    def update_agent_draft(self, state: TutorState, agent_name: str, draft_content: str) -> TutorState:
        """에이전트 대본 업데이트 (기존 API 호환성)"""
        return self.conversation.update_agent_draft(state, agent_name, draft_content)
    
    def add_conversation(self, state: TutorState, agent_name: str, message: str, message_type: str = "system") -> TutorState:
        """현재 세션에 대화 내용 추가 (기존 API 호환성)"""
        return self.conversation.add_conversation(state, agent_name, message, message_type)
    
    def clear_agent_drafts(self, state: TutorState) -> TutorState:
        """에이전트 대본 필드 초기화 (기존 API 호환성)"""
        return self.conversation.clear_agent_drafts(state)
    
    def reset_session_state(self, state: TutorState, new_chapter: bool = False) -> TutorState:
        """세션 상태 초기화 (기존 API 호환성)"""
        return self.session.reset_session_state(state, new_chapter)
    
    def get_quiz_type_from_section(self, state: TutorState, chapter_data: Dict[str, Any]) -> str:
        """현재 섹션의 퀴즈 타입 반환 (기존 API 호환성)"""
        return self.quiz.get_quiz_type_from_section(state, chapter_data)
    
    def update_quiz_type_from_section(self, state: TutorState, chapter_data: Dict[str, Any]) -> TutorState:
        """현재 섹션의 퀴즈 타입으로 State 업데이트 (기존 API 호환성)"""
        return self.quiz.update_quiz_type_from_section(state, chapter_data)
    
    def get_current_section_data(self, state: TutorState, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """현재 섹션 데이터 반환 (기존 API 호환성)"""
        return self.quiz.get_current_section_data(state, chapter_data)
    
    def sync_quiz_types(self, state: TutorState) -> TutorState:
        """퀴즈 타입 동기화 (기존 API 호환성)"""
        return self.quiz.sync_quiz_types(state)
    
    def parse_quiz_from_json(self, state: TutorState, quiz_json: Dict[str, Any]) -> TutorState:
        """ChatGPT에서 생성된 퀴즈 JSON을 State에 파싱 (기존 API 호환성)"""
        return self.quiz.parse_quiz_from_json(state, quiz_json)
    
    def update_evaluation_result(self, state: TutorState, **kwargs) -> TutorState:
        """평가 결과 업데이트 (기존 API 호환성)"""
        return self.quiz.update_evaluation_result(state, **kwargs)
    
    def clear_quiz_data(self, state: TutorState) -> TutorState:
        """퀴즈 관련 데이터 초기화 (기존 API 호환성)"""
        return self.quiz.clear_quiz_data(state)
    
    def to_dict(self, state: TutorState) -> Dict[str, Any]:
        """State를 직렬화 가능한 딕셔너리로 변환 (기존 API 호환성)"""
        return self.factory.to_dict(state)
    
    def from_dict(self, state_dict: Dict[str, Any]) -> TutorState:
        """딕셔너리에서 State 복원 (기존 API 호환성)"""
        return self.factory.from_dict(state_dict)
    
    def validate_state(self, state: TutorState) -> bool:
        """State 유효성 검증 (기존 API 호환성)"""
        return self.validator.validate_state(state)
    
    def update_user_answer(self, state: TutorState, user_answer: str) -> TutorState:
        """사용자 답변만 업데이트 (기존 API 호환성)"""
        return self.quiz.update_user_answer(state, user_answer)
    
    def update_session_decision(self, state: TutorState, decision: str) -> TutorState:
        """세션 완료 후 사용자 결정 업데이트 (기존 API 호환성)"""
        return self.session.update_session_decision(state, decision)
    
    def prepare_next_session(self, state: TutorState, next_chapter: int = None, next_section: int = None) -> TutorState:
        """다음 세션 준비 (기존 API 호환성)"""
        return self.session.prepare_next_session(state, next_chapter, next_section)
    
    def update_workflow_response(self, state: TutorState, workflow_response: Dict[str, Any]) -> TutorState:
        """workflow_response 업데이트 (기존 API 호환성)"""
        return self.agent.update_workflow_response(state, workflow_response)
    
    # ==========================================
    # 새로운 통합 메서드들 (v2.0 신규)
    # ==========================================
    
    def create_session_state(self, user_id: int, user_type: str, chapter: int, section: int) -> TutorState:
        """학습 세션용 State 생성"""
        return self.factory.create_session_state(user_id, user_type, chapter, section)
    
    def get_comprehensive_summary(self, state: TutorState) -> Dict[str, Any]:
        """종합적인 State 요약 정보"""
        return {
            "session_summary": self.session.get_session_summary(state),
            "quiz_summary": self.quiz.get_quiz_summary(state),
            "agent_status": self.agent.get_agent_status(state),
            "conversation_stats": self.conversation.get_conversation_statistics(state),
            "validation_report": self.validator.get_validation_report(state)
        }
    
    def handle_user_message(self, state: TutorState, user_message: str, message_type: str = "user") -> TutorState:
        """사용자 메시지 처리 (대화 기록 추가)"""
        return self.conversation.add_conversation(state, "user", user_message, message_type)
    
    def transition_to_quiz(self, state: TutorState) -> TutorState:
        """퀴즈 모드로 전환 (UI 모드 + 에이전트 + 의도 통합 설정)"""
        return self.agent.transition_to_quiz_mode(state)
    
    def transition_to_chat(self, state: TutorState, target_agent: str = None) -> TutorState:
        """채팅 모드로 전환 (UI 모드 + 에이전트 + 의도 통합 설정)"""
        return self.agent.transition_to_chat_mode(state, target_agent)
    
    def process_quiz_answer(self, state: TutorState, user_answer: str) -> TutorState:
        """퀴즈 답변 처리 (답변 저장 + 객관식 로컬 채점)"""
        updated_state = self.quiz.update_user_answer(state, user_answer)
        
        quiz_type = state.get("quiz_type", "multiple_choice")
        if quiz_type == "multiple_choice":
            updated_state = self.quiz.evaluate_multiple_choice(updated_state, user_answer)
        
        return updated_state
    
    def get_agent_routing_recommendation(self, state: TutorState, user_intent: str) -> str:
        """에이전트 라우팅 추천"""
        return self.agent.get_recommended_next_agent(state, user_intent)
    
    def validate_and_fix_state(self, state: TutorState) -> Tuple[TutorState, bool]:
        """State 검증 및 자동 수정"""
        is_valid = self.validator.validate_state(state)
        
        if not is_valid:
            # 기본값으로 수정 시도
            fixed_state = self.factory.merge_states(
                self._default_state, 
                {k: v for k, v in state.items() if v is not None}
            )
            return fixed_state, False
        
        return state, True
    
    def export_for_database(self, state: TutorState) -> Dict[str, Any]:
        """DB 저장용 데이터 export"""
        return {
            "session_info": {
                "user_id": state.get("user_id"),
                "chapter_number": state.get("current_chapter"),
                "section_number": state.get("current_section"),
                "session_start_time": state.get("session_start_time"),
                "study_duration_minutes": self.session.get_session_duration(state),
                "retry_decision_result": state.get("retry_decision_result")
            },
            "conversations": self.conversation.export_conversations_for_db(state),
            "quiz_info": self._extract_quiz_info_for_db(state) if self.quiz.is_quiz_completed(state) else None
        }
    
    def _extract_quiz_info_for_db(self, state: TutorState) -> Dict[str, Any]:
        """DB 저장용 퀴즈 정보 추출"""
        quiz_type = state.get("quiz_type", "multiple_choice")
        
        base_info = {
            "quiz_type": quiz_type,
            "quiz_content": state.get("quiz_content", ""),
            "quiz_hint": state.get("quiz_hint", ""),
            "user_answer": state.get("user_answer", ""),
            "evaluation_feedback": state.get("evaluation_feedback", ""),
            "hint_usage_count": state.get("hint_usage_count", 0)
        }
        
        if quiz_type == "multiple_choice":
            base_info.update({
                "quiz_options": state.get("quiz_options", []),
                "quiz_correct_answer": state.get("quiz_correct_answer"),
                "quiz_explanation": state.get("quiz_explanation", ""),
                "multiple_answer_correct": state.get("multiple_answer_correct", False)
            })
        elif quiz_type == "subjective":
            base_info.update({
                "quiz_sample_answer": state.get("quiz_sample_answer", ""),
                "quiz_evaluation_criteria": state.get("quiz_evaluation_criteria", []),
                "subjective_answer_score": state.get("subjective_answer_score", 0)
            })
        
        return base_info
    
    # ==========================================
    # 유틸리티 메서드들
    # ==========================================
    
    def copy_state(self, state: TutorState) -> TutorState:
        """State 안전한 복사"""
        return self.factory.copy_state(state)
    
    def merge_states(self, base_state: TutorState, updates: Dict[str, Any]) -> TutorState:
        """State 병합"""
        return self.factory.merge_states(base_state, updates)
    
    def quick_validate(self, state: TutorState) -> bool:
        """빠른 State 검증"""
        return self.validator.quick_validate(state)
    
    def get_state_errors(self, state: TutorState) -> List[str]:
        """State 오류 목록 반환"""
        report = self.validator.get_validation_report(state)
        return [error["message"] for error in report.get("errors", [])]
    
    # ==========================================
    # 디버깅 및 개발 지원 메서드들
    # ==========================================
    
    def debug_state_info(self, state: TutorState) -> Dict[str, Any]:
        """개발용 State 디버깅 정보"""
        return {
            "basic_info": {
                "user_id": state.get("user_id"),
                "user_type": state.get("user_type"),
                "chapter": state.get("current_chapter"),
                "section": state.get("current_section")
            },
            "current_status": {
                "agent": state.get("current_agent"),
                "stage": state.get("session_progress_stage"),
                "ui_mode": state.get("ui_mode"),
                "intent": state.get("user_intent")
            },
            "quiz_status": {
                "type": state.get("quiz_type"),
                "content": bool(state.get("quiz_content")),
                "answered": bool(state.get("user_answer")),
                "evaluated": bool(state.get("evaluation_feedback"))
            },
            "conversation_count": len(state.get("current_session_conversations", [])),
            "session_duration": self.session.get_session_duration(state),
            "validation_status": self.validator.quick_validate(state)
        }
    
    def get_manager_instances(self) -> Dict[str, Any]:
        """모든 관리자 인스턴스 반환 (고급 사용자용)"""
        return {
            "factory": self.factory,
            "validator": self.validator,
            "quiz": self.quiz,
            "session": self.session,
            "conversation": self.conversation,
            "agent": self.agent
        }


# 전역 StateManager 인스턴스 (기존 코드 호환성)
state_manager = StateManager()