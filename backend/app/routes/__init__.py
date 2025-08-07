# backend/app/routes/__init__.py
# API 라우트 모듈 초기화 파일

# 시스템 관련 Blueprint들 import
from .system import health_bp, version_bp

# 기존 main_bp는 더 이상 사용하지 않음 (system Blueprint들로 분리됨)
# 다른 라우트 모듈들도 여기서 import 예정
# from .auth import auth_bp
# from .user import user_bp

# 외부에서 사용할 Blueprint들 노출
__all__ = ['health_bp', 'version_bp']