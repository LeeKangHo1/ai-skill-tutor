# backend/app/services/auth/token_service.py
"""
토큰 관리 서비스
JWT 토큰 생성, 검증, 갱신 등을 담당합니다.
"""


class TokenService:
    """
    토큰 서비스 클래스
    JWT 토큰의 생성, 검증, 갱신을 담당합니다.
    """
    
    def __init__(self):
        """토큰 서비스 초기화"""
        pass
    
    def generate_access_token(self, user_id):
        """
        액세스 토큰 생성
        향후 구현될 예정입니다.
        """
        pass
    
    def generate_refresh_token(self, user_id):
        """
        리프레시 토큰 생성
        향후 구현될 예정입니다.
        """
        pass
    
    def verify_token(self, token):
        """
        토큰 검증
        향후 구현될 예정입니다.
        """
        pass
    
    def refresh_access_token(self, refresh_token):
        """
        액세스 토큰 갱신
        향후 구현될 예정입니다.
        """
        pass