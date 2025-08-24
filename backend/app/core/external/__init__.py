# backend/app/core/external/__init__.py
"""
외부 서비스 연동 모듈
ChromaDB, AI 클라이언트 등 외부 서비스와의 연동을 관리합니다.
"""

from .chroma_client import ChromaDBClient, get_chroma_client
from .vector_db_setup import VectorDBSetup

__all__ = [
    'ChromaDBClient',
    'get_chroma_client', 
    'VectorDBSetup'
]