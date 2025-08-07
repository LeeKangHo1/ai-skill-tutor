# backend/app/routes/diagnosis/__init__.py
"""
사용자 진단 관련 라우트들
사용자 유형 진단 기능을 제공합니다.
"""

from .questions import questions_bp
from .submit import submit_bp

__all__ = ['questions_bp', 'submit_bp']