# backend/app/middleware/request/rate_limit_middleware.py
"""
속도 제한 미들웨어 모듈 (MVP에서는 기본 구현만 제공)
API 요청 속도를 제한하여 서버를 보호합니다.
"""

from functools import wraps
from flask import request, jsonify, g
from typing import Dict, Any, Optional
import time
from collections import defaultdict, deque

class RateLimitMiddleware:
    """속도 제한 미들웨어 클래스"""
    
    def __init__(self):
        """속도 제한 미들웨어 초기화"""
        # 메모리 기반 간단한 속도 제한 (운영 환경에서는 Redis 사용 권장)
        self.request_counts = defaultdict(deque)
        self.default_limit = 100  # 기본: 분당 100회
        self.default_window = 60  # 기본: 60초 윈도우
    
    def get_client_id(self) -> str:
        """
        클라이언트 식별자를 가져옵니다.
        
        Returns:
            str: 클라이언트 식별자
        """
        # 인증된 사용자의 경우 사용자 ID 사용
        if hasattr(g, 'current_user_id') and g.current_user_id:
            return f"user_{g.current_user_id}"
        
        # 세션이 있는 경우 세션 사용자 ID 사용
        if hasattr(g, 'session_user_id') and g.session_user_id:
            return f"session_{g.session_user_id}"
        
        # 그 외의 경우 IP 주소 사용
        return f"ip_{request.remote_addr}"
    
    def is_rate_limited(self, client_id: str, limit: int, window: int) -> bool:
        """
        클라이언트가 속도 제한에 걸렸는지 확인합니다.
        
        Args:
            client_id (str): 클라이언트 식별자
            limit (int): 제한 횟수
            window (int): 시간 윈도우 (초)
            
        Returns:
            bool: 속도 제한 여부
        """
        current_time = time.time()
        client_requests = self.request_counts[client_id]
        
        # 윈도우 밖의 오래된 요청들 제거
        while client_requests and client_requests[0] < current_time - window:
            client_requests.popleft()
        
        # 현재 요청 수가 제한을 초과하는지 확인
        if len(client_requests) >= limit:
            return True
        
        # 현재 요청 시간 기록
        client_requests.append(current_time)
        return False
    
    def rate_limit(self, limit: Optional[int] = None, window: Optional[int] = None):
        """
        속도 제한 데코레이터입니다.
        
        Args:
            limit (Optional[int]): 제한 횟수 (기본값: self.default_limit)
            window (Optional[int]): 시간 윈도우 초 (기본값: self.default_window)
            
        Returns:
            함수 데코레이터
        """
        actual_limit = limit or self.default_limit
        actual_window = window or self.default_window
        
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_id = self.get_client_id()
                
                if self.is_rate_limited(client_id, actual_limit, actual_window):
                    return jsonify({
                        'success': False,
                        'message': f'요청 속도 제한 초과. {actual_window}초 동안 최대 {actual_limit}회 요청 가능합니다.',
                        'retry_after': actual_window
                    }), 429
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def get_rate_limit_status(self, client_id: str, limit: int, window: int) -> Dict[str, Any]:
        """
        클라이언트의 현재 속도 제한 상태를 가져옵니다.
        
        Args:
            client_id (str): 클라이언트 식별자
            limit (int): 제한 횟수
            window (int): 시간 윈도우
            
        Returns:
            Dict[str, Any]: 속도 제한 상태 정보
        """
        current_time = time.time()
        client_requests = self.request_counts[client_id]
        
        # 윈도우 밖의 오래된 요청들 제거
        while client_requests and client_requests[0] < current_time - window:
            client_requests.popleft()
        
        remaining_requests = max(0, limit - len(client_requests))
        reset_time = current_time + window if client_requests else current_time
        
        return {
            'limit': limit,
            'remaining': remaining_requests,
            'reset_time': reset_time,
            'window': window
        }
    
    def clear_client_history(self, client_id: str) -> None:
        """
        특정 클라이언트의 요청 기록을 삭제합니다.
        
        Args:
            client_id (str): 클라이언트 식별자
        """
        if client_id in self.request_counts:
            del self.request_counts[client_id]
    
    def cleanup_old_records(self) -> None:
        """오래된 요청 기록들을 정리합니다."""
        current_time = time.time()
        cleanup_threshold = current_time - (self.default_window * 2)
        
        clients_to_remove = []
        for client_id, requests in self.request_counts.items():
            # 오래된 요청들 제거
            while requests and requests[0] < cleanup_threshold:
                requests.popleft()
            
            # 요청이 없는 클라이언트 제거 대상에 추가
            if not requests:
                clients_to_remove.append(client_id)
        
        # 빈 클라이언트 기록 제거
        for client_id in clients_to_remove:
            del self.request_counts[client_id]

# 전역 속도 제한 미들웨어 인스턴스
rate_limit_middleware = RateLimitMiddleware()

# 편의를 위한 데코레이터 함수
rate_limit = rate_limit_middleware.rate_limit