# backend/app/agents/quiz_generator/__init__.py
"""
퀴즈 생성 에이전트
학습 내용에 대한 퀴즈를 생성하는 에이전트입니다.
"""

from .quiz_generator_agent import QuizGenerator

__all__ = ['QuizGenerator']