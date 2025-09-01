# backend/app/routes/learning/session/qna_stream.py

from flask import Blueprint, request, Response, jsonify
import asyncio
import json
import logging
import uuid
import time
from typing import Dict, Any

from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
from app.utils.response.error_formatter import ErrorFormatter
from app.tools.content.qna_tools_chatgpt_stream import qna_streaming_generation_tool

# Blueprint 설정
qna_stream_bp = Blueprint('qna_stream', __name__)
logger = logging.getLogger(__name__)

# 임시 스트리밍 세션 저장소
# NOTE: 프로덕션 환경에서는 동시성 및 확장성을 위해 Redis 같은 외부 저장소 사용을 권장합니다.
streaming_sessions: Dict[str, Dict[str, Any]] = {}


# --- 스트리밍 실행 엔드포인트 (URL 단순화) ---
@qna_stream_bp.route('/qna-stream/<temp_id>', methods=['GET'])
def stream_qna_response(temp_id: str):
    """
    QnA 답변을 실시간 스트리밍하며 State 관리도 함께 처리
    - QnA Resolver Agent의 State 관리 기능 통합
    - 스트리밍 시작 전/후 State 업데이트 호출
    """
    qna_agent = None
    temp_session_data = None
    
    try:
        print(f"[QnA 스트리밍-실행] 연결 요청 수신 - ID: {temp_id}")
        
        # 1. 임시 세션 정보 조회 및 검증
        temp_session_data = streaming_sessions.get(temp_id)

        if not temp_session_data:
            return Response(_create_error_sse("INVALID_SESSION", "유효하지 않은 스트리밍 세션입니다."), mimetype='text/event-stream')
        
        if time.time() > temp_session_data["expires_at"]:
            streaming_sessions.pop(temp_id, None) # 만료된 세션 정리
            return Response(_create_error_sse("SESSION_EXPIRED", "스트리밍 세션이 만료되었습니다."), mimetype='text/event-stream')

        # 2. QnA Resolver Agent 초기화 및 스트리밍 시작 State 관리
        from app.agents.qna_resolver.qna_resolver_agent import QnAResolverAgent
        qna_agent = QnAResolverAgent()
        
        # 스트리밍 시작 전 State 업데이트
        state_result = qna_agent.process_streaming_state(temp_session_data)
        if not state_result.get("success"):
            print(f"[QnA 스트리밍] State 초기화 실패: {state_result.get('error')}")
            return Response(_create_error_sse("STATE_INIT_ERROR", "State 관리 초기화에 실패했습니다."), mimetype='text/event-stream')
        
        print(f"[QnA 스트리밍] QnA Agent State 초기화 완료")

        # 3. 보안을 위해 한 번 사용한 세션은 즉시 제거 (State 관리 완료 후)
        streaming_sessions.pop(temp_id, None)

        # 4. 세션에서 정보 추출
        user_message = temp_session_data["user_message"]
        current_context = temp_session_data["context"]
        
        print(f"[QnA 스트리밍-실행] 세션 검증 완료, 스트리밍 시작. 질문: '{user_message[:30]}...'")

        # 5. SSE 스트리밍 응답 생성 (State 관리 통합)
        return Response(
            _generate_sse_stream_with_state_management(user_message, current_context, temp_id, qna_agent, temp_session_data),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )
        
    except Exception as e:
        print(f"[QnA 스트리밍-실행] SSE 엔드포인트 오류: {str(e)}")
        
        # 오류 발생 시에도 State 관리 시도
        if qna_agent and temp_session_data:
            try:
                error_response = f"스트리밍 처리 중 오류가 발생했습니다: {str(e)}"
                qna_agent.finalize_streaming_state(temp_session_data, error_response)
                print(f"[QnA 스트리밍] 오류 상황에서도 State 최종 업데이트 완료")
            except Exception as state_error:
                print(f"[QnA 스트리밍] State 오류 처리 실패: {str(state_error)}")
        
        return Response(_create_error_sse("QNA_STREAM_ERROR", f"스트리밍 처리 중 오류가 발생했습니다: {str(e)}"), mimetype='text/event-stream')


