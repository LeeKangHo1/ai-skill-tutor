# backend/app/middleware/error/exception_mapper.py
"""
예외 매핑 모듈
커스텀 예외를 HTTP 상태 코드와 메시지로 매핑합니다.
"""

from typing import Dict, Tuple, Type
from app.utils.common.exceptions import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    BusinessLogicError
)

class ExceptionMapper:
    """예외를 HTTP 응답으로 매핑하는 클래스"""
    
    def __init__(self):
        """예외 매퍼 초기화"""
        self.exception_mappings = self._initialize_mappings()
    
    def _initialize_mappings(self) -> Dict[Type[Exception], Tuple[int, str]]:
        """
        예외 타입과 HTTP 응답 매핑을 초기화합니다.
        
        Returns:
            Dict[Type[Exception], Tuple[int, str]]: 예외 타입별 (상태코드, 기본메시지) 매핑
        """
        return {
            # 검증 관련 예외
            ValidationError: (400, "입력 데이터가 유효하지 않습니다."),
            ValueError: (400, "잘못된 값입니다."),
            TypeError: (400, "잘못된 데이터 타입입니다."),
            
            # 인증 관련 예외
            AuthenticationError: (401, "인증이 필요합니다."),
            
            # 권한 관련 예외
            AuthorizationError: (403, "접근 권한이 없습니다."),
            PermissionError: (403, "권한이 부족합니다."),
            
            # 리소스 관련 예외
            NotFoundError: (404, "요청한 리소스를 찾을 수 없습니다."),
            FileNotFoundError: (404, "파일을 찾을 수 없습니다."),
            
            # 충돌 관련 예외
            ConflictError: (409, "리소스 충돌이 발생했습니다."),
            
            # 비즈니스 로직 예외
            BusinessLogicError: (422, "비즈니스 규칙 위반입니다."),
            
            # 시스템 예외
            ConnectionError: (503, "외부 서비스 연결에 실패했습니다."),
            TimeoutError: (504, "요청 시간이 초과되었습니다."),
        }
    
    def get_http_response(self, exception: Exception) -> Tuple[int, str]:
        """
        예외를 HTTP 상태 코드와 메시지로 변환합니다.
        
        Args:
            exception (Exception): 변환할 예외
            
        Returns:
            Tuple[int, str]: (HTTP 상태 코드, 에러 메시지)
        """
        exception_type = type(exception)
        
        # 직접 매핑된 예외 타입 확인
        if exception_type in self.exception_mappings:
            status_code, default_message = self.exception_mappings[exception_type]
            # 예외에 메시지가 있으면 사용, 없으면 기본 메시지 사용
            message = str(exception) if str(exception) else default_message
            return status_code, message
        
        # 상속 관계 확인
        for mapped_type, (status_code, default_message) in self.exception_mappings.items():
            if isinstance(exception, mapped_type):
                message = str(exception) if str(exception) else default_message
                return status_code, message
        
        # 매핑되지 않은 예외는 500으로 처리
        return 500, "서버 내부 오류가 발생했습니다."
    
    def add_mapping(self, exception_type: Type[Exception], status_code: int, default_message: str) -> None:
        """
        새로운 예외 매핑을 추가합니다.
        
        Args:
            exception_type (Type[Exception]): 예외 타입
            status_code (int): HTTP 상태 코드
            default_message (str): 기본 에러 메시지
        """
        self.exception_mappings[exception_type] = (status_code, default_message)
    
    def remove_mapping(self, exception_type: Type[Exception]) -> None:
        """
        예외 매핑을 제거합니다.
        
        Args:
            exception_type (Type[Exception]): 제거할 예외 타입
        """
        if exception_type in self.exception_mappings:
            del self.exception_mappings[exception_type]
    
    def get_all_mappings(self) -> Dict[str, Tuple[int, str]]:
        """
        모든 예외 매핑을 반환합니다.
        
        Returns:
            Dict[str, Tuple[int, str]]: 예외 이름별 (상태코드, 메시지) 매핑
        """
        return {
            exception_type.__name__: (status_code, message)
            for exception_type, (status_code, message) in self.exception_mappings.items()
        }
    
    def is_client_error(self, exception: Exception) -> bool:
        """
        클라이언트 오류인지 확인합니다 (4xx 상태 코드).
        
        Args:
            exception (Exception): 확인할 예외
            
        Returns:
            bool: 클라이언트 오류 여부
        """
        status_code, _ = self.get_http_response(exception)
        return 400 <= status_code < 500
    
    def is_server_error(self, exception: Exception) -> bool:
        """
        서버 오류인지 확인합니다 (5xx 상태 코드).
        
        Args:
            exception (Exception): 확인할 예외
            
        Returns:
            bool: 서버 오류 여부
        """
        status_code, _ = self.get_http_response(exception)
        return status_code >= 500

# 전역 예외 매퍼 인스턴스
exception_mapper = ExceptionMapper()