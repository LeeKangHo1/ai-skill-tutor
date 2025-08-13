# backend/test_api_manual.py
# 수동 API 테스트 스크립트

import requests
import json

BASE_URL = "http://localhost:5000/api/v1/auth"

def test_availability_check():
    """중복 확인 API 테스트"""
    print("=== 중복 확인 API 테스트 ===")
    
    # login_id 중복 확인
    response = requests.post(f"{BASE_URL}/check-availability", 
                           json={"login_id": "test_user_123"})
    print(f"Login ID 중복 확인: {response.status_code}")
    print(f"응답: {response.json()}")
    print()

def test_user_registration():
    """회원가입 API 테스트"""
    print("=== 회원가입 API 테스트 ===")
    
    import random
    import time
    
    # 고유한 테스트 데이터 생성
    random_num = random.randint(100, 999)
    
    user_data = {
        "login_id": f"test{random_num}",
        "username": f"테스트사용자{random_num}",
        "email": f"test{random_num}@example.com",
        "password": "TestPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print(f"회원가입: {response.status_code}")
    print(f"응답: {response.json()}")
    print()
    
    result = response.json() if response.status_code == 201 else None
    return result, user_data

def test_user_login(login_id, password):
    """로그인 API 테스트"""
    print("=== 로그인 API 테스트 ===")
    
    login_data = {
        "login_id": login_id,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"로그인: {response.status_code}")
    print(f"응답: {response.json()}")
    print()
    
    return response.json() if response.status_code == 200 else None

def test_protected_endpoint(access_token):
    """보호된 엔드포인트 테스트"""
    print("=== 보호된 엔드포인트 테스트 ===")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print(f"사용자 정보 조회: {response.status_code}")
    print(f"응답: {response.json()}")
    print()

def test_token_refresh(refresh_token):
    """토큰 갱신 테스트"""
    print("=== 토큰 갱신 테스트 ===")
    
    response = requests.post(f"{BASE_URL}/refresh", 
                           json={"refresh_token": refresh_token})
    print(f"토큰 갱신: {response.status_code}")
    print(f"응답: {response.json()}")
    print()
    
    return response.json() if response.status_code == 200 else None

def test_logout(access_token, refresh_token):
    """로그아웃 테스트"""
    print("=== 로그아웃 테스트 ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"{BASE_URL}/logout", headers=headers, json={"refresh_token": refresh_token})
    print(f"로그아웃: {response.status_code}")
    print(f"응답: {response.json()}")
    print()

def main():
    """메인 테스트 실행"""
    print("🚀 백엔드 인증 시스템 수동 테스트 시작\n")
    
    try:
        # 1. 중복 확인 테스트
        test_availability_check()
        
        # 2. 회원가입 테스트
        register_result, user_data = test_user_registration()
        if not register_result or not register_result.get('success'):
            print("❌ 회원가입 실패")
            return
        
        access_token = register_result['data']['access_token']
        refresh_token = register_result['data']['refresh_token']
        
        # 3. 보호된 엔드포인트 테스트
        test_protected_endpoint(access_token)
        
        # 4. 로그인 테스트 (새로운 토큰 발급)
        login_result = test_user_login(user_data['login_id'], "TestPass123!")
        if login_result and login_result.get('success'):
            new_access_token = login_result['data']['access_token']
            new_refresh_token = login_result['data']['refresh_token']
            
            # 5. 토큰 갱신 테스트
            refresh_result = test_token_refresh(new_refresh_token)
            
            # 6. 로그아웃 테스트
            test_logout(new_access_token, new_refresh_token)
            
        print("✅ 모든 테스트 완료!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. Flask 앱이 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    main()