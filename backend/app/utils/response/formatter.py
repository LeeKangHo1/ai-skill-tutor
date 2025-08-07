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
    def success_response(data=None, message="Success", status_code=200):
        """
        성공 응답 포맷팅
        향후 구현될 예정입니다.
        """
        pass
    
    @staticmethod
    def error_response(error_message, status_code=400, error_code=None):
        """
        에러 응답 포맷팅
        향후 구현될 예정입니다.
        """
        pass
    
    @staticmethod
    def paginated_response(data, page, per_page, total):
        """
        페이지네이션 응답 포맷팅
        향후 구현될 예정입니다.
        """
        pass
    
    @staticmethod
    def validation_error_response(validation_errors):
        """
        검증 에러 응답 포맷팅
        향후 구현될 예정입니다.
        """
        pass