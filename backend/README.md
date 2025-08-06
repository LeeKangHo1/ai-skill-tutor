# backend/README.md
# AI 활용법 학습 튜터 - 백엔드 (Flask API)

## 개요
Python Flask 기반의 RESTful API 서버로, AI 멀티에이전트 시스템을 통한 개인화된 학습 튜터링 서비스를 제공합니다.

## 기술 스택
- **Python Flask** (Blueprint 기반 구조)
- **MySQL 8.0** (PyMySQL 드라이버)
- **LangChain, LangGraph, LangSmith** (멀티에이전트 시스템)
- **ChromaDB** (벡터 데이터베이스)
- **JWT** (인증), **bcrypt** (암호화)
- **Flask-CORS** (CORS 처리)

## 가상환경 설정 방법

### 1. 가상환경 생성 (프로젝트 루트에서 실행)
```bash
# 프로젝트 루트 디렉토리에서
python -m venv venv
```

### 2. 가상환경 활성화
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. 가상환경 비활성화
```bash
deactivate
```

## 패키지 설치 방법

### 1. 백엔드 디렉토리로 이동
```bash
cd backend
```

### 2. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 설치된 패키지 목록
- **Flask 3.1.1**: 웹 프레임워크
- **Flask-CORS 6.0.1**: CORS 처리
- **PyMySQL 1.1.1**: MySQL 데이터베이스 연결
- **python-dotenv 1.1.1**: 환경변수 관리
- **bcrypt 4.3.0**: 비밀번호 암호화
- **PyJWT 2.10.1**: JWT 토큰 처리

## 환경변수 설정

### 1. .env 파일 생성
```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env
```

### 2. .env 파일 설정 (필수)
```bash
# 데이터베이스 연결 URL (MySQL)
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/ai_skill_tutor

# Flask 시크릿 키 (JWT 토큰 생성용)
SECRET_KEY=your-secret-key-here

# Flask 실행 환경
FLASK_ENV=development
FLASK_DEBUG=True

# 서버 포트
PORT=5000

# CORS 허용 도메인 (프론트엔드 URL)
CORS_ORIGINS=http://localhost:5173
```

## Flask 앱 실행 방법

### 1. 가상환경 활성화 확인
```bash
# 가상환경이 활성화되어 있는지 확인 (프롬프트에 (venv) 표시)
# 활성화되지 않았다면 프로젝트 루트에서 venv\Scripts\activate 실행
```

### 2. 백엔드 디렉토리에서 실행
```bash
# backend 폴더에서 실행
python run.py
```

### 3. 서버 실행 확인
- 서버 주소: http://localhost:5000
- 브라우저에서 접속하면 "AI Skill Tutor API" 메시지 확인 가능

## 기본 엔드포인트 정보

### 현재 구현된 엔드포인트
- **GET /** : API 상태 확인
  - 응답: `{"message": "AI Skill Tutor API"}`
  - 용도: 서버 동작 확인 및 프론트엔드 연결 테스트

### 향후 구현 예정 엔드포인트
- **POST /api/auth/register** : 사용자 회원가입
- **POST /api/auth/login** : 사용자 로그인
- **GET /api/user/profile** : 사용자 프로필 조회
- **POST /api/diagnosis** : AI 수준 진단
- **POST /api/session/start** : 학습 세션 시작
- **GET /api/session/{session_id}** : 학습 세션 조회
- **POST /api/chat** : AI 에이전트와 채팅

## 프로젝트 구조
```
backend/
├── app/                    # Flask 애플리케이션 패키지
│   ├── __init__.py        # Flask 앱 팩토리
│   ├── config.py          # 설정 관리
│   ├── models/            # 데이터 모델 (향후 구현)
│   ├── routes/            # API 라우트 (향후 구현)
│   │   ├── __init__.py
│   │   └── main.py        # 기본 라우트
│   ├── services/          # 비즈니스 로직 (향후 구현)
│   ├── agents/            # AI 에이전트 (향후 구현)
│   ├── tools/             # AI 도구 (향후 구현)
│   ├── utils/             # 유틸리티 함수 (향후 구현)
│   ├── core/              # 핵심 기능 (향후 구현)
│   └── middleware/        # 미들웨어 (향후 구현)
├── tests/                 # 테스트 코드 (향후 구현)
├── migrations/            # 데이터베이스 마이그레이션 (향후 구현)
├── data/                  # 데이터 파일 (향후 구현)
├── logs/                  # 로그 파일 (향후 구현)
├── scripts/               # 유틸리티 스크립트 (향후 구현)
├── requirements.txt       # Python 패키지 의존성
├── run.py                 # Flask 앱 실행 파일
├── .env.example           # 환경변수 템플릿
├── .env                   # 환경변수 (로컬 설정)
├── .gitignore             # Git 무시 파일
└── README.md              # 백엔드 가이드 (이 파일)
```

## 개발 가이드

### 코드 스타일
- **Blueprint 패턴**: 라우트를 기능별로 분리
- **팩토리 패턴**: `create_app()` 함수로 앱 생성
- **환경변수 활용**: 설정값은 .env 파일로 관리
- **한글 주석**: 코드 이해를 위한 한글 주석 작성

### 디버깅
- **Flask 디버그 모드**: 코드 변경 시 자동 재시작
- **로그 확인**: 터미널에서 요청/응답 로그 확인
- **에러 처리**: 기본 404, 500 에러 핸들러 구현

### 테스트 방법
1. **서버 시작 테스트**: `python run.py` 실행 후 http://localhost:5000 접속
2. **API 응답 테스트**: 브라우저 또는 Postman으로 엔드포인트 호출
3. **CORS 테스트**: 프론트엔드에서 API 호출이 정상 작동하는지 확인

## 문제 해결

### 자주 발생하는 문제
1. **가상환경 미활성화**: 프롬프트에 (venv) 표시 확인
2. **패키지 설치 오류**: pip 업그레이드 후 재시도 (`pip install --upgrade pip`)
3. **포트 충돌**: 5000번 포트가 사용 중인 경우 다른 포트 사용
4. **환경변수 오류**: .env 파일 존재 및 설정값 확인

### 로그 확인 방법
```bash
# Flask 앱 실행 시 터미널에서 로그 확인
python run.py

# 요청 로그 예시:
# 127.0.0.1 - - [날짜] "GET / HTTP/1.1" 200 -
```

---
**개발 환경**: Python 3.x, Flask 3.1.1  
**포트**: 5000  
**CORS**: http://localhost:5173 (프론트엔드)