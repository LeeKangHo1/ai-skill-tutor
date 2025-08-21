# Design Document

## Overview

대화형 API 테스터는 백엔드 개발자가 터미널에서 실시간으로 AI 학습 세션 API를 테스트할 수 있는 Python 기반 CLI 도구입니다. 사용자의 자연어 입력을 적절한 HTTP 요청으로 변환하고, API 응답을 분석하여 다음 상호작용을 자동으로 결정하는 지능형 테스터입니다.

## Architecture

### 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Interactive API Tester                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Input Handler  │  │ Request Builder │  │ HTTP Client  │ │
│  │                 │  │                 │  │              │ │
│  │ - 사용자 입력    │  │ - 요청 생성     │  │ - API 호출   │ │
│  │ - 명령어 파싱    │  │ - 페이로드 구성 │  │ - 응답 처리  │ │
│  │ - 입력 검증     │  │ - 헤더 설정     │  │ - 오류 처리  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│           │                     │                    │      │
│           ▼                     ▼                    ▼      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Session Manager │  │Response Analyzer│  │Output Handler│ │
│  │                 │  │                 │  │              │ │
│  │ - 세션 상태     │  │ - 응답 분석     │  │ - 결과 출력  │ │
│  │ - 컨텍스트 관리 │  │ - UI 모드 판단  │  │ - 포맷팅     │ │
│  │ - 토큰 관리     │  │ - 다음 액션 결정│  │ - 에러 표시  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   Backend API Server    │
                    │  http://localhost:5000  │
                    └─────────────────────────┘
```

### 데이터 플로우

```
사용자 입력 → 입력 파싱 → 요청 생성 → API 호출 → 응답 분석 → 출력 표시
     ↑                                                              │
     └──────────────── 다음 상호작용 결정 ←─────────────────────────┘
```

## Components and Interfaces

### 1. InputHandler 클래스

**책임**: 사용자 입력 처리 및 명령어 파싱

```python
class InputHandler:
    def __init__(self):
        self.current_mode = "normal"  # normal, quiz, session_start
        
    def get_user_input(self) -> str:
        """사용자 입력을 받아 반환"""
        
    def parse_command(self, user_input: str) -> dict:
        """명령어를 파싱하여 액션과 파라미터 반환"""
        
    def validate_input(self, command: dict) -> bool:
        """입력 검증"""
        
    def get_session_start_params(self) -> dict:
        """세션 시작 파라미터 입력 받기"""
```

**주요 메서드**:
- `get_user_input()`: 프롬프트 표시 및 사용자 입력 수집
- `parse_command()`: 특수 명령어(/quit, /state, /proceed 등) 파싱
- `validate_input()`: 입력값 유효성 검증
- `get_session_start_params()`: 챕터/섹션 번호 입력 처리

### 2. RequestBuilder 클래스

**책임**: HTTP 요청 생성 및 페이로드 구성

```python
class RequestBuilder:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        
    def build_session_start_request(self, chapter: int, section: int, message: str) -> dict:
        """세션 시작 요청 생성"""
        
    def build_session_message_request(self, message: str) -> dict:
        """세션 메시지 요청 생성"""
        
    def build_quiz_submit_request(self, answer: str) -> dict:
        """퀴즈 답변 제출 요청 생성"""
        
    def build_session_complete_request(self, decision: str) -> dict:
        """세션 완료 요청 생성"""
        
    def build_state_request(self) -> dict:
        """상태 조회 요청 생성"""
```

**주요 메서드**:
- `build_*_request()`: 각 API 엔드포인트별 요청 구성
- `set_auth_token()`: JWT 토큰 설정
- `get_request_info()`: 요청 정보 반환 (디버깅용)

### 3. HTTPClient 클래스

**책임**: HTTP 통신 및 응답 처리

```python
class HTTPClient:
    def __init__(self, timeout: int = 30):
        self.session = requests.Session()
        self.timeout = timeout
        
    def send_request(self, method: str, url: str, data: dict = None, headers: dict = None) -> dict:
        """HTTP 요청 전송 및 응답 반환"""
        
    def handle_response(self, response: requests.Response) -> dict:
        """응답 처리 및 에러 핸들링"""
        
    def check_connection(self, base_url: str) -> bool:
        """서버 연결 상태 확인"""
