# backend/tests/test_auth_integration.py
# 인증 시스템 통합 테스트

import pytest
import json
import time
from unittest.mock import patch

class TestAuthIntegration:
    """인증 시스템 통합 테스트 클래스"""
    
    def test_complete_auth_flow(self, client, clean_database, sample_user_data, auth_headers):
        """완전한 인증 플로우 테스트: 회원가입 → 로그인 → 토큰 사용 → 로그아웃"""
        
        # 1. 회원가입
        register_response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        
        assert register_response.status_code == 201
        register_data = json.loads(register_response.data)
        assert register_data['success'] is True
        assert 'access_token' in register_data['data']
        assert 'refresh_token' in register_data['data']
        
        # 2. 로그인
        login_data = {
            'login_id': sample_user_data['login_id'],
            'password': sample_user_data['password']
        }
        
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert login_response.status_code == 200
        login_result = json.loads(login_response.data)
        assert login_result['success'] is True
        
        access_token = login_result['data']['access_token']
        refresh_token = login_result['data']['refresh_token']
        
        # 3. 인증이 필요한 엔드포인트 접근
        me_response = client.get(
            '/api/v1/auth/me',
            headers=auth_headers(access_token)
        )
        
        assert me_response.status_code == 200
        me_data = json.loads(me_response.data)
        assert me_data['success'] is True
        assert me_data['data']['login_id'] == sample_user_data['login_id']
        
        # 4. 토큰 갱신
        refresh_response = client.post(
            '/api/v1/auth/refresh',
            data=json.dumps({'refresh_token': refresh_token}),
            content_type='application/json'
        )
        
        assert refresh_response.status_code == 200
        refresh_result = json.loads(refresh_response.data)
        assert refresh_result['success'] is True
        assert 'access_token' in refresh_result['data']
        
        # 5. 로그아웃
        logout_response = client.post(
            '/api/v1/auth/logout',
            headers=auth_headers(access_token)
        )
        
        assert logout_response.status_code == 200
        logout_data = json.loads(logout_response.data)
        assert logout_data['success'] is True
        
        # 6. 로그아웃 후 인증 확인 (실패해야 함)
        me_after_logout = client.get(
            '/api/v1/auth/me',
            headers=auth_headers(access_token)
        )
        
        assert me_after_logout.status_code == 401
    
    def test_duplicate_registration_prevention(self, client, clean_database, sample_user_data):
        """중복 회원가입 방지 테스트"""
        
        # 첫 번째 회원가입 (성공)
        first_register = client.post(
            '/api/v1/auth/register',
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        
        assert first_register.status_code == 201
        
        # 동일한 login_id로 두 번째 회원가입 시도 (실패)
        second_register = client.post(
            '/api/v1/auth/register',
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        
        assert second_register.status_code == 409
        second_data = json.loads(second_register.data)
        assert second_data['success'] is False
        assert 'login_id' in second_data['message']
        
        # 동일한 이메일로 다른 login_id 회원가입 시도 (실패)
        duplicate_email_data = sample_user_data.copy()
        duplicate_email_data['login_id'] = 'different_login_id'
        
        third_register = client.post(
            '/api/v1/auth/register',
            data=json.dumps(duplicate_email_data),
            content_type='application/json'
        )
        
        assert third_register.status_code == 409
        third_data = json.loads(third_register.data)
        assert third_data['success'] is False
        assert 'email' in third_data['message']
    
    def test_availability_check(self, client, clean_database, sample_user_data):
        """중복 확인 API 테스트"""
        
        # 사용자 등록
        client.post(
            '/api/v1/auth/register',
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        
        # 기존 login_id 중복 확인 (사용 불가)
        check_login_id = client.post(
            '/api/v1/auth/check-availability',
            data=json.dumps({
                'type': 'login_id',
                'value': sample_user_data['login_id']
            }),
            content_type='application/json'
        )
        
        assert check_login_id.status_code == 200
        login_id_data = json.loads(check_login_id.data)
        assert login_id_data['data']['available'] is False
        
        # 새로운 login_id 중복 확인 (사용 가능)
        check_new_login_id = client.post(
            '/api/v1/auth/check-availability',
            data=json.dumps({
                'type': 'login_id',
                'value': 'new_unique_login_id'
            }),
            content_type='application/json'
        )
        
        assert check_new_login_id.status_code == 200
        new_login_id_data = json.loads(check_new_login_id.data)
        assert new_login_id_data['data']['available'] is True
        
        # 기존 이메일 중복 확인 (사용 불가)
        check_email = client.post(
            '/api/v1/auth/check-availability',
            data=json.dumps({
                'type': 'email',
                'value': sample_user_data['email']
            }),
            content_type='application/json'
        )
        
        assert check_email.status_code == 200
        email_data = json.loads(check_email.data)
        assert email_data['data']['available'] is False
    
    def test_invalid_login_attempts(self, client, clean_database, sample_user_data):
        """잘못된 로그인 시도 테스트"""
        
        # 사용자 등록
        client.post(
            '/api/v1/auth/register',
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        
        # 잘못된 비밀번호로 로그인 시도
        wrong_password_login = client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'login_id': sample_user_data['login_id'],
                'password': 'wrong_password'
            }),
            content_type='application/json'
        )
        
        assert wrong_password_login.status_code == 401
        wrong_password_data = json.loads(wrong_password_login.data)
        assert wrong_password_data['success'] is False
        
        # 존재하지 않는 사용자로 로그인 시도
        nonexistent_user_login = client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'login_id': 'nonexistent_user',
                'password': 'any_password'
            }),
            content_type='application/json'
        )
        
        assert nonexistent_user_login.status_code == 401
        nonexistent_data = json.loads(nonexistent_user_login.data)
        assert nonexistent_data['success'] is False
    
    def test_token_validation_and_refresh(self, client, clean_database, sample_user_data, auth_headers):
        """토큰 검증 및 갱신 테스트"""
        
        # 사용자 등록 및 로그인
        client.post('/api/v1/auth/register', 
                   data=json.dumps(sample_user_data), 
                   content_type='application/json')
        
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'login_id': sample_user_data['login_id'],
                'password': sample_user_data['password']
            }),
            content_type='application/json'
        )
        
        login_data = json.loads(login_response.data)
        access_token = login_data['data']['access_token']
        refresh_token = login_data['data']['refresh_token']
        
        # 토큰 검증
        verify_response = client.post(
            '/api/v1/auth/verify',
            data=json.dumps({'token': access_token}),
            content_type='application/json'
        )
        
        assert verify_response.status_code == 200
        verify_data = json.loads(verify_response.data)
        assert verify_data['success'] is True
        assert verify_data['data']['valid'] is True
        
        # 잘못된 토큰 검증
        invalid_verify = client.post(
            '/api/v1/auth/verify',
            data=json.dumps({'token': 'invalid_token'}),
            content_type='application/json'
        )
        
        assert invalid_verify.status_code == 200
        invalid_data = json.loads(invalid_verify.data)
        assert invalid_data['data']['valid'] is False
        
        # 토큰 갱신
        refresh_response = client.post(
            '/api/v1/auth/refresh',
            data=json.dumps({'refresh_token': refresh_token}),
            content_type='application/json'
        )
        
        assert refresh_response.status_code == 200
        refresh_data = json.loads(refresh_response.data)
        assert refresh_data['success'] is True
        assert 'access_token' in refresh_data['data']
        
        # 새 토큰으로 인증 확인
        new_access_token = refresh_data['data']['access_token']
        me_response = client.get(
            '/api/v1/auth/me',
            headers=auth_headers(new_access_token)
        )
        
        assert me_response.status_code == 200
    
    def test_session_management(self, client, clean_database, sample_user_data, auth_headers):
        """세션 관리 테스트"""
        
        # 사용자 등록
        client.post('/api/v1/auth/register', 
                   data=json.dumps(sample_user_data), 
                   content_type='application/json')
        
        # 첫 번째 로그인
        login1_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'login_id': sample_user_data['login_id'],
                'password': sample_user_data['password']
            }),
            content_type='application/json'
        )
        
        login1_data = json.loads(login1_response.data)
        access_token1 = login1_data['data']['access_token']
        
        # 두 번째 로그인 (다른 디바이스 시뮬레이션)
        login2_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'login_id': sample_user_data['login_id'],
                'password': sample_user_data['password']
            }),
            content_type='application/json'
        )
        
        login2_data = json.loads(login2_response.data)
        access_token2 = login2_data['data']['access_token']
        
        # 활성 세션 목록 조회
        sessions_response = client.get(
            '/api/v1/auth/sessions',
            headers=auth_headers(access_token2)
        )
        
        assert sessions_response.status_code == 200
        sessions_data = json.loads(sessions_response.data)
        assert sessions_data['success'] is True
        # 단일 세션 정책으로 인해 최신 세션만 활성화
        assert len(sessions_data['data']) == 1
        
        # 첫 번째 토큰은 무효화되어야 함
        me_with_old_token = client.get(
            '/api/v1/auth/me',
            headers=auth_headers(access_token1)
        )
        
        assert me_with_old_token.status_code == 401
        
        # 두 번째 토큰은 유효해야 함
        me_with_new_token = client.get(
            '/api/v1/auth/me',
            headers=auth_headers(access_token2)
        )
        
        assert me_with_new_token.status_code == 200
    
    def test_logout_all_devices(self, client, clean_database, sample_user_data, auth_headers):
        """모든 디바이스 로그아웃 테스트"""
        
        # 사용자 등록 및 로그인
        client.post('/api/v1/auth/register', 
                   data=json.dumps(sample_user_data), 
                   content_type='application/json')
        
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'login_id': sample_user_data['login_id'],
                'password': sample_user_data['password']
            }),
            content_type='application/json'
        )
        
        login_data = json.loads(login_response.data)
        access_token = login_data['data']['access_token']
        
        # 모든 디바이스에서 로그아웃
        logout_all_response = client.post(
            '/api/v1/auth/logout-all',
            headers=auth_headers(access_token)
        )
        
        assert logout_all_response.status_code == 200
        logout_all_data = json.loads(logout_all_response.data)
        assert logout_all_data['success'] is True
        
        # 로그아웃 후 토큰 사용 불가 확인
        me_after_logout_all = client.get(
            '/api/v1/auth/me',
            headers=auth_headers(access_token)
        )
        
        assert me_after_logout_all.status_code == 401
    
    def test_validation_errors(self, client, clean_database, invalid_user_data):
        """입력값 검증 오류 테스트"""
        
        # 잘못된 데이터로 회원가입 시도
        register_response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(invalid_user_data),
            content_type='application/json'
        )
        
        assert register_response.status_code == 400
        register_data = json.loads(register_response.data)
        assert register_data['success'] is False
        assert 'details' in register_data
        
        # 검증 오류 세부사항 확인
        details = register_data['details']
        assert 'login_id' in details
        assert 'email' in details
        assert 'password' in details
        assert 'name' in details
        assert 'phone' in details
    
    def test_unauthorized_access(self, client, clean_database):
        """인증 없이 보호된 엔드포인트 접근 테스트"""
        
        # 토큰 없이 /me 엔드포인트 접근
        me_response = client.get('/api/v1/auth/me')
        assert me_response.status_code == 401
        
        # 잘못된 토큰으로 접근
        invalid_headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        
        me_with_invalid_token = client.get(
            '/api/v1/auth/me',
            headers=invalid_headers
        )
        assert me_with_invalid_token.status_code == 401
        
        # Authorization 헤더 형식 오류
        malformed_headers = {
            'Authorization': 'invalid_format_token',
            'Content-Type': 'application/json'
        }
        
        me_with_malformed_header = client.get(
            '/api/v1/auth/me',
            headers=malformed_headers
        )
        assert me_with_malformed_header.status_code == 401