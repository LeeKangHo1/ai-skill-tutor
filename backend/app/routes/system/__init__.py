# backend/app/routes/system/__init__.py
# 시스템 관련 라우트 패키지

from .health import health_bp
from .version import version_bp

# 시스템 관련 Blueprint 목록 (diagnosis와 동일한 형식)
system_blueprints = [
    (health_bp, '/api/v1/system'),
    (version_bp, '/api/v1/system')
]