# --- State 관리가 통합된 스트리밍 Generator ---
def _generate_sse_stream_with_state_management(user_message: str, current_context: Dict[str, Any], session_id: str, qna_agent, temp_session_data: Dict[str, Any]):
    """
    State 관리가 통합된 SSE 스트리밍 Generator
    - 스트리밍 완료 후 QnA Agent를 통해 최종 State 업데이트
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    chunk_count = 0
    accumulated_response = ""  # 완성된 답변 누적용

    try:
        yield _format_sse_data({ "type": "stream_start", "message": "QnA 답변 생성을 시작합니다...", "session_id": session_id })
        
        stream_generator = qna_streaming_generation_tool(user_message, current_context)
        agen = stream_generator.__aiter__()

        while True:
            try:
                chunk = loop.run_until_complete(agen.__anext__())
                if chunk.strip():
                    chunk_count += 1
                    accumulated_response += chunk  # 답변 누적
                    yield _format_sse_data({ "type": "content_chunk", "chunk": chunk, "chunk_id": chunk_count })
            except StopAsyncIteration:
                print(f"[QnA 스트리밍] 스트림 완료. 총 {chunk_count}개 청크 전송.")
                break
    
    except Exception as e:
        print(f"[QnA 스트리밍] _generate_sse_stream 오류: {str(e)}")
        accumulated_response = f"스트리밍 중 오류가 발생했습니다: {str(e)}"
        yield _format_sse_data({ "type": "stream_error", "error": str(e), "message": "스트리밍 중 오류가 발생했습니다." })
    
    finally:
        # 스트리밍 완료 후 QnA Agent를 통한 최종 State 업데이트
        try:
            print(f"[QnA 스트리밍] 완성된 답변으로 State 최종 업데이트 시작")
            print(f"[QnA 스트리밍] 답변 길이: {len(accumulated_response)}자")
            
            finalize_result = qna_agent.finalize_streaming_state(temp_session_data, accumulated_response)
            
            if finalize_result.get("success"):
                print(f"[QnA 스트리밍] State 최종 업데이트 성공")
            else:
                print(f"[QnA 스트리밍] State 최종 업데이트 실패: {finalize_result.get('error')}")
                
        except Exception as state_error:
            print(f"[QnA 스트리밍] State 최종 업데이트 중 예외 발생: {str(state_error)}")
        
        # 스트리밍 완료 신호
        yield _format_sse_data({ "type": "stream_complete", "message": "QnA 답변이 완성되었습니다.", "total_chunks": chunk_count })
        
        # 이벤트 루프 정리
        loop.close()
        print(f"[QnA 스트리밍] 이벤트 루프 종료 및 SSE 스트림 최종 완료.")


def _format_sse_data(data: Dict[str, Any]) -> str:
    """SSE 형식으로 데이터 포맷"""
    json_data = json.dumps(data, ensure_ascii=False)
    return f"data: {json_data}\n\n"


def _create_error_sse(error_code: str, error_message: str) -> str:
    """SSE 에러 메시지 생성"""
    error_data = { "type": "error", "error_code": error_code, "message": error_message }
    return _format_sse_data(error_data)


# --- 개발/디버깅용 헬퍼 함수들 ---
def get_active_streaming_sessions_count():
    """현재 활성 스트리밍 세션 수 반환 (디버깅용)"""
    current_time = time.time()
    active_count = 0
    expired_sessions = []
    
    for session_id, session_data in streaming_sessions.items():
        if current_time <= session_data.get("expires_at", 0):
            active_count += 1
        else:
            expired_sessions.append(session_id)
    
    # 만료된 세션 정리
    for expired_id in expired_sessions:
        streaming_sessions.pop(expired_id, None)
    
    return {
        "active_sessions": active_count,
        "cleaned_expired": len(expired_sessions),
        "total_sessions": len(streaming_sessions)
    }


def cleanup_expired_sessions():
    """만료된 세션들을 정리하는 유틸리티 함수 (선택적 호출)"""
    current_time = time.time()
    expired_sessions = [
        session_id for session_id, session_data in streaming_sessions.items()
        if current_time > session_data.get("expires_at", 0)
    ]
    
    for expired_id in expired_sessions:
        streaming_sessions.pop(expired_id, None)
    
    print(f"[QnA 스트리밍] 만료된 세션 {len(expired_sessions)}개 정리 완료")
    return len(expired_sessions)