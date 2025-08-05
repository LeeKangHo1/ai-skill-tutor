# AI 활용법 학습 튜터 프로젝트 컨텍스트

## 프로젝트 개요
- **프로젝트명**: AI 활용법 학습 튜터 (AI Skill Tutor)
- **목적**: 입사 포트폴리오용 MVP 프로젝트
- **개발 목표**: 빠른 완성, 핵심 기능 중심, 로컬 개발 환경
- **대상 사용자**: AI 입문자 (MVP에서는 이 유형만 구현)

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

## 핵심 아키텍처

### 멀티에이전트 시스템 (LangGraph)
```
SessionManager (세션 관리 전담)
└── LearningSupervisor (사용자 대면 + 라우팅 + 응답 생성)
    ├── TheoryEducator (개념 설명 대본 생성)
    ├── QuizGenerator (문제 출제 대본 생성)
    ├── EvaluationFeedbackAgent (평가 및 피드백 대본 생성)
    └── QnAResolver (질문 답변 대본 생성)
```

### 학습 플로우
1. 회원가입/로그인 → 사용자 진단 → AI 입문자 유형 결정
2. 대시보드에서 챕터 선택 → 학습 진행 페이지
3. **1학습 세션 = 개념 설명 + 1문제 풀이 + 평가 피드백**
4. 세션 완료 시 다음 챕터로 진행 또는 재학습

## 개발 방식

### Spec 분할 전략
1. **인프라/기반 계층**: project-foundation, database-system, authentication-core 등
2. **핵심 비즈니스 로직**: user-diagnosis, session-management, 각 에이전트별 spec
3. **통합 및 고급 기능**: learning-interface, external-services, ui-components
4. **최적화 및 완성**: performance-optimization, testing-deployment

### 개발 원칙
- **MVP 우선**: 복잡한 배포 설정보다 핵심 기능 완성
- **점진적 확장**: 기본 구조부터 시작해서 필요할 때마다 폴더/파일 추가
- **최신 패키지**: 버전 고정 없이 최신 버전 사용, 문제 시 개별 조정
- **포트폴리오 품질**: 코드 가독성과 구조의 명확성 중시

## 주요 문서 위치
- **전체 PRD**: `docs/ai_skill_tutor_prd_v1_3.md`
- **State 설계**: `docs/langgraph_state_design_v1_3.md`
- **DB 설계**: `docs/db_design_v1_3.md`
- **UI 설계**: `docs/ui_design_v1_3.md`
- **API 설계**: `docs/api_docs_v1_3.md`
- **폴더 구조**: `docs/backend_folder_structure.txt`, `docs/frontend_folder_structure.md`

## 현재 진행 상황
- **완료**: project-foundation spec 작성 (requirements, design, tasks)
- **다음 단계**: project-foundation tasks 실행 → 기본 프로젝트 구조 생성

## 중요 참고사항
- 가상환경은 프로젝트 루트에서 생성 (`python -m venv venv`)
- Flask는 Blueprint 구조 사용
- Vue는 Composition API 사용
- 모든 패키지는 최신 버전으로 설치