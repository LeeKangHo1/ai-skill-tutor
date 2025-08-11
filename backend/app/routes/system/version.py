# backend/app/routes/system/version.py
# 버전 및 기본 정보 관련 라우트

from flask import Blueprint

# 버전 정보 Blueprint 생성
version_bp = Blueprint('version', __name__)

@version_bp.route('/')
def index():
    """기본 API 엔드포인트
    
    Returns:
        dict: "AI Skill Tutor API" 메시지 반환
    """
    return {
        "message": "AI Skill Tutor API",
        "status": "running",
        "version": "1.0.0"
    }

@version_bp.route('/version')
def version():
    """버전 정보 엔드포인트
    
    Returns:
        dict: API 버전 및 상태 정보
    """
    from ...utils.response.formatter import success_response
    
    return success_response(
        data={
            "api_name": "AI Skill Tutor API",
            "version": "1.0.0",
            "status": "running",
            "description": "AI 활용법 학습 튜터 백엔드 API"
        },
        message="API 버전 정보를 성공적으로 조회했습니다."
    )