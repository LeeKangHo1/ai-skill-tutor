# backend/app/middleware/auth/session_middleware.py
"""
세션 관리 미들웨어 모듈
사용자 세션 상태를 관리하고 검증합니다.
"""

from functools import wraps
from flask import request, jsonify, g
from typing import Optional, Dict, Any
from app.models import UserAuthToken, User

class SessionMiddleware:
    """세션 관리 미들웨어 클래스"""
    
    def __init__(self):
        """세션 미들웨어 초기화"""
        pass
    
    def get_session_token(self) -> Optional[str]:
        """
        요청에서 세션 토큰을 추출합니다.
        
        Returns:
            Optional[str]: 세션 토큰 또는 None
        """
        # 헤더에서 세션 토큰 확인
        session_token = request.headers.get('X-Session-Token')
        if session_token:
            return session_token
        
        # 쿠키에서 세션 토큰 확인
        session_token = request.cookies.get('session_token')
        if session_token:
            return session_token
        
        return None
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        세션 토큰의 유효성을 검증합니다.
        
        Args:
            session_token (str): 세션 토큰
            
        Returns:
            Optional[Dict[str, Any]]: 세션 정보 또는 None
        """
        try:
            # 데이터베이스에서 토큰 조회
            auth_token = UserAuthToken.query.filter_by(
                token=session_token,
                is_active=True
            ).first()
            
            if not auth_token:
                return None
            
            # 토큰 만료 확인
            if auth_token.is_expired():
                auth_token.is_active = False
                auth_token.save()
                return None
            
            # 사용자 정보 조회
            user = User.query.get(auth_token.user_id)
            if not user or not user.is_active:
                return None
            
            return {
                'user_id': user.id,
                'email': user.email,
                'user_type': user.user_type,
                'token_id': auth_token.id,
                'session_token': session_token
            }
        except Exception as e:
            print(f"세션 검증 오류: {e}")
            return None
    
    def require_session(self, f):
        """
        유효한 세션이 필요한 엔드포인트에 사용하는 데코레이터입니다.
        
        Args:
            f: 보호할 함수
            
        Returns:
            함수 래퍼
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_token = self.get_session_token()
            
            if not session_token:
                return jsonify({
                    'success': False,
                    'message': '세션 토큰이 필요합니다.'
                }), 401
            
            session_info = self.validate_session(session_token)
            if not session_info:
                return jsonify({
                    'success': False,
                    'message': '유효하지 않은 세션입니다.'
                }), 401
            
            # 세션 정보를 g 객체에 저장
            g.session_user_id = session_info['user_id']
            g.session_user_email = session_info['email']
            g.session_user_type = session_info['user_type']
            g.session_token_id = session_info['token_id']
            g.session_token = session_info['session_token']
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def optional_session(self, f):
        """
        선택적 세션 데코레이터입니다. 세션이 있으면 검증하지만 없어도 허용합니다.
        
        Args:
            f: 함수
            
        Returns:
            함수 래퍼
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_token = self.get_session_token()
            
            if session_token:
                session_info = self.validate_session(session_token)
                if session_info:
                    g.session_user_id = session_info['user_id']
                    g.session_user_email = session_info['email']
                    g.session_user_type = session_info['user_type']
                    g.session_token_id = session_info['token_id']
                    g.session_token = session_info['session_token']
                else:
                    g.session_user_id = None
                    g.session_user_email = None
                    g.session_user_type = None
                    g.session_token_id = None
                    g.session_token = None
            else:
                g.session_user_id = None
                g.session_user_email = None
                g.session_user_type = None
                g.session_token_id = None
                g.session_token = None
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def invalidate_session(self, session_token: str) -> bool:
        """
        세션을 무효화합니다.
        
        Args:
            session_token (str): 무효화할 세션 토큰
            
        Returns:
            bool: 무효화 성공 여부
        """
        try:
            auth_token = UserAuthToken.query.filter_by(
                token=session_token,
                is_active=True
            ).first()
            
            if auth_token:
                auth_token.is_active = False
                auth_token.save()
                return True
            
            return False
        except Exception as e:
            print(f"세션 무효화 오류: {e}")
            return False

# 전역 세션 미들웨어 인스턴스
session_middleware = SessionMiddleware()

# 편의를 위한 데코레이터 함수들
require_session = session_middleware.require_session
optional_session = session_middleware.optional_session