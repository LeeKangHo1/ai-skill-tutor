# backend/app/routes/diagnosis/submit.py
"""
진단 결과 제출 라우트
사용자의 진단 답변을 처리하고 결과를 반환합니다.
"""

from flask import Blueprint

# 진단 결과 제출 Blueprint 생성
submit_bp = Blueprint('diagnosis_submit', __name__, url_prefix='/diagnosis')


@submit_bp.route('/submit', methods=['POST'])
def submit_diagnosis():
    """
    진단 결과 제출 엔드포인트
    향후 진단 처리 서비스와 연동하여 구현될 예정입니다.
    """
    return {"message": "Diagnosis submit endpoint - to be implemented"}