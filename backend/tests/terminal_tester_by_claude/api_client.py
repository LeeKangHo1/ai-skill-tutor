# backend/tests/terminal_tester_by_claude/api_client.py
# HTTP 요청 및 API 호출 관리

import requests
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from config import config
from display_utils import DisplayUtils


class APIClient:
    """API 호출 및 HTTP 요청 관리 클래스"""
    
    def __init__(self, auth_manager=None):
        """
        API 클라이언트 초기화
        
        Args:
            auth_manager: 인증 관리자 인스턴스
        """
        self.auth_manager = auth_manager
        self.session = requests.Session()
        self.last_request_time = None
        
        # 기본 헤더 설정
        self.session.headers.update({
            'Content-Type': config.CONTENT_TYPE,
            'User-Agent': 'AI-Tutor-Terminal-Tester/1.0'
        })
    
    def set_auth_manager(self, auth_manager):
        """인증 관리자 설정 (순환 참조 방지용)"""
        self.auth_manager = auth_manager
    
    def _prepare_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """요청 헤더 준비"""
        headers = {
            'Content-Type': config.CONTENT_TYPE
        }
        
        # 인증 헤더 추가
        if include_auth and self.auth_manager:
            auth_header = self.auth_manager.get_auth_header()
            if auth_header:
                headers.update(auth_header)
        
        return headers
    
    def _log_request(self, method: str, url: str, data: Optional[Dict] = None):
        """요청 로그 출력"""
        DisplayUtils.print_info(f"📤 {method.upper()} {url}")
        if data and isinstance(data, dict):
            # 비밀번호 등 민감 정보 마스킹
            safe_data = self._mask_sensitive_data(data)
            DisplayUtils.print_colored(f"   요청 데이터: {json.dumps(safe_data, ensure_ascii=False)}", "purple")
    
    def _log_response(self, response: requests.Response, duration: float):
        """응답 로그 출력"""
        status_color = "green" if 200 <= response.status_code < 300 else "red"
        DisplayUtils.print_colored(
            f"📥 응답: {response.status_code} ({duration:.2f}s)", 
            status_color
        )
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """민감한 데이터 마스킹"""
        sensitive_keys = ['password', 'token', 'refresh_token', 'access_token']
        masked_data = data.copy()
        
        for key in sensitive_keys:
            if key in masked_data:
                masked_data[key] = "***MASKED***"
        
        return masked_data
    
    def _handle_response(self, response: requests.Response, endpoint: str = "") -> Tuple[bool, Dict[str, Any]]:
        """응답 처리 및 에러 핸들링"""
        try:
            # JSON 파싱 시도
            response_data = response.json()
        except ValueError:
            # JSON이 아닌 응답 처리
            response_data = {
                "raw_response": response.text,
                "status_code": response.status_code
            }
        
        # 상태 코드별 처리
        if 200 <= response.status_code < 300:
            # 성공 응답
            return True, response_data
        
        elif response.status_code == 401:
            # 인증 오류 - 토큰 갱신 시도
            if self.auth_manager and endpoint != "login":  # 로그인 요청이 아닌 경우에만
                DisplayUtils.print_warning("토큰이 만료되었습니다. 자동 갱신을 시도합니다...")
                
                if self.auth_manager.refresh_token():
                    DisplayUtils.print_success("토큰이 갱신되었습니다.")
                    return False, {"retry_with_new_token": True}
                else:
                    DisplayUtils.print_error("토큰 갱신에 실패했습니다. 다시 로그인해주세요.")
        
        # 기타 에러 응답
        error_data = {
            "status_code": response.status_code,
            "endpoint": endpoint,
            "error": response_data if response_data else {"message": response.text}
        }
        
        return False, error_data
    
    def _make_request(
        self, 
        method: str, 
        endpoint_key: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        include_auth: bool = True,
        retry_count: int = 0
    ) -> Tuple[bool, Dict[str, Any]]:
        """실제 HTTP 요청 수행"""
        try:
            # URL 생성
            url = config.get_full_url(endpoint_key)
            
            # 헤더 준비
            headers = self._prepare_headers(include_auth)
            
            # 요청 시작 시간
            start_time = datetime.now()
            
            # 요청 로그
            self._log_request(method, url, data)
            
            # HTTP 요청 수행
            if method.upper() == 'GET':
                response = self.session.get(
                    url, 
                    params=params, 
                    headers=headers,
                    timeout=config.REQUEST_TIMEOUT
                )
            elif method.upper() == 'POST':
                response = self.session.post(
                    url, 
                    json=data, 
                    params=params,
                    headers=headers,
                    timeout=config.REQUEST_TIMEOUT
                )
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
            
            # 응답 시간 계산
            duration = (datetime.now() - start_time).total_seconds()
            self.last_request_time = duration
            
            # 응답 로그
            self._log_response(response, duration)
            
            # 응답 처리
            success, response_data = self._handle_response(response, endpoint_key)
            
            # 토큰 갱신 후 재시도 처리
            if not success and response_data.get("retry_with_new_token") and retry_count < config.MAX_RETRY_ATTEMPTS:
                DisplayUtils.print_info("새 토큰으로 요청을 재시도합니다...")
                return self._make_request(method, endpoint_key, data, params, include_auth, retry_count + 1)
            
            return success, response_data
            
        except requests.exceptions.Timeout:
            error_data = {
                "error": {
                    "code": "REQUEST_TIMEOUT",
                    "message": f"요청 시간 초과 ({config.REQUEST_TIMEOUT}초)"
                },
                "endpoint": endpoint_key
            }
            return False, error_data
            
        except requests.exceptions.ConnectionError:
            error_data = {
                "error": {
                    "code": "CONNECTION_ERROR",
                    "message": "서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요."
                },
                "endpoint": endpoint_key
            }
            return False, error_data
            
        except requests.exceptions.RequestException as e:
            error_data = {
                "error": {
                    "code": "REQUEST_ERROR",
                    "message": f"요청 중 오류 발생: {str(e)}"
                },
                "endpoint": endpoint_key
            }
            return False, error_data
            
        except Exception as e:
            error_data = {
                "error": {
                    "code": "UNEXPECTED_ERROR",
                    "message": f"예상치 못한 오류: {str(e)}"
                },
                "endpoint": endpoint_key
            }
            return False, error_data
    
    def get(
        self, 
        endpoint_key: str, 
        params: Optional[Dict[str, Any]] = None,
        include_auth: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """GET 요청"""
        return self._make_request('GET', endpoint_key, params=params, include_auth=include_auth)
    
    def post(
        self, 
        endpoint_key: str, 
        data: Optional[Dict[str, Any]] = None,
        include_auth: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """POST 요청"""
        return self._make_request('POST', endpoint_key, data=data, include_auth=include_auth)
    
    # === 인증 관련 API ===
    
    def login(self, login_id: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """사용자 로그인"""
        login_data = {
            "login_id": login_id,
            "password": password
        }
        return self.post("login", login_data, include_auth=False)
    
    def refresh_token(self, refresh_token: str) -> Tuple[bool, Dict[str, Any]]:
        """토큰 갱신"""
        refresh_data = {
            "refresh_token": refresh_token
        }
        return self.post("refresh", refresh_data, include_auth=False)
    
    def logout(self) -> Tuple[bool, Dict[str, Any]]:
        """로그아웃"""
        return self.post("logout")
    
    # === 학습 세션 관련 API ===
    
    def start_session(self, chapter: int, section: int, user_message: str = None) -> Tuple[bool, Dict[str, Any]]:
        """학습 세션 시작"""
        session_data = {
            "chapter_number": chapter,
            "section_number": section,
            "user_message": user_message if user_message else f"{chapter}챕터 {section}섹션을 시작할게요"  # 기본 메시지 추가
        }
        
        return self.post("session_start", session_data)
    
    def send_message(self, message: str, message_type: str = "user") -> Tuple[bool, Dict[str, Any]]:
        """세션 메시지 전송"""
        message_data = {
            "user_message": message,
            "message_type": message_type
        }
        return self.post("session_message", message_data)
    
    def submit_quiz_answer(self, answer: str) -> Tuple[bool, Dict[str, Any]]:
        """퀴즈 답변 제출"""
        quiz_data = {
            "user_answer": answer
        }
        return self.post("quiz_submit", quiz_data)
    
    def complete_session(self, proceed_decision: str) -> Tuple[bool, Dict[str, Any]]:
        """세션 완료"""
        complete_data = {
            "proceed_decision": proceed_decision
        }
        return self.post("session_complete", complete_data)
    
    # === 시스템 관련 API ===
    
    def check_health(self) -> Tuple[bool, Dict[str, Any]]:
        """서버 상태 확인"""
        return self.get("health", include_auth=False)
    
    def get_version(self) -> Tuple[bool, Dict[str, Any]]:
        """서버 버전 정보"""
        return self.get("version", include_auth=False)
    
    # === 유틸리티 메서드 ===
    
    def test_connection(self) -> bool:
        """서버 연결 테스트"""
        try:
            success, _ = self.check_health()
            return success
        except Exception:
            return False
    
    def get_last_request_duration(self) -> Optional[float]:
        """마지막 요청 소요 시간 반환"""
        return self.last_request_time
    
    def clear_session(self):
        """세션 초기화 (쿠키, 헤더 등)"""
        self.session.cookies.clear()
        # 기본 헤더만 유지
        self.session.headers.clear()
        self.session.headers.update({
            'Content-Type': config.CONTENT_TYPE,
            'User-Agent': 'AI-Tutor-Terminal-Tester/1.0'
        })


# 편의를 위한 전역 함수들
def create_api_client(auth_manager=None) -> APIClient:
    """API 클라이언트 생성"""
    return APIClient(auth_manager)


def test_server_connection() -> bool:
    """서버 연결 테스트 (전역 함수)"""
    try:
        client = APIClient()
        return client.test_connection()
    except Exception as e:
        DisplayUtils.print_error(f"연결 테스트 실패: {str(e)}")
        return False