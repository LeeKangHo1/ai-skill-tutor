# backend/app/models/user/user.py
"""
사용자 기본 정보 모델
사용자의 기본 정보와 계정 관리를 담당합니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class User:
    """사용자 기본 정보를 관리하는 모델 클래스"""
    
    def __init__(self, user_id: Optional[int] = None, login_id: str = "", 
                 username: str = "", email: str = "", password_hash: str = "",
                 user_type: str = "unassigned", diagnosis_completed: bool = False,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.user_id = user_id
        self.login_id = login_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.user_type = user_type
        self.diagnosis_completed = diagnosis_completed
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'user_id': self.user_id,
            'login_id': self.login_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'user_type': self.user_type,
            'diagnosis_completed': self.diagnosis_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        created_at = None
        updated_at = None
        
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
            user_id=data.get('user_id'),
            login_id=data.get('login_id', ''),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            user_type=data.get('user_type', 'unassigned'),
            diagnosis_completed=data.get('diagnosis_completed', False),
            created_at=created_at,
            updated_at=updated_at
        )