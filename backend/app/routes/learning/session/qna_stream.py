# backend/app/routes/learning/session/qna_stream.py

from flask import Blueprint, request, Response
import asyncio
import json
import logging
from typing import Dict, Any

from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
from app.utils.response.error_formatter import ErrorFormatter
from app.tools.content.qna_tools_chatgpt_stream import qna_streaming_generation_tool

# Blueprint 설정
qna_stream_bp = Blueprint('qna_stream', __name__)
logger = logging.getLogger(__name__)

@qna_stream_bp.route('/qna-stream/<session_id>', methods=['GET'])
@require_auth
def stream_qna_response(session_id):
    """
    QnA 실시간 스트리밍 엔드포인트 (Server-Sent Events)
    
    URL: GET /api/v1/learning/qna-stream/{session_id}
    Query Parameters:
        - user_message: 사용자 질문 (required)
        - chapter: 현재 챕터 (optional)
        - section: 현재 섹션 (optional)
    
    Response: Server-Sent Events 스트림
    """
    try:
        print(f"[QnA 스트리밍] SSE 요청 수신 - 세션: {session_id}")
        
        # 1. 사용자 인증 확인
        current_user = get_current_user_from_request()
        if not current_user:
            return ErrorFormatter.format_authentication_error("token_invalid")
        
        # 2. 쿼리 파라미터에서 사용자 질문 추출
        user_message = request.args.get('user_message', '').strip()
        if not user_message:
            return Response(
                _create_error_sse("USER_MESSAGE_REQUIRED", "사용자 메시지가 필요합니다."),
                mimetype='text/event-stream'
            )
        
        print(f"[QnA 스트리밍] 사용자 메시지: '{user_message}'")
        
        # 3. 학습 컨텍스트 정보 추출
        current_chapter = request.args.get('chapter', current_user.get('current_chapter', 1))
        current_section = request.args.get('section', current_user.get('current_section', 1))
        
        current_context = {
            "chapter": current_chapter,
            "section": current_section,
            "theory_draft": ""  # 필요시 추가
        }
        
        print(f"[QnA 스트리밍] 컨텍스트 설정 - 챕터: {current_chapter}, 섹션: {current_section}")
        
        # 4. SSE 스트리밍 응답 생성
        return Response(
            _generate_sse_stream(user_message, current_context, session_id),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
        
    except Exception as e:
        print(f"[QnA 스트리밍] SSE 엔드포인트 오류: {str(e)}")
        return Response(
            _create_error_sse("QNA_STREAM_ERROR", f"스트리밍 처리 중 오류가 발생했습니다: {str(e)}"),
            mimetype='text/event-stream'
        )


def _generate_sse_stream(user_message: str, current_context: Dict[str, Any], session_id: str):
    """
    SSE 형식으로 QnA 스트리밍 응답 생성 (수정된 버전)
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    chunk_count = 0

    try:
        print(f"[QnA 스트리밍] _generate_sse_stream 시작")

        # 1. 스트리밍 시작 알림
        yield _format_sse_data({
            "type": "stream_start",
            "message": "QnA 답변 생성을 시작합니다...",
            "session_id": session_id
        })

        # 2. 비동기 스트리밍 도구 실행 및 실시간 처리
        stream_generator = qna_streaming_generation_tool(user_message, current_context)
        
        # 비동기 제너레이터의 이터레이터를 가져옵니다.
        agen = stream_generator.__aiter__()

        while True:
            try:
                # 이벤트 루프를 통해 비동기적으로 다음 청크를 가져옵니다.
                chunk = loop.run_until_complete(agen.__anext__())
                if chunk.strip():
                    chunk_count += 1
                    # 받은 청크를 즉시 SSE 형식으로 yield 합니다.
                    yield _format_sse_data({
                        "type": "content_chunk",
                        "chunk": chunk,
                        "chunk_id": chunk_count
                    })
            except StopAsyncIteration:
                # 스트림이 끝나면 루프를 종료합니다.
                print(f"[QnA 스트리밍] 스트림 완료. 총 {chunk_count}개 청크 전송.")
                break
    
    except Exception as e:
        print(f"[QnA 스트리밍] _generate_sse_stream 오류: {str(e)}")
        # 오류 발생 시 에러 이벤트를 전송합니다.
        yield _format_sse_data({
            "type": "stream_error",
            "error": str(e),
            "message": "스트리밍 중 오류가 발생했습니다."
        })
    
    finally:
        # 3. 스트리밍 완료 알림 (성공/실패 여부와 관계없이 항상 실행)
        yield _format_sse_data({
            "type": "stream_complete",
            "message": "QnA 답변이 완성되었습니다.",
            "total_chunks": chunk_count
        })
        loop.close()
        print(f"[QnA 스트리밍] 이벤트 루프 종료 및 SSE 스트림 최종 완료.")


def _format_sse_data(data: Dict[str, Any]) -> str:
    """
    데이터를 SSE 형식으로 포맷팅
    
    Args:
        data: 전송할 데이터 딕셔너리
        
    Returns:
        str: SSE 형식 문자열
    """
    json_data = json.dumps(data, ensure_ascii=False)
    return f"data: {json_data}\n\n"


def _create_error_sse(error_code: str, error_message: str) -> str:
    """
    SSE 형식의 에러 응답 생성
    
    Args:
        error_code: 에러 코드
        error_message: 에러 메시지
        
    Returns:
        str: SSE 형식 에러 응답
    """
    error_data = {
        "type": "error",
        "error_code": error_code,
        "message": error_message
    }
    return _format_sse_data(error_data)


@qna_stream_bp.route('/qna-stream-test', methods=['GET'])
@require_auth  
def test_sse_connection():
    """
    SSE 연결 테스트용 엔드포인트
    - 간단한 카운터로 SSE 동작 확인
    """
    def generate_test_stream():
        import time
        
        for i in range(5):
            yield _format_sse_data({
                "type": "test_chunk",
                "message": f"테스트 메시지 {i+1}",
                "count": i+1
            })
            time.sleep(1)  # 1초 간격
            
        yield _format_sse_data({
            "type": "test_complete",
            "message": "테스트 완료"
        })
    
    return Response(
        generate_test_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )