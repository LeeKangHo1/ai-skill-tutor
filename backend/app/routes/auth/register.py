# backend/app/routes/auth/register.py
"""
회원가입 라우트
사용자 회원가입 기능을 제공합니다.
"""

from flask import Blueprint

# 회원가입 Blueprint 생성
register_bp = Blueprint('register', __name__, url_prefix='/auth')


@register_bp.route('/register', methods=['POST'])
def register():
    """
    사용자 회원가입 엔드포인트
    향후 사용자 등록 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": "Register endpoint - to be implemented"}