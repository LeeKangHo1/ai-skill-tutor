# app/services/auth/token_service.py

from typing import Dict, Any, Optional
from datetime import datetime

from app.utils.database.connection import fetch_one, execute_query
from app.utils.auth.jwt_handler import (
    decode_token, generate_access_token, generate_refresh_token,
    extract_user_from_token
)
from app.utils.common.exceptions import AuthenticationError


class TokenService:
    """토큰 관리 관련 비즈니스 로직을 처리하는 서비스"""
    
    @staticmethod
    def validate_refresh_token(refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        리프레시 토큰 검증 및 사용자 정보 조회
        
        Args:
            refresh_token (str): 리프레시 토큰
            
        Returns:
            dict | None: 토큰 정보 및 사용자 정보
        """
        # JWT 토큰 디코딩
        payload = decode_token(refresh_token)
        if not payload or payload.get('token_type') != 'refresh':
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        # 데이터베이스에서 토큰 유효성 확인
        token_data = fetch_one(
            """
            SELECT 
                uat.token_id, uat.user_id, uat.expires_at, uat.is_active,
                u.login_id, u.username, u.user_type, u.diagnosis_completed,
                up.current_chapter
            FROM user_auth_tokens uat
            JOIN users u ON uat.user_id = u.user_id
            LEFT JOIN user_progress up ON u.user_id = up.user_id
            WHERE uat.refresh_token = %s AND uat.is_active = TRUE
            """,
            (refresh_token,)
        )
        
        if not token_data:
            return None
        
        # 만료 시간 확인
        if token_data['expires_at'] < datetime.utcnow():
            # 만료된 토큰은 비활성화
            TokenService.deactivate_token(token_data['token_id'])
            return None
        
        return {
            'token_id': token_data['token_id'],
            'user_info': {
                'user_id': token_data['user_id'],
                'login_id': token_data['login_id'],
                'username': token_data['username'],
                'user_type': token_data['user_type'],
                'diagnosis_completed': bool(token_data['diagnosis_completed']),
                'current_chapter': token_data['current_chapter'] or 1
            }
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
        """
        Access Token 갱신
        
        Args:
            refresh_token (str): 리프레시 토큰
            
        Returns:
            dict: 새로운 토큰들
            
        Raises:
            AuthenticationError: 토큰 검증 실패
        """
        # 리프레시 토큰 검증
        token_info = TokenService.validate_refresh_token(refresh_token)
        if not token_info:
            raise AuthenticationError("유효하지 않은 리프레시 토큰입니다.")
        
        user_info = token_info['user_info']
        
        # 새로운 토큰 생성
        token_data = {
            'user_id': user_info['user_id'],
            'login_id': user_info['login_id'],
            'user_type': user_info['user_type']
        }
        
        new_access_token = generate_access_token(token_data)
        new_refresh_token = generate_refresh_token(user_info['user_id'])
        
        # 기존 리프레시 토큰 비활성화
        TokenService.deactivate_token(token_info['token_id'])
        
        # 새 리프레시 토큰 저장
        TokenService.save_refresh_token(user_info['user_id'], new_refresh_token)
        
        return {
            'success': True,
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'user_info': user_info,
            'message': '토큰이 갱신되었습니다.'
        }
    
    @staticmethod
    def save_refresh_token(user_id: int, refresh_token: str, device_info: Optional[str] = None) -> None:
        """
        새 리프레시 토큰 저장
        
        Args:
            user_id (int): 사용자 ID
            refresh_token (str): 리프레시 토큰
            device_info (str, optional): 디바이스 정보
        """
        from datetime import timedelta
        
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        execute_query(
            """
            INSERT INTO user_auth_tokens (user_id, refresh_token, expires_at, device_info)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, refresh_token, expires_at, device_info)
        )
    
    @staticmethod
    def deactivate_token(token_id: int) -> None:
        """
        특정 토큰 비활성화
        
        Args:
            token_id (int): 토큰 ID
        """
        execute_query(
            "UPDATE user_auth_tokens SET is_active = FALSE WHERE token_id = %s",
            (token_id,)
        )
    
    @staticmethod
    def logout_user(refresh_token: str) -> Dict[str, Any]:
        """
        사용자 로그아웃 처리
        
        Args:
            refresh_token (str): 리프레시 토큰
            
        Returns:
            dict: 로그아웃 결과
        """
        # 리프레시 토큰으로 토큰 ID 조회
        token_data = fetch_one(
            "SELECT token_id FROM user_auth_tokens WHERE refresh_token = %s AND is_active = TRUE",
            (refresh_token,)
        )
        
        if token_data:
            # 토큰 비활성화
            TokenService.deactivate_token(token_data['token_id'])
        
        return {
            'success': True,
            'message': '로그아웃이 완료되었습니다.'
        }
    
    @staticmethod
    def logout_all_devices(user_id: int) -> Dict[str, Any]:
        """
        모든 디바이스에서 로그아웃
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            dict: 로그아웃 결과
        """
        execute_query(
            "UPDATE user_auth_tokens SET is_active = FALSE WHERE user_id = %s AND is_active = TRUE",
            (user_id,)
        )
        
        return {
            'success': True,
            'message': '모든 디바이스에서 로그아웃되었습니다.'
        }
    
    @staticmethod
    def get_active_sessions(user_id: int) -> Dict[str, Any]:
        """
        사용자의 활성 세션 목록 조회
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            dict: 활성 세션 정보
        """
        sessions = fetch_one(
            """
            SELECT 
                token_id, device_info, created_at, expires_at
            FROM user_auth_tokens 
            WHERE user_id = %s AND is_active = TRUE AND expires_at > NOW()
            ORDER BY created_at DESC
            """,
            (user_id,),
            fetch_all=True
        )
        
        return {
            'success': True,
            'data': {
                'active_sessions': sessions or [],
                'total_count': len(sessions) if sessions else 0
            }
        }
    
    @staticmethod
    def verify_access_token(access_token: str) -> Optional[Dict[str, Any]]:
        """
        Access Token 검증 및 사용자 정보 반환
        
        Args:
            access_token (str): Access Token
            
        Returns:
            dict | None: 사용자 정보
        """
        user_info = extract_user_from_token(access_token)
        if not user_info:
            return None
        
        # 사용자가 여전히 존재하는지 확인
        user_exists = fetch_one(
            "SELECT user_id FROM users WHERE user_id = %s",
            (user_info['user_id'],)
        )
        
        if not user_exists:
            return None
        
        return user_info


# 편의를 위한 함수 형태 인터페이스
def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """Access Token 갱신 편의 함수"""
    return TokenService.refresh_access_token(refresh_token)


def logout_user(refresh_token: str) -> Dict[str, Any]:
    """로그아웃 처리 편의 함수"""
    return TokenService.logout_user(refresh_token)


def verify_access_token(access_token: str) -> Optional[Dict[str, Any]]:
    """Access Token 검증 편의 함수"""
    return TokenService.verify_access_token(access_token)