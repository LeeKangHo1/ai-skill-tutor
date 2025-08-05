# backend/run.py
# Flask 애플리케이션 실행 파일

import os
from app import create_app

# 환경 설정 (기본값: development)
config_name = os.environ.get('FLASK_ENV', 'development')

# Flask 앱 생성
app = create_app(config_name)

if __name__ == '__main__':
    # 개발 서버 실행
    app.run(
        host='0.0.0.0',  # 모든 인터페이스에서 접근 가능
        port=5000,       # 포트 5000 사용
        debug=True       # 디버그 모드 활성화
    )