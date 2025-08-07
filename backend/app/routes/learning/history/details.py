# backend/app/routes/learning/history/details.py
"""
학습 기록 상세 조회 라우트
특정 학습 세션의 상세 기록을 제공합니다.
"""

from flask import Blueprint

# 학습 기록 상세 Blueprint 생성
details_bp = Blueprint('history_details', __name__, url_prefix='/learning/history')


@details_bp.route('/details/<session_id>', methods=['GET'])
def get_history_details(session_id):
    """
    학습 기록 상세 조회 엔드포인트
    향후 학습 기록 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": f"History details endpoint for {session_id} - to be implemented"}