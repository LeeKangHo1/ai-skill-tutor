# backend/app/routes/system/health.py
# 헬스 체크 관련 라우트

from flask import Blueprint

# 헬스 체크 Blueprint 생성
health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """헬스 체크 엔드포인트
    
    Returns:
        dict: 서버 상태 정보
    """
    return {
        "status": "healthy",
        "message": "서버가 정상적으로 동작 중입니다."
    }