# backend/app/routes/dashboard/__init__.py
"""
대시보드 관련 라우트들
사용자 대시보드 기능을 제공합니다.
"""

from .overview import overview_bp
from .statistics import statistics_bp

__all__ = ['overview_bp', 'statistics_bp']