# backend/app/utils/response/formatter.py
"""
응답 포맷터
API 응답을 일관된 형식으로 포맷팅하는 유틸리티입니다.
"""


class ResponseFormatter:
    """
    응답 포맷터 클래스
    API 응답을 표준화된 형식으로 포맷팅합니다.
    """

    @staticmethod
    def success_response(data=None, message="요청이 성공적으로 처리되었습니다.", status_code=200):
        """
        성공 응답 포맷팅
        """
        return {
            "success": True,
            "data": data,
            "message": message
        }, status_code

    @staticmethod
    def error_response(code, message, details=None, status_code=400):
        """에러 응답 포맷팅 (파라미터 순서 개선)"""
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {}
            }
        }, status_code

    @staticmethod
    def paginated_response(data, page, per_page, total, message="데이터가 성공적으로 조회되었습니다."):
        """
        페이지네이션 응답 포맷팅
        """
        return {
            "success": True,
            "data": {
                "items": data,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            },
            "message": message
        }, 200

    @staticmethod
    def validation_error_response(validation_errors):
        """
        검증 에러 응답 포맷팅
        """
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "입력값이 올바르지 않습니다.",
                "details": validation_errors
            }
        }, 400

# backend/app/utils/response/formatter.py 맨 아래

# 외부에서 함수처럼 import할 수 있도록 alias로 노출
success_response = ResponseFormatter.success_response
error_response = ResponseFormatter.error_response
paginated_response = ResponseFormatter.paginated_response
validation_error_response = ResponseFormatter.validation_error_response