```

**주요 메서드**:
- `send_request()`: HTTP 요청 전송
- `handle_response()`: 응답 상태 코드 및 JSON 파싱
- `check_connection()`: 백엔드 서버 연결 확인

### 4. ResponseAnalyzer 클래스

**책임**: API 응답 분석 및 다음 액션 결정

```python
class ResponseAnalyzer:
    def analyze_response(self, response: dict) -> dict:
        """응답을 분석하여 다음 액션 결정"""
        
    def determine_ui_mode(self, workflow_response: dict) -> str:
        """UI 모드 판단 (chat/quiz)"""
        
    def extract_content(self, response: dict) -> dict:
        """응답에서 컨텐츠 추출"""
        
    def should_switch_to_quiz_mode(self, response: dict) -> bool:
        """퀴즈 모드 전환 여부 판단"""
```

**주요 메서드**:
- `analyze_response()`: 응답 구조 분석
- `determine_ui_mode()`: ui_mode 필드 기반 모드 결정
- `extract_content()`: 표시할 컨텐츠 추출
- `should_switch_to_quiz_mode()`: 퀴즈 모드 전환 조건 확인

### 5. SessionManager 클래스

**책임**: 세션 상태 관리 및 컨텍스트 유지

```python
class SessionManager:
    def __init__(self):
        self.current_session = None
        self.session_history = []
        self.auth_token = None
        
    def start_new_session(self, chapter: int, section: int) -> None:
        """새 세션 시작"""
        
    def update_session_state(self, response: dict) -> None:
        """세션 상태 업데이트"""
        
    def get_current_mode(self) -> str:
        """현재 상호작용 모드 반환"""
        
    def set_auth_token(self, token: str) -> None:
        """인증 토큰 설정"""
```

**주요 메서드**:
- `start_new_session()`: 새 학습 세션 초기화
- `update_session_state()`: API 응답 기반 상태 업데이트
- `get_current_mode()`: 현재 모드 (normal/quiz) 반환
- `clear_session()`: 세션 정리

### 6. OutputHandler 클래스

**책임**: 결과 출력 및 사용자 인터페이스

```python
class OutputHandler:
    def __init__(self):
        self.colors = {
            'success': '\033[92m',
            'error': '\033[91m',
            'info': '\033[94m',
            'warning': '\033[93m',
            'reset': '\033[0m'
        }
        
    def display_response(self, response: dict, request_info: dict) -> None:
        """API 응답 표시"""
        
    def display_quiz(self, quiz_content: dict) -> None:
        """퀴즈 내용 표시"""
        
    def display_error(self, error: dict) -> None:
        """에러 메시지 표시"""
        
    def display_help(self) -> None:
        """도움말 표시"""
```

**주요 메서드**:
- `display_response()`: 구조화된 응답 출력
- `display_quiz()`: 퀴즈 형식 출력
- `display_error()`: 에러 메시지 포맷팅
- `display_help()`: 사용법 안내

## Data Models

### 1. SessionState 데이터 모델

```python
@dataclass
class SessionState:
    chapter_number: int = None
    section_number: int = None
    current_agent: str = None
    session_progress_stage: str = None
    ui_mode: str = "chat"
    is_active: bool = False
    last_response: dict = None
    created_at: datetime = None
```

### 2. RequestInfo 데이터 모델

```python
@dataclass
class RequestInfo:
    method: str
    url: str
    endpoint: str
    payload: dict
    headers: dict
    timestamp: datetime
```

### 3. Command 데이터 모델

```python
@dataclass
class Command:
    action: str  # session_start, message, quiz_answer, complete, state, quit
    parameters: dict
    is_special_command: bool = False
