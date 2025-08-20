# backend/app/routes/dashboard/overview.py
"""
대시보드 개요 라우트
사용자의 학습 현황, 통계, 챕터별 진행 상태를 조회하는 API 엔드포인트입니다.
"""

import logging
from flask import Blueprint, request, jsonify

from app.services.dashboard.dashboard_service import dashboard_service
from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
from app.utils.response.formatter import success_response, error_response
from app.utils.response.error_formatter import ErrorFormatter

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
overview_bp = Blueprint('dashboard_overview', __name__)


@overview_bp.route('/overview', methods=['GET'])
@require_auth
def get_dashboard_overview():
    """
    대시보드 개요 데이터 조회 API
        
    Returns:
        JSON: 대시보드 개요 데이터
        
    Example:
        GET /api/v1/dashboard/overview
        Headers: Authorization: Bearer {access_token}
        
        Response:
        {
            "success": true,
            "data": {
                "user_progress": {
                    "current_chapter": 2,
                    "current_section": 1,
                    "completion_percentage": 25.0
                },
                "learning_statistics": {
                    "total_study_time_minutes": 150,
                    "total_study_sessions": 8,
                    "multiple_choice_accuracy": 85.5,
                    "subjective_average_score": 78.2,
                    "total_multiple_choice_count": 12,
                    "total_subjective_count": 6,
                    "last_study_date": "2025-08-05"
                },
                "chapter_status": [...]
            },
            "message": "대시보드 데이터를 성공적으로 조회했습니다."
        }
    """
    try:
        # JWT 토큰에서 직접 사용자 정보 추출
        current_user = get_current_user_from_request()
        if not current_user:
            logger.error("JWT 토큰에서 사용자 정보를 추출할 수 없습니다.")
            return ErrorFormatter.format_authentication_error("token_invalid")
        
        # JWT 토큰에서 사용자 ID 추출
        user_id = current_user.get('user_id')
        if not user_id:
            logger.error("JWT 토큰에 user_id가 없습니다.")
            return ErrorFormatter.format_authentication_error("token_invalid")
        
        # 사용자 유형 확인 (진단 완료 여부 체크용)
        user_type = current_user.get('user_type')
        diagnosis_completed = current_user.get('diagnosis_completed', False)
        
        # 진단이 완료되지 않은 경우 접근 제한
        if not diagnosis_completed or user_type == 'unassigned':
            logger.warning(f"진단 미완료 사용자의 대시보드 접근 시도: user_id={user_id}")
            return error_response(
                code="DIAGNOSIS_NOT_COMPLETED",
                message="진단을 먼저 완료해주세요.",
                status_code=403
            )
        
        logger.info(f"대시보드 개요 조회 요청: user_id={user_id}, user_type={user_type}")
        
        # 대시보드 서비스 호출
        result = dashboard_service.get_dashboard_overview(user_id)
        
        # 결과가 튜플 형태로 반환되므로 그대로 반환
        return result
        
    except Exception as e:
        logger.error(f"대시보드 개요 조회 중 예상치 못한 오류: {e}")
        return ErrorFormatter.format_external_api_error("대시보드 API", e)


@overview_bp.route('/health', methods=['GET'])
def dashboard_health_check():
    """
    대시보드 모듈 헬스 체크 API
    
    Returns:
        JSON: 대시보드 모듈 상태 정보
        
    Example:
        GET /api/v1/dashboard/health
        
        Response:
        {
            "success": true,
            "data": {
                "status": "healthy",
                "timestamp": "2025-08-19T10:30:00Z",
                "module": "dashboard"
            },
            "message": "대시보드 모듈이 정상 작동 중입니다."
        }
    """
    try:
        from datetime import datetime
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "module": "dashboard",
            "endpoints": [
                "/dashboard/overview"
            ]
        }
        
        logger.debug("대시보드 헬스 체크 성공")
        return success_response(
            data=health_data,
            message="대시보드 모듈이 정상 작동 중입니다."
        )
        
    except Exception as e:
        logger.error(f"대시보드 헬스 체크 오류: {e}")
        return ErrorFormatter.format_external_api_error("대시보드 헬스 체크", e)


# 에러 핸들러
@overview_bp.errorhandler(404)
def not_found_error(error):
    """404 에러 핸들러"""
    logger.warning(f"대시보드 라우트에서 404 에러: {request.url}")
    return error_response(
        code="ENDPOINT_NOT_FOUND",
        message="요청한 엔드포인트를 찾을 수 없습니다.",
        status_code=404
    )


@overview_bp.errorhandler(405)
def method_not_allowed_error(error):
    """405 에러 핸들러"""
    logger.warning(f"대시보드 라우트에서 405 에러: {request.method} {request.url}")
    return error_response(
        code="METHOD_NOT_ALLOWED",
        message="허용되지 않는 HTTP 메서드입니다.",
        details={"allowed_methods": ["GET"]},
        status_code=405
    )


@overview_bp.errorhandler(500)
def internal_server_error(error):
    """500 에러 핸들러"""
    logger.error(f"대시보드 라우트에서 500 에러: {error}")
    return ErrorFormatter.format_external_api_error("대시보드 서버", error)