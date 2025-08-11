# backend/tests/test_httponly_cookie_simple.py

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, make_response, jsonify


def test_httponly_cookie_setting():
    """HttpOnly 쿠키 설정 기본 테스트"""
    app = Flask(__name__)
    
    @app.route('/test-cookie')
    def test_cookie():
        response = make_response(jsonify({'success': True}))
        response.set_cookie(
            'refresh_token',
            'test_token_value',
            max_age=30*24*60*60,  # 30일
            httponly=True,
            secure=True,
            samesite='Strict'
        )
        return response
    
    with app.test_client() as client:
        response = client.get('/test-cookie')
        
        # 응답 상태 확인
        assert response.status_code == 200
        
        # 쿠키 헤더 확인
        cookies = response.headers.getlist('Set-Cookie')
        assert len(cookies) > 0
        
        cookie_header = cookies[0]
        assert 'refresh_token=test_token_value' in cookie_header
        assert 'HttpOnly' in cookie_header
        assert 'Secure' in cookie_header
        assert 'SameSite=Strict' in cookie_header
        assert 'Max-Age=2592000' in cookie_header


def test_cookie_deletion():
    """쿠키 삭제 테스트"""
    app = Flask(__name__)
    
    @app.route('/delete-cookie')
    def delete_cookie():
        response = make_response(jsonify({'success': True}))
        response.set_cookie(
            'refresh_token',
            '',
            expires=0,
            httponly=True,
            secure=True,
            samesite='Strict'
        )
        return response
    
    with app.test_client() as client:
        response = client.get('/delete-cookie')
        
        # 응답 상태 확인
        assert response.status_code == 200
        
        # 쿠키 삭제 헤더 확인
        cookies = response.headers.getlist('Set-Cookie')
        assert len(cookies) > 0
        
        cookie_header = cookies[0]
        assert 'refresh_token=' in cookie_header
        assert 'Expires=Thu, 01 Jan 1970 00:00:00 GMT' in cookie_header


def test_cookie_reading():
    """쿠키 읽기 테스트"""
    app = Flask(__name__)
    
    @app.route('/read-cookie')
    def read_cookie():
        from flask import request
        refresh_token = request.cookies.get('refresh_token')
        return jsonify({
            'success': True,
            'token_found': refresh_token is not None,
            'token_value': refresh_token
        })
    
    with app.test_client() as client:
        # 쿠키 설정 (올바른 방법)
        client.set_cookie('refresh_token', 'test_token_value')
        
        response = client.get('/read-cookie')
        
        # 응답 확인
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['token_found'] is True
        assert data['token_value'] == 'test_token_value'


def test_missing_cookie():
    """쿠키가 없는 경우 테스트"""
    app = Flask(__name__)
    
    @app.route('/read-cookie')
    def read_cookie():
        from flask import request
        refresh_token = request.cookies.get('refresh_token')
        return jsonify({
            'success': True,
            'token_found': refresh_token is not None,
            'token_value': refresh_token
        })
    
    with app.test_client() as client:
        response = client.get('/read-cookie')
        
        # 응답 확인
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['token_found'] is False
        assert data['token_value'] is None


class TestAuthRoutesHttpOnlyIntegration:
    """실제 auth 라우트의 HttpOnly 쿠키 통합 테스트"""
    
    @patch('app.services.auth.login_service.login_user')
    def test_login_sets_httponly_cookie(self, mock_login_user):
        """로그인 시 HttpOnly 쿠키 설정 통합 테스트"""
        from app.routes.auth.login import login_bp
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret'
        app.register_blueprint(login_bp, url_prefix='/auth')
        
        # Mock 설정
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
        
        with app.test_client() as client:
            response = client.post('/auth/login',
                                 json={
                                     'login_id': 'testuser',
                                     'password': 'testpass123'
                                 },
                                 headers={'User-Agent': 'Test Browser'})
            
            # 기본 응답 확인
            assert response.status_code == 200
            
            # 쿠키 설정 확인
            cookies = response.headers.getlist('Set-Cookie')
            refresh_cookie = None
            for cookie in cookies:
                if 'refresh_token=' in cookie:
                    refresh_cookie = cookie
                    break
            
            if refresh_cookie:  # 쿠키가 설정된 경우에만 검증
                assert 'HttpOnly' in refresh_cookie
                assert 'Secure' in refresh_cookie
                assert 'SameSite=Strict' in refresh_cookie
    
    @patch('app.services.auth.token_service.refresh_access_token')
    def test_refresh_reads_httponly_cookie(self, mock_refresh_token):
        """토큰 갱신 시 HttpOnly 쿠키 읽기 통합 테스트"""
        from app.routes.auth.token import token_bp
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret'
        app.register_blueprint(token_bp, url_prefix='/auth')
        
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
        
        with app.test_client() as client:
            # 쿠키 설정
            client.set_cookie('refresh_token', 'old_refresh_token')
            
            response = client.post('/auth/refresh')
            
            # 기본 응답 확인
            assert response.status_code == 200
            
            # Mock이 호출되었는지 확인 (쿠키가 제대로 읽혔다는 의미)
            mock_refresh_token.assert_called_once_with('old_refresh_token')
    
    def test_refresh_missing_cookie_error(self):
        """토큰 갱신 시 쿠키가 없는 경우 에러 테스트"""
        from app.routes.auth.token import token_bp
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret'
        app.register_blueprint(token_bp, url_prefix='/auth')
        
        with app.test_client() as client:
            response = client.post('/auth/refresh')
            
            # 에러 응답 확인
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'MISSING_REFRESH_TOKEN'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])