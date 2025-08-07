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
        검증 에러 포맷팅
        향후 구현될 예정입니다.
        """
        pass
    
    @staticmethod
    def format_authentication_error(error_type):
        """
        인증 에러 포맷팅
        향후 구현될 예정입니다.
        """
        pass
    
    @staticmethod
    def format_authorization_error(resource, action):
        """
        권한 에러 포맷팅
        향후 구현될 예정입니다.
        """
        pass
    
    @staticmethod
    def format_database_error(error):
        """
        데이터베이스 에러 포맷팅
        향후 구현될 예정입니다.
        """
        pass
    
    @staticmethod
    def format_external_api_error(service_name, error):
        """
        외부 API 에러 포맷팅
        향후 구현될 예정입니다.
        """
        pass