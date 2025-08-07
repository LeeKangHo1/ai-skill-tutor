# backend/app/middleware/auth/jwt_middleware.py
"""
JWT 검증 미들웨어 모듈
JWT 토큰의 유효성을 검증하고 사용자 인증을 처리합니다.
"""

from functools import wraps
from flask import request, jsonify, g
import jwt
import os
from typing import Optional, Dict, Any

class JWTMiddleware:
    """JWT 토큰 검증 미들웨어 클래스"""
    
    def __init__(self):
        """JWT 미들웨어 초기화"""
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
        self.algorithm = 'HS256'
        self.token_prefix = 'Bearer '
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        JWT 토큰을 검증하고 페이로드를 반환합니다.
        
        Args:
            token (str): JWT 토큰
            
        Returns:
            Optional[Dict[str, Any]]: 토큰 페이로드 또는 None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_token_from_header(self) -> Optional[str]:
        """
        요청 헤더에서 JWT 토큰을 추출합니다.
        
        Returns:
            Optional[str]: JWT 토큰 또는 None
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        if not auth_header.startswith(self.token_prefix):
            return None
        
        return auth_header[len(self.token_prefix):]
    
    def require_auth(self, f):
        """
        인증이 필요한 엔드포인트에 사용하는 데코레이터입니다.
        
        Args:
            f: 보호할 함수
            
        Returns:
            함수 래퍼
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self.get_token_from_header()
            
            if not token:
                return jsonify({
                    'success': False,
                    'message': '인증 토큰이 필요합니다.'
                }), 401
            
            payload = self.verify_token(token)
            if not payload:
                return jsonify({
                    'success': False,
                    'message': '유효하지 않은 토큰입니다.'
                }), 401
            
            # 사용자 정보를 g 객체에 저장
            g.current_user_id = payload.get('user_id')
            g.current_user_email = payload.get('email')
            g.token_payload = payload
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def optional_auth(self, f):
        """
        선택적 인증 데코레이터입니다. 토큰이 있으면 검증하지만 없어도 허용합니다.
        
        Args:
            f: 함수
            
        Returns:
            함수 래퍼
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self.get_token_from_header()
            
            if token:
                payload = self.verify_token(token)
                if payload:
                    g.current_user_id = payload.get('user_id')
                    g.current_user_email = payload.get('email')
                    g.token_payload = payload
                else:
                    g.current_user_id = None
                    g.current_user_email = None
                    g.token_payload = None
            else:
                g.current_user_id = None
                g.current_user_email = None
                g.token_payload = None
            
            return f(*args, **kwargs)
        
        return decorated_function

# 전역 JWT 미들웨어 인스턴스
jwt_middleware = JWTMiddleware()

# 편의를 위한 데코레이터 함수들
require_auth = jwt_middleware.require_auth
optional_auth = jwt_middleware.optional_auth