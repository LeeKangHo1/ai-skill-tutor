# backend/app/routes/dashboard/__init__.py
# 대시보드 라우트 Blueprint 정의

from .overview import dashboard_overview_bp

# 대시보드 관련 Blueprint 목록
dashboard_blueprints = [
    (dashboard_overview_bp, '/api/v1/dashboard')
]