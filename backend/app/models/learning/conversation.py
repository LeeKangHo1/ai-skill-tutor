# backend/app/models/learning/conversation.py
"""
세션 대화 기록 모델
학습 세션 중 발생한 대화 내용을 관리합니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class SessionConversation:
    """세션 대화 기록을 관리하는 모델 클래스"""
    
    def __init__(self, conversation_id: Optional[int] = None, session_id: Optional[int] = None,
                 message_sequence: int = 1, agent_name: str = "",
                 message_type: str = "user", message_content: str = "",
                 message_timestamp: Optional[datetime] = None,
                 session_progress_stage: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.conversation_id = conversation_id
        self.session_id = session_id  # v2.0: INT 타입으로 변경
        self.message_sequence = message_sequence
        self.agent_name = agent_name
        self.message_type = message_type  # 'user', 'system', 'tool'
        self.message_content = message_content
        self.message_timestamp = message_timestamp or datetime.now()
        self.session_progress_stage = session_progress_stage
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'conversation_id': self.conversation_id,
            'session_id': self.session_id,
            'message_sequence': self.message_sequence,
            'agent_name': self.agent_name,
            'message_type': self.message_type,
            'message_content': self.message_content,
            'message_timestamp': self.message_timestamp.isoformat() if self.message_timestamp else None,
            'session_progress_stage': self.session_progress_stage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionConversation':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        message_timestamp = None
        created_at = None
        
        if data.get('message_timestamp'):
            if isinstance(data['message_timestamp'], str):
                message_timestamp = datetime.fromisoformat(data['message_timestamp'].replace('Z', '+00:00'))
            else:
                message_timestamp = data['message_timestamp']
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        return cls(
            conversation_id=data.get('conversation_id'),
            session_id=data.get('session_id'),  # v2.0: INT 타입으로 변경
            message_sequence=data.get('message_sequence', 1),
            agent_name=data.get('agent_name', ''),
            message_type=data.get('message_type', 'user'),
            message_content=data.get('message_content', ''),
            message_timestamp=message_timestamp,
            session_progress_stage=data.get('session_progress_stage'),
            created_at=created_at
        )
    
    def validate_message_type(self, msg_type: str) -> bool:
        """메시지 타입 검증 - v2.0"""
        return msg_type in ['user', 'system', 'tool']
    
    def set_message_type(self, msg_type: str) -> None:
        """메시지 타입 설정 - v2.0 검증 포함"""
        if not self.validate_message_type(msg_type):
            raise ValueError(f"잘못된 메시지 타입입니다: {msg_type}. 'user', 'system', 'tool'만 가능합니다.")
        self.message_type = msg_type
    
    def get_message_preview(self, max_length: int = 100) -> str:
        """메시지 내용 미리보기 - v2.0 로깅용"""
        if not self.message_content:
            return ""
        
        if len(self.message_content) <= max_length:
            return self.message_content
        
        return self.message_content[:max_length] + "..."
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """대화 요약 정보 반환 - v2.0 디버깅 및 로깅용"""
        return {
            'conversation_id': self.conversation_id,
            'session_id': self.session_id,
            'sequence': self.message_sequence,
            'agent': self.agent_name,
            'type': self.message_type,
            'content_length': len(self.message_content) if self.message_content else 0,
            'preview': self.get_message_preview(50),
            'stage': self.session_progress_stage,
            'timestamp': self.message_timestamp.isoformat() if self.message_timestamp else None
        }