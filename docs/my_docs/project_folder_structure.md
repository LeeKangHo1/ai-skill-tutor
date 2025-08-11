# 백엔드 폴더 구조 (v1.3 - 2025.08.11 업데이트)

```
backend/
├── app/                              # Flask 애플리케이션 메인 디렉토리
│   ├── __init__.py                   # Flask 앱 팩토리 함수 (Blueprint 등록 방식 개선)
│   ├── config/                       # 설정 파일들
│   │   ├── __init__.py
│   │   ├── base.py                   # 기본 설정
│   │   ├── development.py            # 개발 환경 설정
│   │   ├── production.py             # 운영 환경 설정
│   │   └── testing.py                # 테스트 환경 설정
│   ├── models/                       # 데이터베이스 모델
│   │   ├── __init__.py
│   │   ├── user/                     # 사용자 관련 모델들
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # 기본 사용자 모델
│   │   │   ├── auth_token.py         # 인증 토큰 모델
│   │   │   └── user_progress.py      # 사용자 진행 상태 모델
│   │   ├── learning/                 # 학습 관련 모델들
│   │   │   ├── __init__.py
│   │   │   ├── session.py            # 학습 세션 모델
│   │   │   ├── conversation.py       # 대화 기록 모델
│   │   │   └── quiz.py               # 퀴즈 관련 모델
│   │   └── chapter/                  # 챕터 관련 모델들
│   │       ├── __init__.py
│   │       └── chapter.py            # 챕터 모델
│   ├── routes/                       # API 라우트 (Blueprint)
│   │   ├── __init__.py               # ✅ 수정됨: system_blueprints, diagnosis_blueprints import
│   │   ├── diagnosis/                # 진단 관련 라우트 (완성됨)
│   │   │   ├── __init__.py           # diagnosis_blueprints 정의
│   │   │   ├── questions.py          # ✅ 구현됨: 진단 문항 조회 API
│   │   │   └── submit.py             # ✅ 구현됨: 진단 결과 제출 + 유형 선택 API
│   │   ├── system/                   # 시스템 관련 라우트 (완성됨)
│   │   │   ├── __init__.py           # ✅ 수정됨: system_blueprints 정의
│   │   │   ├── health.py             # ✅ 구현됨: 헬스체크 API
│   │   │   └── version.py            # ✅ 구현됨: 기본 API 정보 + /version 엔드포인트
│   │   ├── auth/                     # ✅ 인증 관련 라우트 (완성됨)
│   │   │   ├── __init__.py           # auth_blueprints 정의
│   │   │   ├── login.py              # ✅ 구현됨: 로그인/로그아웃/사용자정보 API
│   │   │   ├── register.py           # ✅ 구현됨: 회원가입/중복확인 API
│   │   │   └── token.py              # ✅ 구현됨: 토큰 갱신/검증/세션관리 API
│   │   ├── dashboard/                # 대시보드 라우트 (미구현)
│   │   │   ├── __init__.py
│   │   │   ├── overview.py           # 대시보드 개요
│   │   │   └── statistics.py         # 통계 정보
│   │   └── learning/                 # 학습 세션 라우트 (미구현)
│   │       ├── __init__.py
│   │       ├── session/              # 세션 관리
│   │       │   ├── __init__.py
│   │       │   ├── start.py          # 세션 시작
│   │       │   ├── message.py        # 메시지 처리
│   │       │   └── status.py         # 세션 상태
│   │       ├── quiz/                 # 퀴즈 관리
│   │       │   ├── __init__.py
│   │       │   ├── submit.py         # 답변 제출
│   │       │   └── hint.py           # 힌트 요청
│   │       └── history/              # 학습 기록
│   │           ├── __init__.py
│   │           ├── list.py           # 기록 목록
│   │           └── details.py        # 상세 조회
│   ├── services/                     # 비즈니스 로직 서비스
│   │   ├── __init__.py
│   │   ├── diagnosis_service.py      # ✅ 구현됨: 진단 점수 계산 및 유형 추천
│   │   ├── auth/                     # ✅ 인증 서비스 (완성됨)
│   │   │   ├── __init__.py
│   │   │   ├── login_service.py      # ✅ 구현됨: 로그인 처리 및 토큰 발급
│   │   │   ├── register_service.py   # ✅ 구현됨: 회원가입 처리 및 검증
│   │   │   └── token_service.py      # ✅ 구현됨: 토큰 갱신/검증/세션관리
│   │   ├── user/                     # 사용자 관리 서비스 (미구현)
│   │   │   ├── __init__.py
│   │   │   ├── profile_service.py    # 프로필 관리
│   │   │   └── progress_service.py   # 진행 상태 관리
│   │   ├── learning/                 # 학습 진행 서비스 (미구현)
│   │   │   ├── __init__.py
│   │   │   ├── session_service.py    # 세션 관리 서비스
│   │   │   ├── content_service.py    # 컨텐츠 처리 서비스
│   │   │   └── quiz_service.py       # 퀴즈 처리 서비스
│   │   └── statistics/               # 통계 처리 서비스 (미구현)
│   │       ├── __init__.py
│   │       ├── dashboard_service.py  # 대시보드 통계
│   │       └── report_service.py     # 리포트 생성
│   ├── agents/                       # LangGraph 에이전트 시스템 (부분 구현)
│   │   ├── __init__.py               # ✅ 수정됨: 실제 구조에 맞춰 import 정리
│   │   ├── base/                     # 기본 에이전트 구성 요소
│   │   │   ├── __init__.py           # ✅ 구현됨: BaseAgent, AgentConfig 등 export
│   │   │   ├── base_agent.py         # ✅ 구현됨: 기본 에이전트 클래스
│   │   │   └── agent_config.py       # ✅ 구현됨: 에이전트 설정
│   │   ├── session_manager/          # 세션 관리 에이전트
│   │   │   ├── __init__.py           # ✅ 수정됨: SessionManager, SessionHandlers export
│   │   │   ├── agent.py              # SessionManager 에이전트
│   │   │   └── handlers.py           # 세션 처리 핸들러
│   │   ├── learning_supervisor/      # 학습 감독 에이전트
│   │   │   ├── __init__.py           # ✅ 수정됨: LearningSupervisor 등 export
│   │   │   ├── agent.py              # LearningSupervisor 에이전트
│   │   │   ├── router.py             # 라우팅 로직
│   │   │   └── response_generator.py # 응답 생성기
│   │   ├── theory_educator/          # 이론 교육 에이전트
│   │   │   ├── __init__.py           # ✅ 수정됨: TheoryEducator만 export (간소화)
│   │   │   └── agent.py              # TheoryEducator 에이전트
│   │   ├── quiz_generator/           # 퀴즈 생성 에이전트
│   │   │   ├── __init__.py           # ✅ 수정됨: QuizGenerator만 export (간소화)
│   │   │   └── agent.py              # QuizGenerator 에이전트
│   │   ├── evaluation_feedback/      # 평가 피드백 에이전트
│   │   │   ├── __init__.py           # ✅ 수정됨: EvaluationFeedbackAgent만 export (간소화)
│   │   │   └── agent.py              # EvaluationFeedbackAgent
│   │   └── qna_resolver/             # 질문 답변 에이전트
│   │       ├── __init__.py           # ✅ 수정됨: QnAResolver 등 export
│   │       ├── agent.py              # QnAResolver 에이전트
│   │       ├── query_processor.py    # 질문 처리기
│   │       └── answer_generator.py   # 답변 생성기
│   ├── tools/                        # LangGraph 도구 함수들 (미구현)
│   │   ├── __init__.py
│   │   ├── content/                  # 컨텐츠 생성 도구
│   │   │   ├── __init__.py
│   │   │   ├── theory_tools.py       # 이론 설명 생성
│   │   │   ├── quiz_tools.py         # 퀴즈 생성 도구
│   │   │   └── feedback_tools.py     # 피드백 생성 도구
│   │   ├── external/                 # 외부 연동 도구
│   │   │   ├── __init__.py
│   │   │   ├── chatgpt_tools.py      # ChatGPT API 연동
│   │   │   ├── vector_search_tools.py # ChromaDB 벡터 검색
│   │   │   └── web_search_tools.py   # 웹 검색 도구
│   │   ├── analysis/                 # 분석/평가 도구
│   │   │   ├── __init__.py
│   │   │   ├── evaluation_tools.py   # 답변 평가 도구
│   │   │   ├── intent_analysis_tools.py # 의도 분석 도구
│   │   │   └── context_tools.py      # 맥락 통합 도구
│   │   └── session/                  # 세션 관리 도구
│   │       ├── __init__.py
│   │       ├── session_init_tools.py # 세션 초기화 도구
│   │       └── session_completion_tools.py # 세션 완료 분석 도구
│   ├── utils/                        # 유틸리티 함수
│   │   ├── __init__.py
│   │   ├── database/                 # ✅ 데이터베이스 유틸리티 (완성됨)
│   │   │   ├── __init__.py
│   │   │   ├── connection.py         # ✅ 구현됨: DB 연결 관리
│   │   │   ├── query_builder.py      # ✅ 구현됨: 쿼리 빌더
│   │   │   └── transaction.py        # ✅ 구현됨: 트랜잭션 관리
│   │   ├── auth/                     # ✅ 인증 유틸리티 (완성됨)
│   │   │   ├── __init__.py
│   │   │   ├── jwt_handler.py        # ✅ 구현됨: JWT 토큰 생성/검증/데코레이터
│   │   │   └── password_handler.py   # ✅ 구현됨: bcrypt 비밀번호 해시화/검증
│   │   ├── validation/               # 검증 유틸리티
│   │   │   ├── __init__.py
│   │   │   ├── input_validators.py   # 입력 검증
│   │   │   └── business_validators.py # 비즈니스 룰 검증
│   │   ├── response/                 # ✅ 응답 처리 유틸리티 (완성됨)
│   │   │   ├── __init__.py
│   │   │   ├── formatter.py          # ✅ 구현됨: 표준화된 응답 포맷터
│   │   │   └── error_formatter.py    # ✅ 구현됨: 에러 응답 전용 포맷터
│   │   └── common/                   # ✅ 공통 유틸리티 (완성됨)
│   │       ├── __init__.py
│   │       ├── exceptions.py         # ✅ 구현됨: 계층적 커스텀 예외 클래스
│   │       ├── constants.py          # 상수 정의
│   │       └── helpers.py            # 헬퍼 함수들
│   ├── core/                         # 핵심 시스템 구성 요소 (미구현)
│   │   ├── __init__.py
│   │   ├── langraph/                 # LangGraph 관련
│   │   │   ├── __init__.py
│   │   │   ├── workflow.py           # 워크플로우 정의
│   │   │   ├── state_manager.py      # State 관리 시스템
│   │   │   └── graph_builder.py      # 그래프 빌더
│   │   ├── database/                 # 데이터베이스 관련
│   │   │   ├── __init__.py
│   │   │   ├── mysql_client.py       # MySQL 클라이언트
│   │   │   └── migration_runner.py   # 마이그레이션 실행기
│   │   ├── external/                 # 외부 서비스 연동
│   │   │   ├── __init__.py
│   │   │   ├── vector_db.py          # ChromaDB 연동
│   │   │   └── chatgpt_client.py     # ChatGPT API 클라이언트
│   │   └── cache/                    # 캐시 관련
│   │       ├── __init__.py
│   │       └── redis_client.py       # Redis 클라이언트 (선택사항)
│   └── middleware/                   # ✅ 미들웨어 (부분 구현)
│       ├── __init__.py               # ✅ 구현됨: 미들웨어 초기화 함수
│       ├── auth/                     # ✅ 인증 미들웨어 (완성됨)
│       │   ├── __init__.py
│       │   ├── jwt_middleware.py     # ✅ 구현됨: JWT 검증 및 g 객체 설정
│       │   └── session_middleware.py # 세션 관리 미들웨어
│       ├── request/                  # 요청 처리 미들웨어
│       │   ├── __init__.py
│       │   ├── cors_middleware.py    # CORS 처리
│       │   ├── rate_limit_middleware.py # 속도 제한
│       │   └── request_validator.py  # 요청 검증
│       └── error/                    # 에러 처리 미들웨어
│           ├── __init__.py
│           ├── error_handler.py      # 전역 에러 핸들러
│           └── exception_mapper.py   # 예외 매핑
├── tests/                            # 테스트 코드
│   ├── __init__.py
│   ├── test_auth.py                  # 인증 테스트
│   ├── test_agents.py                # 에이전트 테스트
│   ├── test_services.py              # 서비스 테스트
│   ├── test_diagnosis.py             # ✅ 신규: 진단 시스템 테스트
│   └── test_tools.py                 # 도구 테스트
├── migrations/                       # 데이터베이스 마이그레이션
│   ├── 001_initial_schema.sql        # 초기 스키마
│   ├── 002_add_indexes.sql           # 인덱스 추가
│   └── 003_user_progress.sql         # 사용자 진행 상태
├── data/                            # 정적 데이터
│   ├── diagnosis_questions.json      # ✅ 구현됨: 진단 퀴즈 문항 (option value 수정)
│   ├── chapter_contents.json         # 챕터 내용
│   └── quiz_templates.json           # 퀴즈 템플릿
├── logs/                            # 로그 파일
│   ├── app.log                      # 애플리케이션 로그
│   ├── error.log                    # 에러 로그
│   └── access.log                   # 액세스 로그
├── scripts/                         # 스크립트
│   ├── init_db.py                   # DB 초기화 스크립트
│   ├── seed_data.py                 # 시드 데이터 생성
│   └── backup_db.py                 # DB 백업 스크립트
├── requirements.txt                  # Python 패키지 의존성
├── .env.example                     # 환경변수 예시 파일
├── .env                            # 환경변수 파일 (gitignore)
├── .gitignore                      # Git 무시 파일
├── Dockerfile                      # Docker 컨테이너 설정
├── docker-compose.yml              # Docker Compose 설정
├── README.md                       # 프로젝트 설명
└── run.py                         # Flask 애플리케이션 실행 파일
```

