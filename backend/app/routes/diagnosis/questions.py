# backend/app/routes/diagnosis/questions.py
"""
진단 문항 라우트
사용자 진단을 위한 문항들을 제공합니다.
"""

from flask import Blueprint

# 진단 문항 Blueprint 생성
questions_bp = Blueprint('diagnosis_questions', __name__, url_prefix='/diagnosis')


@questions_bp.route('/questions', methods=['GET'])
def get_questions():
    """
    진단 문항 조회 엔드포인트
    향후 진단 문항 데이터와 연동하여 구현될 예정입니다.
    """
    return {"message": "Diagnosis questions endpoint - to be implemented"}