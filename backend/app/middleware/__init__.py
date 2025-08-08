# app/middleware/__init__.py

from .auth.jwt_middleware import JWTMiddleware


def init_middlewares(app):
    """
    모든 미들웨어를 Flask 앱에 등록
    
    Args:
        app (Flask): Flask 애플리케이션 인스턴스
    """
    # JWT 인증 미들웨어 등록
    jwt_middleware = JWTMiddleware(app)
    
    # 향후 추가될 미들웨어들
    # CORS 미들웨어 (이미 Flask-CORS로 처리됨)
    # Rate Limiting 미들웨어
    # Request Validation 미들웨어
    # Error Handling 미들웨어 (이미 error_handlers로 처리됨)
    
    return {
        'jwt_middleware': jwt_middleware
    }