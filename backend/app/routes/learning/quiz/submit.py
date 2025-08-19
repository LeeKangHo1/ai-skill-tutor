# backend/app/routes/learning/quiz/submit.py
# 퀴즈 답변 제출 라우트

from flask import Blueprint, request, jsonify
from app.services.learning.session_service import session_service
from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
from app.utils.response.formatter import ResponseFormatter
from app.utils.response.error_formatter import ErrorFormatter

# Blueprint 생성
quiz_submit_bp = Blueprint('quiz_submit', __name__)


@quiz_submit_bp.route('/submit', methods=['POST'])
@require_auth
def submit_quiz_answer():
    """
    퀴즈 답변 제출
    
    Request Body:
    {
        "user_answer": "2"  // 객관식: "1", "2", "3", "4" / 주관식: 자유 텍스트
    }
    
    Response:
    {
        "success": true,
        "data": {
            "workflow_response": {
                "current_agent": "evaluation_feedback_agent",
                "session_progress_stage": "quiz_and_feedback_completed",
                "ui_mode": "chat",
                "evaluation_result": {
                    "quiz_type": "multiple_choice",
                    "is_answer_correct": true,
                    "score": 100,
                    "feedback": {
                        "title": "🎉 정답입니다!",
                        "content": "훌륭합니다. LLM의 핵심 특징을...",
                        "explanation": "실시간 인터넷 검색은 LLM의 기본 기능이 아닙니다.",
                        "next_step_decision": "proceed"
                    }
                }
            }
        },
        "message": "퀴즈 답변이 평가되었습니다."
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
        user_answer = request_data.get('user_answer')
        
        # 입력값 검증
        validation_errors = []
        
        if user_answer is None or user_answer == "":
            validation_errors.append("user_answer는 필수 입력값입니다.")
        
        if not isinstance(user_answer, str):
            validation_errors.append("user_answer는 문자열이어야 합니다.")
        
        # 답변 길이 제한 (주관식 고려)
        if isinstance(user_answer, str) and len(user_answer.strip()) > 2000:
            validation_errors.append("답변은 2000자를 초과할 수 없습니다.")
        
        # 객관식 답변 형식 검증 (선택적 - 클라이언트에서 보장하는 것이 좋음)
        if isinstance(user_answer, str) and user_answer.strip() in ['1', '2', '3', '4']:
            # 객관식으로 추정되는 경우 추가 검증 없음 (유효한 형식)
            pass
        elif isinstance(user_answer, str) and len(user_answer.strip()) == 0:
            validation_errors.append("답변을 입력해주세요.")
        
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
        
        # 세션 서비스 호출 - 퀴즈 답변 제출
        result = session_service.submit_quiz_answer(
            token=token,
            user_answer=user_answer.strip()
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
            elif error_code == 'INVALID_QUIZ_ANSWER':
                return ResponseFormatter.error_response(
                    "INVALID_QUIZ_ANSWER",
                    "퀴즈 답변 형식이 올바르지 않습니다.",
                    status_code=400
                )
            elif error_code == 'QUIZ_NOT_AVAILABLE':
                return ResponseFormatter.error_response(
                    "QUIZ_NOT_AVAILABLE",
                    "현재 퀴즈가 활성화되지 않았습니다.",
                    status_code=409
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
            "QUIZ_SUBMIT_ERROR", 
            f"퀴즈 답변 제출 중 예상치 못한 오류가 발생했습니다: {str(e)}"
        )


@quiz_submit_bp.errorhandler(400)
def handle_bad_request(error):
    """400 에러 핸들러"""
    return ResponseFormatter.error_response(
        "BAD_REQUEST", 
        "잘못된 요청입니다."
    )


@quiz_submit_bp.errorhandler(401)
def handle_unauthorized(error):
    """401 에러 핸들러"""
    return ErrorFormatter.format_authentication_error("token_invalid")


@quiz_submit_bp.errorhandler(404)
def handle_not_found(error):
    """404 에러 핸들러"""
    return ResponseFormatter.error_response(
        "NOT_FOUND",
        "요청한 리소스를 찾을 수 없습니다.",
        status_code=404
    )


@quiz_submit_bp.errorhandler(409)
def handle_conflict(error):
    """409 에러 핸들러"""
    return ResponseFormatter.error_response(
        "CONFLICT",
        "요청이 현재 상태와 충돌합니다.",
        status_code=409
    )


@quiz_submit_bp.errorhandler(500)
def handle_internal_error(error):
    """500 에러 핸들러"""
    return ResponseFormatter.error_response(
        "INTERNAL_SERVER_ERROR", 
        "서버 내부 오류가 발생했습니다."
    )


@quiz_submit_bp.errorhandler(501)
def handle_not_implemented(error):
    """501 에러 핸들러"""
    return ResponseFormatter.error_response(
        "NOT_IMPLEMENTED", 
        "해당 기능은 아직 구현되지 않았습니다.",
        status_code=501
    )