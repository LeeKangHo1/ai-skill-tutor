# backend/app/middleware/error/error_handler.py
"""
전역 에러 핸들러 모듈
애플리케이션 전체의 예외를 처리하고 적절한 응답을 생성합니다.
"""

from flask import Flask, jsonify, request
import traceback
import logging
import os
from typing import Dict, Any, Tuple

class ErrorHandler:
    """전역 에러 핸들러 클래스"""
    
    def __init__(self):
        """에러 핸들러 초기화"""
        self.logger = logging.getLogger(__name__)
        self.debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    def init_app(self, app: Flask) -> None:
        """
        Flask 앱에 에러 핸들러를 등록합니다.
        
        Args:
            app (Flask): Flask 애플리케이션 인스턴스
        """
        # 400 Bad Request
        @app.errorhandler(400)
        def handle_bad_request(error):
            return self._create_error_response(
                400, 
                "잘못된 요청입니다.", 
                error
            )
        
        # 401 Unauthorized
        @app.errorhandler(401)
        def handle_unauthorized(error):
            return self._create_error_response(
                401, 
                "인증이 필요합니다.", 
                error
            )
        
        # 403 Forbidden
        @app.errorhandler(403)
        def handle_forbidden(error):
            return self._create_error_response(
                403, 
                "접근 권한이 없습니다.", 
                error
            )
        
        # 404 Not Found
        @app.errorhandler(404)
        def handle_not_found(error):
            return self._create_error_response(
                404, 
                "요청한 리소스를 찾을 수 없습니다.", 
                error
            )
        
        # 405 Method Not Allowed
        @app.errorhandler(405)
        def handle_method_not_allowed(error):
            return self._create_error_response(
                405, 
                "허용되지 않은 HTTP 메서드입니다.", 
                error
            )
        
        # 413 Request Entity Too Large
        @app.errorhandler(413)
        def handle_request_too_large(error):
            return self._create_error_response(
                413, 
                "요청 크기가 너무 큽니다.", 
                error
            )
        
        # 429 Too Many Requests
        @app.errorhandler(429)
        def handle_too_many_requests(error):
            return self._create_error_response(
                429, 
                "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.", 
                error
            )
        
        # 500 Internal Server Error
        @app.errorhandler(500)
        def handle_internal_server_error(error):
            return self._create_error_response(
                500, 
                "서버 내부 오류가 발생했습니다.", 
                error
            )
        
        # 일반적인 Exception 처리
        @app.errorhandler(Exception)
        def handle_general_exception(error):
            # 로그 기록
            self.logger.error(f"예상치 못한 오류 발생: {str(error)}")
            self.logger.error(f"요청 URL: {request.url}")
            self.logger.error(f"요청 메서드: {request.method}")
            if self.debug_mode:
                self.logger.error(f"스택 트레이스:\n{traceback.format_exc()}")
            
            return self._create_error_response(
                500, 
                "예상치 못한 오류가 발생했습니다.", 
                error
            )
    
    def _create_error_response(self, status_code: int, message: str, error: Exception) -> Tuple[Dict[str, Any], int]:
        """
        에러 응답을 생성합니다.
        
        Args:
            status_code (int): HTTP 상태 코드
            message (str): 에러 메시지
            error (Exception): 발생한 예외
            
        Returns:
            Tuple[Dict[str, Any], int]: 응답 데이터와 상태 코드
        """
        response_data = {
            'success': False,
            'error': {
                'code': status_code,
                'message': message,
                'timestamp': self._get_current_timestamp()
            }
        }
        
        # 개발 환경에서는 추가 디버그 정보 포함
        if self.debug_mode:
            response_data['error']['debug'] = {
                'type': type(error).__name__,
                'details': str(error),
                'url': request.url,
                'method': request.method
            }
            
            # 스택 트레이스 포함 (500 에러의 경우)
            if status_code == 500:
                response_data['error']['debug']['traceback'] = traceback.format_exc()
        
        return jsonify(response_data), status_code
    
    def _get_current_timestamp(self) -> str:
        """
        현재 타임스탬프를 ISO 형식으로 반환합니다.
        
        Returns:
            str: ISO 형식 타임스탬프
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """
        에러를 로그에 기록합니다.
        
        Args:
            error (Exception): 기록할 예외
            context (Dict[str, Any]): 추가 컨텍스트 정보
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'url': request.url if request else 'N/A',
            'method': request.method if request else 'N/A',
            'user_agent': request.headers.get('User-Agent') if request else 'N/A',
            'remote_addr': request.remote_addr if request else 'N/A'
        }
        
        if context:
            error_info.update(context)
        
        self.logger.error(f"에러 발생: {error_info}")
        
        if self.debug_mode:
            self.logger.error(f"스택 트레이스:\n{traceback.format_exc()}")

# 전역 에러 핸들러 인스턴스
error_handler = ErrorHandler()