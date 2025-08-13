# backend/tests/0813/test_three_agents/conftest.py
"""
pytest 설정 파일 - 세 에이전트 통합 테스트용
"""

import pytest
import sys
import os
from unittest.mock import patch

# 백엔드 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """테스트 환경 설정"""
    # 환경변수 설정 (테스트용)
    os.environ.setdefault('FLASK_ENV', 'testing')
    os.environ.setdefault('OPENAI_API_KEY', 'test-key')
    os.environ.setdefault('GOOGLE_API_KEY', 'test-key')
    os.environ.setdefault('LANGCHAIN_API_KEY', 'test-key')
    os.environ.setdefault('LANGCHAIN_PROJECT', 'test-project')
    
    print("테스트 환경 설정 완료")
    yield
    print("테스트 환경 정리 완료")

@pytest.fixture
def mock_openai_response():
    """OpenAI API 응답 모킹"""
    return {
        "theory": "이것은 테스트용 이론 설명입니다.",
        "quiz": {
            "question": "테스트 문제입니다.",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        },
        "feedback": "이것은 테스트용 피드백입니다."
    }

@pytest.fixture
def mock_gemini_response():
    """Gemini API 응답 모킹"""
    return {
        "theory": "이것은 Gemini 테스트용 이론 설명입니다.",
        "quiz": {
            "question": "Gemini 테스트 문제입니다.",
            "type": "subjective",
            "example_answer": "예시 답변입니다."
        },
        "feedback": "이것은 Gemini 테스트용 피드백입니다."
    }