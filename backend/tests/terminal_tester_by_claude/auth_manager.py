# backend/tests/terminal_tester_by_claude/auth_manager.py
# 사용자 인증 및 토큰 관리

import json
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from config import config
from display_utils import DisplayUtils


class AuthManager:
    """사용자 인증 및 JWT 토큰 관리 클래스"""
    
    def __init__(self):
        """인증 관리자 초기화"""
        self.api_client = None  # API 클라이언트는 나중에 설정 (순환 참조 방지)
        
        # 토큰 정보
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # 사용자 정보
        self.user_info = {}
        self.is_logged_in = False
        
        # 토큰 갱신 관련
        self.auto_refresh_enabled = True
        self.refresh_threshold = config.TOKEN_REFRESH_THRESHOLD  # 5분
    
    def set_api_client(self, api_client):
        """API 클라이언트 설정 (순환 참조 방지용)"""
        self.api_client = api_client
    
    def login(self, login_id: str = None, password: str = None) -> bool:
        """
        사용자 로그인
        
        Args:
            login_id: 로그인 ID (None이면 입력 받음)
            password: 비밀번호 (None이면 입력 받음)
            
        Returns:
            bool: 로그인 성공 여부
        """
        try:
            # 사용자 정보 입력 받기
            if login_id is None:
                DisplayUtils.print_login_prompt()
                login_id = DisplayUtils.get_user_input(config.PROMPTS["login_id"])
                
                if not login_id:
                    DisplayUtils.print_error("로그인 ID를 입력해주세요.")
                    return False
            
            if password is None:
                password = DisplayUtils.get_password_input(config.PROMPTS["password"])
                
                if not password:
                    DisplayUtils.print_error("비밀번호를 입력해주세요.")
                    return False
            
            # 로그인 시도
            DisplayUtils.print_loading("로그인 중...")
            
            if not self.api_client:
                DisplayUtils.clear_loading()
                DisplayUtils.print_error("API 클라이언트가 설정되지 않았습니다.")
                return False
            
            success, response = self.api_client.login(login_id, password)
            DisplayUtils.clear_loading()
            
            if success:
                # 로그인 성공 - 토큰 정보 저장
                self._process_login_response(response)
                DisplayUtils.print_success(f"환영합니다, {self.user_info.get('username', login_id)}님!")
                DisplayUtils.print_info(f"사용자 타입: {self.user_info.get('user_type', 'unknown')}")
                
                # 진단 완료 상태 확인
                if self.user_info.get('diagnosis_completed'):
                    DisplayUtils.print_success("진단이 완료된 사용자입니다. 학습 세션을 시작할 수 있습니다.")
                else:
                    DisplayUtils.print_warning("진단이 완료되지 않은 사용자입니다.")
                
                return True
            else:
                # 로그인 실패
                DisplayUtils.print_api_error(response, "로그인")
                return False
                
        except Exception as e:
            DisplayUtils.print_error(f"로그인 중 오류 발생: {str(e)}")
            return False
    
    def _process_login_response(self, response: Dict[str, Any]):
        """로그인 응답 처리 및 토큰 저장"""
        try:
            data = response.get('data', {})
            
            # 토큰 정보 저장
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token')
            
            # 사용자 정보 저장
            self.user_info = data.get('user_info', {})
            
            # 토큰 만료 시간 계산 (JWT 디코딩해서 추출)
            if self.access_token:
                try:
                    # JWT 디코딩 (검증 없이 페이로드만 추출)
                    payload = jwt.decode(self.access_token, options={"verify_signature": False})
                    exp_timestamp = payload.get('exp')
                    if exp_timestamp:
                        self.token_expires_at = datetime.fromtimestamp(exp_timestamp)
                except Exception:
                    # JWT 디코딩 실패 시 기본값 설정 (1시간 후)
                    self.token_expires_at = datetime.now() + timedelta(hours=1)
            
            # 로그인 상태 설정
            self.is_logged_in = True
            
            DisplayUtils.print_info(f"토큰 만료 시간: {self.token_expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            DisplayUtils.print_error(f"로그인 응답 처리 중 오류: {str(e)}")
            raise
    
    def logout(self) -> bool:
        """
        사용자 로그아웃
        
        Returns:
            bool: 로그아웃 성공 여부
        """
        try:
            if not self.is_logged_in:
                DisplayUtils.print_warning("로그인 상태가 아닙니다.")
                return True
            
            # 서버에 로그아웃 요청
            if self.api_client:
                DisplayUtils.print_loading("로그아웃 중...")
                success, response = self.api_client.logout()
                DisplayUtils.clear_loading()
                
                if not success:
                    DisplayUtils.print_warning("서버 로그아웃 요청 실패 (로컬 세션은 정리됩니다)")
                    DisplayUtils.print_api_error(response, "로그아웃")
            
            # 로컬 세션 정리
            self._clear_session()
            DisplayUtils.print_success("로그아웃되었습니다.")
            return True
            
        except Exception as e:
            DisplayUtils.print_error(f"로그아웃 중 오류 발생: {str(e)}")
            # 오류가 발생해도 로컬 세션은 정리
            self._clear_session()
            return False
    
    def _clear_session(self):
        """세션 정보 초기화"""
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.user_info = {}
        self.is_logged_in = False
        
        # API 클라이언트 세션도 초기화
        if self.api_client:
            self.api_client.clear_session()
    
    def refresh_token_if_needed(self) -> bool:
        """
        필요시 토큰 자동 갱신
        
        Returns:
            bool: 갱신 성공 여부 (갱신이 필요없으면 True)
        """
        if not self.auto_refresh_enabled or not self.is_logged_in:
            return True
        
        if not self.token_expires_at:
            return True
        
        # 만료 임계점 확인
        time_until_expiry = (self.token_expires_at - datetime.now()).total_seconds()
        
        if time_until_expiry <= self.refresh_threshold:
            DisplayUtils.print_info("토큰이 곧 만료됩니다. 자동 갱신을 시도합니다...")
            return self.refresh_token()
        
        return True
    
    def refresh_token(self) -> bool:
        """
        토큰 수동 갱신
        
        Returns:
            bool: 갱신 성공 여부
        """
        try:
            if not self.refresh_token:
                DisplayUtils.print_error("Refresh Token이 없습니다. 다시 로그인해주세요.")
                self._clear_session()
                return False
            
            if not self.api_client:
                DisplayUtils.print_error("API 클라이언트가 설정되지 않았습니다.")
                return False
            
            DisplayUtils.print_loading("토큰 갱신 중...")
            success, response = self.api_client.refresh_token(self.refresh_token)
            DisplayUtils.clear_loading()
            
            if success:
                # 새 토큰으로 업데이트
                data = response.get('data', {})
                old_access_token = self.access_token[:20] + "..." if self.access_token else "None"
                
                self.access_token = data.get('access_token')
                new_refresh = data.get('refresh_token')
                if new_refresh:  # 새 refresh_token이 있으면 업데이트
                    self.refresh_token = new_refresh
                
                # 새 토큰 만료 시간 계산
                if self.access_token:
                    try:
                        payload = jwt.decode(self.access_token, options={"verify_signature": False})
                        exp_timestamp = payload.get('exp')
                        if exp_timestamp:
                            self.token_expires_at = datetime.fromtimestamp(exp_timestamp)
                    except Exception:
                        self.token_expires_at = datetime.now() + timedelta(hours=1)
                
                new_access_token = self.access_token[:20] + "..." if self.access_token else "None"
                DisplayUtils.print_success("토큰이 성공적으로 갱신되었습니다.")
                DisplayUtils.print_info(f"이전 토큰: {old_access_token}")
                DisplayUtils.print_info(f"새 토큰: {new_access_token}")
                DisplayUtils.print_info(f"새 만료 시간: {self.token_expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                return True
            else:
                # 토큰 갱신 실패
                DisplayUtils.print_error("토큰 갱신에 실패했습니다. 다시 로그인해주세요.")
                DisplayUtils.print_api_error(response, "토큰 갱신")
                self._clear_session()
                return False
                
        except Exception as e:
            DisplayUtils.print_error(f"토큰 갱신 중 오류 발생: {str(e)}")
            return False
    
    def get_auth_header(self) -> Optional[Dict[str, str]]:
        """
        인증 헤더 반환
        
        Returns:
            Dict[str, str]: Authorization 헤더 또는 None
        """
        if not self.is_logged_in or not self.access_token:
            return None
        
        # 토큰 자동 갱신 시도
        if not self.refresh_token_if_needed():
            return None
        
        return {
            "Authorization": f"Bearer {self.access_token}"
        }
    
    def is_token_valid(self) -> bool:
        """
        토큰 유효성 확인
        
        Returns:
            bool: 토큰 유효 여부
        """
        if not self.is_logged_in or not self.access_token:
            return False
        
        if not self.token_expires_at:
            return True  # 만료 시간을 모르면 유효하다고 가정
        
        return datetime.now() < self.token_expires_at
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        토큰 정보 반환
        
        Returns:
            Dict: 토큰 관련 정보
        """
        if not self.is_logged_in:
            return {"logged_in": False}
        
        time_until_expiry = None
        if self.token_expires_at:
            time_until_expiry = (self.token_expires_at - datetime.now()).total_seconds()
        
        return {
            "logged_in": self.is_logged_in,
            "has_access_token": bool(self.access_token),
            "has_refresh_token": bool(self.refresh_token),
            "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "time_until_expiry_seconds": max(0, time_until_expiry) if time_until_expiry else None,
            "is_valid": self.is_token_valid(),
            "user_info": self.user_info
        }
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        사용자 정보 반환
        
        Returns:
            Dict: 사용자 정보
        """
        return self.user_info.copy()
    
    def print_auth_status(self):
        """인증 상태 출력"""
        DisplayUtils.print_separator()
        DisplayUtils.print_colored("🔐 인증 상태", "bold")
        DisplayUtils.print_separator("-", 60)
        
        if self.is_logged_in:
            DisplayUtils.print_success(f"로그인됨: {self.user_info.get('username', 'Unknown')}")
            DisplayUtils.print_info(f"사용자 ID: {self.user_info.get('user_id', 'N/A')}")
            DisplayUtils.print_info(f"로그인 ID: {self.user_info.get('login_id', 'N/A')}")
            DisplayUtils.print_info(f"사용자 타입: {self.user_info.get('user_type', 'N/A')}")
            DisplayUtils.print_info(f"진단 완료: {'예' if self.user_info.get('diagnosis_completed') else '아니오'}")
            
            if self.token_expires_at:
                time_left = (self.token_expires_at - datetime.now()).total_seconds()
                if time_left > 0:
                    hours = int(time_left // 3600)
                    minutes = int((time_left % 3600) // 60)
                    DisplayUtils.print_info(f"토큰 만료까지: {hours}시간 {minutes}분")
                else:
                    DisplayUtils.print_warning("토큰이 만료되었습니다!")
            
            # 현재 진행 상황
            current_chapter = self.user_info.get('current_chapter')
            current_section = self.user_info.get('current_section')
            if current_chapter and current_section:
                DisplayUtils.print_info(f"현재 진행: {current_chapter}챕터 {current_section}섹션")
        else:
            DisplayUtils.print_error("로그인되지 않음")
            DisplayUtils.print_info("'login' 명령어로 로그인하세요.")
        
        DisplayUtils.print_separator()
    
    def require_login(self) -> bool:
        """
        로그인 필요 시 확인 및 안내
        
        Returns:
            bool: 로그인 상태
        """
        if not self.is_logged_in:
            DisplayUtils.print_error("이 명령어를 사용하려면 로그인이 필요합니다.")
            DisplayUtils.print_info("'login' 명령어를 사용하여 로그인하세요.")
            return False
        
        # 토큰 유효성 확인
        if not self.is_token_valid():
            DisplayUtils.print_warning("토큰이 만료되었습니다. 토큰 갱신을 시도합니다...")
            if not self.refresh_token():
                DisplayUtils.print_error("토큰 갱신에 실패했습니다. 다시 로그인해주세요.")
                return False
        
        return True
    
    def enable_auto_refresh(self):
        """자동 토큰 갱신 활성화"""
        self.auto_refresh_enabled = True
        DisplayUtils.print_success("자동 토큰 갱신이 활성화되었습니다.")
    
    def disable_auto_refresh(self):
        """자동 토큰 갱신 비활성화"""
        self.auto_refresh_enabled = False
        DisplayUtils.print_warning("자동 토큰 갱신이 비활성화되었습니다.")


# 편의를 위한 전역 함수들
def create_auth_manager() -> AuthManager:
    """인증 관리자 생성"""
    return AuthManager()