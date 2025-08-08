# backend/app/utils/response/error_formatter.py
"""
에러 응답 포맷터
에러 상황에 대한 응답을 포맷팅하는 유틸리티입니다.
"""


class ErrorFormatter:
    """
    에러 포맷터 클래스
    다양한 에러 상황에 대한 응답을 표준화합니다.
    """

    @staticmethod
    def format_validation_error(field_errors):
        """
        입력 필드 검증 에러 포맷팅
        :param field_errors: {"email": "이메일 형식이 잘못되었습니다.", "password": "비밀번호는 8자 이상이어야 합니다."}
        """
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "입력값이 올바르지 않습니다.",
                "details": field_errors
            }
        }, 400

    @staticmethod
    def format_authentication_error(error_type="invalid_credentials"):
        """
        인증 실패 에러 포맷팅
        :param error_type: "invalid_credentials", "token_expired", "token_invalid" 등
        """
        messages = {
            "invalid_credentials": ("AUTH_INVALID_CREDENTIALS", "로그인 정보가 올바르지 않습니다."),
            "token_expired": ("AUTH_TOKEN_EXPIRED", "토큰이 만료되었습니다."),
            "token_invalid": ("AUTH_TOKEN_INVALID", "유효하지 않은 토큰입니다."),
            "refresh_expired": ("AUTH_REFRESH_TOKEN_EXPIRED", "리프레시 토큰이 만료되었습니다.")
        }
        code, message = messages.get(error_type, ("AUTH_ERROR", "인증에 실패하였습니다."))

        return {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": {}
            }
        }, 401

    @staticmethod
    def format_authorization_error(resource="해당 리소스", action="접근"):
        """
        권한 없음 에러 포맷팅
        """
        return {
            "success": False,
            "error": {
                "code": "AUTH_FORBIDDEN",
                "message": f"{resource}에 대해 {action} 권한이 없습니다.",
                "details": {}
            }
        }, 403

    @staticmethod
    def format_database_error(error: Exception):
        """
        데이터베이스 에러 포맷팅
        """
        return {
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "데이터베이스 오류가 발생하였습니다.",
                "details": {
                    "error_message": str(error)
                }
            }
        }, 500

    @staticmethod
    def format_external_api_error(service_name="외부 서비스", error=None):
        """
        외부 API 연동 실패 에러 포맷팅
        """
        return {
            "success": False,
            "error": {
                "code": "EXTERNAL_API_ERROR",
                "message": f"{service_name} 호출 중 오류가 발생하였습니다.",
                "details": {
                    "error_message": str(error) if error else ""
                }
            }
        }, 503
