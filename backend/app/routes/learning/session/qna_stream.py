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


# --- 1단계: 인증 및 스트리밍 준비 엔드포인트 ---
@qna_stream_bp.route('/qna-stream/start', methods=['POST'])
@require_auth
def start_qna_stream_session():
    """
    QnA 스트리밍 세션을 시작하고, 스트리밍에 사용할 임시 ID를 발급합니다.
    """
    try:
        print(f"[QnA 스트리밍-준비] 세션 시작 요청 수신")
        
        # 1. 사용자 인증 및 정보 가져오기
        current_user = get_current_user_from_request()
        if not current_user:
            return ErrorFormatter.format_authentication_error("token_invalid")

        # 2. 요청 데이터에서 사용자 질문 추출
        request_data = request.get_json()
        user_message = request_data.get('user_message', '').strip()
        if not user_message:
            return jsonify({
                "success": False, 
                "error": {"code": "VALIDATION_ERROR", "message": "user_message가 필요합니다."}
            }), 400

        # 3. 임시 스트리밍 ID 생성
        temp_id = str(uuid.uuid4())
        
        # 4. 임시 세션 정보 저장 (유효시간 30초)
        session_data = {
            "user": current_user,
            "user_message": user_message,
            "context": {
                "chapter": request_data.get('chapter', current_user.get('current_chapter', 1)),
                "section": request_data.get('section', current_user.get('current_section', 1)),
            },
            "expires_at": time.time() + 30  # 30초 후 만료
        }
        streaming_sessions[temp_id] = session_data
        
        print(f"[QnA 스트리밍-준비] 임시 ID 발급 완료: {temp_id}")
        
        # 5. 임시 ID를 클라이언트에 반환
        return jsonify({
            "success": True,
            "data": { "stream_session_id": temp_id },
            "message": "스트리밍 세션이 준비되었습니다."
        }), 200

    except Exception as e:
        print(f"[QnA 스트리밍-준비] 오류 발생: {str(e)}")
        return jsonify({
            "success": False,
            "error": {"code": "STREAM_SETUP_ERROR", "message": f"스트리밍 준비 중 오류 발생: {str(e)}"}
        }), 500


# --- 2단계: 스트리밍 실행 엔드포인트 ---
@qna_stream_bp.route('/qna-stream/stream/<temp_id>', methods=['GET'])
def stream_qna_response(temp_id: str):
    """
    발급받은 임시 ID를 사용하여 QnA 답변을 실시간 스트리밍합니다.
    (이 엔드포인트는 @require_auth를 사용하지 않습니다.)
    """
    try:
        print(f"[QnA 스트리밍-실행] 연결 요청 수신 - ID: {temp_id}")
        
        # 1. 임시 세션 정보 조회 및 검증
        session_data = streaming_sessions.get(temp_id)

        if not session_data:
            return Response(_create_error_sse("INVALID_SESSION", "유효하지 않은 스트리밍 세션입니다."), mimetype='text/event-stream')
        
        if time.time() > session_data["expires_at"]:
            streaming_sessions.pop(temp_id, None) # 만료된 세션 정리
            return Response(_create_error_sse("SESSION_EXPIRED", "스트리밍 세션이 만료되었습니다."), mimetype='text/event-stream')

        # 2. 보안을 위해 한 번 사용한 세션은 즉시 제거
        streaming_sessions.pop(temp_id, None)

        # 3. 세션에서 정보 추출
        user_message = session_data["user_message"]
        current_context = session_data["context"]
        
        print(f"[QnA 스트리밍-실행] 세션 검증 완료, 스트리밍 시작. 질문: '{user_message[:30]}...'")

        # 4. SSE 스트리밍 응답 생성
        return Response(
            _generate_sse_stream(user_message, current_context, temp_id),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )
        
    except Exception as e:
        print(f"[QnA 스트리밍-실행] SSE 엔드포인트 오류: {str(e)}")
        return Response(_create_error_sse("QNA_STREAM_ERROR", f"스트리밍 처리 중 오류가 발생했습니다: {str(e)}"), mimetype='text/event-stream')


# --- Helper Functions (기존과 거의 동일) ---
def _generate_sse_stream(user_message: str, current_context: Dict[str, Any], session_id: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    chunk_count = 0

    try:
        yield _format_sse_data({ "type": "stream_start", "message": "QnA 답변 생성을 시작합니다...", "session_id": session_id })
        
        stream_generator = qna_streaming_generation_tool(user_message, current_context)
        agen = stream_generator.__aiter__()

        while True:
            try:
                chunk = loop.run_until_complete(agen.__anext__())
                if chunk.strip():
                    chunk_count += 1
                    yield _format_sse_data({ "type": "content_chunk", "chunk": chunk, "chunk_id": chunk_count })
            except StopAsyncIteration:
                print(f"[QnA 스트리밍] 스트림 완료. 총 {chunk_count}개 청크 전송.")
                break
    
    except Exception as e:
        print(f"[QnA 스트리밍] _generate_sse_stream 오류: {str(e)}")
        yield _format_sse_data({ "type": "stream_error", "error": str(e), "message": "스트리밍 중 오류가 발생했습니다." })
    
    finally:
        yield _format_sse_data({ "type": "stream_complete", "message": "QnA 답변이 완성되었습니다.", "total_chunks": chunk_count })
        loop.close()
        print(f"[QnA 스트리밍] 이벤트 루프 종료 및 SSE 스트림 최종 완료.")


def _format_sse_data(data: Dict[str, Any]) -> str:
    json_data = json.dumps(data, ensure_ascii=False)
    return f"data: {json_data}\n\n"


def _create_error_sse(error_code: str, error_message: str) -> str:
    error_data = { "type": "error", "error_code": error_code, "message": error_message }
    return _format_sse_data(error_data)