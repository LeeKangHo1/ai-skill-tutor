# backend/app/routes/learning/session/start.py
# 학습 세션 시작 API 라우트

from flask import Blueprint, request, jsonify
from app.utils.auth.jwt_handler import token_required
from app.utils.response.formatter import success_response, error_response
from app.utils.response.error_formatter import handle_error
from app.services.learning.session_service import SessionService
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
learning_session_start_bp = Blueprint('learning_session_start', __name__)

# SessionService 인스턴스
session_service = SessionService()

@learning_session_start_bp.route('/start', methods=['POST'])
@token_required
def start_learning_session(current_user):
    """
    학습 세션 시작 API
    
    LangGraph 워크플로우를 초기화하고 첫 번째 세션을 시작합니다.
    SessionManager.session_initialization_tool을 호출하여 세션을 준비합니다.
    
    Request Body:
        chapter_number (int): 시작할 챕터 번호
        section_number (int): 시작할 섹션 번호
        user_message (str, optional): 사용자 시작 메시지
    
    Returns:
        JSON: 세션 시작 결과
        - session_info: 세션 기본 정보
        - workflow_response: LangGraph 워크플로우 응답
    """
    try:
        user_id = current_user['user_id']
        data = request.get_json()
        
        if not data:
            return error_response(
                "VALIDATION_ERROR",
                "요청 데이터가 필요합니다.",
                status_code=400
            )
        
        # 필수 파라미터 검증
        chapter_number = data.get('chapter_number')
        section_number = data.get('section_number')
        user_message = data.get('user_message', '학습을 시작하겠습니다')
        
        if not chapter_number or not section_number:
            return error_response(
                "VALIDATION_ERROR",
                "chapter_number와 section_number는 필수입니다.",
                status_code=400
            )
        
        # 타입 검증
        try:
            chapter_number = int(chapter_number)
            section_number = int(section_number)
        except (ValueError, TypeError):
            return error_response(
                "VALIDATION_ERROR",
                "chapter_number와 section_number는 정수여야 합니다.",
                status_code=400
            )
        
        # 범위 검증
        if chapter_number < 1 or section_number < 1:
            return error_response(
                "VALIDATION_ERROR",
                "chapter_number와 section_number는 1 이상이어야 합니다.",
                status_code=400
            )
        
        logger.info(f"학습 세션 시작 요청 - 사용자 ID: {user_id}, 챕터: {chapter_number}, 섹션: {section_number}")
        
        # 세션 시작 처리
        session_result = session_service.start_session(
            user_id=user_id,
            chapter_number=chapter_number,
            section_number=section_number,
            user_message=user_message
        )
        
        if not session_result:
            logger.error(f"세션 시작 실패 - 사용자 ID: {user_id}")
            return error_response(
                "SESSION_START_FAILED",
                "학습 세션 시작에 실패했습니다.",
                status_code=500
            )
        
        logger.info(f"학습 세션 시작 성공 - 사용자 ID: {user_id}, 챕터: {chapter_number}, 섹션: {section_number}")
        return success_response(
            data=session_result,
            message="학습 세션이 성공적으로 시작되었습니다."
        )
        
    except ValueError as e:
        logger.error(f"학습 세션 시작 검증 오류 - 사용자 ID: {current_user.get('user_id')}: {e}")
        return error_response(
            "VALIDATION_ERROR",
            str(e),
            status_code=400
        )
        
    except Exception as e:
        logger.error(f"학습 세션 시작 오류 - 사용자 ID: {current_user.get('user_id')}: {e}")
        return handle_error(e, "학습 세션 시작 중 오류가 발생했습니다.")