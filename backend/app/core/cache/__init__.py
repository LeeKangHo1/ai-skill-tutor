# backend/app/core/cache/__init__.py
"""
캐시 관련 모듈
Redis 클라이언트 등 캐시 시스템을 관리합니다.
"""

from .redis_client import RedisClient

__all__ = ['RedisClient']