# backend/tests/test_auth_utils.py
# 인증 유틸리티 단위 테스트

import pytest
import os
import time
from unittest.mock import patch
import jwt

from app.utils.auth.password_handler import PasswordHandler
from app.utils.auth.jwt_handler import JWTHandler
from app.utils.common.exceptions import ValidationError, AuthenticationError
from app.utils.common.exceptions import ValidationError, AuthenticationError

class TestPasswordHandler:
    """비밀번호 핸들러 테스트"""
    
    def test_hash_password_success(self):
        """비밀번호 해시화 성공 테스트"""
        password = 'TestPassword123!'
        hashed = PasswordHandler.hash_password(password)
        
        # 해시된 비밀번호는 원본과 달라야 함
        assert hashed != password
        # bcrypt 해시 형식 확인 ($2b$로 시작)
        assert hashed.startswith('$2b$')
        # 길이 확인 (bcrypt는 보통 60자)
        assert len(hashed) == 60
    
    def test_verify_password_success(self):
        """비밀번호 검증 성공 테스트"""
        password = 'TestPassword123!'
        hashed = PasswordHandler.hash_password(password)
        
        # 올바른 비밀번호 검증
        assert PasswordHandler.verify_password(password, hashed) is True
    
    def test_verify_password_failure(self):
        """비밀번호 검증 실패 테스트"""
        password = 'TestPassword123!'
        wrong_password = 'WrongPassword456!'
        hashed = PasswordHandler.hash_password(password)
        
        # 잘못된 비밀번호 검증
        assert PasswordHandler.verify_password(wrong_password, hashed) is False
    
    def test_validate_password_strength_success(self):
        """비밀번호 강도 검증 성공 테스트"""
        strong_passwords = [
            'TestPass123!',
            'MySecure456@',
            'Strong789#Password',
            'Valid123$Pass'
        ]
        
        for password in strong_passwords:
            # 예외가 발생하지 않아야 함
            PasswordHandler.validate_password_strength(password)
    
    def test_validate_password_strength_failures(self):
        """비밀번호 강도 검증 실패 테스트"""
        weak_passwords = [
            ('123', '8자 이상'),  # 너무 짧음
            ('12345678', '영문자'),  # 영문자 없음
            ('abcdefgh', '숫자'),  # 숫자 없음
            ('Test 123!', '공백'),  # 공백 포함
        ]
        
        for password, expected_error in weak_passwords:
            is_valid, errors = PasswordHandler.validate_password_strength(password)
            assert is_valid is False
            assert any(expected_error in error for error in errors)

