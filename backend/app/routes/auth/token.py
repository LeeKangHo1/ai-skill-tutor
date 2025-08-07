# backend/app/routes/auth/token.py
"""
토큰 관리 라우트
JWT 토큰 갱신 및 검증 기능을 제공합니다.
"""

from flask import Blueprint

# 토큰 관리 Blueprint 생성
token_bp = Blueprint('token', __name__, url_prefix='/auth')


@token_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    토큰 갱신 엔드포인트
    향후 JWT 토큰 갱신 로직과 함께 구현될 예정입니다.
    """
    return {"message": "Token refresh endpoint - to be implemented"}


@token_bp.route('/verify', methods=['POST'])
def verify_token():
    """
    토큰 검증 엔드포인트
    향후 JWT 토큰 검증 로직과 함께 구현될 예정입니다.
    """
    return {"message": "Token verify endpoint - to be implemented"}