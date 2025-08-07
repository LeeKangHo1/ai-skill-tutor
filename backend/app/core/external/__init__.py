# backend/app/core/external/__init__.py
"""
외부 서비스 연동 모듈
ChromaDB, ChatGPT API 등 외부 서비스와의 연동을 관리합니다.
"""

from .vector_db import VectorDBClient
from .chatgpt_client import ChatGPTClient

__all__ = ['VectorDBClient', 'ChatGPTClient']