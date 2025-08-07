# backend/app/routes/system/__init__.py
# 시스템 관련 라우트 패키지

from .health import health_bp
from .version import version_bp

# 시스템 관련 Blueprint들을 외부에서 import할 수 있도록 노출
__all__ = ['health_bp', 'version_bp']