---


# 프론트엔드 폴더 구조 (v1.3 - 2025.08.11 업데이트)

```
ai-skill-tutor-frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
│       ├── images/
│       │   ├── logo.png
│       │   └── icons/
│       └── fonts/
├── src/
│   ├── main.js                    # Vue 앱 진입점
│   ├── App.vue                    # ✅ 수정됨: 퀵 액션 영역 제거, 깔끔한 구조로 정리
│   ├── router/
│   │   ├── index.js               # ✅ 수정됨: 인증 가드 적용 및 라우트 보안 설정
│   │   └── authGuard.js           # ✅ 구현됨: 페이지별 접근 권한 제어 가드
│   ├── stores/
│   │   ├── index.js               # Pinia store 설정
│   │   ├── authStore.js           # ✅ 구현됨: 인증 상태 관리 및 자동 토큰 갱신
│   │   ├── tutorStore.js          # 학습 세션 상태 관리 (미구현)
│   │   ├── dashboardStore.js      # 대시보드 상태 관리 (미구현)
│   │   └── diagnosisStore.js      # ✅ 구현됨: 진단 관련 상태 관리 (완전 구현)
│   ├── views/
│   │   ├── common/                # 공통 페이지
│   │   │   ├── HomeView.vue           # 홈 페이지 (기본)
│   │   │   └── AboutView.vue          # 소개 페이지 (기본)
│   │   ├── auth/                  # 인증 관련 페이지
│   │   │   └── LoginPage.vue          # ✅ 구현됨: 통합 인증 페이지 (탭 기반 로그인/회원가입)
│   │   ├── diagnosis/             # 진단 관련 페이지
│   │   │   ├── DiagnosisPage.vue      # ✅ 구현됨: 사용자 진단 페이지 (완전 구현)
│   │   │   └── DiagnosisResultPage.vue # ✅ 신규: 진단 결과 및 유형 선택 페이지 (완전 구현)
│   │   ├── dashboard/             # 대시보드 관련 페이지
│   │   │   └── DashboardPage.vue      # 대시보드 페이지 (미구현)
│   │   └── learning/              # 학습 관련 페이지
│   │       └── LearningPage.vue       # 학습 진행 페이지 (미구현)
│   ├── components/
│   │   ├── common/
│   │   │   ├── HeaderComponent.vue   # ✅ 구현됨: 로그인 상태별 헤더 (로그인/로그아웃 버튼)
│   │   │   ├── LoadingModal.vue      # 로딩 모달 (미구현)
│   │   │   └── AlertMessage.vue      # 알림 메시지 (미구현)
│   │   ├── auth/                  # ✅ 인증 관련 컴포넌트 (완성됨)
│   │   │   ├── LoginForm.vue         # ✅ 구현됨: 실시간 검증 로그인 폼
│   │   │   └── RegisterForm.vue      # ✅ 구현됨: 중복 확인 및 검증 회원가입 폼
│   │   ├── diagnosis/             # ✅ 진단 관련 컴포넌트 (완전 구현)
│   │   │   ├── DiagnosisQuestion.vue  # ✅ 구현됨: 문항 표시 및 답변 수집
│   │   │   └── ProgressBar.vue        # ✅ 구현됨: 진행률 표시
│   │   ├── dashboard/             # 대시보드 관련 컴포넌트 (미구현)
│   │   │   ├── LearningStats.vue
│   │   │   ├── ChapterList.vue
│   │   │   └── ChapterCard.vue
│   │   └── learning/              # 학습 관련 컴포넌트 (미구현)
│   │       ├── SessionProgressIndicator.vue
│   │       ├── MainContentArea.vue
│   │       ├── content/
│   │       │   ├── TheoryContent.vue
│   │       │   ├── QuizContent.vue
│   │       │   ├── FeedbackContent.vue
│   │       │   └── SessionCompleteContent.vue
│   │       └── chat/
│   │           ├── ChatArea.vue
│   │           ├── ChatHistory.vue
│   │           ├── ChatInput.vue
│   │           └── QuizAnswerInput.vue
│   ├── composables/
│   │   ├── useAuth.js             # 인증 관련 컴포저블 (미구현)
│   │   ├── useApi.js              # API 호출 컴포저블 (미구현)
│   │   ├── useLearning.js         # 학습 세션 컴포저블 (미구현)
│   │   └── useNotification.js     # 알림 컴포저블 (미구현)
│   ├── services/
│   │   ├── api.js                 # ✅ 구현됨: HTTP 클라이언트 + 자동 토큰 갱신 인터셉터
│   │   ├── authService.js         # ✅ 구현됨: 인증 관련 API (로그인/회원가입/중복확인)
│   │   ├── learningService.js     # 학습 관련 API (미구현)
│   │   ├── dashboardService.js    # 대시보드 관련 API (미구현)
│   │   └── diagnosisService.js    # ✅ 구현됨: 진단 관련 API (완전 구현)
│   ├── utils/
│   │   ├── constants.js           # 상수 정의
│   │   ├── helpers.js             # 유틸리티 함수
│   │   ├── validators.js          # 입력값 검증 함수
│   │   ├── formatters.js          # 데이터 포맷팅 함수
│   │   ├── tokenManager.js        # ✅ 구현됨: Access Token 관리 유틸리티
│   │   └── cookieUtils.js         # ✅ 구현됨: 쿠키 관리 유틸리티
│   ├── styles/
│   │   ├── main.scss              # 메인 스타일시트
│   │   ├── variables.scss         # SCSS 변수
│   │   ├── mixins.scss            # SCSS 믹스인
│   │   ├── components/
│   │   │   ├── _buttons.scss
│   │   │   ├── _forms.scss
│   │   │   ├── _cards.scss
│   │   │   └── _modals.scss
│   │   └── pages/
│   │       ├── _login.scss
│   │       ├── _dashboard.scss
│   │       ├── _learning.scss
│   │       ├── _diagnosis.scss    # ✅ 신규: 진단 페이지 스타일
│   │       └── _diagnosis-result.scss # ✅ 신규: 진단 결과 페이지 스타일
│   └── assets/
│       ├── images/
│       └── icons/
├── .env                           # 환경 변수 (개발용)
├── .env.production                # 환경 변수 (운영용)
├── .gitignore
├── package.json                   # ✅ 수정됨: 새로운 의존성 추가 가능성
├── vite.config.js                 # Vite 설정
├── index.html                     # ✅ 수정됨: FontAwesome CDN 추가
└── README.md
```

