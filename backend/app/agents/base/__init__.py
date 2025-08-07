# backend/app/agents/base/__init__.py
"""
기본 에이전트 구성 요소들
모든 에이전트가 공통으로 사용하는 기본 클래스와 설정을 제공합니다.
"""

from .base_agent import BaseAgent
from .agent_config import AgentConfig

__all__ = ['BaseAgent', 'AgentConfig']