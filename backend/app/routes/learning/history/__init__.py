# backend/app/routes/learning/history/__init__.py
"""
학습 기록 관련 라우트들
사용자의 학습 기록 조회 기능을 제공합니다.
"""

from .list import list_bp
from .details import details_bp

__all__ = ['list_bp', 'details_bp']