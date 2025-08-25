# 백엔드 폴더 구조 (v2.0 MVP - 2025.08.25 업데이트)

```
backend/
├── app/                              # Flask 애플리케이션 메인 디렉토리
│   ├── __init__.py                   # Flask 앱 팩토리 함수 (Blueprint 등록, CORS 설정, 로깅)
│   ├── agents/                       # LangGraph 에이전트 시스템
│   │   ├── __init__.py               # 에이전트 모듈 초기화, 에이전트 별 단일 인스턴스 생성
│   │   ├── evaluation_feedback/      # 평가 피드백 에이전트
│   │   │   ├── __init__.py           # 
│   │   │   └── evaluation_feedback_agent.py # ✅EvaluationFeedbackAgent 핵심 코드
│   │   ├── learning_supervisor/      # 학습 감독 에이전트
│   │   │   ├── __init__.py           # 
│   │   │   ├── learning_supervisor_agent.py # ✅LearningSupervisor 핵심 코드
│   │   │   ├── response_generator.py # 최종 응답 생성기
│   │   │   └── supervisor_router.py  # LangGraph conditional_edges용 라우터 함수
│   │   ├── qna_resolver/             # 질문 답변 에이전트
│   │   │   ├── __init__.py           # 
│   │   │   ├── qna_resolver_agent.py # ✅QnA 에이전트 핵심 코드
│   │   ├── quiz_generator/           # 퀴즈 생성 에이전트
│   │   │   ├── __init__.py           # 
│   │   │   └── quiz_generator_agent.py # ✅QuizGenerator 에이전트 핵심 코드
│   │   ├── session_manager/          # 세션 관리 에이전트
│   │   │   ├── __init__.py           # 
│   │   │   ├── session_handlers.py   # 세션 처리 핸들러
│   │   │   └── session_manager_agent.py # ✅SessionManager 에이전트 핵심 코드
│   │   └── theory_educator/          # 이론 교육 에이전트
│   │       ├── __init__.py           # 
│   │       └── theory_educator_agent.py # ✅TheoryEducator 에이전트 핵심 코드
│   ├── config/                       # 설정 파일들
│   │   ├── __init__.py
│   │   ├── base.py                   # 기본 설정
│   │   ├── db_config.py              # 데이터베이스 설정 전용
│   │   ├── development.py            # 개발 환경 설정
│   │   ├── production.py             # 운영 환경 설정 (미구현)
│   │   └── testing.py                # 테스트 환경 설정 (미구현)
│   ├── core/                         # 핵심 시스템 구성 요소
│   │   ├── __init__.py
│   │   ├── database/                 # 데이터베이스 관련 (미사용 폴더, utils/database 파일을 사용)
│   │   ├── external/                 # 외부 서비스 연동
│   │   │   ├── __init__.py
│   │   │   ├── chroma_client.py      # ChromaDB 연결 설정 및 관리
│   │   │   └── vector_db.py          # 벡터 데이터베이스 초기 구축 및 데이터 삽입 클래스
│   │   └── langraph/                 # ✅LangGraph 관련
│   │       ├── __init__.py
│   │       ├── managers/             # 도메인별 State 관리자
│   │       │   ├── __init__.py       # 모든 관리자 export
│   │       │   ├── agent_manager.py  # 에이전트 전환 관리
│   │       │   ├── conversation_manager.py # 대화 관리
│   │       │   ├── quiz_manager.py   # 퀴즈 관련 State 관리
│   │       │   └── session_manager.py # 세션 진행 State 관리
│   │       ├── state/                # State 정의 및 기본 관리
│   │       │   ├── __init__.py       # State 관련 export
│   │       │   ├── state_definition.py # TutorState TypedDict 정의
│   │       │   ├── state_factory.py  # State 생성 및 초기화
│   │       │   └── state_validator.py # State 유효성 검증
│   │       ├── graph_builder.py      # 랭그래프 빌더
│   │       ├── state_manager.py      # State 관리 통합 래퍼 클래스 (호환성)
│   │       └── workflow.py           # 워크플로우 정의
│   ├── models/                       # 데이터베이스 모델 (미사용)
│   │   ├── __init__.py               # 직접 SQL 쿼리를 사용하고 있으며, ORM 모델은 비활성화 상태
│   │   ├── chapter/                  # 챕터 관련 모델들 (미사용)
│   │   │   ├── __init__.py
│   │   │   └── chapter.py            # 챕터 모델
│   │   ├── learning/                 # 학습 관련 모델들 (미사용)
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py       # 대화 기록 모델
│   │   │   ├── quiz.py               # 퀴즈 관련 모델
│   │   │   └── session.py            # 학습 세션 모델
│   │   └── user/                     # 사용자 관련 모델들 (미사용)
│   │       ├── __init__.py
│   │       ├── auth_token.py         # 인증 토큰 모델
│   │       ├── user.py               # 기본 사용자 모델
│   │       └── user_progress.py      # 사용자 진행 상태 모델
│   ├── routes/                       # API 라우트 (Blueprint)
│   │   ├── __init__.py               # system_blueprints, diagnosis_blueprints import
│   │   ├── auth/                     # 인증 관련 라우트
│   │   │   ├── __init__.py           # auth_blueprints 정의
│   │   │   ├── login.py              # 로그인/로그아웃/사용자정보 API
│   │   │   ├── register.py           # 회원가입/중복확인 API
│   │   │   └── token.py              # 토큰 갱신/검증/세션관리 API
│   │   ├── dashboard/                
│   │   │   ├── __init__.py
│   │   │   ├── overview.py           # 대시보드 라우트
│   │   ├── diagnosis/                # 진단 관련 라우트
│   │   │   ├── __init__.py           # diagnosis_blueprints 정의
│   │   │   ├── questions.py          # 진단 문항 조회 API
│   │   │   └── submit.py             # 진단 결과 제출 + 유형 선택 API
│   │   ├── learning/                 # 학습 세션 라우트
│   │   │   ├── __init__.py
│   │   │   ├── quiz/                 # 퀴즈 관리
│   │   │   │   ├── __init__.py
│   │   │   │   └── submit.py         # 답변 제출
│   │   │   └── session/              # 세션 관리
│   │   │       ├── __init__.py
│   │   │       ├── complete.py       # 세션 정리
│   │   │       ├── message.py        # 메시지 처리
│   │   │       └── start.py          # 세션 시작
│   │   └── system/                   # 시스템 관련 라우트
│   │       ├── __init__.py           # system_blueprints 정의
│   │       ├── health.py             # 헬스체크 API
│   │       └── version.py            # 기본 API 정보 + /version 엔드포인트
│   ├── services/                     # 비즈니스 로직 서비스
│   │   ├── __init__.py
│   │   ├── auth/                     # 인증 서비스
│   │   │   ├── __init__.py
│   │   │   ├── login_service.py      # 로그인 처리 및 토큰 발급
│   │   │   ├── register_service.py   # 회원가입 처리 및 검증
│   │   │   └── token_service.py      # 토큰 갱신/검증/세션관리
│   │   ├── dashboard/                # 대쉬보드
│   │   │   ├── __init__.py
│   │   │   └── dashboard_service.py  # 대시보드 통계 서비스
│   │   ├── learning/                 # 학습 진행 서비스
│   │   │   ├── __init__.py
│   │   │   └── session_service.py    # 학습 관련 서비스 로직
│   │   ├── diagnosis_service.py      # 진단 점수 계산 및 유형 추천
│   ├── tools/                        # LangGraph 도구 함수들
│   │   ├── __init__.py
│   │   ├── analysis/                 # 분석/평가 도구
│   │   │   ├── __init__.py
│   │   │   ├── evaluation_tools.py   # 로컬 채점
│   │   │   └── intent_analysis_tools.py # 의도 분석 도구
│   │   ├── content/                  # 컨텐츠 생성 도구
│   │   │   ├── __init__.py
│   │   │   ├── feedback_tools_chatgpt.py # ChatGPT 기반 피드백 생성 도구
│   │   │   ├── qna_tools_chatgpt.py    # LangChain Agent 기반 QnA 답변 생성
│   │   │   ├── quiz_tools_chatgpt.py   # ChatGPT 기반 퀴즈 생성 도구
│   │   │   └── theory_tools_chatgpt.py # ChatGPT 기반 이론 설명 생성
│   │   ├── external/                 # 외부 연동 도구
│   │   │   ├── __init__.py
│   │   │   ├── vector_search_tools.py # ChromaDB 벡터 검색
│   │   │   └── web_search_tools.py   # 웹 검색 도구 (미구현)
│   └── utils/                        # 유틸리티 함수
│       ├── __init__.py
│       ├── auth/                     # 인증 유틸리티
│       │   ├── __init__.py
│       │   ├── jwt_handler.py        # JWT 토큰 생성/검증/데코레이터
│       │   └── password_handler.py   # bcrypt 비밀번호 해시화/검증
│       ├── common/                   # 공통 유틸리티
│       │   ├── __init__.py
│       │   ├── chat_logger.py        # 사용자별 JSON 대화 로그 저장 시스템
│       │   ├── constants.py          # 상수 정의
│       │   ├── exceptions.py         # 계층적 커스텀 예외 클래스
│       │   ├── graph_visualizer.py   # 랭그래프 실행 시 그래프 그림 저장
│       │   └── helpers.py            # 헬퍼 함수들
│       ├── database/                 # 데이터베이스 유틸리티
│       │   ├── __init__.py
│       │   ├── connection.py         # DB 연결 관리
│       │   ├── query_builder.py      # 쿼리 빌더
│       │   └── transaction.py        # 트랜잭션 관리
│       ├── logging/                  # 로깅 유틸리티
│       │   ├── __init__.py
│       │   └── logger.py             # 백엔드 애플리케이션 로깅 시스템(access, app, error)
│       ├── response/                 # 응답 처리 유틸리티
│       │   ├── __init__.py
│       │   ├── error_formatter.py    # 에러 응답 전용 포맷터
│       │   └── formatter.py          # 표준화된 응답 포맷터
│       └── validation/               # 검증 유틸리티(미사용)
│           └── __init__.py
├── data/                            # 정적 데이터 
│   ├── chapters/                     # 챕터별 데이터
│   │   ├── chapter_01.json ~ chapter_08.json # 학습 기초 데이터
│   │   └── chapters_metadata.json    # 챕터 메타데이터
│   ├── chat_log/                     # 사용자별 대화 로그 저장
│   │   ├── user1/                    # user + user_id
│   │   └── ... (생략)                 
│   ├── chroma_db/                    # ChromaDB 벡터 데이터베이스
│   │   ├── chroma.sqlite3            # ChromaDB SQLite 파일
│   │   └── e126144a-9665-45db-b45a-3be8a69f21f3/ # 벡터 컬렉션 데이터
│   ├── contents_beginner.md          # 초급자용 컨텐츠
│   ├── diagnosis_questions.json      # 진단 퀴즈 문항
│   ├── qna_context_metadata.json     # QnA 컨텍스트 메타데이터
│   ├── tutor_workflow_graph.png      # LangGraph 워크플로우 시각화
│   └── vector_insertion_log.json     # 벡터DB 자료 삽입 로그
├── logs/                            # 로그 파일
│   ├── access.log                   # 액세스 로그
│   ├── app.log                      # 애플리케이션 로그
│   └── error.log                    # 에러 로그
├── migrations/                       # 데이터베이스 마이그레이션
│   ├── create_schema.py              # 스키마 생성 스크립트
│   ├── schema.sql                    # SQL 스키마 파일
│   └── verify_schema.py              # 스키마 검증 스크립트
├── scripts/                         # 유틸리티 스크립트
│   ├── check_db_schema.py           # 데이터베이스 스키마 확인
│   ├── check_table_structure.py     # 테이블 구조 확인
│   ├── clear_all_tables.py          # 모든 테이블 데이터 초기화
│   ├── migrate_duration_to_seconds.py # 지속시간 초 단위 마이그레이션
│   └── README.md                    # 스크립트 사용법 안내
├── tests/                            # 테스트 코드 (날짜별 폴더 구조, 내용 생략)
│   ├── 0818/                         # 2025-08-18 테스트 (LangGraph 인터랙티브)
│   ├── 0820/                         # 2025-08-20 테스트 (통합 테스트)
│   ├── 0821/                         # 2025-08-21 테스트 (API 테스터)
│   ├── 0824/                         # 2025-08-12 테스트 (QnA 기능 테스트)
│   └── terminal_tester_by_claude/    # 최종 백엔드 터미널 테스터
├── .env                            # 환경변수 파일 (gitignore)
├── .env.example                     # 환경변수 예시 파일
├── .gitignore                      # Git 무시 파일
├── README.md                       # 프로젝트 설명
├── requirements.txt                # Python 패키지 의존성
└── run.py                          # Flask 애플리케이션 실행 파일
```

