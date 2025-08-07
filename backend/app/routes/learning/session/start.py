# backend/app/routes/learning/session/start.py
"""
세션 시작 라우트
새로운 학습 세션을 시작합니다.
"""

from flask import Blueprint

# 세션 시작 Blueprint 생성
start_bp = Blueprint('session_start', __name__, url_prefix='/learning/session')


@start_bp.route('/start', methods=['POST'])
def start_session():
    """
    학습 세션 시작 엔드포인트
    향후 세션 관리 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": "Session start endpoint - to be implemented"}