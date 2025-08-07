# backend/app/core/cache/redis_client.py
"""
Redis 캐시 클라이언트 모듈 (선택사항)
Redis를 사용한 캐싱 기능을 제공합니다.
"""

import redis
from typing import Any, Optional, Union
import json
import os

class RedisClient:
    """Redis 캐시 클라이언트 클래스"""
    
    def __init__(self):
        """Redis 클라이언트 초기화"""
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', 6379))
        self.db = int(os.getenv('REDIS_DB', 0))
        self.password = os.getenv('REDIS_PASSWORD')
        
        self.client = None
        self._connect()
    
    def _connect(self) -> None:
        """Redis 서버에 연결합니다."""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 연결 테스트
            self.client.ping()
        except Exception as e:
            print(f"Redis 연결 실패: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """
        Redis 연결 상태를 확인합니다.
        
        Returns:
            bool: 연결 상태
        """
        if not self.client:
            return False
        
        try:
            self.client.ping()
            return True
        except Exception:
            return False
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        키-값을 Redis에 저장합니다.
        
        Args:
            key (str): 저장할 키
            value (Any): 저장할 값
            expire (Optional[int]): 만료 시간 (초)
            
        Returns:
            bool: 저장 성공 여부
        """
        if not self.is_connected():
            return False
        
        try:
            # 복잡한 객체는 JSON으로 직렬화
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = self.client.set(key, value, ex=expire)
            return bool(result)
        except Exception as e:
            print(f"Redis SET 실패 {key}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Redis에서 값을 가져옵니다.
        
        Args:
            key (str): 가져올 키
            default (Any): 기본값
            
        Returns:
            Any: 저장된 값 또는 기본값
        """
        if not self.is_connected():
            return default
        
        try:
            value = self.client.get(key)
            if value is None:
                return default
            
            # JSON 문자열인지 확인하고 파싱 시도
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            print(f"Redis GET 실패 {key}: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """
        Redis에서 키를 삭제합니다.
        
        Args:
            key (str): 삭제할 키
            
        Returns:
            bool: 삭제 성공 여부
        """
        if not self.is_connected():
            return False
        
        try:
            result = self.client.delete(key)
            return bool(result)
        except Exception as e:
            print(f"Redis DELETE 실패 {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        키가 존재하는지 확인합니다.
        
        Args:
            key (str): 확인할 키
            
        Returns:
            bool: 키 존재 여부
        """
        if not self.is_connected():
            return False
        
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"Redis EXISTS 실패 {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        키에 만료 시간을 설정합니다.
        
        Args:
            key (str): 키
            seconds (int): 만료 시간 (초)
            
        Returns:
            bool: 설정 성공 여부
        """
        if not self.is_connected():
            return False
        
        try:
            return bool(self.client.expire(key, seconds))
        except Exception as e:
            print(f"Redis EXPIRE 실패 {key}: {e}")
            return False
    
    def flush_db(self) -> bool:
        """
        현재 데이터베이스의 모든 키를 삭제합니다.
        
        Returns:
            bool: 삭제 성공 여부
        """
        if not self.is_connected():
            return False
        
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            print(f"Redis FLUSHDB 실패: {e}")
            return False