---


# 프론트엔드 폴더 구조 (v2.0 MVP - 2025.08.25 업데이트)

```
frontend/
├── node_modules/                  # NPM 패키지 (내용 생략)
├── src/                           # 소스 코드
│   ├── __tests__/                 # 테스트 파일
│   │   └── basic.test.js          # 기본 테스트
│   ├── assets/                    # 정적 자원 (미사용)
│   │   ├── icons/                 # 아이콘 파일들
│   │   └── images/                # 이미지 파일들
│   ├── components/                
│   │   ├── auth/                  # 인증 관련 컴포넌트
│   │   │   ├── LoginForm.vue      # 로그인 폼 컴포넌트
│   │   │   └── RegisterForm.vue   # 회원가입 폼 컴포넌트
│   │   ├── common/                # 공통 컴포넌트
│   │   │   └── HeaderComponent.vue # 홈페이지 공통 헤더 컴포넌트
│   │   ├── dashboard/             # 대시보드 관련 컴포넌트
│   │   │   ├── ChapterCard.vue    # 챕터 카드 컴포넌트
│   │   │   └── ChapterSection.vue # 챕터 섹션 컴포넌트
│   │   ├── diagnosis/             # 진단 관련 컴포넌트
│   │   │   ├── DiagnosisQuestion.vue # 진단 질문 컴포넌트
│   │   │   └── ProgressBar.vue    # 진단 진행률 바 컴포넌트
│   │   └── learning/              # 학습 관련 컴포넌트
│   │       ├── ChatInteraction.vue # 채팅 상호작용 컴포넌트 (학습 페이지 오른쪽)
│   │       ├── FeedbackContent.vue # 피드백 내용 컴포넌트
│   │       ├── MainContentArea.vue # 메인 콘텐츠 영역(이론, 퀴즈, 피드백) 컴포넌트 (학습 페이지 왼쪽)
│   │       ├── QuizContent.vue    # 퀴즈 내용 컴포넌트
│   │       ├── QuizInteraction.vue # 퀴즈 답변 제출 컴포넌트
│   │       └── TheoryContent.vue  # 이론 내용 컴포넌트
│   ├── router/                    # Vue Router 설정
│   │   ├── authGuard.js           # 인증 가드
│   │   └── index.js               # 라우터 설정 (인증 가드 적용)
│   ├── services/                  # API 서비스
│   │   ├── api.js                 # HTTP 인터셉터가 포함된 API 클라이언트
│   │   ├── authService.js         # 인증 관련 API
│   │   ├── dashboardService.js    # 대시보드 관련 API
│   │   ├── diagnosisService.js    # 진단 관련 API
│   │   ├── index.js               # 서비스 통합 export
│   │   └── learningService.js     # 학습 관련 API
│   ├── stores/                    # Pinia 상태 관리
│   │   ├── authStore.js           # 인증 상태 관리
│   │   ├── dashboardStore.js      # 대시보드 상태 관리
│   │   ├── diagnosisStore.js      # 진단 상태 관리
│   │   ├── index.js               # Pinia store 설정
│   │   └── learningStore.js       # 학습 세션 상태 관리
│   ├── styles/                    # 스타일시트
│   │   ├── components/            # 컴포넌트별 스타일
│   │   │   └── _buttons.scss      # 버튼 스타일
│   │   ├── main.scss              # 메인 스타일시트
│   │   └── variables.scss         # 전역에서 사용하는 SCSS 변수
│   ├── utils/                     # 유틸리티 함수
│   │   ├── cookieUtils.js         # 쿠키 관리 유틸리티
│   │   ├── dataMappers.js         # 데이터 매핑 함수
│   │   └── tokenManager.js        # Access Token 관리 유틸리티
│   ├── views/                     
│   │   ├── auth/                  # 인증 관련 페이지
│   │   │   └── LoginPage.vue      # 로그인 페이지
│   │   ├── common/                
│   │   │   ├── AboutView.vue      # 소개 페이지
│   │   │   └── HomeView.vue       # 홈 페이지
│   │   ├── dashboard/             
│   │   │   └── DashboardPage.vue  # 대시보드 메인 페이지
│   │   ├── diagnosis/             
│   │   │   ├── DiagnosisPage.vue  # 진단 테스트 페이지
│   │   │   └── DiagnosisResultPage.vue # 진단 결과 페이지
│   │   └── learning/              
│   │       └── LearningPage.vue   # 학습 세션 페이지
│   ├── main.js                    # Vue 앱 초기화 및 전역 설정
│   └── App.vue                    # Vue 앱 루트 컴포넌트 (백엔드 연결 상태 표시)
├── .env                           # 환경 변수
├── .gitignore                     # Git 무시 파일
├── index.html                     # HTML 템플릿
├── package-lock.json              # NPM 패키지 잠금 파일
├── package.json                   # NPM 패키지 설정
├── README.md                      # 프로젝트 설명
└── vite.config.js                 # Vite 설정 (Vue DevTools 포함)
```

---

# 프로젝트 루트 구조 (v2.0 MVP - 2025.08.25 업데이트)

```
ai-skill-tutor/
├── .git/                          # Git 버전 관리
├── .gitignore                     # Git 무시 파일 (루트)
├── .kiro/                         # Kiro IDE 설정
├── .vscode/                       # VS Code 설정
├── backend/                       # 백엔드 (Flask + Python)
├── docs/                          # 프로젝트 문서
│   ├── my_docs/                   # 개발 문서
│   └── vector_docs/               # 벡터DB 관련 문서
├── frontend/                      # 프론트엔드 (Vue 3)
├── node_modules/                  # 루트 레벨 Node.js 패키지
├── venv/                          # Python 가상환경
├── copilot-instructions.md        # GitHub Copilot 지침
├── package-lock.json              # 루트 레벨 NPM 잠금 파일
├── package.json                   # 루트 레벨 NPM 설정
├── README.md                      # 프로젝트 메인 README
└── requirements.txt               # 루트 레벨 Python 의존성
```

