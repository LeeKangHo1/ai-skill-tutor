# backend/app/__init__.py
# Flask 애플리케이션 팩토리 파일

from flask import Flask, request, g
from flask_cors import CORS
from .config import config
from .utils.logging.logger import app_logger, log_api_access
import time

def create_app(config_name='default'):
    """Flask 애플리케이션 팩토리 함수
    
    Args:
        config_name (str): 사용할 설정 이름 ('development', 'production', 'default')
    
    Returns:
        Flask: 설정된 Flask 애플리케이션 인스턴스
    """
    # Flask 앱 인스턴스 생성
    app = Flask(__name__)
    
    # 설정 로드
    app.config.from_object(config[config_name])
    
    # 로깅 시스템 초기화
    app_logger.init_app(app)
    
    # CORS 설정 (프론트엔드와의 통신을 위해)
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,  # HttpOnly 쿠키 사용을 위해 필요
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # 요청 전후 처리 (로깅용)
    register_request_handlers(app)
    
    # Blueprint 등록
    register_blueprints(app)

    # 기본 에러 핸들러 등록
    register_error_handlers(app)
    
    return app

def register_request_handlers(app):
    """요청 전후 처리 함수 등록"""
    
    @app.before_request
    def before_request():
        """요청 시작 시간 기록"""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """요청 완료 후 로그 기록"""
        if hasattr(g, 'start_time'):
            response_time = int((time.time() - g.start_time) * 1000)  # 밀리초
            
            # API 접근 로그 기록
            log_api_access(
                method=request.method,
                endpoint=request.endpoint or request.path,
                status_code=response.status_code,
                response_time=response_time,
                user_id=getattr(g, 'current_user_id', None)
            )
        
        return response

def register_blueprints(app):
    """Blueprint 등록 함수
    
    Args:
        app (Flask): Flask 애플리케이션 인스턴스
    """
    # 시스템 관련 Blueprint들 등록
    from .routes.system import system_blueprints
    for blueprint, url_prefix in system_blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
    
    # 진단 관련 Blueprint들 등록
    from .routes.diagnosis import diagnosis_blueprints
    for blueprint, url_prefix in diagnosis_blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
    
    # 인증 관련 Blueprint들 등록
    from .routes.auth import register_bp, login_bp, token_bp
    app.register_blueprint(register_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(login_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(token_bp, url_prefix='/api/v1/auth')
    
    # 학습 관련 Blueprint들 등록
    from .routes.learning.session.start import session_start_bp
    from .routes.learning.session.message import session_message_bp
    from .routes.learning.quiz.submit import quiz_submit_bp
    from .routes.learning.session.complete import session_complete_bp
    app.register_blueprint(session_start_bp, url_prefix='/api/v1/learning/session')
    app.register_blueprint(session_message_bp, url_prefix='/api/v1/learning/session')
    app.register_blueprint(quiz_submit_bp, url_prefix='/api/v1/learning/quiz')
    app.register_blueprint(session_complete_bp, url_prefix='/api/v1/learning/session')

    from .routes.learning.session.message_qna import message_qna_bp
    app.register_blueprint(message_qna_bp, url_prefix='/api/v1/learning')
    from .routes.learning.session.qna_stream import qna_stream_bp
    app.register_blueprint(qna_stream_bp, url_prefix='/api/v1/learning')

    # 대시보드 관련 Blueprint들 등록
    from .routes.dashboard.overview import overview_bp
    app.register_blueprint(overview_bp, url_prefix='/api/v1/dashboard')
    

def register_error_handlers(app):
    """에러 핸들러 등록 함수
    
    Args:
        app (Flask): Flask 애플리케이션 인스턴스
    """
    from .utils.logging.logger import log_error
    
    @app.errorhandler(404)
    def not_found(error):
        """404 에러 핸들러"""
        app.logger.warning(f"404 Error: {request.path}")
        return {"error": "Not found", "message": "요청한 리소스를 찾을 수 없습니다."}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 에러 핸들러"""
        log_error(error, {"path": request.path, "method": request.method})
        return {"error": "Internal server error", "message": "서버 내부 오류가 발생했습니다."}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """400 에러 핸들러"""
        app.logger.warning(f"400 Error: {request.path} - {error}")
        return {"error": "Bad request", "message": "잘못된 요청입니다."}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """401 에러 핸들러"""
        app.logger.warning(f"403 Error: {request.path}")
        return {"error": "Unauthorized", "message": "인증이 필요합니다."}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """403 에러 핸들러"""
        app.logger.warning(f"403 Error: {request.path}")
        return {"error": "Forbidden", "message": "접근 권한이 없습니다."}, 403