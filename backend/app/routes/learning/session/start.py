# backend/app/routes/learning/session/start.py
# 학습 세션 시작 라우트

from flask import Blueprint, request, jsonify
from app.services.learning.session_service import session_service
from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
from app.utils.response.formatter import ResponseFormatter
from app.utils.response.error_formatter import ErrorFormatter

# Blueprint 생성
session_start_bp = Blueprint('session_start', __name__)


@session_start_bp.route('/start', methods=['POST'])
@require_auth
def start_learning_session():
    """
    학습 세션 시작
    
    Request Body:
    {
        "chapter_number": 2,
        "section_number": 1,
        "user_message": "2챕터 시작할게요"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "session_info": {
                "chapter_number": 2,
                "section_number": 1,
                "chapter_title": "LLM이란 무엇인가",
                "section_title": "2챕터 1섹션",
                "estimated_duration": "15분"
            },
            "workflow_response": {
                "current_agent": "theory_educator",
                "session_progress_stage": "theory_completed",
                "ui_mode": "chat",
                "content": {
                    "type": "theory",
                    "title": "2챕터 1섹션",
                    "content": "LLM은 대규모 언어 모델로...",
                    "key_points": [...],
                    "examples": [...]
                }
            }
        },
        "message": "학습 세션이 시작되었습니다."
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
        chapter_number = request_data.get('chapter_number')
        section_number = request_data.get('section_number')
        user_message = request_data.get('user_message', '')
        
        # 입력값 검증
        validation_errors = []
        
        if not isinstance(chapter_number, int) or chapter_number < 1:
            validation_errors.append("chapter_number는 1 이상의 정수여야 합니다.")
        
        if not isinstance(section_number, int) or section_number < 1:
            validation_errors.append("section_number는 1 이상의 정수여야 합니다.")
        
        if not user_message or not isinstance(user_message, str):
            validation_errors.append("user_message는 빈 문자열이 아닌 문자열이어야 합니다.")
        
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
        result = session_service.start_session(
            token=token,
            chapter_number=chapter_number,
            section_number=section_number,
            user_message=user_message
        )
        
        # 응답 반환
        if result.get('success'):
            return jsonify(result), 200
        else:
            # 에러 코드에 따른 HTTP 상태 코드 결정
            error_code = result.get('error', {}).get('code', '')
            
            if error_code in ['AUTH_TOKEN_INVALID', 'AUTH_TOKEN_EXPIRED']:
                return ErrorFormatter.format_authentication_error("token_invalid")
            elif error_code == 'DIAGNOSIS_NOT_COMPLETED':
                return ErrorFormatter.format_authorization_error("학습", "접근")
            elif error_code in ['CHAPTER_ACCESS_DENIED', 'SECTION_ACCESS_DENIED']:
                return ErrorFormatter.format_authorization_error("해당 챕터/섹션", "접근")
            else:
                return jsonify(result), 500
        
    except Exception as e:
        return ResponseFormatter.error_response(
            "SESSION_START_ERROR", 
            f"세션 시작 중 예상치 못한 오류가 발생했습니다: {str(e)}"
        )


@session_start_bp.errorhandler(400)
def handle_bad_request(error):
    """400 에러 핸들러"""
    return ResponseFormatter.error_response(
        "BAD_REQUEST", 
        "잘못된 요청입니다."
    )


@session_start_bp.errorhandler(401)
def handle_unauthorized(error):
    """401 에러 핸들러"""
    return ErrorFormatter.format_authentication_error("token_invalid")


@session_start_bp.errorhandler(403)
def handle_forbidden(error):
    """403 에러 핸들러"""
    return ErrorFormatter.format_authorization_error()


@session_start_bp.errorhandler(500)
def handle_internal_error(error):
    """500 에러 핸들러"""
    return ResponseFormatter.error_response(
        "INTERNAL_SERVER_ERROR", 
        "서버 내부 오류가 발생했습니다."
    )