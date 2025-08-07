# backend/app/routes/learning/history/list.py
"""
학습 기록 목록 라우트
사용자의 학습 기록 목록을 제공합니다.
"""

from flask import Blueprint

# 학습 기록 목록 Blueprint 생성
list_bp = Blueprint('history_list', __name__, url_prefix='/learning/history')


@list_bp.route('/list', methods=['GET'])
def get_history_list():
    """
    학습 기록 목록 조회 엔드포인트
    향후 학습 기록 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": "History list endpoint - to be implemented"}