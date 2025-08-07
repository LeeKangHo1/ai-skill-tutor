# backend/app/routes/learning/quiz/submit.py
"""
퀴즈 답변 제출 라우트
사용자의 퀴즈 답변을 처리합니다.
"""

from flask import Blueprint

# 퀴즈 답변 제출 Blueprint 생성
submit_bp = Blueprint('quiz_submit', __name__, url_prefix='/learning/quiz')


@submit_bp.route('/submit', methods=['POST'])
def submit_answer():
    """
    퀴즈 답변 제출 엔드포인트
    향후 퀴즈 처리 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": "Quiz submit endpoint - to be implemented"}