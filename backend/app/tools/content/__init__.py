# backend/app/tools/content/__init__.py
"""
컨텐츠 생성 도구들
이론 설명, 퀴즈, 피드백 생성을 위한 도구 함수들을 제공합니다.
"""

# from .theory_tools_gemini import theory_generation_tool as theory_generation_tool_gemini  # gemini_client 삭제로 임시 주석
from .theory_tools_chatgpt import theory_generation_tool as theory_generation_tool_chatgpt
from .quiz_tools_chatgpt import quiz_generation_tool
from .feedback_tools_chatgpt import (
    evaluate_subjective_with_feedback,
    generate_multiple_choice_feedback,
    generate_simple_feedback
)

__all__ = [
    # 'theory_generation_tool_gemini',  # gemini_client 삭제로 임시 주석
    'theory_generation_tool_chatgpt', 
    'quiz_generation_tool',
    'evaluate_subjective_with_feedback',
    'generate_multiple_choice_feedback',
    'generate_simple_feedback'
]