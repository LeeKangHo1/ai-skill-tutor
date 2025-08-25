# backend/app/utils/logging/logger.py

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class AppLogger:
    """
    애플리케이션 로깅 시스템
    """

    def __init__(self, app=None):
        self.app = app
        self.handlers_configured = False
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Flask 앱에 로깅 설정 초기화"""
        if not self.handlers_configured:
            self.setup_logging(app)
            self.handlers_configured = True

    def setup_logging(self, app):
        """로깅 설정"""
        log_dir = os.path.join(os.path.dirname(app.root_path), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"로그 디렉토리 생성: {log_dir}")

        for handler in app.logger.handlers[:]:
            app.logger.removeHandler(handler)

        log_level = app.config.get('LOG_LEVEL', 'INFO')
        app.logger.setLevel(getattr(logging, log_level))

        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        self._setup_file_handlers(app, log_dir, formatter)
        self._setup_console_handler(app, formatter)

        app.logger.info("로깅 시스템이 초기화되었습니다.")
        print("로깅 시스템 설정 완료")

    def _setup_file_handlers(self, app, log_dir, formatter):
        """파일 핸들러들 설정 (RotatingFileHandler 사용)"""

        app_log_path = os.path.join(log_dir, 'app.log')
        app_handler = RotatingFileHandler(
            app_log_path,
            maxBytes=1 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(formatter)
        app.logger.addHandler(app_handler)
        print(f"앱 로그 파일: {app_log_path}")

        error_log_path = os.path.join(log_dir, 'error.log')
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        app.logger.addHandler(error_handler)
        print(f"에러 로그 파일: {error_log_path}")

        self._setup_access_logger(log_dir)

    def _setup_access_logger(self, log_dir):
        """접근 로그 설정 (RotatingFileHandler 사용)"""
        access_logger = logging.getLogger('access')

        for handler in access_logger.handlers[:]:
            access_logger.removeHandler(handler)

        access_log_path = os.path.join(log_dir, 'access.log')
        access_handler = RotatingFileHandler(
            access_log_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        access_formatter = logging.Formatter(
            '[%(asctime)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        access_handler.setFormatter(access_formatter)
        access_logger.addHandler(access_handler)
        access_logger.setLevel(logging.INFO)
        access_logger.propagate = False
        print(f"접근 로그 파일: {access_log_path}")

    def _setup_console_handler(self, app, formatter):
        """콘솔 핸들러 설정"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)
        print("콘솔 핸들러 설정 완료")


def log_api_access(method, endpoint, status_code, response_time=None, user_id=None):
    """
    API 접근 로그 기록
    """
    access_logger = logging.getLogger('access')

    log_message = f"{method} {endpoint} - {status_code}"

    if response_time:
        log_message += f" - {response_time}ms"

    if user_id:
        log_message += f" - user:{user_id}"

    access_logger.info(log_message)


def log_error(error, context=None):
    """
    에러 로그 기록
    """
    import traceback
    from flask import current_app

    error_message = f"Error: {str(error)}"

    if context:
        error_message += f" | Context: {context}"

    error_message += f"\nTraceback: {traceback.format_exc()}"

    if current_app:
        current_app.logger.error(error_message)
    else:
        logging.error(error_message)


def log_user_action(user_id, action, details=None):
    """
    사용자 행동 로그 기록
    """
    from flask import current_app

    log_message = f"User {user_id}: {action}"

    if details:
        log_message += f" | Details: {details}"

    if current_app:
        current_app.logger.info(log_message)
    else:
        logging.info(log_message)


app_logger = AppLogger()
