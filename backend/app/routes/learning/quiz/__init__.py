# backend/app/routes/learning/quiz/__init__.py
"""
퀴즈 관리 관련 라우트들
퀴즈 답변 제출 및 힌트 요청 기능을 제공합니다.
"""

from .submit import quiz_submit_bp

__all__ = ['quiz_submit_bp']