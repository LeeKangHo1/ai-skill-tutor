# backend/app/models/learning/session.py
"""
학습 세션 모델 v2.0
AUTO_INCREMENT 기반 세션 ID와 섹션별 학습을 지원합니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class LearningSession:
    """학습 세션 정보를 관리하는 모델 클래스 - v2.0 AUTO_INCREMENT 기반"""
    
    def __init__(self, session_id: Optional[int] = None, user_id: int = 0,
                 chapter_number: int = 1, section_number: int = 1,
                 session_start_time: Optional[datetime] = None,
                 session_end_time: Optional[datetime] = None,
                 study_duration_minutes: Optional[int] = None,
                 retry_decision_result: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.session_id = session_id  # v2.0: AUTO_INCREMENT INT 타입
        self.user_id = user_id
        self.chapter_number = chapter_number
        self.section_number = section_number  # v2.0: 섹션별 학습 지원
        self.session_start_time = session_start_time
        self.session_end_time = session_end_time
        self.study_duration_minutes = study_duration_minutes
        self.retry_decision_result = retry_decision_result  # v2.0: 'proceed' 또는 'retry'
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'chapter_number': self.chapter_number,
            'section_number': self.section_number,  # v2.0: 섹션 정보 추가
            'session_start_time': self.session_start_time.isoformat() if self.session_start_time else None,
            'session_end_time': self.session_end_time.isoformat() if self.session_end_time else None,
            'study_duration_minutes': self.study_duration_minutes,
            'retry_decision_result': self.retry_decision_result,  # v2.0: 필드명 변경
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
            session_id=data.get('session_id'),  # v2.0: INT 타입으로 변경
            user_id=data.get('user_id', 0),
            chapter_number=data.get('chapter_number', 1),
            section_number=data.get('section_number', 1),  # v2.0: 섹션 정보 추가
            session_start_time=session_start_time,
            session_end_time=session_end_time,
            study_duration_minutes=data.get('study_duration_minutes'),
            retry_decision_result=data.get('retry_decision_result'),  # v2.0: 필드명 변경
            created_at=created_at
        )
    
    def calculate_duration(self) -> Optional[int]:
        """세션 시작/종료 시간으로부터 학습 시간 계산 (분 단위) - v2.0"""
        if not self.session_start_time or not self.session_end_time:
            return None
        
        duration = self.session_end_time - self.session_start_time
        return int(duration.total_seconds() / 60)
    
    def update_duration(self) -> None:
        """학습 시간을 자동으로 계산하여 업데이트 - v2.0"""
        calculated_duration = self.calculate_duration()
        if calculated_duration is not None:
            self.study_duration_minutes = calculated_duration
    
    def is_completed(self) -> bool:
        """세션이 완료되었는지 확인 - v2.0"""
        return (self.session_end_time is not None and 
                self.retry_decision_result is not None)
    
    def validate_retry_decision(self, decision: str) -> bool:
        """재학습 결정 값 검증 - v2.0"""
        return decision in ['proceed', 'retry']
    
    def set_retry_decision(self, decision: str) -> None:
        """재학습 결정 설정 - v2.0 검증 포함"""
        if not self.validate_retry_decision(decision):
            raise ValueError(f"잘못된 재학습 결정 값입니다: {decision}. 'proceed' 또는 'retry'만 가능합니다.")
        self.retry_decision_result = decision
    
    def get_session_summary(self) -> Dict[str, Any]:
        """세션 요약 정보 반환 - v2.0 디버깅 및 로깅용"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'chapter_section': f"{self.chapter_number}.{self.section_number}",
            'duration_minutes': self.study_duration_minutes,
            'is_completed': self.is_completed(),
            'retry_decision': self.retry_decision_result,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }