# backend/app/routes/learning/session/message_qna.py

from flask import Blueprint, request, jsonify
from app.services.learning.session_service import session_service
from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
from app.utils.response.formatter import ResponseFormatter
from app.utils.response.error_formatter import ErrorFormatter
from app.core.langraph.state_manager import state_manager
from app.agents.qna_resolver.qna_resolver_agent import QnAResolverAgent
from app.agents.learning_supervisor.response_generator import response_generator

# Blueprint 설정
message_qna_bp = Blueprint('message_qna', __name__)

@message_qna_bp.route('/message-qna', methods=['POST'])
@require_auth
def handle_qna_message():
    """
    QnA 전용 메시지 처리 엔드포인트 (테스트용)
    - 기존 /session/message와 완전 분리
    - 스트리밍 없이 일반 QnA 응답 생성
    - 동작 확인 후 스트리밍 기능 추가 예정
    """
    try:
        print(f"[QnA 전용] QnA 요청 처리 시작")
        
        # 1. 요청 데이터 검증
        request_data = request.get_json()
        if not request_data:
            return ResponseFormatter.error_response(
                "VALIDATION_ERROR", 
                "요청 데이터가 필요합니다."
            )
        
        user_message = request_data.get('user_message', '').strip()
        if not user_message:
            return ResponseFormatter.error_response(
                "VALIDATION_ERROR", 
                "사용자 메시지가 필요합니다."
            )
        
        print(f"[QnA 전용] 사용자 메시지: '{user_message}'")
        
        # 2. 현재 사용자 정보 가져오기
        current_user = get_current_user_from_request()
        if not current_user:
            return ErrorFormatter.format_authentication_error("token_invalid")
        
        # 3. 기본 TutorState 생성 (QnA 전용)
        state = state_manager.initialize_state(
            user_id=current_user['user_id'],
            user_type=current_user.get('user_type', 'beginner'),
            current_chapter=current_user.get('current_chapter', 1),
            current_section=current_user.get('current_section', 1)
        )
        
        # 4. 사용자 메시지를 대화 기록에 추가
        state = state_manager.add_conversation(
            state,
            agent_name="user",
            message=user_message,
            message_type="user"
        )
        
        print(f"[QnA 전용] TutorState 초기화 완료")
        
        # 5. QnA Resolver Agent 직접 실행
        qna_agent = QnAResolverAgent()
        processed_state = qna_agent.process(state)
        
        print(f"[QnA 전용] QnA Agent 처리 완료")
        
        # 6. Response Generator로 최종 응답 생성
        final_state = response_generator.generate_final_response(processed_state)
        
        print(f"[QnA 전용] 최종 응답 생성 완료")
        
        # 7. workflow_response 구조로 응답 반환
        workflow_response = final_state.get("workflow_response", {})
        
        if not workflow_response:
            print(f"[QnA 전용] workflow_response가 생성되지 않음")
            return ResponseFormatter.error_response(
                "QNA_GENERATION_FAILED", 
                "QnA 응답 생성에 실패했습니다."
            )
        
        # 8. 성공 응답
        response_data = {
            "workflow_response": workflow_response,
            "processing_info": {
                "agent": "qna_resolver",
                "message_processed": True,
                "streaming": False  # 현재는 일반 응답
            }
        }
        
        print(f"[QnA 전용] 응답 전송 완료")
        
        return jsonify({
            "success": True,
            "data": response_data,
            "message": "QnA 응답이 생성되었습니다."
        }), 200
        
    except Exception as e:
        print(f"[QnA 전용] 처리 중 오류 발생: {str(e)}")
        return ResponseFormatter.error_response(
            "QNA_PROCESSING_ERROR",
            f"QnA 처리 중 오류가 발생했습니다: {str(e)}"
        )