# backend/app/routes/learning/session/message.py
# 학습 세션 메시지 처리 라우트

from flask import Blueprint, request, jsonify
from app.services.learning.session_service import session_service
from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
from app.utils.response.formatter import ResponseFormatter
from app.utils.response.error_formatter import ErrorFormatter

# Blueprint 생성
session_message_bp = Blueprint('session_message', __name__)


@session_message_bp.route('/message', methods=['POST'])
@require_auth
def process_session_message():
    """
    학습 세션 메시지 처리 (통합 워크플로우)
    
    Request Body:
    {
        "user_message": "다음 단계로 넘어가주세요",
        "message_type": "user"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "workflow_response": {
                "current_agent": "quiz_generator",
                "session_progress_stage": "theory_completed",
                "ui_mode": "quiz",
                "content": {
                    "type": "quiz",
                    "quiz_type": "multiple_choice",
                    "question": "다음 중 LLM의 특징이 아닌 것은?",
                    "options": [...],
                    "hint": "LLM의 'L'이 무엇을 의미하는지 생각해보세요."
                }
            }
        },
        "message": "메시지가 처리되었습니다."
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
        user_message = request_data.get('user_message')
        message_type = request_data.get('message_type', 'user')
        
        # 입력값 검증
        validation_errors = []
        
        if not user_message or not isinstance(user_message, str) or not user_message.strip():
            validation_errors.append("user_message는 빈 문자열이 아닌 문자열이어야 합니다.")
        
        if message_type not in ['user', 'system']:
            validation_errors.append("message_type은 'user' 또는 'system'이어야 합니다.")
        
        # 메시지 길이 제한 (선택적)
        if user_message and len(user_message) > 1000:
            validation_errors.append("메시지는 1000자를 초과할 수 없습니다.")
        
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
        
        # 세션 서비스 호출
        result = session_service.process_message(
            token=token,
            user_message=user_message.strip()
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
            elif error_code == 'WORKFLOW_EXECUTION_ERROR':
                return ResponseFormatter.error_response(
                    "WORKFLOW_EXECUTION_ERROR",
                    "워크플로우 실행 중 오류가 발생했습니다.",
                    status_code=500
                )
            else:
                return jsonify(result), 500
        
    except Exception as e:
        return ResponseFormatter.error_response(
            "MESSAGE_PROCESS_ERROR", 
            f"메시지 처리 중 예상치 못한 오류가 발생했습니다: {str(e)}"
        )


@session_message_bp.route('/message/status', methods=['GET'])
@require_auth
def get_message_status():
    """
    현재 세션 메시지 상태 조회 (선택적 기능)
    
    Response:
    {
        "success": true,
        "data": {
            "session_info": {
                "has_active_session": true,
                "current_chapter": 2,
                "current_section": 1,
                "session_progress_stage": "theory_completed",
                "last_activity": "2025-08-19T10:30:00"
            }
        },
        "message": "세션 상태를 조회했습니다."
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
        result = session_service.get_session_status(token)
        
        # 응답 반환
        if result.get('success'):
            return jsonify(result), 200
        else:
            # 에러 코드에 따른 HTTP 상태 코드 결정
            error_code = result.get('error', {}).get('code', '')
            
            if error_code in ['AUTH_TOKEN_INVALID', 'AUTH_TOKEN_EXPIRED']:
                return ErrorFormatter.format_authentication_error("token_invalid")
            else:
                return jsonify(result), 500
        
    except Exception as e:
        return ResponseFormatter.error_response(
            "SESSION_STATUS_ERROR", 
            f"세션 상태 조회 중 예상치 못한 오류가 발생했습니다: {str(e)}"
        )


@session_message_bp.errorhandler(400)
def handle_bad_request(error):
    """400 에러 핸들러"""
    return ResponseFormatter.error_response(
        "BAD_REQUEST", 
        "잘못된 요청입니다."
    )


@session_message_bp.errorhandler(401)
def handle_unauthorized(error):
    """401 에러 핸들러"""
    return ErrorFormatter.format_authentication_error("token_invalid")


@session_message_bp.errorhandler(404)
def handle_not_found(error):
    """404 에러 핸들러"""
    return ResponseFormatter.error_response(
        "NOT_FOUND",
        "요청한 리소스를 찾을 수 없습니다.",
        status_code=404
    )


@session_message_bp.errorhandler(500)
def handle_internal_error(error):
    """500 에러 핸들러"""
    return ResponseFormatter.error_response(
        "INTERNAL_SERVER_ERROR", 
        "서버 내부 오류가 발생했습니다."
    )