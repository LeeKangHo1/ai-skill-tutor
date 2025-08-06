# backend/app/routes/main.py
# 메인 API 라우트 파일

from flask import Blueprint

# 메인 Blueprint 생성
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
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

@main_bp.route('/health')
def health_check():
    """헬스 체크 엔드포인트
    
    Returns:
        dict: 서버 상태 정보
    """
    return {
        "status": "healthy",
        "message": "서버가 정상적으로 동작 중입니다."
    }