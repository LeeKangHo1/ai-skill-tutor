# backend/app/utils/common/exceptions.py
"""
커스텀 예외 클래스들
애플리케이션에서 사용하는 커스텀 예외들을 정의합니다.
"""


class BaseCustomException(Exception):
    """기본 커스텀 예외 클래스"""
    
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(BaseCustomException):
    """검증 에러 예외"""
    pass


class AuthenticationError(BaseCustomException):
    """인증 에러 예외"""
    pass


class AuthorizationError(BaseCustomException):
    """권한 에러 예외"""
    pass


class DatabaseError(BaseCustomException):
    """데이터베이스 에러 예외"""
    pass


class ExternalAPIError(BaseCustomException):
    """외부 API 에러 예외"""
    pass


class SessionError(BaseCustomException):
    """세션 관련 에러 예외"""
    pass


class AgentError(BaseCustomException):
    """에이전트 관련 에러 예외"""
    pass