# backend/tests/test_auth_services.py
# 인증 서비스 단위 테스트

import pytest
from unittest.mock import patch, MagicMock
import bcrypt

from app.services.auth.register_service import RegisterService
from app.services.auth.login_service import LoginService
from app.services.auth.token_service import TokenService
from app.utils.common.exceptions import ValidationError, DuplicateError, AuthenticationError

class TestRegisterService:
    """회원가입 서비스 테스트"""
    
    def test_validate_registration_data_success(self):
        """유효한 회원가입 데이터 검증 성공"""
        valid_data = {
            'login_id': 'test_user',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'name': '테스트사용자',
            'phone': '010-1234-5678'
        }
        
        # 예외가 발생하지 않아야 함
        RegisterService.validate_registration_data(valid_data)
    
    def test_validate_registration_data_failures(self):
        """회원가입 데이터 검증 실패 케이스들"""
        
        # 짧은 login_id
        with pytest.raises(ValidationError) as exc_info:
            RegisterService.validate_registration_data({
                'login_id': 'ab',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'name': '테스트사용자',
                'phone': '010-1234-5678'
            })
        assert 'login_id' in str(exc_info.value)
        
        # 잘못된 이메일 형식
        with pytest.raises(ValidationError) as exc_info:
            RegisterService.validate_registration_data({
                'login_id': 'test_user',
                'email': 'invalid-email',
                'password': 'TestPass123!',
                'name': '테스트사용자',
                'phone': '010-1234-5678'
            })
        assert 'email' in str(exc_info.value)
        
        # 약한 비밀번호
        with pytest.raises(ValidationError) as exc_info:
            RegisterService.validate_registration_data({
                'login_id': 'test_user',
                'email': 'test@example.com',
                'password': '123',
                'name': '테스트사용자',
                'phone': '010-1234-5678'
            })
        assert 'password' in str(exc_info.value)
    
    @patch('app.services.auth.register_service.execute_query')
    def test_check_duplicates_no_duplicates(self, mock_execute_query):
        """중복 없음 확인 테스트"""
        # 중복 없음을 시뮬레이션
        mock_execute_query.return_value = []
        
        # 예외가 발생하지 않아야 함
        RegisterService.check_duplicates('test_user', 'test@example.com')
        
        # 쿼리가 두 번 호출되어야 함 (login_id, email 각각)
        assert mock_execute_query.call_count == 2
    
    @patch('app.services.auth.register_service.execute_query')
    def test_check_duplicates_login_id_exists(self, mock_execute_query):
        """login_id 중복 확인 테스트"""
        # login_id 중복 시뮬레이션
        mock_execute_query.side_effect = [
            [{'login_id': 'test_user'}],  # login_id 중복
            []  # email 중복 없음
        ]
        
        with pytest.raises(DuplicateError) as exc_info:
            RegisterService.check_duplicates('test_user', 'test@example.com')
        
        assert 'login_id' in str(exc_info.value)
    
    @patch('app.services.auth.register_service.execute_query')
    def test_check_duplicates_email_exists(self, mock_execute_query):
        """이메일 중복 확인 테스트"""
        # 이메일 중복 시뮬레이션
        mock_execute_query.side_effect = [
            [],  # login_id 중복 없음
            [{'email': 'test@example.com'}]  # email 중복
        ]
        
        with pytest.raises(DuplicateError) as exc_info:
            RegisterService.check_duplicates('test_user', 'test@example.com')
        
        assert 'email' in str(exc_info.value)

