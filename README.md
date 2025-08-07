# AI 활용법 학습 튜터 (AI Skill Tutor)

## 프로젝트 개요
**입사 포트폴리오용 MVP 프로젝트**로, AI 입문자를 위한 개인화된 학습 튜터 시스템입니다.

### 포트폴리오 목적
- **빠른 개발과 핵심 기능 중심**: 복잡한 배포 설정보다는 로컬 개발 환경에서 동작하는 완성도 높은 MVP
- **최신 기술 스택 활용**: Flask + Vue 3 + LangGraph를 통한 현대적인 웹 애플리케이션 개발 역량 증명
- **AI 멀티에이전트 시스템**: LangChain/LangGraph를 활용한 전문화된 AI 에이전트들의 협력 시스템 구현

### MVP 범위
- **대상 사용자**: AI 입문자 (초급 수준만 구현)
- **핵심 기능**: 사용자 진단 → 개인화된 학습 경로 → 1:1 AI 튜터링 → 실시간 피드백
- **학습 플로우**: 1세션 = 개념 설명 + 1문제 풀이 + 평가 피드백

## 기술 스택

### 백엔드
- **Python Flask** (Blueprint 기반 구조)
- **MySQL 8.0** (PyMySQL 사용)
- **LangChain, LangGraph, LangSmith** (멀티에이전트 시스템)
- **ChromaDB** (벡터 데이터베이스)
- **JWT** 인증, **bcrypt** 암호화

### 프론트엔드
- **Vue 3** (Vite + Composition API)
- **Pinia** (상태관리)
- **Vue Router** (라우팅)
- **Axios** (HTTP 통신)
- **SCSS + Bootstrap** (스타일링)

## 전체 실행 방법

### 1. 프로젝트 클론 및 초기 설정
```bash
git clone <repository-url>
cd ai-skill-tutor
```

### 2. Python 가상환경 설정
```bash
# 가상환경 생성 (프로젝트 루트에서 실행)
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 3. 백엔드 설정 및 실행
```bash
# 백엔드 디렉토리로 이동
cd backend

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정 (.env.example을 참고하여 .env 파일 생성)
cp .env.example .env

# Flask 애플리케이션 실행
python run.py
```
백엔드 서버가 http://localhost:5000 에서 실행됩니다.

### 4. 프론트엔드 설정 및 실행 (새 터미널)
```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 패키지 설치
npm install

# 개발 서버 실행
npm run dev
```
프론트엔드 서버가 http://localhost:5173 에서 실행됩니다.

### 5. 통합 테스트
- 백엔드: http://localhost:5000 접속하여 "AI Skill Tutor API" 메시지 확인
- 프론트엔드: http://localhost:5173 접속하여 "AI 활용법 학습 튜터" 페이지 확인
- 프론트엔드에서 백엔드 API 호출이 정상 작동하는지 확인

## 프로젝트 구조
```
ai-skill-tutor/
├── backend/                 # Python Flask API 서버
├── frontend/               # Vue.js 클라이언트 애플리케이션
├── docs/                   # 프로젝트 설계 문서
├── .kiro/                  # Kiro 설정 및 specs
├── venv/                   # Python 가상환경
├── README.md               # 프로젝트 가이드
└── .gitignore              # Git 무시 파일
```

## 멀티에이전트 시스템 아키텍처
```
SessionManager (세션 관리 전담)
└── LearningSupervisor (사용자 대면 + 라우팅 + 응답 생성)
    ├── TheoryEducator (개념 설명 대본 생성)
    ├── QuizGenerator (문제 출제 대본 생성)
    ├── EvaluationFeedbackAgent (평가 및 피드백 대본 생성)
    └── QnAResolver (질문 답변 대본 생성)
```

## 학습 플로우
1. **회원가입/로그인** → 사용자 진단 → AI 입문자 유형 결정
2. **대시보드**에서 챕터 선택 → 학습 진행 페이지
3. **1학습 세션** = 개념 설명 + 1문제 풀이 + 평가 피드백
4. 세션 완료 시 다음 챕터로 진행 또는 재학습

## 주요 기능 (MVP 범위)
- **사용자 진단**: AI 입문자 수준 판별 및 맞춤형 학습 경로 제공
- **멀티에이전트 튜터링**: LangGraph 기반 전문화된 AI 에이전트들의 협력
- **실시간 피드백**: 학습 과정에서 즉시 제공되는 개인화된 AI 피드백
- **학습 세션 관리**: 체계적인 학습 진도 추적 및 성취도 분석

## 개발 진행 상황
- [x] 프로젝트 기본 구조 설계 및 환경 설정
- [x] Python 가상환경 및 Flask 기본 구조 구축
- [x] Vue 3 프론트엔드 애플리케이션 구축
- [x] 기본 API 연동 및 CORS 설정
- [ ] 데이터베이스 설계 및 구축
- [ ] 사용자 인증 시스템 (JWT)
- [ ] 멀티에이전트 시스템 구현 (LangGraph)
- [ ] AI 진단 기능
- [ ] 학습 세션 관리 시스템

## 참고 문서
- [전체 PRD](docs/my_docs/ai_skill_tutor_prd_v1_3.md)
- [랭그래프 State 설계](docs/my_docs/langgraph_state_design_v1_3.md)
- [DB 설계](docs/my_docs/db_design_v1_3.md)
- [API 설계](docs/my_docs/api_docs_v1_3.md)
- [UI 설계](docs/my_docs/ui_design_v1_3.md)
- [프로젝트 폴더 구조](docs/my_docs/project_folder_structure.md)

## 라이선스
이 프로젝트는 포트폴리오 목적으로 개발되었습니다.

---
**개발자**: AI 활용법 학습 튜터 프로젝트  
**개발 기간**: 2025년 1월 ~ 진행중  
**목적**: 입사 포트폴리오용 MVP