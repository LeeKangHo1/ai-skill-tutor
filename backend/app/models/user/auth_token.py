# backend/app/models/user/auth_token.py
"""
사용자 인증 토큰 모델
JWT 토큰 관리 및 인증 상태를 담당합니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class UserAuthToken:
    """사용자 인증 토큰을 관리하는 모델 클래스"""
    
    def __init__(self, token_id: Optional[int] = None, user_id: int = 0,
                 refresh_token: str = "", expires_at: Optional[datetime] = None,
                 is_active: bool = True, device_info: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.token_id = token_id
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.is_active = is_active
        self.device_info = device_info
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'token_id': self.token_id,
            'user_id': self.user_id,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'device_info': self.device_info,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserAuthToken':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        expires_at = None
        created_at = None
        
        if data.get('expires_at'):
            if isinstance(data['expires_at'], str):
                expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
            else:
                expires_at = data['expires_at']
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        return cls(
            token_id=data.get('token_id'),
            user_id=data.get('user_id', 0),
            refresh_token=data.get('refresh_token', ''),
            expires_at=expires_at,
            is_active=data.get('is_active', True),
            device_info=data.get('device_info'),
            created_at=created_at
        )