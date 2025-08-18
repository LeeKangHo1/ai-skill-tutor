# backend/app/routes/dashboard/overview.py
# 대시보드 개요 API 라우트

from flask import Blueprint, jsonify, request
from ...utils.auth.jwt_handler import token_required
from ...utils.response.formatter import success_response, error_response
from ...utils.response.error_formatter import handle_error
from ...services.dashboard.dashboard_service import DashboardService
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
dashboard_overview_bp = Blueprint('dashboard_overview', __name__)

# DashboardService 인스턴스
dashboard_service = DashboardService()

@dashboard_overview_bp.route('/overview', methods=['GET'])
@token_required
def get_dashboard_overview(current_user):
    """
    대시보드 개요 정보 조회 API
    
    사용자의 학습 진행 상태, 통계 정보, 챕터별 상태를 종합적으로 제공합니다.
    
    Returns:
        JSON: 대시보드 개요 데이터
        - user_progress: 현재 진행 상태
        - learning_statistics: 학습 통계
        - chapter_status: 챕터별 상태 배열
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"대시보드 개요 조회 요청 - 사용자 ID: {user_id}")
        
        # 대시보드 개요 데이터 조회
        overview_data = dashboard_service.get_dashboard_overview(user_id)
        
        if not overview_data:
            logger.warning(f"대시보드 데이터를 찾을 수 없음 - 사용자 ID: {user_id}")
            return error_response(
                "NOT_FOUND",
                "대시보드 데이터를 찾을 수 없습니다.",
                status_code=404
            )
        
        logger.info(f"대시보드 개요 조회 성공 - 사용자 ID: {user_id}")
        return success_response(
            data=overview_data,
            message="대시보드 개요를 성공적으로 조회했습니다."
        )
        
    except ValueError as e:
        logger.error(f"대시보드 개요 조회 검증 오류 - 사용자 ID: {current_user.get('user_id')}: {e}")
        return error_response(
            "VALIDATION_ERROR",
            str(e),
            status_code=400
        )
        
    except Exception as e:
        logger.error(f"대시보드 개요 조회 오류 - 사용자 ID: {current_user.get('user_id')}: {e}")
        return handle_error(e, "대시보드 개요 조회 중 오류가 발생했습니다.")