# backend/app/routes/dashboard/overview.py
# 대시보드 개요 API 라우트

from flask import Blueprint, jsonify, request
from app.utils.auth.jwt_handler import token_required
from app.utils.response.formatter import success_response, error_response
from app.utils.response.error_formatter import handle_error
from app.services.dashboard.dashboard_service import DashboardService
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
    
    user_statistics 테이블의 학습 통계 정보만 제공합니다.
    
    Returns:
        JSON: 대시보드 개요 데이터
        - total_study_time_minutes: 총 학습 시간 (분)
        - total_study_sessions: 총 학습 횟수  
        - total_completed_sessions: 완료한 학습 세션 수
        - multiple_choice_accuracy: 객관식 정답률 (%)
        - subjective_average_score: 주관식 평균 점수
        - last_study_date: 마지막 학습 날짜
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"대시보드 개요 조회 요청 - 사용자 ID: {user_id}")
        
        # 대시보드 개요 데이터 조회 (user_statistics 테이블만)
        overview_data = dashboard_service.get_dashboard_overview(user_id)
        
        if overview_data is None:
            logger.warning(f"사용자 통계 데이터를 찾을 수 없음 - 사용자 ID: {user_id}")
            return error_response(
                "NOT_FOUND",
                "사용자 통계 데이터를 찾을 수 없습니다.",
                status_code=404
            )
        
        logger.info(f"대시보드 개요 조회 성공 - 사용자 ID: {user_id}")
        return success_response(
            data=overview_data,
            message="대시보드 통계를 성공적으로 조회했습니다."
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