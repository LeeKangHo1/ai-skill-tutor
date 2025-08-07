# backend/app/routes/auth/login.py
"""
로그인/로그아웃 라우트
사용자 로그인 및 로그아웃 기능을 제공합니다.
"""

from flask import Blueprint

# 로그인 Blueprint 생성
login_bp = Blueprint('login', __name__, url_prefix='/auth')


@login_bp.route('/login', methods=['POST'])
def login():
    """
    사용자 로그인 엔드포인트
    향후 인증 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": "Login endpoint - to be implemented"}


@login_bp.route('/logout', methods=['POST'])
def logout():
    """
    사용자 로그아웃 엔드포인트
    향후 토큰 무효화 로직과 함께 구현될 예정입니다.
    """
    return {"message": "Logout endpoint - to be implemented"}