# backend/app/routes/learning/quiz/hint.py
"""
퀴즈 힌트 요청 라우트
사용자에게 퀴즈 힌트를 제공합니다.
"""

from flask import Blueprint

# 퀴즈 힌트 Blueprint 생성
hint_bp = Blueprint('quiz_hint', __name__, url_prefix='/learning/quiz')


@hint_bp.route('/hint', methods=['POST'])
def get_hint():
    """
    퀴즈 힌트 요청 엔드포인트
    향후 힌트 생성 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": "Quiz hint endpoint - to be implemented"}