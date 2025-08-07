# backend/app/routes/dashboard/statistics.py
"""
대시보드 통계 라우트
사용자의 학습 통계 정보를 제공합니다.
"""

from flask import Blueprint

# 대시보드 통계 Blueprint 생성
statistics_bp = Blueprint('dashboard_statistics', __name__, url_prefix='/dashboard')


@statistics_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    대시보드 통계 조회 엔드포인트
    향후 통계 처리 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": "Dashboard statistics endpoint - to be implemented"}