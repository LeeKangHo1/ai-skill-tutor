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
    
    # Blueprint 등록 (추후 라우트 추가 시 사용)
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # 기본 에러 핸들러 등록
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """에러 핸들러 등록 함수"""
    
    @app.errorhandler(404)
    def not_found(error):
        """404 에러 핸들러"""
        return {"error": "Not found", "message": "요청한 리소스를 찾을 수 없습니다."}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 에러 핸들러"""
        return {"error": "Internal server error", "message": "서버 내부 오류가 발생했습니다."}, 500