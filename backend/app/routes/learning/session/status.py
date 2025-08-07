# backend/app/routes/learning/session/status.py
"""
세션 상태 라우트
학습 세션의 현재 상태를 조회합니다.
"""

from flask import Blueprint

# 세션 상태 Blueprint 생성
status_bp = Blueprint('session_status', __name__, url_prefix='/learning/session')


@status_bp.route('/status/<session_id>', methods=['GET'])
def get_session_status(session_id):
    """
    세션 상태 조회 엔드포인트
    향후 세션 관리 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": f"Session status endpoint for {session_id} - to be implemented"}