# backend/app/routes/diagnosis/__init__.py

from .questions import diagnosis_questions_bp
from .submit import diagnosis_submit_bp

# 진단 관련 Blueprint 목록
diagnosis_blueprints = [
    (diagnosis_questions_bp, '/api/v1/diagnosis'),
    (diagnosis_submit_bp, '/api/v1/diagnosis')
]