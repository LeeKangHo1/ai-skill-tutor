# backend/app/routes/dashboard/overview.py
"""
대시보드 개요 라우트
사용자 대시보드의 전체 개요 정보를 제공합니다.
"""

from flask import Blueprint

# 대시보드 개요 Blueprint 생성
overview_bp = Blueprint('dashboard_overview', __name__, url_prefix='/dashboard')


@overview_bp.route('/overview', methods=['GET'])
def get_overview():
    """
    대시보드 개요 조회 엔드포인트
    향후 사용자 진행 상태 및 통계 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": "Dashboard overview endpoint - to be implemented"}