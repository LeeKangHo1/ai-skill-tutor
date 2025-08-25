## File Creation and Code Writing Rules

 - At the top of each file, add a comment indicating the file path and file name, like: `# path/to/filename.py`
 - Add brief Korean comments explaining the purpose of each core function or block of logic.


## Korean Response Rules - Language Settings

 - All responses must be written in Korean.
 - Code comments should be written in Korean whenever possible.
 - Technical terms should be written in both English and Korean when necessary (e.g., "컨테이너(container)").
 - Error messages or logs must remain in their original language, but explanations should be provided in Korean.

## Korean Response Rules - Exception Cases

 - The code itself (e.g., variable names, function names) must be written in English.
 - Official documentation or command-line instructions should remain in their original language.
 - Exceptions can be made only if the user explicitly requests another language.

## Terminal Command Execution Rules

 - Before executing any command, check if the virtual environment is activated. If not, activate it before running commands.
 - All terminal commands must be based on Windows PowerShell.

---

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

## AI 모델 및 임베딩 시스템

### 모델 선택 기준
- **일반 학습**: GPT-4o-mini

### 임베딩 시스템
- **text-embedding-3-large 고정 사용**: ChromaDB 벡터 저장

## 핵심 아키텍처

## 멀티에이전트 시스템 아키텍처 (v2.0)
```
SessionManager (✅ 완성 - 세션 생명주기 관리, DB 저장)
└── LearningSupervisor (✅ 완성 - 워크플로우 시작점/끝점, 라우팅 및 응답 생성)
    ├── TheoryEducator (✅ 완성 - 벡터 DB 기반 이론 설명 생성)
    ├── QuizGenerator (✅ 완성 - 퀴즈 및 힌트 동시 생성)
    ├── EvaluationFeedbackAgent (✅ 완성 - 객관식/주관식 통합 평가)
    └── QnAResolver (✅ 완성 - LangChain Agent 기반 RAG 시스템)
```

### 학습 플로우
1. 회원가입/로그인 → 사용자 진단 → AI 입문자 유형 결정
2. 대시보드에서 챕터 선택 → 학습 진행 페이지
3. **1학습 세션 = 개념 설명 + 1문제 풀이 + 평가 피드백**
4. 세션 완료 시 다음 챕터로 진행 또는 재학습

## 주요 문서 위치
- **전체 PRD**: `docs/my_docs/ai_skill_tutor_prd_v2_0.md`
- **State 설계**: `docs/my_docs/langgraph_state_design_v2_0.md`
- **DB 설계**: `docs/my_docs/db_design_v2_0.md`
- **UI 설계**: `docs/my_docs/ui_design_v2_0.md`
- **API 설계**: `docs/my_docs/api_docs_v2_0.md`
- **폴더 구조**: `docs/my_docs/project_folder_structure.md`
- **백엔드 구현 로그**: `docs/my_docs/implementation_log.md` (최신 개발 상황 및 변경사항)
- **프론트엔드 구현 로그**: `docs/my_docs/implementation_log_front.md` (최신 개발 상황 및 변경사항)

## 보안 가이드라인
- **환경변수 관리**: 실제 비밀번호, API 키, 데이터베이스 정보는 절대 코드나 문서에 하드코딩하지 않음
- **.env 파일**: 실제 환경변수는 .env 파일에서 관리하고, .env.example에는 예시 형태로만 작성
- **Spec 문서**: 설계 문서에는 실제 비밀번호 대신 `os.getenv()` 형태나 플레이스홀더 사용
- **Git 관리**: .env 파일은 .gitignore에 포함하여 버전 관리에서 제외
- **포트폴리오 배포**: 웹 배포 시에도 실제 운영 정보가 노출되지 않도록 주의
- **데이터베이스**: 개발용과 배포용 데이터베이스 분리, 기본 계정(root) 사용 금지
- **JWT 시크릿**: JWT_SECRET_KEY는 충분히 복잡한 랜덤 문자열 사용
- **코드 작성 규칙**: 모든 코드(메인 코드, 테스트 코드 포함)에서 환경변수는 반드시 `os.getenv()` 또는 `python-dotenv`를 통해 .env 파일에서 읽어와야 함
- **테스트 환경**: 테스트 파일에서도 하드코딩된 값 사용 금지, 테스트용 환경변수 또는 모킹 사용

## Implementation Log 작성 규칙

1. **최신 로그가 위로**: 새로운 구현 내용은 파일 상단에 추가하여 최신 정보가 먼저 보이도록 함
2. **사용자 지시 전에는 작성하지 않음**: 사용자가 명시적으로 요청하기 전까지는 implementation_log.md에 내용을 추가하지 않음
