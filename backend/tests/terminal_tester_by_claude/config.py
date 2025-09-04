# backend/tests/terminal_tester_by_claude/config.py
# 터미널 테스터 설정 파일

import os


class Config:
    """터미널 테스터 설정 클래스"""
    
    # API 기본 설정
    BASE_URL = "http://localhost:5000/api/v1"
    CONTENT_TYPE = "application/json"
    
    # API 엔드포인트 경로
    ENDPOINTS = {
        # 인증 관련
        "login": "/auth/login",
        "refresh": "/auth/refresh",
        "logout": "/auth/logout",
        
        # 학습 세션 관련  
        "session_start": "/learning/session/start",
        "session_message": "/learning/session/message", 
        "quiz_submit": "/learning/quiz/submit",
        "session_complete": "/learning/session/complete",
        
        # 기타
        "health": "/system/health",
        "version": "/system/version"
    }
    
    # 요청 타임아웃 설정 (초)
    REQUEST_TIMEOUT = 30
    
    # 토큰 관련 설정
    TOKEN_REFRESH_THRESHOLD = 300  # 5분 전에 토큰 갱신
    MAX_RETRY_ATTEMPTS = 3
    
    # 디스플레이 설정
    JSON_INDENT = 2
    MAX_DISPLAY_LENGTH = 5000  # JSON 출력 최대 길이
    
    # 명령어 도움말
    COMMANDS_HELP = {
        "login": "사용자 로그인 - 사용법: login",
        "start": "학습 세션 시작 - 사용법: start <챕터> <섹션> [메시지]",
        "msg": "메시지 전송 - 사용법: msg <메시지 내용>", 
        "quiz": "퀴즈 답변 제출 - 사용법: quiz <답변>",
        "complete": "세션 완료 - 사용법: complete <proceed|retry>",
        "state": "현재 TutorState 조회 - 사용법: state",
        "health": "서버 상태 확인 - 사용법: health",
        "version": "서버 버전 확인 - 사용법: version",
        "help": "명령어 도움말 표시 - 사용법: help",
        "clear": "화면 지우기 - 사용법: clear",
        "quit": "프로그램 종료 - 사용법: quit"
    }
    
    # 사용자 입력 프롬프트
    PROMPTS = {
        "main": "AI튜터> ",
        "login_id": "로그인 ID: ",
        "password": "비밀번호: ",
        "confirm": "계속하시겠습니까? (y/n): "
    }
    
    # 컬러 코드 (터미널 출력용)
    COLORS = {
        "reset": "\033[0m",
        "red": "\033[91m",
        "green": "\033[92m", 
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "underline": "\033[4m"
    }
    
    # 메시지 템플릿
    MESSAGES = {
        "welcome": """
🤖 AI 활용법 학습 튜터 - 터미널 테스터 v1.0
========================================
백엔드 멀티에이전트 시스템 테스트 도구

사용 가능한 명령어: login, start, msg, quiz, complete, state, help, quit
시작하려면 'login' 명령어로 로그인하세요.
        """,
        
        "login_success": "✅ 로그인 성공!",
        "login_required": "❌ 로그인이 필요합니다. 'login' 명령어를 사용하세요.",
        "invalid_command": "❌ 알 수 없는 명령어입니다. 'help'를 입력하여 도움말을 확인하세요.",
        "goodbye": "👋 AI 튜터 터미널 테스터를 종료합니다.",
        "server_error": "❌ 서버 연결 오류가 발생했습니다.",
        
        "session_flow": """
📚 학습 세션 진행 순서:
1. start <챕터> <섹션> - 세션 시작
2. msg "다음 단계로 가주세요" - 다음 단계 요청  
3. quiz "답변" - 퀴즈 답변 제출
4. complete proceed|retry - 세션 완료
        """
    }
    
    # 환경변수 기반 설정 오버라이드
    @classmethod
    def load_from_env(cls):
        """환경변수에서 설정 로드 (선택사항)"""
        if os.getenv("API_BASE_URL"):
            cls.BASE_URL = os.getenv("API_BASE_URL")
        
        if os.getenv("REQUEST_TIMEOUT"):
            cls.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT"))
    
    # 전체 URL 생성 헬퍼
    @classmethod 
    def get_full_url(cls, endpoint_key: str) -> str:
        """엔드포인트 키로 전체 URL 생성"""
        if endpoint_key not in cls.ENDPOINTS:
            raise ValueError(f"Unknown endpoint: {endpoint_key}")
        
        return cls.BASE_URL + cls.ENDPOINTS[endpoint_key]
    
    # 컬러 출력 헬퍼
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """텍스트에 컬러 적용"""
        if color not in cls.COLORS:
            return text
        
        return f"{cls.COLORS[color]}{text}{cls.COLORS['reset']}"


# 기본 설정 인스턴스
config = Config()

# 환경변수 기반 설정 로드
config.load_from_env()