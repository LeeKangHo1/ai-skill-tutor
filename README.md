# AI 활용법 학습 튜터 (AI Skill Tutor)

## 프로젝트 개요
**입사 포트폴리오용 MVP 프로젝트**로, AI 입문자를 위한 개인화된 멀티에이전트 기반 학습 튜터 시스템입니다.

### 포트폴리오 목적
- **빠른 개발과 핵심 기능 중심**: 복잡한 배포 설정보다는 로컬 개발 환경에서 동작하는 완성도 높은 MVP
- **최신 기술 스택 활용**: Flask + Vue 3 + LangGraph를 통한 현대적인 웹 애플리케이션 개발 역량 증명
- **AI 멀티에이전트 시스템**: LangChain/LangGraph를 활용한 전문화된 AI 에이전트들의 협력 시스템 구현
- **RAG 시스템**: ChromaDB 벡터 데이터베이스를 활용한 지능형 검색 및 답변 생성

### MVP 범위
- **대상 사용자**: AI 입문자 (초급 수준 8개 챕터 완전 구현)
- **핵심 기능**: 사용자 진단 → 개인화된 학습 경로 → 1:1 AI 튜터링 → 실시간 피드백
- **학습 플로우**: 1세션 = 개념 설명 + 1문제 풀이 + 평가 피드백
- **하이브리드 UX**: 자유 대화 모드와 제한 UI 모드의 적절한 조합

## 기술 스택

### 백엔드
- **Python Flask** (Blueprint 기반 구조)
- **MySQL 8.0** (PyMySQL 사용)
- **LangChain, LangGraph, LangSmith** (멀티에이전트 시스템)
- **ChromaDB** (벡터 데이터베이스, RAG 시스템)
- **JWT** 인증, **bcrypt** 암호화
- **OpenAI GPT-4o-mini** (AI 모델)
- **text-embedding-3-large** (임베딩 모델)

### 프론트엔드
- **Vue 3** (Vite + Composition API)
- **Pinia** (상태관리)
- **Vue Router** (라우팅)
- **Axios** (HTTP 통신)
- **SCSS + Bootstrap** (스타일링)

### AI 모델 및 임베딩
- **일반 학습**: GPT-4o-mini (비용 효율성)
- **임베딩**: text-embedding-3-large (ChromaDB 벡터 저장)
- **LangSmith**: 자동 추적 및 성능 모니터링

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
# .env 파일에서 다음 항목들을 설정해주세요:
# - DATABASE_URL (MySQL 연결 정보)
# - JWT_SECRET_KEY (JWT 토큰 암호화 키)
# - OPENAI_API_KEY (OpenAI API 키)
# - LANGSMITH_API_KEY (LangSmith 추적용, 선택사항)

# MySQL 데이터베이스 생성 및 테이블 생성
# (MySQL 서버가 실행 중이어야 합니다)

# ChromaDB 벡터 데이터베이스 구축 (최초 1회만)
python -c "from app.services.external.vector_db_setup import setup_vector_database; setup_vector_database()"

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

## 멀티에이전트 시스템 아키텍처 (v2.0)
```
SessionManager (✅ 완성 - 세션 생명주기 관리, DB 저장)
└── LearningSupervisor (✅ 완성 - 워크플로우 시작점/끝점, 라우팅 및 응답 생성)
    ├── TheoryEducator (✅ 완성 - 벡터 DB 기반 이론 설명 생성)
    ├── QuizGenerator (✅ 완성 - 퀴즈 및 힌트 동시 생성)
    ├── EvaluationFeedbackAgent (✅ 완성 - 객관식/주관식 통합 평가)
    └── QnAResolver (✅ 완성 - LangChain Agent 기반 RAG 시스템)
```

### 핵심 기술적 특징
- **중앙집중식 라우팅**: LearningSupervisor 기반 통합 라우팅 관리
- **LCEL 파이프라인**: `PromptTemplate | ChatOpenAI | OutputParser` 표준 패턴
- **Function Calling**: QnAResolver의 지능형 벡터 검색 자동화
- **트랜잭션 기반 DB 저장**: 4개 테이블 동시 저장으로 데이터 무결성 보장
- **비용 최적화**: ChatGPT 1회 호출로 채점+피드백 동시 처리

## 학습 플로우
1. **회원가입/로그인** → 사용자 진단 → AI 입문자 유형 결정
2. **대시보드**에서 챕터 선택 → 학습 진행 페이지
3. **1학습 세션** = 개념 설명 + 1문제 풀이 + 평가 피드백
4. 세션 완료 시 다음 챕터로 진행 또는 재학습

## 주요 기능 (MVP 범위)