```

## Error Handling

### 에러 처리 전략

1. **네트워크 에러**
   - 연결 실패 시 재시도 안내
   - 타임아웃 처리
   - 서버 상태 확인 제안

2. **API 에러**
   - HTTP 상태 코드별 처리
   - 에러 메시지 파싱 및 표시
   - 복구 가능한 에러 안내

3. **입력 에러**
   - 잘못된 명령어 안내
   - 올바른 형식 제안
   - 도움말 자동 표시

4. **세션 에러**
   - 세션 상태 불일치 처리
   - 세션 재시작 안내
   - 상태 초기화 옵션

### 에러 코드 매핑

```python
ERROR_MESSAGES = {
    'CONNECTION_ERROR': '백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.',
    'TIMEOUT_ERROR': '요청 시간이 초과되었습니다. 다시 시도해주세요.',
    'AUTH_ERROR': '인증에 실패했습니다. 토큰을 확인해주세요.',
    'VALIDATION_ERROR': '입력값이 올바르지 않습니다.',
    'SESSION_ERROR': '세션 상태에 문제가 있습니다. 새 세션을 시작해주세요.',
    'UNKNOWN_ERROR': '알 수 없는 오류가 발생했습니다.'
}
```

## Testing Strategy

### 1. 단위 테스트

**테스트 대상**:
- InputHandler: 명령어 파싱 로직
- RequestBuilder: 요청 생성 로직
- ResponseAnalyzer: 응답 분석 로직
- SessionManager: 상태 관리 로직

**테스트 방법**:
- Mock 객체를 사용한 독립적 테스트
- 다양한 입력 케이스 검증
- 에러 상황 시뮬레이션

### 2. 통합 테스트

**테스트 시나리오**:
- 완전한 학습 세션 플로우
- 퀴즈 답변 및 피드백 처리
- 에러 상황 복구
- 세션 완료 처리

**테스트 환경**:
- Mock 백엔드 서버 사용
- 실제 API 응답 시뮬레이션
- 다양한 워크플로우 시나리오

### 3. 사용성 테스트

**테스트 항목**:
- 사용자 인터페이스 직관성
- 에러 메시지 명확성
- 도움말 유용성
- 응답 시간 적절성

## Implementation Details

### 1. 메인 애플리케이션 구조

```python
class InteractiveAPITester:
    def __init__(self):
        self.input_handler = InputHandler()
        self.request_builder = RequestBuilder("http://localhost:5000/api/v1")
        self.http_client = HTTPClient()
        self.response_analyzer = ResponseAnalyzer()
        self.session_manager = SessionManager()
        self.output_handler = OutputHandler()
        
    def run(self):
        """메인 실행 루프"""
        self.output_handler.display_help()
        
        while True:
            try:
                user_input = self.input_handler.get_user_input()
                command = self.input_handler.parse_command(user_input)
                
                if command.action == "quit":
                    break
                    
                response = self.process_command(command)
                self.handle_response(response)
                
            except KeyboardInterrupt:
                print("\n테스트를 종료합니다.")
                break
            except Exception as e:
                self.output_handler.display_error({"message": str(e)})
```

### 2. 명령어 처리 로직

```python
def process_command(self, command: Command) -> dict:
    """명령어별 처리 로직"""
    if command.action == "session_start":
        return self.handle_session_start(command.parameters)
    elif command.action == "message":
        return self.handle_message(command.parameters)
    elif command.action == "quiz_answer":
        return self.handle_quiz_answer(command.parameters)
    elif command.action == "complete":
        return self.handle_session_complete(command.parameters)
    elif command.action == "state":
        return self.handle_state_request()
    else:
        raise ValueError(f"알 수 없는 명령어: {command.action}")
```

### 3. 응답 처리 플로우

```python
def handle_response(self, response: dict) -> None:
    """응답 처리 및 다음 액션 결정"""
    # 응답 분석
    analysis = self.response_analyzer.analyze_response(response)
    
    # 세션 상태 업데이트
    self.session_manager.update_session_state(response)
    
    # 결과 출력
    self.output_handler.display_response(response, analysis)
    
    # UI 모드 전환
    if analysis.get("ui_mode") == "quiz":
        self.input_handler.current_mode = "quiz"
    else:
        self.input_handler.current_mode = "normal"
```

### 4. 설정 관리

```python
CONFIG = {
    "base_url": "http://localhost:5000/api/v1",
    "timeout": 30,
    "default_user_type": "beginner",
    "test_token": None,  # 테스트용 JWT 토큰
    "colors_enabled": True,
    "debug_mode": False
}
```

## Security Considerations

### 1. 토큰 관리
- JWT 토큰을 메모리에만 저장
- 세션 종료 시 토큰 정리
- 토큰 만료 시 재인증 안내

### 2. 입력 검증
- 사용자 입력 sanitization
- SQL injection 방지
- XSS 방지를 위한 출력 이스케이프

### 3. 네트워크 보안
- HTTPS 사용 권장
- 요청 타임아웃 설정
- 민감 정보 로깅 방지

## Performance Optimization

### 1. 응답 시간 최적화
- HTTP 연결 재사용 (Session 객체)
- 요청 타임아웃 적절히 설정
- 비동기 처리 고려 (필요시)

### 2. 메모리 관리
- 세션 히스토리 크기 제한
- 불필요한 데이터 정리
- 가비지 컬렉션 최적화

### 3. 사용자 경험
- 응답 대기 중 로딩 표시
- 긴 응답 내용 페이징
- 컬러 출력으로 가독성 향상

---

이 설계는 요구사항에서 정의한 모든 기능을 포함하며, 확장 가능하고 유지보수가 용이한 구조로 설계되었습니다. 각 컴포넌트는 단일 책임 원칙을 따르며, 느슨한 결합을 통해 테스트와 수정이 용이하도록 구성되었습니다.