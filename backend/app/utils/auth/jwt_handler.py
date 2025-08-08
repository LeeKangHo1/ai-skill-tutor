# app/utils/auth/jwt_handler.py

import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from functools import wraps
from flask import request, jsonify, current_app


class JWTHandler:
    """JWT 토큰 생성, 검증, 관리를 담당하는 클래스"""
    
    def __init__(self):
        # 환경변수에서 비밀키 가져오기 (개발용 기본값 포함)
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
        self.algorithm = 'HS256'
        
        # 토큰 만료 시간 설정 (분 단위)
        self.access_token_expire_minutes = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 60))  # 1시간
        self.refresh_token_expire_days = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 30))  # 30일
    
    def generate_access_token(self, user_data: Dict[str, Any]) -> str:
        """
        Access Token 생성
        
        Args:
            user_data (dict): 토큰에 포함할 사용자 정보
                - user_id: 사용자 ID
                - login_id: 로그인 ID  
                - user_type: 사용자 유형
                
        Returns:
            str: 생성된 access token
        """
        now = datetime.utcnow()
        payload = {
            'user_id': user_data['user_id'],
            'login_id': user_data['login_id'],
            'user_type': user_data.get('user_type', 'unassigned'),
            'token_type': 'access',
            'iat': now,  # issued at
            'exp': now + timedelta(minutes=self.access_token_expire_minutes)  # expiration
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_id: int) -> str:
        """
        Refresh Token 생성
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            str: 생성된 refresh token
        """
        now = datetime.utcnow()
        payload = {
            'user_id': user_id,
            'token_type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=self.refresh_token_expire_days)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        토큰 디코딩 및 검증
        
        Args:
            token (str): 검증할 JWT 토큰
            
        Returns:
            dict | None: 성공 시 payload, 실패 시 None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            # 토큰 만료
            return None
        except jwt.InvalidTokenError:
            # 유효하지 않은 토큰
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        토큰 만료 여부 확인
        
        Args:
            token (str): 확인할 JWT 토큰
            
        Returns:
            bool: 만료 여부 (True: 만료됨, False: 유효함)
        """
        try:
            jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return False
        except jwt.ExpiredSignatureError:
            return True
        except jwt.InvalidTokenError:
            return True
    
    def extract_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        토큰에서 사용자 정보 추출
        
        Args:
            token (str): JWT 토큰
            
        Returns:
            dict | None: 사용자 정보 또는 None
        """
        payload = self.decode_token(token)
        if not payload:
            return None
        
        return {
            'user_id': payload.get('user_id'),
            'login_id': payload.get('login_id'),
            'user_type': payload.get('user_type', 'unassigned')
        }


# 전역 인스턴스
jwt_handler = JWTHandler()


# 편의를 위한 함수 형태 인터페이스
def generate_access_token(user_data: Dict[str, Any]) -> str:
    """Access Token 생성 편의 함수"""
    return jwt_handler.generate_access_token(user_data)


def generate_refresh_token(user_id: int) -> str:
    """Refresh Token 생성 편의 함수"""
    return jwt_handler.generate_refresh_token(user_id)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """토큰 디코딩 편의 함수"""
    return jwt_handler.decode_token(token)


def extract_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """토큰에서 사용자 정보 추출 편의 함수"""
    return jwt_handler.extract_user_from_token(token)


def get_current_user_from_request() -> Optional[Dict[str, Any]]:
    """
    현재 요청에서 사용자 정보 추출
    Authorization 헤더에서 Bearer 토큰을 가져와 사용자 정보 반환
    
    Returns:
        dict | None: 사용자 정보 또는 None
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return extract_user_from_token(token)


def require_auth(f):
    """
    인증이 필요한 라우트에 사용하는 데코레이터
    
    Usage:
        @require_auth
        def protected_route():
            current_user = get_current_user_from_request()
            # ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user_from_request()
        if not current_user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'AUTH_TOKEN_REQUIRED',
                    'message': '인증이 필요합니다.'
                }
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function