class TestLoginService:
    """로그인 서비스 테스트"""
    
    @patch('app.services.auth.login_service.execute_query')
    def test_authenticate_user_success(self, mock_execute_query):
        """사용자 인증 성공 테스트"""
        # 비밀번호 해시 생성
        password = 'TestPass123!'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # DB에서 사용자 정보 반환 시뮬레이션
        mock_execute_query.return_value = [{
            'user_id': 1,
            'login_id': 'test_user',
            'password_hash': hashed_password.decode('utf-8'),
            'user_type': 'beginner',
            'name': '테스트사용자',
            'email': 'test@example.com',
            'current_chapter_id': 1
        }]
        
        result = LoginService.authenticate_user('test_user', password)
        
        assert result is not None
        assert result['user_id'] == 1
        assert result['login_id'] == 'test_user'
        assert result['user_type'] == 'beginner'
    
    @patch('app.services.auth.login_service.execute_query')
    def test_authenticate_user_not_found(self, mock_execute_query):
        """존재하지 않는 사용자 인증 실패 테스트"""
        # 사용자 없음 시뮬레이션
        mock_execute_query.return_value = []
        
        with pytest.raises(AuthenticationError) as exc_info:
            LoginService.authenticate_user('nonexistent_user', 'password')
        
        assert '로그인 정보가 올바르지 않습니다' in str(exc_info.value)
    
    @patch('app.services.auth.login_service.execute_query')
    def test_authenticate_user_wrong_password(self, mock_execute_query):
        """잘못된 비밀번호 인증 실패 테스트"""
        # 올바른 비밀번호로 해시 생성
        correct_password = 'TestPass123!'
        hashed_password = bcrypt.hashpw(correct_password.encode('utf-8'), bcrypt.gensalt())
        
        # DB에서 사용자 정보 반환 시뮬레이션
        mock_execute_query.return_value = [{
            'user_id': 1,
            'login_id': 'test_user',
            'password_hash': hashed_password.decode('utf-8'),
            'user_type': 'beginner',
            'name': '테스트사용자',
            'email': 'test@example.com',
            'current_chapter_id': 1
        }]
        
        # 잘못된 비밀번호로 인증 시도
        with pytest.raises(AuthenticationError) as exc_info:
            LoginService.authenticate_user('test_user', 'wrong_password')
        
        assert '로그인 정보가 올바르지 않습니다' in str(exc_info.value)

class TestTokenService:
    """토큰 서비스 테스트"""
    
    @patch('app.services.auth.token_service.execute_query')
    def test_get_active_tokens_success(self, mock_execute_query):
        """활성 토큰 조회 성공 테스트"""
        # 활성 토큰 시뮬레이션
        mock_execute_query.return_value = [
            {
                'token_id': 1,
                'access_token': 'access_token_1',
                'refresh_token': 'refresh_token_1',
                'device_info': 'Chrome/Windows',
                'created_at': '2025-08-08 10:00:00',
                'expires_at': '2025-08-08 11:00:00'
            }
        ]
        
        result = TokenService.get_active_tokens(1)
        
        assert len(result) == 1
        assert result[0]['token_id'] == 1
        assert result[0]['access_token'] == 'access_token_1'
    
    @patch('app.services.auth.token_service.execute_query')
    def test_get_active_tokens_empty(self, mock_execute_query):
        """활성 토큰 없음 테스트"""
        # 활성 토큰 없음 시뮬레이션
        mock_execute_query.return_value = []
        
        result = TokenService.get_active_tokens(1)
        
        assert result == []
    
    @patch('app.services.auth.token_service.execute_transaction')
    def test_revoke_token_success(self, mock_execute_transaction):
        """토큰 무효화 성공 테스트"""
        # 트랜잭션 성공 시뮬레이션
        mock_execute_transaction.return_value = True
        
        result = TokenService.revoke_token(1, 1)
        
        assert result is True
        mock_execute_transaction.assert_called_once()
    
    @patch('app.services.auth.token_service.execute_transaction')
    def test_revoke_all_tokens_success(self, mock_execute_transaction):
        """모든 토큰 무효화 성공 테스트"""
        # 트랜잭션 성공 시뮬레이션
        mock_execute_transaction.return_value = True
        
        result = TokenService.revoke_all_tokens(1)
        
        assert result is True
        mock_execute_transaction.assert_called_once()
    
    @patch('app.services.auth.token_service.execute_query')
    def test_find_token_by_refresh_token_success(self, mock_execute_query):
        """Refresh Token으로 토큰 찾기 성공 테스트"""
        # 토큰 정보 시뮬레이션
        mock_execute_query.return_value = [{
            'token_id': 1,
            'user_id': 1,
            'access_token': 'access_token_1',
            'refresh_token': 'refresh_token_1',
            'expires_at': '2025-08-08 11:00:00'
        }]
        
        result = TokenService.find_token_by_refresh_token('refresh_token_1')
        
        assert result is not None
        assert result['token_id'] == 1
        assert result['user_id'] == 1
    
    @patch('app.services.auth.token_service.execute_query')
    def test_find_token_by_refresh_token_not_found(self, mock_execute_query):
        """Refresh Token으로 토큰 찾기 실패 테스트"""
        # 토큰 없음 시뮬레이션
        mock_execute_query.return_value = []
        
        result = TokenService.find_token_by_refresh_token('nonexistent_token')
        
        assert result is None