class TestJWTHandler:
    """JWT 핸들러 테스트"""
    
    def test_generate_tokens_success(self):
        """토큰 생성 성공 테스트"""
        jwt_handler = JWTHandler()
        user_data = {
            'user_id': 1,
            'login_id': 'test_user',
            'user_type': 'beginner'
        }
        
        access_token = jwt_handler.generate_access_token(user_data)
        refresh_token = jwt_handler.generate_refresh_token(user_data['user_id'])
        
        # 토큰이 생성되어야 함
        assert access_token is not None
        assert refresh_token is not None
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        
        # JWT 형식 확인 (3개 부분으로 구성)
        assert len(access_token.split('.')) == 3
        assert len(refresh_token.split('.')) == 3
    
    def test_verify_token_success(self):
        """토큰 검증 성공 테스트"""
        jwt_handler = JWTHandler()
        user_data = {
            'user_id': 1,
            'login_id': 'test_user',
            'user_type': 'beginner'
        }
        
        access_token = jwt_handler.generate_access_token(user_data)
        
        # 토큰 검증
        payload = jwt_handler.decode_token(access_token)
        
        assert payload is not None
        assert payload['user_id'] == 1
        assert payload['login_id'] == 'test_user'
        assert payload['user_type'] == 'beginner'
    
    def test_verify_token_invalid(self):
        """잘못된 토큰 검증 테스트"""
        jwt_handler = JWTHandler()
        invalid_tokens = [
            'invalid_token',
            'invalid.token.format',
            '',
            None
        ]
        
        for token in invalid_tokens:
            payload = jwt_handler.decode_token(token)
            assert payload is None
    
    @patch.dict(os.environ, {
        'JWT_SECRET_KEY': 'test_secret_key',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '0'  # 즉시 만료
    })
    def test_verify_token_expired(self):
        """만료된 토큰 검증 테스트"""
        jwt_handler = JWTHandler()
        user_data = {
            'user_id': 1,
            'login_id': 'test_user',
            'user_type': 'beginner'
        }
        
        access_token = jwt_handler.generate_access_token(user_data)
        
        # 토큰 만료를 위해 잠시 대기
        time.sleep(1)
        
        # 만료된 토큰 검증
        payload = jwt_handler.decode_token(access_token)
        
        assert payload is None
    
    def test_extract_user_info_success(self):
        """사용자 정보 추출 성공 테스트"""
        jwt_handler = JWTHandler()
        user_data = {
            'user_id': 1,
            'login_id': 'test_user',
            'user_type': 'beginner'
        }
        
        access_token = jwt_handler.generate_access_token(user_data)
        
        # 사용자 정보 추출
        extracted_info = jwt_handler.extract_user_from_token(access_token)
        
        assert extracted_info is not None
        assert extracted_info['user_id'] == 1
        assert extracted_info['login_id'] == 'test_user'
        assert extracted_info['user_type'] == 'beginner'
    
    def test_extract_user_info_invalid_token(self):
        """잘못된 토큰에서 사용자 정보 추출 실패 테스트"""
        jwt_handler = JWTHandler()
        invalid_token = 'invalid_token'
        
        extracted_info = jwt_handler.extract_user_from_token(invalid_token)
        
        assert extracted_info is None
    
    def test_token_payload_structure(self):
        """토큰 페이로드 구조 확인 테스트"""
        jwt_handler = JWTHandler()
        user_data = {
            'user_id': 1,
            'login_id': 'test_user',
            'user_type': 'beginner'
        }
        
        access_token = jwt_handler.generate_access_token(user_data)
        refresh_token = jwt_handler.generate_refresh_token(user_data['user_id'])
        
        # Access Token 페이로드 확인
        access_payload = jwt_handler.decode_token(access_token)
        assert 'user_id' in access_payload
        assert 'login_id' in access_payload
        assert 'user_type' in access_payload
        assert 'exp' in access_payload  # 만료 시간
        assert 'iat' in access_payload  # 발급 시간
        assert 'token_type' in access_payload
        assert access_payload['token_type'] == 'access'
        
        # Refresh Token 페이로드 확인
        refresh_payload = jwt_handler.decode_token(refresh_token)
        assert 'user_id' in refresh_payload
        assert 'exp' in refresh_payload
        assert 'iat' in refresh_payload
        assert 'token_type' in refresh_payload
        assert refresh_payload['token_type'] == 'refresh'
    
    def test_different_token_types(self):
        """Access Token과 Refresh Token 구분 테스트"""
        jwt_handler = JWTHandler()
        user_data = {
            'user_id': 1,
            'login_id': 'test_user',
            'user_type': 'beginner'
        }
        
        access_token = jwt_handler.generate_access_token(user_data)
        refresh_token = jwt_handler.generate_refresh_token(user_data['user_id'])
        
        # 토큰들이 서로 달라야 함
        assert access_token != refresh_token
        
        # 각 토큰의 타입 확인
        access_payload = jwt_handler.decode_token(access_token)
        refresh_payload = jwt_handler.decode_token(refresh_token)
        
        assert access_payload['token_type'] == 'access'
        assert refresh_payload['token_type'] == 'refresh'
        
        # Refresh Token의 만료 시간이 더 길어야 함
        assert refresh_payload['exp'] > access_payload['exp']