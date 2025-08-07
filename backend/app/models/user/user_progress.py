# backend/app/models/user/user_progress.py
"""
사용자 진행 상태 및 통계 모델
사용자의 학습 진행 상태와 통계 정보를 관리합니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class UserProgress:
    """사용자 학습 진행 상태를 관리하는 모델 클래스"""
    
    def __init__(self, progress_id: Optional[int] = None, user_id: int = 0,
                 current_chapter: int = 1, last_study_date: Optional[datetime] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.progress_id = progress_id
        self.user_id = user_id
        self.current_chapter = current_chapter
        self.last_study_date = last_study_date
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'progress_id': self.progress_id,
            'user_id': self.user_id,
            'current_chapter': self.current_chapter,
            'last_study_date': self.last_study_date.date().isoformat() if self.last_study_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProgress':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        last_study_date = None
        created_at = None
        updated_at = None
        
        if data.get('last_study_date'):
            if isinstance(data['last_study_date'], str):
                # DATE 타입은 날짜만 포함하므로 시간 부분을 추가
                last_study_date = datetime.fromisoformat(data['last_study_date'])
            else:
                last_study_date = data['last_study_date']
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            else:
                updated_at = data['updated_at']
        
        return cls(
            progress_id=data.get('progress_id'),
            user_id=data.get('user_id', 0),
            current_chapter=data.get('current_chapter', 1),
            last_study_date=last_study_date,
            created_at=created_at,
            updated_at=updated_at
        )


class UserStatistics:
    """사용자 학습 통계를 관리하는 모델 클래스"""
    
    def __init__(self, stats_id: Optional[int] = None, user_id: int = 0,
                 total_study_time_minutes: int = 0, total_study_sessions: int = 0,
                 total_completed_sessions: int = 0, total_correct_answers: int = 0,
                 average_accuracy: float = 0.00, last_study_date: Optional[datetime] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.stats_id = stats_id
        self.user_id = user_id
        self.total_study_time_minutes = total_study_time_minutes
        self.total_study_sessions = total_study_sessions
        self.total_completed_sessions = total_completed_sessions
        self.total_correct_answers = total_correct_answers
        self.average_accuracy = average_accuracy
        self.last_study_date = last_study_date
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'stats_id': self.stats_id,
            'user_id': self.user_id,
            'total_study_time_minutes': self.total_study_time_minutes,
            'total_study_sessions': self.total_study_sessions,
            'total_completed_sessions': self.total_completed_sessions,
            'total_correct_answers': self.total_correct_answers,
            'average_accuracy': float(self.average_accuracy),
            'last_study_date': self.last_study_date.date().isoformat() if self.last_study_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStatistics':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        last_study_date = None
        created_at = None
        updated_at = None
        
        if data.get('last_study_date'):
            if isinstance(data['last_study_date'], str):
                last_study_date = datetime.fromisoformat(data['last_study_date'])
            else:
                last_study_date = data['last_study_date']
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            else:
                updated_at = data['updated_at']
        
        return cls(
            stats_id=data.get('stats_id'),
            user_id=data.get('user_id', 0),
            total_study_time_minutes=data.get('total_study_time_minutes', 0),
            total_study_sessions=data.get('total_study_sessions', 0),
            total_completed_sessions=data.get('total_completed_sessions', 0),
            total_correct_answers=data.get('total_correct_answers', 0),
            average_accuracy=float(data.get('average_accuracy', 0.00)),
            last_study_date=last_study_date,
            created_at=created_at,
            updated_at=updated_at
        )