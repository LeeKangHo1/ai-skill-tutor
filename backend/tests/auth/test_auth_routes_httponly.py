# backend/tests/test_auth_routes_httponly.py

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.auth.login import login_bp
from app.routes.auth.register import register_bp
from app.routes.auth.token import token_bp


@pytest.fixture
def test_app():
    """테스트용 Flask 앱 생성"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Blueprint 등록
    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(register_bp, url_prefix='/auth')
    app.register_blueprint(token_bp, url_prefix='/auth')
    
    return app


@pytest.fixture
def client(test_app):
    """테스트 클라이언트 생성"""
    return test_app.test_client()


def set_cookie_helper(client, name, value):
    """쿠키 설정 헬퍼 함수"""
    with client.session_transaction() as sess:
        client.set_cookie('localhost', name, value)


class TestLoginRoutes:
    """로그인 관련 라우트 테스트"""
    
    @patch('app.routes.auth.login.login_user')
    @patch('app.utils.response.formatter.success_response')
    def test_login_success_with_httponly_cookie(self, mock_success_response, mock_login_user, client):
        """로그인 성공 시 HttpOnly 쿠키 설정 테스트"""
        # Mock 데이터 설정
        mock_login_user.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'user_info': {
                'user_id': 1,
                'login_id': 'testuser',
                'username': '테스트유저',
                'user_type': 'beginner',
                'diagnosis_completed': True,
                'current_chapter': 1
            },
            'message': '로그인이 완료되었습니다.'
        }
        
        # Mock response 객체 생성
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.data = json.dumps({
            'success': True,
            'data': {
                'access_token': 'test_access_token',
                'user_info': {
                    'user_id': 1,
                    'login_id': 'testuser',
                    'username': '테스트유저',
                    'user_type': 'beginner',
                    'diagnosis_completed': True,
                    'current_chapter': 1
                }
            }
        })
        mock_response.headers = {'Set-Cookie': 'refresh_token=test_refresh_token; HttpOnly; Secure; SameSite=Strict; Max-Age=2592000'}
        mock_success_response.return_value = mock_response
        
        # 로그인 요청
        response = client.post('/auth/login', 
                             json={
                                 'login_id': 'testuser',
                                 'password': 'testpass123'
                             },
                             headers={'User-Agent': 'Test Browser'})
        
        # 응답 검증
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['user_info']['login_id'] == 'testuser'
    
    def test_login_invalid_content_type(self, client):
        """잘못된 Content-Type 테스트"""
        response = client.post('/auth/login', 
                             data='invalid data',
                             content_type='text/plain')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'INVALID_CONTENT_TYPE'
    
    def test_login_empty_request_body(self, client):
        """빈 요청 본문 테스트"""
        response = client.post('/auth/login', 
                             data='',
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'EMPTY_REQUEST_BODY'
    
    @patch('app.routes.auth.login.logout_user')
    @patch('app.routes.auth.login.get_current_user_from_request')
    @patch('app.routes.auth.login.require_auth')
    def test_logout_with_httponly_cookie(self, mock_require_auth, mock_get_user, mock_logout_user, client):
        """HttpOnly 쿠키를 사용한 로그아웃 테스트"""
        # Mock 설정
        mock_require_auth.return_value = lambda f: f  # 데코레이터 우회
        mock_get_user.return_value = {'user_id': 1, 'login_id': 'testuser'}
        mock_logout_user.return_value = {'message': '로그아웃이 완료되었습니다.'}
        
        # 쿠키와 함께 로그아웃 요청
        client.set_cookie('refresh_token', 'test_refresh_token')
        response = client.post('/auth/logout',
                             headers={'Authorization': 'Bearer test_access_token'})
        
        # 응답 검증
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    @patch('app.routes.auth.login.get_current_user_from_request')
    @patch('app.routes.auth.login.require_auth')
    def test_logout_missing_refresh_token_cookie(self, mock_require_auth, mock_get_user, client):
        """refresh_token 쿠키가 없는 경우 테스트"""
        mock_require_auth.return_value = lambda f: f  # 데코레이터 우회
        mock_get_user.return_value = {'user_id': 1, 'login_id': 'testuser'}
        
        response = client.post('/auth/logout',
                             headers={'Authorization': 'Bearer test_access_token'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'MISSING_REFRESH_TOKEN'


class TestRegisterRoutes:
    """회원가입 관련 라우트 테스트"""
    
    @patch('app.routes.auth.register.register_user')
    @patch('app.utils.auth.jwt_handler.generate_access_token')
    @patch('app.utils.auth.jwt_handler.generate_refresh_token')
    @patch('app.services.auth.token_service.TokenService.save_refresh_token')
    def test_register_success_with_httponly_cookie(self, mock_save_token, mock_gen_refresh, 
                                                  mock_gen_access, mock_register_user, client):
        """회원가입 성공 시 HttpOnly 쿠키 설정 테스트"""
        # Mock 설정
        mock_register_user.return_value = {
            'user_info': {
                'user_id': 1,
                'login_id': 'newuser',
                'username': '신규유저',
                'user_type': 'beginner',
                'diagnosis_completed': False
            },
            'message': '회원가입이 완료되었습니다.'
        }
        mock_gen_access.return_value = 'test_access_token'
        mock_gen_refresh.return_value = 'test_refresh_token'
        
        # 회원가입 요청
        response = client.post('/auth/register',
                             json={
                                 'login_id': 'newuser',
                                 'username': '신규유저',
                                 'email': 'newuser@test.com',
                                 'password': 'newpass123'
                             },
                             headers={'User-Agent': 'Test Browser'})
        
        # 응답 검증
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['login_id'] == 'newuser'
        
        # HttpOnly 쿠키 검증
        cookies = response.headers.getlist('Set-Cookie')
        refresh_cookie = None
        for cookie in cookies:
            if 'refresh_token=' in cookie:
                refresh_cookie = cookie
                break
        
        assert refresh_cookie is not None
        assert 'HttpOnly' in refresh_cookie
        assert 'Secure' in refresh_cookie
        assert 'SameSite=Strict' in refresh_cookie
    
    def test_register_invalid_content_type(self, client):
        """잘못된 Content-Type 테스트"""
        response = client.post('/auth/register',
                             data='invalid data',
                             content_type='text/plain')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'INVALID_CONTENT_TYPE'
    
    @patch('app.services.auth.register_service.RegisterService.check_duplicates')
    def test_check_availability_login_id(self, mock_check_duplicates, client):
        """로그인 ID 사용 가능 여부 확인 테스트"""
        mock_check_duplicates.return_value = {}  # 중복 없음
        
        response = client.post('/auth/check-availability',
                             json={'login_id': 'testuser'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['login_id']['available'] is True
    
    @patch('app.services.auth.register_service.RegisterService.check_duplicates')
    def test_check_availability_duplicate_email(self, mock_check_duplicates, client):
        """이메일 중복 확인 테스트"""
        mock_check_duplicates.return_value = {
            'email': '이미 사용 중인 이메일입니다.'
        }
        
        response = client.post('/auth/check-availability',
                             json={'email': 'duplicate@test.com'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['email']['available'] is False


class TestTokenRoutes:
    """토큰 관련 라우트 테스트"""
    
    @patch('app.routes.auth.token.refresh_access_token')
    def test_refresh_token_with_httponly_cookie(self, mock_refresh_token, client):
        """HttpOnly 쿠키를 사용한 토큰 갱신 테스트"""
        # Mock 설정
        mock_refresh_token.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'user_info': {
                'user_id': 1,
                'login_id': 'testuser',
                'username': '테스트유저',
                'user_type': 'beginner',
                'diagnosis_completed': True,
                'current_chapter': 1
            },
            'message': '토큰이 갱신되었습니다.'
        }
        
        # 쿠키와 함께 토큰 갱신 요청
        client.set_cookie('refresh_token', 'old_refresh_token')
        response = client.post('/auth/refresh')
        
        # 응답 검증
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['access_token'] == 'new_access_token'
        assert data['data']['user_info']['login_id'] == 'testuser'
    
    def test_refresh_token_missing_cookie(self, client):
        """refresh_token 쿠키가 없는 경우 테스트"""
        response = client.post('/auth/refresh')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'MISSING_REFRESH_TOKEN'
    
    @patch('app.services.auth.token_service.TokenService.verify_access_token')
    def test_verify_token_success(self, mock_verify_token, client):
        """토큰 검증 성공 테스트"""
        mock_verify_token.return_value = {
            'user_id': 1,
            'login_id': 'testuser',
            'user_type': 'beginner'
        }
        
        response = client.post('/auth/verify',
                             json={'access_token': 'valid_access_token'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['valid'] is True
        assert data['data']['user_info']['login_id'] == 'testuser'
    
    @patch('app.services.auth.token_service.TokenService.verify_access_token')
    def test_verify_token_invalid(self, mock_verify_token, client):
        """토큰 검증 실패 테스트"""
        mock_verify_token.return_value = None
        
        response = client.post('/auth/verify',
                             json={'access_token': 'invalid_access_token'})
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_TOKEN_INVALID'
    
    def test_verify_token_missing_access_token(self, client):
        """access_token이 없는 경우 테스트"""
        response = client.post('/auth/verify', json={'other_field': 'value'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'MISSING_ACCESS_TOKEN'
    
    @patch('app.routes.auth.token.get_current_user_from_request')
    @patch('app.services.auth.token_service.TokenService.get_active_sessions')
    @patch('app.routes.auth.token.require_auth')
    def test_get_sessions_success(self, mock_require_auth, mock_get_sessions, mock_get_user, client):
        """활성 세션 목록 조회 테스트"""
        from datetime import datetime
        
        mock_require_auth.return_value = lambda f: f  # 데코레이터 우회
        mock_get_user.return_value = {'user_id': 1, 'login_id': 'testuser'}
        mock_get_sessions.return_value = {
            'data': {
                'active_sessions': [
                    {
                        'token_id': 1,
                        'device_info': 'Test Browser',
                        'created_at': datetime(2024, 1, 1, 12, 0, 0),
                        'expires_at': datetime(2024, 1, 31, 12, 0, 0)
                    }
                ],
                'total_count': 1
            }
        }
        
        response = client.get('/auth/sessions',
                            headers={'Authorization': 'Bearer test_access_token'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']['active_sessions']) == 1
        assert data['data']['total_count'] == 1
    
    @patch('app.routes.auth.token.get_current_user_from_request')
    @patch('app.utils.database.connection.fetch_one')
    @patch('app.services.auth.token_service.TokenService.deactivate_token')
    @patch('app.routes.auth.token.require_auth')
    def test_revoke_session_success(self, mock_require_auth, mock_deactivate, mock_fetch_one, mock_get_user, client):
        """특정 세션 무효화 테스트"""
        mock_require_auth.return_value = lambda f: f  # 데코레이터 우회
        mock_get_user.return_value = {'user_id': 1, 'login_id': 'testuser'}
        mock_fetch_one.return_value = {'user_id': 1}
        
        response = client.delete('/auth/revoke/1',
                               headers={'Authorization': 'Bearer test_access_token'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        mock_deactivate.assert_called_once_with(1)
    
    @patch('app.routes.auth.token.get_current_user_from_request')
    @patch('app.utils.database.connection.fetch_one')
    @patch('app.routes.auth.token.require_auth')
    def test_revoke_session_not_found(self, mock_require_auth, mock_fetch_one, mock_get_user, client):
        """존재하지 않는 세션 무효화 테스트"""
        mock_require_auth.return_value = lambda f: f  # 데코레이터 우회
        mock_get_user.return_value = {'user_id': 1, 'login_id': 'testuser'}
        mock_fetch_one.return_value = None
        
        response = client.delete('/auth/revoke/999',
                               headers={'Authorization': 'Bearer test_access_token'})
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SESSION_NOT_FOUND'
    
    @patch('app.routes.auth.token.get_current_user_from_request')
    @patch('app.utils.database.connection.fetch_one')
    @patch('app.routes.auth.token.require_auth')
    def test_revoke_session_access_denied(self, mock_require_auth, mock_fetch_one, mock_get_user, client):
        """다른 사용자의 세션 무효화 시도 테스트"""
        mock_require_auth.return_value = lambda f: f  # 데코레이터 우회
        mock_get_user.return_value = {'user_id': 1, 'login_id': 'testuser'}
        mock_fetch_one.return_value = {'user_id': 2}  # 다른 사용자의 토큰
        
        response = client.delete('/auth/revoke/1',
                               headers={'Authorization': 'Bearer test_access_token'})
        
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'ACCESS_DENIED'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])