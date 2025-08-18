# backend/app/core/langraph/managers/conversation_manager.py
# 대화 관리 전담 모듈

import copy
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..state.state_definition import TutorState


class ConversationManager:
    """
    대화 관리를 담당하는 클래스
    
    주요 기능:
    - 세션 내 대화 기록 관리
    - 에이전트 대본 저장/조회
    - 메시지 추가 및 검색
    - 대화 히스토리 요약
    - 최근 세션 요약 관리
    - 대화 기록 초기화
    """
    
    def __init__(self):
        """ConversationManager 초기화"""
        pass
    
    def add_conversation(self, 
                        state: TutorState,
                        agent_name: str,
                        message: str,
                        message_type: str = "system") -> TutorState:
        """
        현재 세션에 대화 내용 추가
        
        Args:
            state: 현재 State
            agent_name: 에이전트 이름
            message: 메시지 내용
            message_type: 메시지 유형 ("user", "system", "tool")
        
        Returns:
            대화가 추가된 State
        """
        updated_state = copy.deepcopy(state)
        
        conversation_item = {
            "agent_name": agent_name,
            "message": message,
            "timestamp": datetime.now(),
            "message_type": message_type,
            "session_stage": state.get("session_progress_stage", "session_start")
        }
        
        current_conversations = updated_state.get("current_session_conversations", [])
        current_conversations.append(conversation_item)
        updated_state["current_session_conversations"] = current_conversations
        
        return updated_state
    
    def add_user_message(self, 
                        state: TutorState, 
                        message: str) -> TutorState:
        """
        사용자 메시지 추가
        
        Args:
            state: 현재 State
            message: 사용자 메시지
        
        Returns:
            사용자 메시지가 추가된 State
        """
        return self.add_conversation(
            state, 
            agent_name="user", 
            message=message, 
            message_type="user"
        )
    
    def add_system_message(self, 
                          state: TutorState, 
                          agent_name: str, 
                          message: str) -> TutorState:
        """
        시스템 메시지 추가
        
        Args:
            state: 현재 State
            agent_name: 에이전트 이름
            message: 시스템 메시지
        
        Returns:
            시스템 메시지가 추가된 State
        """
        return self.add_conversation(
            state, 
            agent_name=agent_name, 
            message=message, 
            message_type="system"
        )
    
    def get_conversations_by_agent(self, 
                                  state: TutorState, 
                                  agent_name: str) -> List[Dict[str, Any]]:
        """
        특정 에이전트의 대화 기록 조회
        
        Args:
            state: 현재 State
            agent_name: 에이전트 이름
        
        Returns:
            해당 에이전트의 대화 기록 리스트
        """
        conversations = state.get("current_session_conversations", [])
        return [conv for conv in conversations if conv.get("agent_name") == agent_name]
    
    def get_conversations_by_stage(self, 
                                  state: TutorState, 
                                  stage: str) -> List[Dict[str, Any]]:
        """
        특정 세션 단계의 대화 기록 조회
        
        Args:
            state: 현재 State
            stage: 세션 진행 단계
        
        Returns:
            해당 단계의 대화 기록 리스트
        """
        conversations = state.get("current_session_conversations", [])
        return [conv for conv in conversations if conv.get("session_stage") == stage]
    
    def get_recent_conversations(self, 
                               state: TutorState, 
                               count: int = 5) -> List[Dict[str, Any]]:
        """
        최근 대화 기록 조회
        
        Args:
            state: 현재 State
            count: 조회할 메시지 수
        
        Returns:
            최근 대화 기록 리스트
        """
        conversations = state.get("current_session_conversations", [])
        return conversations[-count:] if conversations else []
    
    def clear_conversations(self, state: TutorState) -> TutorState:
        """
        현재 세션 대화 기록 초기화
        
        Args:
            state: 현재 State
        
        Returns:
            대화 기록이 초기화된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state["current_session_conversations"] = []
        return updated_state
    
    def get_conversation_count(self, state: TutorState) -> int:
        """
        현재 세션 대화 개수 반환
        
        Args:
            state: 현재 State
        
        Returns:
            대화 개수
        """
        conversations = state.get("current_session_conversations", [])
        return len(conversations)
    
    def update_agent_draft(self, 
                          state: TutorState, 
                          agent_name: str, 
                          draft_content: str) -> TutorState:
        """
        에이전트 대본 업데이트
        
        Args:
            state: 현재 State
            agent_name: 에이전트 이름
            draft_content: 대본 내용
        
        Returns:
            대본이 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        draft_field_map = {
            "theory_educator": "theory_draft",
            "quiz_generator": "quiz_draft", 
            "evaluation_feedback_agent": "feedback_draft",
            "qna_resolver": "qna_draft"
        }
        
        if agent_name in draft_field_map:
            field_name = draft_field_map[agent_name]
            updated_state[field_name] = draft_content
        
        return updated_state
    
    def get_agent_draft(self, 
                       state: TutorState, 
                       agent_name: str) -> str:
        """
        에이전트 대본 조회
        
        Args:
            state: 현재 State
            agent_name: 에이전트 이름
        
        Returns:
            에이전트 대본 내용
        """
        draft_field_map = {
            "theory_educator": "theory_draft",
            "quiz_generator": "quiz_draft",
            "evaluation_feedback_agent": "feedback_draft", 
            "qna_resolver": "qna_draft"
        }
        
        if agent_name in draft_field_map:
            field_name = draft_field_map[agent_name]
            return state.get(field_name, "")
        
        return ""
    
    def clear_agent_drafts(self, state: TutorState) -> TutorState:
        """
        모든 에이전트 대본 초기화
        
        Args:
            state: 현재 State
        
        Returns:
            대본이 초기화된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state.update({
            "theory_draft": "",
            "quiz_draft": "",
            "feedback_draft": "",
            "qna_draft": ""
        })
        return updated_state
    
    def get_all_drafts(self, state: TutorState) -> Dict[str, str]:
        """
        모든 에이전트 대본 조회
        
        Args:
            state: 현재 State
        
        Returns:
            에이전트별 대본 딕셔너리
        """
        return {
            "theory_educator": state.get("theory_draft", ""),
            "quiz_generator": state.get("quiz_draft", ""),
            "evaluation_feedback_agent": state.get("feedback_draft", ""),
            "qna_resolver": state.get("qna_draft", "")
        }
    
    def add_recent_session_summary(self, 
                                  state: TutorState,
                                  chapter: int,
                                  section: int, 
                                  topic: str,
                                  summary: str) -> TutorState:
        """
        최근 세션 요약 추가
        
        Args:
            state: 현재 State
            chapter: 챕터 번호
            section: 섹션 번호
            topic: 주제
            summary: 요약 내용
        
        Returns:
            세션 요약이 추가된 State
        """
        updated_state = copy.deepcopy(state)
        
        session_summary = {
            "chapter": str(chapter),
            "section": str(section),
            "topic": topic,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
        recent_summaries = updated_state.get("recent_sessions_summary", [])
        recent_summaries.append(session_summary)
        
        # 최대 5개까지만 유지
        if len(recent_summaries) > 5:
            recent_summaries = recent_summaries[-5:]
        
        updated_state["recent_sessions_summary"] = recent_summaries
        return updated_state
    
    def get_recent_session_summaries(self, 
                                   state: TutorState, 
                                   count: int = 5) -> List[Dict[str, str]]:
        """
        최근 세션 요약 조회
        
        Args:
            state: 현재 State
            count: 조회할 세션 수
        
        Returns:
            최근 세션 요약 리스트
        """
        summaries = state.get("recent_sessions_summary", [])
        return summaries[-count:] if summaries else []
    
    def clear_recent_session_summaries(self, state: TutorState) -> TutorState:
        """
        최근 세션 요약 초기화
        
        Args:
            state: 현재 State
        
        Returns:
            세션 요약이 초기화된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state["recent_sessions_summary"] = []
        return updated_state
    
    def create_conversation_summary(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 세션 대화 요약 생성
        
        Args:
            state: 현재 State
        
        Returns:
            대화 요약 정보
        """
        conversations = state.get("current_session_conversations", [])
        
        # 메시지 유형별 통계
        message_stats = {"user": 0, "system": 0, "tool": 0}
        agent_stats = {}
        stage_stats = {}
        
        for conv in conversations:
            msg_type = conv.get("message_type", "system")
            agent = conv.get("agent_name", "unknown")
            stage = conv.get("session_stage", "unknown")
            
            message_stats[msg_type] = message_stats.get(msg_type, 0) + 1
            agent_stats[agent] = agent_stats.get(agent, 0) + 1
            stage_stats[stage] = stage_stats.get(stage, 0) + 1
        
        # 첫 번째와 마지막 메시지 시간
        first_message_time = None
        last_message_time = None
        
        if conversations:
            first_message_time = conversations[0].get("timestamp")
            last_message_time = conversations[-1].get("timestamp")
        
        return {
            "total_messages": len(conversations),
            "message_stats": message_stats,
            "agent_stats": agent_stats,
            "stage_stats": stage_stats,
            "first_message_time": first_message_time,
            "last_message_time": last_message_time,
            "session_duration": self._calculate_conversation_duration(conversations)
        }
    
    def _calculate_conversation_duration(self, conversations: List[Dict[str, Any]]) -> int:
        """
        대화 지속 시간 계산 (분 단위)
        
        Args:
            conversations: 대화 기록 리스트
        
        Returns:
            대화 지속 시간 (분)
        """
        if len(conversations) < 2:
            return 0
        
        try:
            first_time = conversations[0].get("timestamp")
            last_time = conversations[-1].get("timestamp")
            
            if isinstance(first_time, str):
                first_time = datetime.fromisoformat(first_time)
            if isinstance(last_time, str):
                last_time = datetime.fromisoformat(last_time)
            
            if first_time and last_time:
                duration = last_time - first_time
                return int(duration.total_seconds() / 60)
        except (ValueError, TypeError):
            pass
        
        return 0
    
    def find_conversations_by_keyword(self, 
                                    state: TutorState, 
                                    keyword: str) -> List[Dict[str, Any]]:
        """
        키워드로 대화 검색
        
        Args:
            state: 현재 State
            keyword: 검색 키워드
        
        Returns:
            키워드가 포함된 대화 기록 리스트
        """
        conversations = state.get("current_session_conversations", [])
        keyword_lower = keyword.lower()
        
        matching_conversations = []
        for conv in conversations:
            message = conv.get("message", "")
            if keyword_lower in message.lower():
                matching_conversations.append(conv)
        
        return matching_conversations
    
    def get_conversation_context(self, 
                               state: TutorState, 
                               context_size: int = 3) -> str:
        """
        QnA를 위한 대화 맥락 생성
        
        Args:
            state: 현재 State
            context_size: 포함할 최근 메시지 수
        
        Returns:
            대화 맥락 문자열
        """
        recent_conversations = self.get_recent_conversations(state, context_size)
        
        context_parts = []
        for conv in recent_conversations:
            agent = conv.get("agent_name", "unknown")
            message = conv.get("message", "")
            msg_type = conv.get("message_type", "system")
            
            if msg_type == "user":
                context_parts.append(f"사용자: {message}")
            else:
                context_parts.append(f"{agent}: {message}")
        
        return "\n".join(context_parts)
    
    def export_conversations_for_db(self, state: TutorState) -> List[Dict[str, Any]]:
        """
        DB 저장용 대화 기록 포맷 변환
        
        Args:
            state: 현재 State
        
        Returns:
            DB 저장용 대화 기록 리스트
        """
        conversations = state.get("current_session_conversations", [])
        formatted_conversations = []
        
        for i, conv in enumerate(conversations, 1):
            formatted_conv = {
                "message_sequence": i,
                "agent_name": conv.get("agent_name", "unknown"),
                "message_type": conv.get("message_type", "system"),
                "message_content": conv.get("message", ""),
                "message_timestamp": conv.get("timestamp", datetime.now()),
                "session_progress_stage": conv.get("session_stage", "")
            }
            formatted_conversations.append(formatted_conv)
        
        return formatted_conversations
    
    def get_conversation_statistics(self, state: TutorState) -> Dict[str, Any]:
        """
        대화 통계 정보 반환
        
        Args:
            state: 현재 State
        
        Returns:
            대화 통계 정보
        """
        conversations = state.get("current_session_conversations", [])
        
        if not conversations:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "system_messages": 0,
                "unique_agents": 0,
                "session_stages": 0,
                "conversation_duration_minutes": 0
            }
        
        user_messages = len([c for c in conversations if c.get("message_type") == "user"])
        system_messages = len([c for c in conversations if c.get("message_type") == "system"])
        unique_agents = len(set(c.get("agent_name") for c in conversations))
        unique_stages = len(set(c.get("session_stage") for c in conversations))
        
        return {
            "total_messages": len(conversations),
            "user_messages": user_messages,
            "system_messages": system_messages,
            "unique_agents": unique_agents,
            "session_stages": unique_stages,
            "conversation_duration_minutes": self._calculate_conversation_duration(conversations)
        }


# 전역 ConversationManager 인스턴스
conversation_manager = ConversationManager()