### ✅ 완성된 기능
- **사용자 인증 시스템**: JWT + HttpOnly 쿠키 + 단일 세션 정책
- **사용자 진단**: 5-7문항 기반 AI 입문자 수준 판별
- **멀티에이전트 튜터링**: LangGraph 기반 5개 전문화된 AI 에이전트 협력
- **벡터 기반 RAG**: ChromaDB + OpenAI 임베딩을 활용한 지능형 검색
- **학습 세션 관리**: 체계적인 학습 진도 추적 및 DB 저장
- **평가 시스템**: 객관식(로컬) + 주관식(ChatGPT) 통합 평가
- **실시간 Q&A**: Function Calling 기반 맥락적 질문 답변

### 🔄 프론트엔드 구현
- **하이브리드 UX**: Vue.js 기반 chat/quiz 모드 자동 전환
- **대시보드**: 학습 진행 상황 및 통계 시각화
- **학습 진행 페이지**: 에이전트별 테마 및 상호작용 UI

## 개발 진행 상황

### ✅ 백엔드 완성 (2025-08-24 기준)
- [x] 프로젝트 기본 구조 설계 및 환경 설정
- [x] Python 가상환경 및 Flask Blueprint 구조 구축
- [x] MySQL 데이터베이스 설계 및 구축 (4개 테이블)
- [x] 사용자 인증 시스템 (JWT + HttpOnly 쿠키)
- [x] 사용자 진단 시스템 (5-7문항 + 점수 계산)
- [x] 멀티에이전트 시스템 구현 (LangGraph + 5개 에이전트)
- [x] ChromaDB 벡터 데이터베이스 구축 (157개 청크)
- [x] RAG 시스템 구현 (벡터 검색 + Function Calling)
- [x] 학습 세션 관리 시스템 (트랜잭션 기반 DB 저장)
- [x] 대시보드 API (진행 상황 + 통계 + 챕터 상태)

### ✅ 프론트엔드 완성
- [x] Vue 3 + Vite 프론트엔드 애플리케이션 구축
- [x] 인증 UI (로그인/회원가입 + 자동 토큰 갱신)
- [x] 진단 UI (문항 진행 + 결과 표시 + 유형 선택)
- [x] 대시보드 UI (학습 진행 상황 + 통계 시각화)
- [x] 하이브리드 UX 시스템 (chat/quiz 모드 자동 전환)

### ✅ 최근 완료 작업 (2025-08-25 MVP 완성)
- [x] 학습 진행 페이지 백엔드 연동
- [x] 8개 챕터 상세 학습 자료 완성
- [x] 간단한 사용자 테스트

## 참고 문서
- [전체 PRD v2.0](docs/my_docs/ai_skill_tutor_prd_v2_0.md) - 프로젝트 요구사항 및 아키텍처
- [랭그래프 State 설계 v2.0](docs/my_docs/langgraph_state_design_v2_0.md) - 멀티에이전트 상태 관리
- [DB 설계 v2.0](docs/my_docs/db_design_v2_0.md) - 데이터베이스 스키마
- [API 설계 v2.0](docs/my_docs/api_docs_v2_0.md) - REST API 명세
- [UI 설계 v2.0](docs/my_docs/ui_design_v2_0.md) - 프론트엔드 설계
- [프로젝트 폴더 구조](docs/my_docs/project_folder_structure.md) - 디렉토리 구조
- [구현 로그](docs/my_docs/implementation_log.md) - 최신 개발 진행 상황
- [프론트엔드 구현 로그](docs/my_docs/implementation_log_front.md) - 프론트엔드 개발 기록

## 라이선스
이 프로젝트는 포트폴리오 목적으로 개발되었습니다.

## 기술적 성과

### 멀티에이전트 시스템
- **LangGraph 워크플로우**: 5개 전문화된 AI 에이전트의 협력 시스템
- **중앙집중식 라우팅**: 의도 분석 2단계 시스템으로 100% 정확한 에이전트 라우팅
- **State 일관성**: TutorState 필드 정의로 LangGraph 안정성 확보

### RAG 시스템
- **벡터 데이터베이스**: ChromaDB + OpenAI 임베딩으로 157개 학습 청크 저장
- **Function Calling**: ChatGPT Agent가 필요시에만 벡터 검색 수행
- **폴백 전략**: 벡터 검색 실패 시 JSON 파일 기반 자동 폴백

### 성능 최적화
- **비용 효율성**: ChatGPT 1회 호출로 채점+피드백 동시 처리
- **DB 무결성**: 트랜잭션 기반 4개 테이블 동시 저장
- **토큰 효율성**: 메타데이터 최적화로 토큰 사용량 50% 절약

---
**개발자**: AI 활용법 학습 튜터 프로젝트  
**개발 기간**: 2025년 7월 28일 ~ 8월 25일 MVP 완성  
**목적**: 입사 포트폴리오용 MVP  
**최종 업데이트**: 2025년 8월 25일