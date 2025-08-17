# backend/app/routes/learning/session/message.py

from flask import Blueprint, request, g
from app.utils.response.formatter import success_response, error_response
from app.utils.response.error_formatter import format_error_response
from app.utils.auth.jwt_handler import jwt_required
from app.core.langraph.workflow import execute_workflow
from app.core.langraph.state_manager import StateManager
from app.utils.common.exceptions import ValidationError, WorkflowExecutionError
import logging

# Blueprint 정의
message_bp = Blueprint('learning_session_message', __name__)
logger = logging.getLogger(__name__)

@message_bp.route('/message', methods=['POST'])
@jwt_required
def handle_session_message():
    """
    통합 학습 세션 메시지 처리 API
    
    모든 학습 상호작용을 단일 엔드포인트로 처리:
    - 이론 설명 요청
    - 퀴즈 진행 요청  
    - 질문 답변 요청
    - 세션 완료 요청
    
    SupervisorRouter가 사용자 의도를 분석하여 적절한 에이전트로 라우팅
    """
    try:
        # 요청 데이터 검증
        data = request.get_json()
        if not data:
            return error_response("요청 데이터가 없습니다.", "MISSING_REQUEST_DATA", 400)
        
        user_message = data.get('user_message', '').strip()
        if not user_message:
            return error_response("메시지를 입력해주세요.", "EMPTY_MESSAGE", 400)
        
        message_type = data.get('message_type', 'user')
        
        # 현재 사용자 정보 확인
        user_id = g.user.get('user_id')
        if not user_id:
            return error_response("사용자 정보를 찾을 수 없습니다.", "USER_NOT_FOUND", 401)
        
        # StateManager 초기화 및 현재 상태 로드
        state_manager = StateManager()
        
        # 현재 학습 진행 상태 조회 (user_progress 테이블에서)
        current_state = state_manager.load_current_learning_state(user_id)
        if not current_state:
            return error_response(
                "학습 세션을 먼저 시작해주세요.", 
                "SESSION_NOT_STARTED", 
                400
            )
        
        # 사용자 메시지를 State에 추가
        state_manager.add_user_message(current_state, user_message, message_type)
        
        logger.info(f"Processing message for user {user_id}: {user_message[:50]}...")
        
        # LangGraph 워크플로우 실행
        # execute_workflow는 현재 상태를 기반으로 SupervisorRouter가 적절한 에이전트 선택
        try:
            final_state = execute_workflow(current_state)
        except Exception as e:
            logger.error(f"Workflow execution failed for user {user_id}: {str(e)}")
            return error_response(
                "AI 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "WORKFLOW_EXECUTION_ERROR",
                500
            )
        
        # workflow_response 구조 생성
        workflow_response = _build_workflow_response(final_state)
        
        # 응답 구성
        response_data = {
            "workflow_response": workflow_response,
            "session_info": {
                "chapter_number": final_state.get("current_chapter"),
                "section_number": final_state.get("current_section"),
                "session_progress_stage": final_state.get("session_progress_stage"),
                "current_agent": final_state.get("current_agent")
            }
        }
        
        logger.info(f"Message processed successfully for user {user_id}, agent: {final_state.get('current_agent')}")
        
        return success_response(
            response_data,
            "메시지가 성공적으로 처리되었습니다."
        )
        
    except ValidationError as e:
        return format_error_response(e, "VALIDATION_ERROR", 400)
    except WorkflowExecutionError as e:
        return format_error_response(e, "WORKFLOW_EXECUTION_ERROR", 500)
    except Exception as e:
        logger.error(f"Unexpected error in handle_session_message: {str(e)}")
        return error_response(
            "서버 내부 오류가 발생했습니다.",
            "INTERNAL_SERVER_ERROR",
            500
        )


def _build_workflow_response(state):
    """
    State 정보를 기반으로 프론트엔드용 workflow_response 구조 생성
    
    각 에이전트별로 적절한 응답 구조를 만들어 하이브리드 UX 지원
    """
    current_agent = state.get("current_agent", "")
    session_stage = state.get("session_progress_stage", "")
    
    # 기본 응답 구조
    workflow_response = {
        "current_agent": current_agent,
        "session_progress_stage": session_stage,
        "ui_mode": "chat",  # 기본값
        "content": {}
    }
    
    # 에이전트별 컨텐츠 구성
    if current_agent == "theory_educator":
        workflow_response.update({
            "ui_mode": "chat",
            "content": {
                "type": "theory",
                "title": f"{state.get('current_chapter')}챕터 {state.get('current_section')}섹션",
                "content": state.get("theory_draft", ""),
                "key_points": _extract_key_points(state.get("theory_draft", "")),
                "examples": _extract_examples(state.get("theory_draft", ""))
            }
        })
        
    elif current_agent == "quiz_generator":
        workflow_response.update({
            "ui_mode": "quiz",
            "content": {
                "type": "quiz",
                "quiz_type": state.get("quiz_type", "multiple_choice"),
                "question": state.get("quiz_content", ""),
                "options": state.get("quiz_options", []),
                "hint": state.get("quiz_hint", "")
            }
        })
        
    elif current_agent == "evaluation_feedback_agent":
        workflow_response.update({
            "ui_mode": "chat",
            "content": {
                "type": "feedback",
                "title": "평가 결과",
                "feedback": state.get("feedback_draft", ""),
                "is_correct": state.get("multiple_answer_correct"),
                "score": state.get("subjective_answer_score"),
                "next_step_decision": state.get("retry_decision_result", "proceed")
            }
        })
        
    elif current_agent == "qna_resolver":
        workflow_response.update({
            "ui_mode": "chat",
            "content": {
                "type": "qna",
                "title": "질문 답변",
                "answer": state.get("qna_draft", ""),
                "related_topics": []  # 향후 확장
            }
        })
        
    elif current_agent == "session_manager":
        workflow_response.update({
            "ui_mode": "chat",
            "content": {
                "type": "session_complete",
                "title": "세션 완료",
                "message": "학습 세션이 완료되었습니다.",
                "next_chapter": state.get("current_chapter"),
                "next_section": state.get("current_section"),
                "summary": state.get("session_summary", "")
            }
        })
    
    return workflow_response


def _extract_key_points(theory_content):
    """이론 설명에서 핵심 포인트 추출 (간단한 패턴 매칭)"""
    if not theory_content:
        return []
    
    # 향후 더 정교한 추출 로직으로 개선 가능
    key_points = []
    lines = theory_content.split('\n')
    for line in lines:
        if '핵심' in line or '중요' in line or '포인트' in line:
            key_points.append(line.strip())
    
    return key_points[:3]  # 최대 3개


def _extract_examples(theory_content):
    """이론 설명에서 예시 추출 (간단한 패턴 매칭)"""
    if not theory_content:
        return []
    
    examples = []
    lines = theory_content.split('\n')
    for line in lines:
        if '예시' in line or '예를 들어' in line or '예:' in line:
            examples.append(line.strip())
    
    return examples[:3]  # 최대 3개