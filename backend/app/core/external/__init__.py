# backend/app/core/external/__init__.py
"""
외부 서비스 연동 모듈
ChromaDB, AI 클라이언트 등 외부 서비스와의 연동을 관리합니다.
"""

from .vector_db import VectorDBClient

__all__ = ['VectorDBClient']