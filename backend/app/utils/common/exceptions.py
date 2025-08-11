# backend/app/utils/common/exceptions.py
"""
커스텀 예외 클래스들
애플리케이션에서 사용하는 커스텀 예외들을 정의합니다.
"""


class BaseCustomException(Exception):
    """기본 커스텀 예외 클래스"""

    def __init__(self, message, details=None, error_code=None):
        self.message = message
        self.details = details or {}
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(BaseCustomException):
    """입력값 검증 실패 시"""
    def __init__(self, message="입력값이 올바르지 않습니다.", details=None, error_code="VALIDATION_ERROR"):
        super().__init__(message, details, error_code)


class AuthenticationError(BaseCustomException):
    """인증 실패 (로그인 정보 오류 등)"""
    def __init__(self, message="인증이 실패하였습니다.", details=None, error_code="AUTH_INVALID_CREDENTIALS"):
        super().__init__(message, details, error_code)


class AuthorizationError(BaseCustomException):
    """권한 없음 (토큰은 있지만 접근 권한 부족)"""
    def __init__(self, message="접근 권한이 없습니다.", details=None, error_code="AUTH_FORBIDDEN"):
        super().__init__(message, details, error_code)


class DatabaseError(BaseCustomException):
    """데이터베이스 관련 에러"""
    def __init__(self, message="데이터베이스 오류가 발생하였습니다.", details=None, error_code="DATABASE_ERROR"):
        super().__init__(message, details, error_code)


class ExternalAPIError(BaseCustomException):
    """외부 API 연동 실패"""
    def __init__(self, message="외부 서비스 연결에 실패하였습니다.", details=None, error_code="EXTERNAL_API_ERROR"):
        super().__init__(message, details, error_code)


class SessionError(BaseCustomException):
    """세션 처리 중 오류 발생"""
    def __init__(self, message="세션 처리 중 오류가 발생하였습니다.", details=None, error_code="SESSION_ERROR"):
        super().__init__(message, details, error_code)


class AgentError(BaseCustomException):
    """에이전트 처리 오류"""
    def __init__(self, message="에이전트 처리 중 오류가 발생하였습니다.", details=None, error_code="AGENT_ERROR"):
        super().__init__(message, details, error_code)


class DuplicateError(BaseCustomException):
    """중복된 로그인ID 또는 이메일 등"""
    def __init__(self, message="이미 존재하는 값입니다.", details=None, error_code="DUPLICATE_VALUE"):
        super().__init__(message, details, error_code)


class NotFoundError(BaseCustomException):
    """리소스를 찾을 수 없음"""
    def __init__(self, message="요청한 리소스를 찾을 수 없습니다.", details=None, error_code="NOT_FOUND"):
        super().__init__(message, details, error_code)


class ConflictError(BaseCustomException):
    """리소스 충돌 (이미 처리된 요청 등)"""
    def __init__(self, message="요청이 현재 상태와 충돌합니다.", details=None, error_code="CONFLICT"):
        super().__init__(message, details, error_code)


class RateLimitError(BaseCustomException):
    """요청 횟수 제한 초과"""
    def __init__(self, message="요청 횟수 제한을 초과했습니다.", details=None, error_code="RATE_LIMIT_EXCEEDED"):
        super().__init__(message, details, error_code)


class ServiceUnavailableError(BaseCustomException):
    """서비스 일시적 사용 불가"""
    def __init__(self, message="서비스가 일시적으로 사용할 수 없습니다.", details=None, error_code="SERVICE_UNAVAILABLE"):
        super().__init__(message, details, error_code)


class AgentException(BaseCustomException):
    """에이전트 실행 중 발생하는 예외"""
    def __init__(self, message="에이전트 실행 중 오류가 발생하였습니다.", details=None, error_code="AGENT_EXCEPTION"):
        super().__init__(message, details, error_code)


class StateValidationException(BaseCustomException):
    """State 검증 실패 시 발생하는 예외"""
    def __init__(self, message="State 검증에 실패하였습니다.", details=None, error_code="STATE_VALIDATION_ERROR"):
        super().__init__(message, details, error_code)