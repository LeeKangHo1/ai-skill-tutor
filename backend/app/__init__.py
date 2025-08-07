# backend/app/__init__.py
# Flask 애플리케이션 팩토리 파일

from flask import Flask
from flask_cors import CORS
from .config import config

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
    
    # CORS 설정 (프론트엔드와의 통신을 위해)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Blueprint 등록
    register_blueprints(app)
    
    # 기본 에러 핸들러 등록
    register_error_handlers(app)
    
    return app

def register_blueprints(app):
    """Blueprint 등록 함수
    
    Args:
        app (Flask): Flask 애플리케이션 인스턴스
    """
    # 시스템 관련 Blueprint들 등록
    from .routes.system import health_bp, version_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(version_bp)
    
    # 향후 추가될 Blueprint들을 위한 주석
    # 인증 관련 Blueprint
    # from .routes.auth import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # 사용자 관련 Blueprint
    # from .routes.user import user_bp
    # app.register_blueprint(user_bp, url_prefix='/api/user')
    
    # 학습 관련 Blueprint
    # from .routes.learning import learning_bp
    # app.register_blueprint(learning_bp, url_prefix='/api/learning')

def register_error_handlers(app):
    """에러 핸들러 등록 함수
    
    Args:
        app (Flask): Flask 애플리케이션 인스턴스
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """404 에러 핸들러"""
        return {"error": "Not found", "message": "요청한 리소스를 찾을 수 없습니다."}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 에러 핸들러"""
        return {"error": "Internal server error", "message": "서버 내부 오류가 발생했습니다."}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """400 에러 핸들러"""
        return {"error": "Bad request", "message": "잘못된 요청입니다."}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """401 에러 핸들러"""
        return {"error": "Unauthorized", "message": "인증이 필요합니다."}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """403 에러 핸들러"""
        return {"error": "Forbidden", "message": "접근 권한이 없습니다."}, 403