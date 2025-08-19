# backend/app/routes/learning/session/complete.py
# 학습 세션 완료 라우트

from flask import Blueprint, request, jsonify
from app.services.learning.session_service import session_service
from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
from app.utils.response.formatter import ResponseFormatter
from app.utils.response.error_formatter import ErrorFormatter

# Blueprint 생성
session_complete_bp = Blueprint('session_complete', __name__)


@session_complete_bp.route('/complete', methods=['POST'])
@require_auth
def complete_learning_session():
    """
    학습 세션 완료 처리
    
    Request Body:
    {
        "proceed_decision": "proceed"  // "proceed": 다음 단계 진행, "retry": 현재 구간 재학습
    }
    
    Response:
    {
        "success": true,
        "data": {
            "workflow_response": {
                "current_agent": "session_manager",
                "session_progress_stage": "session_start",
                "ui_mode": "chat",
                "session_completion": {
                    "completed_chapter": 2,
                    "completed_section": 1,
                    "next_chapter": 2,
                    "next_section": 2,
                    "session_summary": "2챕터 1섹션을 성공적으로 완료했습니다.",
                    "study_time_minutes": 15
                }
            }
        },
        "message": "세션이 완료되었습니다."
    }
    """
    try:
        # 요청 데이터 검증
        request_data = request.get_json()
        if not request_data:
            return ResponseFormatter.error_response(
                "VALIDATION_ERROR", 
                "요청 데이터가 필요합니다."
            )
        
        # 필수 필드 검증
        proceed_decision = request_data.get('proceed_decision')
        
        # 입력값 검증
        validation_errors = []
        
        if not proceed_decision:
            validation_errors.append("proceed_decision은 필수 입력값입니다.")
        
        if proceed_decision not in ['proceed', 'retry']:
            validation_errors.append("proceed_decision은 'proceed' 또는 'retry'여야 합니다.")
        
        if validation_errors:
            return ResponseFormatter.validation_error_response(validation_errors)
        
        # 현재 사용자 정보 가져오기
        current_user = get_current_user_from_request()
        if not current_user:
            return ErrorFormatter.format_authentication_error("token_invalid")
        
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return ErrorFormatter.format_authentication_error("token_invalid")
        
        token = auth_header.split(' ')[1]
        
        # 세션 서비스 호출 - 세션 완료 처리
        result = session_service.complete_session(
            token=token,
            proceed_decision=proceed_decision
        )
        
        # 응답 반환
        if result.get('success'):
            return jsonify(result), 200
        else:
            # 에러 코드에 따른 HTTP 상태 코드 결정
            error_code = result.get('error', {}).get('code', '')
            
            if error_code in ['AUTH_TOKEN_INVALID', 'AUTH_TOKEN_EXPIRED']:
                return ErrorFormatter.format_authentication_error("token_invalid")
            elif error_code == 'SESSION_NOT_FOUND':
                return ResponseFormatter.error_response(
                    "SESSION_NOT_FOUND",
                    "활성 세션을 찾을 수 없습니다.",
                    status_code=404
                )
            elif error_code == 'INVALID_DECISION':
                return ResponseFormatter.error_response(
                    "INVALID_DECISION",
                    "유효하지 않은 결정입니다.",
                    status_code=400
                )
            elif error_code == 'SESSION_NOT_READY_FOR_COMPLETION':
                return ResponseFormatter.error_response(
                    "SESSION_NOT_READY_FOR_COMPLETION",
                    "세션이 완료 가능한 상태가 아닙니다.",
                    status_code=409
                )
            elif error_code == 'WORKFLOW_EXECUTION_ERROR':
                return ResponseFormatter.error_response(
                    "WORKFLOW_EXECUTION_ERROR",
                    "워크플로우 실행 중 오류가 발생했습니다.",
                    status_code=500
                )
            elif error_code == 'DATABASE_SAVE_ERROR':
                return ErrorFormatter.format_database_error(Exception("세션 완료 데이터 저장 실패"))
            else:
                return jsonify(result), 500
        
    except Exception as e:
        return ResponseFormatter.error_response(
            "SESSION_COMPLETE_ERROR", 
            f"세션 완료 처리 중 예상치 못한 오류가 발생했습니다: {str(e)}"
        )


@session_complete_bp.route('/status', methods=['GET'])
@require_auth
def get_session_completion_status():
    """
    세션 완료 가능 상태 확인 (선택적 기능)
    
    Response:
    {
        "success": true,
        "data": {
            "can_complete": true,
            "session_stage": "quiz_and_feedback_completed",
            "required_conditions": {
                "theory_completed": true,
                "quiz_completed": true,
                "feedback_received": true
            },
            "completion_options": ["proceed", "retry"]
        },
        "message": "세션 완료 상태를 조회했습니다."
    }
    """
    try:
        # 현재 사용자 정보 가져오기
        current_user = get_current_user_from_request()
        if not current_user:
            return ErrorFormatter.format_authentication_error("token_invalid")
        
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return ErrorFormatter.format_authentication_error("token_invalid")
        
        token = auth_header.split(' ')[1]
        
        # 세션 상태 조회
        session_status_result = session_service.get_session_status(token)
        
        if not session_status_result.get('success'):
            return jsonify(session_status_result), 404
        
        session_info = session_status_result.get('data', {}).get('session_info', {})
        
        if not session_info.get('has_active_session'):
            return ResponseFormatter.error_response(
                "SESSION_NOT_FOUND",
                "활성 세션이 없습니다.",
                status_code=404
            )
        
        # 완료 가능 상태 판단
        session_stage = session_info.get('session_progress_stage', '')
        can_complete = session_stage == 'quiz_and_feedback_completed'
        
        completion_status = {
            "can_complete": can_complete,
            "session_stage": session_stage,
            "required_conditions": {
                "theory_completed": session_stage in ['theory_completed', 'quiz_and_feedback_completed'],
                "quiz_completed": session_stage == 'quiz_and_feedback_completed',
                "feedback_received": session_stage == 'quiz_and_feedback_completed'
            },
            "completion_options": ["proceed", "retry"] if can_complete else []
        }
        
        return ResponseFormatter.success_response(
            data=completion_status,
            message="세션 완료 상태를 조회했습니다."
        )
        
    except Exception as e:
        return ResponseFormatter.error_response(
            "SESSION_STATUS_ERROR", 
            f"세션 완료 상태 조회 중 예상치 못한 오류가 발생했습니다: {str(e)}"
        )


@session_complete_bp.errorhandler(400)
def handle_bad_request(error):
    """400 에러 핸들러"""
    return ResponseFormatter.error_response(
        "BAD_REQUEST", 
        "잘못된 요청입니다."
    )


@session_complete_bp.errorhandler(401)
def handle_unauthorized(error):
    """401 에러 핸들러"""
    return ErrorFormatter.format_authentication_error("token_invalid")


@session_complete_bp.errorhandler(404)
def handle_not_found(error):
    """404 에러 핸들러"""
    return ResponseFormatter.error_response(
        "NOT_FOUND",
        "요청한 리소스를 찾을 수 없습니다.",
        status_code=404
    )


@session_complete_bp.errorhandler(409)
def handle_conflict(error):
    """409 에러 핸들러"""
    return ResponseFormatter.error_response(
        "CONFLICT",
        "요청이 현재 상태와 충돌합니다.",
        status_code=409
    )


@session_complete_bp.errorhandler(500)
def handle_internal_error(error):
    """500 에러 핸들러"""
    return ResponseFormatter.error_response(
        "INTERNAL_SERVER_ERROR", 
        "서버 내부 오류가 발생했습니다."
    )