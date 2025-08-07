# backend/app/models/learning/session.py
"""
학습 세션 모델
사용자의 학습 세션 정보와 세션 ID 생성을 담당합니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import time


def generate_session_id(user_id: int, chapter: int, session_count: int) -> str:
    """
    세션 ID를 생성하는 함수
    형식: user{id}_ch{chapter}_session{count:03d}_{timestamp}
    
    Args:
        user_id: 사용자 ID
        chapter: 챕터 번호
        session_count: 세션 순서 번호
    
    Returns:
        생성된 세션 ID 문자열
    """
    timestamp = int(time.time())
    return f"user{user_id}_ch{chapter}_session{session_count:03d}_{timestamp}"


class LearningSession:
    """학습 세션 정보를 관리하는 모델 클래스"""
    
    def __init__(self, session_id: str = "", user_id: int = 0,
                 chapter_number: int = 1, session_sequence: int = 1,
                 session_start_time: Optional[datetime] = None,
                 session_end_time: Optional[datetime] = None,
                 study_duration_minutes: Optional[int] = None,
                 session_decision_result: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.chapter_number = chapter_number
        self.session_sequence = session_sequence
        self.session_start_time = session_start_time
        self.session_end_time = session_end_time
        self.study_duration_minutes = study_duration_minutes
        self.session_decision_result = session_decision_result
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'chapter_number': self.chapter_number,
            'session_sequence': self.session_sequence,
            'session_start_time': self.session_start_time.isoformat() if self.session_start_time else None,
            'session_end_time': self.session_end_time.isoformat() if self.session_end_time else None,
            'study_duration_minutes': self.study_duration_minutes,
            'session_decision_result': self.session_decision_result,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningSession':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        session_start_time = None
        session_end_time = None
        created_at = None
        
        if data.get('session_start_time'):
            if isinstance(data['session_start_time'], str):
                session_start_time = datetime.fromisoformat(data['session_start_time'].replace('Z', '+00:00'))
            else:
                session_start_time = data['session_start_time']
        
        if data.get('session_end_time'):
            if isinstance(data['session_end_time'], str):
                session_end_time = datetime.fromisoformat(data['session_end_time'].replace('Z', '+00:00'))
            else:
                session_end_time = data['session_end_time']
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        return cls(
            session_id=data.get('session_id', ''),
            user_id=data.get('user_id', 0),
            chapter_number=data.get('chapter_number', 1),
            session_sequence=data.get('session_sequence', 1),
            session_start_time=session_start_time,
            session_end_time=session_end_time,
            study_duration_minutes=data.get('study_duration_minutes'),
            session_decision_result=data.get('session_decision_result'),
            created_at=created_at
        )