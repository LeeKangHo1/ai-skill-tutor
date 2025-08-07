# backend/app/routes/learning/session/message.py
"""
세션 메시지 처리 라우트
학습 세션 중 사용자 메시지를 처리합니다.
"""

from flask import Blueprint

# 세션 메시지 처리 Blueprint 생성
message_bp = Blueprint('session_message', __name__, url_prefix='/learning/session')


@message_bp.route('/message', methods=['POST'])
def process_message():
    """
    세션 메시지 처리 엔드포인트
    향후 LangGraph 에이전트 시스템과 연동하여 구현될 예정입니다.
    """
    return {"message": "Session message endpoint - to be implemented"}