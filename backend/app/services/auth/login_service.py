# app/services/auth/login_service.py

from typing import Dict, Any, Optional
from datetime import datetime

from app.utils.database.connection import fetch_one, execute_query
from app.utils.auth.password_handler import verify_password
from app.utils.auth.jwt_handler import generate_access_token, generate_refresh_token
from app.utils.common.exceptions import ValidationError, AuthenticationError


class LoginService:
    """로그인 관련 비즈니스 로직을 처리하는 서비스"""
    
    @staticmethod
    def validate_login_data(data: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """
        로그인 데이터 검증
        
        Args:
            data (dict): 로그인 데이터
                - login_id: 로그인 ID
                - password: 비밀번호
                
        Returns:
            tuple: (유효성 여부, 에러 정보 또는 정제된 데이터)
        """
        errors = {}
        
        # 필수 필드 검증
        if not data.get('login_id') or not str(data['login_id']).strip():
            errors['login_id'] = "로그인 ID를 입력해주세요."
        
        if not data.get('password'):
            errors['password'] = "비밀번호를 입력해주세요."
        
        if errors:
            return False, {'field_errors': errors}
        
        return True, {
            'login_id': str(data['login_id']).strip(),
            'password': str(data['password'])
        }
    
    @staticmethod
    def authenticate_user(login_id: str, password: str) -> Optional[Dict[str, Any]]:
        """
        사용자 인증
        
        Args:
            login_id (str): 로그인 ID
            password (str): 비밀번호
            
        Returns:
            dict | None: 인증된 사용자 정보 또는 None
        """
        # 사용자 정보 조회 (진행 상태 포함)
        user_data = fetch_one(
            """
            SELECT 
                u.user_id, u.login_id, u.username, u.email,
                u.password_hash, u.user_type, u.diagnosis_completed,
                up.current_chapter
            FROM users u
            LEFT JOIN user_progress up ON u.user_id = up.user_id
            WHERE u.login_id = %s
            """,
            (login_id,)
        )
        
        if not user_data:
            return None
        
        # 비밀번호 검증
        if not verify_password(password, user_data['password_hash']):
            return None
        
        # 인증 성공 시 사용자 정보 반환 (비밀번호 해시 제외)
        return {
            'user_id': user_data['user_id'],
            'login_id': user_data['login_id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'user_type': user_data['user_type'],
            'diagnosis_completed': bool(user_data['diagnosis_completed']),
            'current_chapter': user_data['current_chapter'] or 1
        }
    
    @staticmethod
    def invalidate_existing_tokens(user_id: int) -> None:
        """
        기존 활성 토큰들을 무효화 (단일 세션 정책)
        
        Args:
            user_id (int): 사용자 ID
        """
        execute_query(
            "UPDATE user_auth_tokens SET is_active = FALSE WHERE user_id = %s AND is_active = TRUE",
            (user_id,)
        )
    
    @staticmethod
    def save_refresh_token(user_id: int, refresh_token: str, device_info: Optional[str] = None) -> None:
        """
        리프레시 토큰을 데이터베이스에 저장
        
        Args:
            user_id (int): 사용자 ID
            refresh_token (str): 리프레시 토큰
            device_info (str, optional): 디바이스 정보
        """
        from datetime import datetime, timedelta
        
        expires_at = datetime.utcnow() + timedelta(days=30)  # 30일 후 만료
        
        execute_query(
            """
            INSERT INTO user_auth_tokens (user_id, refresh_token, expires_at, device_info)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, refresh_token, expires_at, device_info)
        )
    
    @staticmethod
    def generate_tokens(user_info: Dict[str, Any]) -> Dict[str, str]:
        """
        JWT 토큰 생성
        
        Args:
            user_info (dict): 사용자 정보
            
        Returns:
            dict: 생성된 토큰들
        """
        # Access Token 생성용 데이터
        token_data = {
            'user_id': user_info['user_id'],
            'login_id': user_info['login_id'],
            'user_type': user_info['user_type']
        }
        
        access_token = generate_access_token(token_data)
        refresh_token = generate_refresh_token(user_info['user_id'])
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    @staticmethod
    def update_last_login(user_id: int) -> None:
        """
        마지막 로그인 시간 업데이트
        
        Args:
            user_id (int): 사용자 ID
        """
        execute_query(
            "UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
            (user_id,)
        )
    
    @staticmethod
    def login_user(login_data: Dict[str, Any], device_info: Optional[str] = None) -> Dict[str, Any]:
        """
        로그인 전체 프로세스 처리
        
        Args:
            login_data (dict): 로그인 요청 데이터
            device_info (str, optional): 디바이스 정보
            
        Returns:
            dict: 로그인 결과
            
        Raises:
            ValidationError: 입력값 검증 실패
            AuthenticationError: 인증 실패
        """
        # 1. 입력값 검증
        is_valid, validation_result = LoginService.validate_login_data(login_data)
        if not is_valid:
            raise ValidationError("입력값이 올바르지 않습니다.", validation_result)
        
        validated_data = validation_result
        
        # 2. 사용자 인증
        user_info = LoginService.authenticate_user(
            validated_data['login_id'],
            validated_data['password']
        )
        
        if not user_info:
            raise AuthenticationError("로그인 정보가 올바르지 않습니다.")
        
        # 3. 기존 토큰 무효화 (단일 세션 정책)
        LoginService.invalidate_existing_tokens(user_info['user_id'])
        
        # 4. 새 토큰 생성
        tokens = LoginService.generate_tokens(user_info)
        
        # 5. 리프레시 토큰 저장
        LoginService.save_refresh_token(
            user_info['user_id'], 
            tokens['refresh_token'],
            device_info
        )
        
        # 6. 마지막 로그인 시간 업데이트
        LoginService.update_last_login(user_info['user_id'])
        
        return {
            'success': True,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'user_info': user_info,
            'message': '로그인이 완료되었습니다.'
        }


# 편의를 위한 함수 형태 인터페이스
def login_user(login_data: Dict[str, Any], device_info: Optional[str] = None) -> Dict[str, Any]:
    """로그인 처리 편의 함수"""
    return LoginService.login_user(login_data, device_info)