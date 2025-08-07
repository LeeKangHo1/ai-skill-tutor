# backend/app/middleware/request/cors_middleware.py
"""
CORS 처리 미들웨어 모듈
Cross-Origin Resource Sharing 설정을 관리합니다.
"""

from flask import Flask
from flask_cors import CORS
import os
from typing import List, Optional

class CORSMiddleware:
    """CORS 처리 미들웨어 클래스"""
    
    def __init__(self):
        """CORS 미들웨어 초기화"""
        self.allowed_origins = self._get_allowed_origins()
        self.allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        self.allowed_headers = [
            'Content-Type',
            'Authorization',
            'X-Session-Token',
            'X-Requested-With'
        ]
        self.expose_headers = ['X-Total-Count', 'X-Page-Count']
        self.supports_credentials = True
        self.max_age = 86400  # 24시간
    
    def _get_allowed_origins(self) -> List[str]:
        """
        허용된 오리진 목록을 가져옵니다.
        
        Returns:
            List[str]: 허용된 오리진 목록
        """
        origins_env = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173')
        origins = [origin.strip() for origin in origins_env.split(',')]
        
        # 개발 환경에서는 추가 오리진 허용
        if os.getenv('FLASK_ENV') == 'development':
            dev_origins = [
                'http://localhost:3000',
                'http://localhost:5173',
                'http://localhost:8080',
                'http://127.0.0.1:5173',
                'http://127.0.0.1:3000'
            ]
            origins.extend(dev_origins)
        
        return list(set(origins))  # 중복 제거
    
    def init_app(self, app: Flask) -> None:
        """
        Flask 앱에 CORS 설정을 적용합니다.
        
        Args:
            app (Flask): Flask 애플리케이션 인스턴스
        """
        CORS(
            app,
            origins=self.allowed_origins,
            methods=self.allowed_methods,
            allow_headers=self.allowed_headers,
            expose_headers=self.expose_headers,
            supports_credentials=self.supports_credentials,
            max_age=self.max_age
        )
        
        # 개발 환경에서는 CORS 로그 출력
        if os.getenv('FLASK_ENV') == 'development':
            print(f"CORS 설정 완료:")
            print(f"  - 허용된 오리진: {self.allowed_origins}")
            print(f"  - 허용된 메서드: {self.allowed_methods}")
            print(f"  - 허용된 헤더: {self.allowed_headers}")
    
    def is_origin_allowed(self, origin: str) -> bool:
        """
        특정 오리진이 허용되는지 확인합니다.
        
        Args:
            origin (str): 확인할 오리진
            
        Returns:
            bool: 허용 여부
        """
        return origin in self.allowed_origins
    
    def add_allowed_origin(self, origin: str) -> None:
        """
        허용된 오리진을 추가합니다.
        
        Args:
            origin (str): 추가할 오리진
        """
        if origin not in self.allowed_origins:
            self.allowed_origins.append(origin)
    
    def remove_allowed_origin(self, origin: str) -> None:
        """
        허용된 오리진을 제거합니다.
        
        Args:
            origin (str): 제거할 오리진
        """
        if origin in self.allowed_origins:
            self.allowed_origins.remove(origin)

# 전역 CORS 미들웨어 인스턴스
cors_middleware = CORSMiddleware()