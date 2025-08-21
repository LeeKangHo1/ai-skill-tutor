# 백엔드 폴더 구조 (v2.0 - 2025.08.18 업데이트)

```
backend/
├── app/                              # Flask 애플리케이션 메인 디렉토리
│   ├── __init__.py                   # Flask 앱 팩토리 함수 (Blueprint 등록 방식 개선)
│   ├── agents/                       # LangGraph 에이전트 시스템
│   │   ├── __init__.py               # 
│   │   ├── evaluation_feedback/      # 평가 피드백 에이전트
│   │   │   ├── __init__.py           # 
│   │   │   └── evaluation_feedback_agent.py # ✅ 구현됨: EvaluationFeedbackAgent
│   │   ├── learning_supervisor/      # 학습 감독 에이전트
│   │   │   ├── __init__.py           # 
│   │   │   ├── learning_supervisor_agent.py # ✅ 구현됨: LearningSupervisor 에이전트
│   │   │   ├── response_generator.py # ✅ 구현됨: 최종 응답 생성기
│   │   │   └── supervisor_router.py  # ✅ 구현됨: LangGraph conditional_edges용 라우터 함수
│   │   ├── qna_resolver/             # 미구현: 질문 답변 에이전트
│   │   │   ├── __init__.py           # 
│   │   │   ├── answer_generator.py   # 답변 생성기
│   │   │   ├── qna_resolver_agent.py # "QnAResolver가 호출되었습니다" 메시지만 반환
│   │   │   └── query_processor.py    # 질문 처리기
│   │   ├── quiz_generator/           # 퀴즈 생성 에이전트
│   │   │   ├── __init__.py           # 
│   │   │   └── quiz_generator_agent.py # ✅ 구현됨: QuizGenerator 에이전트
│   │   ├── session_manager/          # 세션 관리 에이전트
│   │   │   ├── __init__.py           # 
│   │   │   ├── session_handlers.py   # ✅ 구현됨:세션 처리 핸들러
│   │   │   └── session_manager_agent.py # ✅ 구현됨:SessionManager 에이전트
│   │   └── theory_educator/          # 이론 교육 에이전트
│   │       ├── __init__.py           # 
│   │       └── theory_educator_agent.py # ✅ 구현됨: TheoryEducator 에이전트
│   ├── config/                       # 설정 파일들
│   │   ├── __init__.py
│   │   ├── base.py                   # ✅ 구현됨:기본 설정
│   │   ├── db_config.py              # ✅ 구현됨:데이터베이스 설정 전용
│   │   ├── development.py            # 개발 환경 설정
│   │   ├── production.py             # 운영 환경 설정
│   │   └── testing.py                # 테스트 환경 설정
│   ├── core/                         # 핵심 시스템 구성 요소 (부분 구현)
│   │   ├── __init__.py
│   │   ├── database/                 # ✅ 데이터베이스 관련 (구현됨)
│   │   │   ├── __init__.py
│   │   │   ├── migration_runner.py   # ✅ 구현됨: 마이그레이션 실행기
│   │   │   └── mysql_client.py       # ✅ 구현됨: MySQL 클라이언트
│   │   ├── external/                 # 외부 서비스 연동 (미구현)
│   │   │   ├── __init__.py
│   │   │   └── vector_db.py          # ChromaDB 연동
│   │   └── langraph/                 # ✅ 구현됨: LangGraph 관련 (v2.0 대규모 리팩토링)
│   │       ├── __init__.py
│   │       ├── state/                # ✅ 신규: State 정의 및 기본 관리
│   │       │   ├── __init__.py       # 모든 State 관련 export
│   │       │   ├── state_definition.py # ✅ 구현됨: TutorState TypedDict 정의
│   │       │   ├── state_factory.py  # ✅ 구현됨: State 생성 및 초기화
│   │       │   └── state_validator.py # ✅ 구현됨: State 유효성 검증
│   │       ├── managers/             # ✅ 신규: 도메인별 State 관리자
│   │       │   ├── __init__.py       # 모든 관리자 export
│   │       │   ├── agent_manager.py  # ✅ 구현됨: 에이전트 전환 관리
│   │       │   ├── conversation_manager.py # ✅ 구현됨: 대화 관리
│   │       │   ├── quiz_manager.py   # ✅ 구현됨: 퀴즈 관련 State 관리
│   │       │   └── session_manager.py # ✅ 구현됨: 세션 진행 State 관리
│   │       ├── graph_builder.py      # ✅ 구현됨그래프 빌더
│   │       ├── state_manager.py      # ✅ 구현됨: 통합 래퍼 클래스 (호환성)
│   │       └── workflow.py           # ✅ 구현됨워크플로우 정의
│   ├── models/                       # 데이터베이스 모델
│   │   ├── __init__.py
│   │   ├── chapter/                  # 챕터 관련 모델들
│   │   │   ├── __init__.py
│   │   │   └── chapter.py            # 챕터 모델
│   │   ├── learning/                 # 학습 관련 모델들
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py       # 대화 기록 모델
│   │   │   ├── quiz.py               # 퀴즈 관련 모델
│   │   │   └── session.py            # 학습 세션 모델
│   │   └── user/                     # 사용자 관련 모델들
│   │       ├── __init__.py
│   │       ├── auth_token.py         # 인증 토큰 모델
│   │       ├── user.py               # 기본 사용자 모델
│   │       └── user_progress.py      # 사용자 진행 상태 모델
│   ├── routes/                       # API 라우트 (Blueprint)
│   │   ├── __init__.py               # ✅ 수정됨: system_blueprints, diagnosis_blueprints import
│   │   ├── auth/                     # ✅ 인증 관련 라우트 (완성됨)
│   │   │   ├── __init__.py           # auth_blueprints 정의
│   │   │   ├── login.py              # ✅ 구현됨: 로그인/로그아웃/사용자정보 API
│   │   │   ├── register.py           # ✅ 구현됨: 회원가입/중복확인 API
│   │   │   └── token.py              # ✅ 구현됨: 토큰 갱신/검증/세션관리 API
│   │   ├── dashboard/                # 대시보드 라우트 (미구현)
│   │   │   ├── __init__.py
│   │   │   ├── overview.py           # 대시보드 개요
│   │   │   └── statistics.py         # 통계 정보
│   │   ├── diagnosis/                # 진단 관련 라우트 (완성됨)
│   │   │   ├── __init__.py           # diagnosis_blueprints 정의
│   │   │   ├── questions.py          # ✅ 구현됨: 진단 문항 조회 API
│   │   │   └── submit.py             # ✅ 구현됨: 진단 결과 제출 + 유형 선택 API
│   │   ├── learning/                 # 학습 세션 라우트 (미구현)
│   │   │   ├── __init__.py
│   │   │   ├── history/              # 학습 기록
│   │   │   │   ├── __init__.py
│   │   │   │   ├── details.py        # 상세 조회
│   │   │   │   └── list.py           # 기록 목록
│   │   │   ├── quiz/                 # 퀴즈 관리
│   │   │   │   ├── __init__.py
│   │   │   │   ├── hint.py           # 힌트 요청
│   │   │   │   └── submit.py         # 답변 제출
│   │   │   └── session/              # 세션 관리
│   │   │       ├── __init__.py
│   │   │       ├── complete.py       # ✅ 구현됨: 세션 정리
│   │   │       ├── message.py        # ✅ 구현됨: 메시지 처리
│   │   │       └── start.py          # ✅ 구현됨: 세션 시작
│   │   └── system/                   # 시스템 관련 라우트 (완성됨)
│   │       ├── __init__.py           # ✅ 수정됨: system_blueprints 정의
│   │       ├── health.py             # ✅ 구현됨: 헬스체크 API
│   │       └── version.py            # ✅ 구현됨: 기본 API 정보 + /version 엔드포인트
│   ├── services/                     # 비즈니스 로직 서비스
│   │   ├── __init__.py
│   │   ├── auth/                     # ✅ 인증 서비스 (완성됨)
│   │   │   ├── __init__.py
│   │   │   ├── login_service.py      # ✅ 구현됨: 로그인 처리 및 토큰 발급
│   │   │   ├── register_service.py   # ✅ 구현됨: 회원가입 처리 및 검증
│   │   │   └── token_service.py      # ✅ 구현됨: 토큰 갱신/검증/세션관리
│   │   ├── diagnosis_service.py      # ✅ 구현됨: 진단 점수 계산 및 유형 추천
│   │   ├── learning/                 # 학습 진행 서비스 (미구현)
│   │   │   ├── __init__.py
│   │   │   ├── content_service.py    # 컨텐츠 처리 서비스
│   │   │   ├── quiz_service.py       # 퀴즈 처리 서비스
│   │   │   └── session_service.py    # ✅ 구현됨: 세션 관리 서비스
│   │   ├── dashboard/               # 대쉬보드
│   │   │   ├── __init__.py
│   │   │   └── dashboard_service.py  # 대시보드 통계 서비스
│   ├── tools/                        # LangGraph 도구 함수들 (부분 구현)
│   │   ├── __init__.py
│   │   ├── analysis/                 # 분석/평가 도구
│   │   │   ├── __init__.py
│   │   │   ├── context_tools.py      # 맥락 통합 도구
│   │   │   ├── evaluation_tools.py   # ✅ 구현됨: 로컬 채점
│   │   │   └── intent_analysis_tools.py # ✅ 구현됨: 의도 분석 도구
│   │   ├── content/                  # 컨텐츠 생성 도구
│   │   │   ├── __init__.py
│   │   │   ├── feedback_tools_chatgpt.py   ✅ 구현됨: ChatGPT 기반 피드백 생성 도구
│   │   │   ├── quiz_tools_chatgpt.py   # ✅ 구현됨: ChatGPT 기반 퀴즈 생성 도구
│   │   │   └── theory_tools_chatgpt.py # ✅ 구현됨: ChatGPT 기반 이론 설명 생성
│   │   ├── external/                 # 외부 연동 도구
│   │   │   ├── __init__.py
│   │   │   ├── chatgpt_tools.py      # ChatGPT API 연동
│   │   │   ├── vector_search_tools.py # ChromaDB 벡터 검색
│   │   │   └── web_search_tools.py   # 웹 검색 도구
│   │   └── session/                  # 세션 관리 도구
│   │       ├── __init__.py
│   │       ├── session_completion_tools.py # 세션 완료 분석 도구
│   │       └── session_init_tools.py # 세션 초기화 도구
│   └── utils/                        # 유틸리티 함수
│       ├── __init__.py
│       ├── auth/                     # ✅ 인증 유틸리티 (완성됨)
│       │   ├── __init__.py
│       │   ├── jwt_handler.py        # ✅ 구현됨: JWT 토큰 생성/검증/데코레이터
│       │   └── password_handler.py   # ✅ 구현됨: bcrypt 비밀번호 해시화/검증
│       ├── common/                   # 공통 유틸리티
│       │   ├── __init__.py
│       │   ├── chat_logger.py        # ✅ 구현됨: 사용자별 JSON 대화 로그 저장 시스템
│       │   ├── constants.py          # 상수 정의
│       │   ├── exceptions.py         # 일부 구현: 계층적 커스텀 예외 클래스
│       │   ├── graph_visualizer.py   # ✅ 구현됨: 랭그래프 실행 시 그래프 그림 저장
│       │   └── helpers.py            # 헬퍼 함수들
│       ├── database/                 # ✅ 데이터베이스 유틸리티 (완성됨)
│       │   ├── __init__.py
│       │   ├── connection.py         # ✅ 구현됨: DB 연결 관리
│       │   ├── query_builder.py      # ✅ 구현됨: 쿼리 빌더
│       │   └── transaction.py        # ✅ 구현됨: 트랜잭션 관리
│       ├── logging/                  # ✅ 신규: 로깅 유틸리티
│       │   └── __init__.py
│       ├── response/                 # ✅ 응답 처리 유틸리티 (완성됨)
│       │   ├── __init__.py
│       │   ├── error_formatter.py    # ✅ 구현됨: 에러 응답 전용 포맷터
│       │   └── formatter.py          # ✅ 구현됨: 표준화된 응답 포맷터
│       └── validation/               # 검증 유틸리티
│           ├── __init__.py
│           ├── business_validators.py # 비즈니스 룰 검증
│           └── input_validators.py   # 입력 검증
├── data/                            # 정적 데이터
│   ├── chapters/                     # ✅ 신규: 챕터별 데이터 (chapter_01.json ~ chapter_08.json)
│   ├── chat_log/                     # ✅ 신규: 사용자별 대화 로그 저장
│   │   └── user999/                  # 사용자별 폴더 구조
│   ├── contents_beginner.md          # ✅ 신규: 초급자용 컨텐츠
│   ├── diagnosis_questions.json      # ✅ 구현됨: 진단 퀴즈 문항 (option value 수정)
│   └── tutor_workflow_graph.png      # ✅ 신규: LangGraph 워크플로우 시각화
├── logs/                            # 로그 파일
│   ├── access.log                   # 액세스 로그
│   ├── app.log                      # 애플리케이션 로그
│   └── error.log                    # 에러 로그
├── migrations/                       # 데이터베이스 마이그레이션
│   ├── create_schema.py              # ✅ 신규: 스키마 생성 스크립트
│   ├── schema.sql                    # ✅ 신규: SQL 스키마 파일
│   └── verify_schema.py              # ✅ 신규: 스키마 검증 스크립트
├── scripts/                         # 스크립트
│   ├── .gitkeep                     # 빈 폴더 유지용 파일
│   ├── clear_all_data.py            # ✅ 신규: 모든 데이터 초기화 스크립트
│   └── validate_schema.py           # ✅ 신규: 스키마 유효성 검증 스크립트
├── tests/                            # 테스트 코드 (날짜별 폴더 구조)
│   └── 0818/                         # ✅ 2025-08-18 테스트 (LangGraph 인터랙티브)
├── .env                            # 환경변수 파일 (gitignore)
├── .env.example                     # 환경변수 예시 파일
├── .gitignore                      # Git 무시 파일
├── README.md                       # 프로젝트 설명
├── requirements.txt                  # Python 패키지 의존성
└── run.py                         # Flask 애플리케이션 실행 파일
```

---


# 프론트엔드 폴더 구조 (v2.0 - 2025.08.21 업데이트)

```
frontend/
├── src/
│   ├── __tests__/                 # 테스트 파일
│   │   └── basic.test.js          # 기본 테스트
│   ├── App.vue                    # Vue 앱 루트 컴포넌트
│   ├── assets/
│   │   ├── icons/                 # 아이콘 파일들
│   │   └── images/                # 이미지 파일들
│   ├── components/
│   │   ├── auth/                  # 인증 관련 컴포넌트
│   │   ├── common/                # 공통 컴포넌트
│   │   ├── dashboard/             # 대시보드 관련 컴포넌트
│   │   ├── diagnosis/             # 진단 관련 컴포넌트
│   │   └── learning/              # 학습 관련 컴포넌트
│   ├── main.js                    # Vue 앱 진입점
│   ├── router/
│   │   ├── authGuard.js           # 인증 가드
│   │   └── index.js               # 라우터 설정
│   ├── services/
│   │   ├── api.js                 # HTTP 클라이언트
│   │   ├── authService.js         # 인증 관련 API
│   │   ├── dashboardService.js    # 대시보드 관련 API
│   │   ├── diagnosisService.js    # 진단 관련 API
│   │   ├── index.js               # 서비스 통합 export
│   │   └── learningService.js     # 학습 관련 API
│   ├── stores/
│   │   ├── authStore.js           # 인증 상태 관리
│   │   ├── dashboardStore.js      # 대시보드 상태 관리
│   │   ├── diagnosisStore.js      # 진단 상태 관리
│   │   ├── index.js               # Pinia store 설정
│   │   └── tutorStore.js          # 학습 세션 상태 관리
│   ├── styles/
│   │   ├── components/            # 컴포넌트별 스타일
│   │   ├── pages/                 # 페이지별 스타일
│   │   ├── main.scss              # 메인 스타일시트
│   │   └── variables.scss         # SCSS 변수
│   ├── test-setup.js              # 테스트 설정 파일
│   ├── utils/
│   │   ├── constants.js           # 상수 정의
│   │   ├── cookieUtils.js         # 쿠키 관리 유틸리티
│   │   ├── formatting.js          # 데이터 포맷팅 함수
│   │   ├── helpers.js             # 유틸리티 함수
│   │   ├── tokenManager.js        # Access Token 관리 유틸리티
│   │   └── validation.js          # 입력값 검증 함수
│   └── views/
│       ├── __tests__/             # 뷰 테스트 파일
│       ├── auth/                  # 인증 관련 페이지
│       ├── common/                # 공통 페이지
│       ├── dashboard/             # 대시보드 관련 페이지
│       ├── diagnosis/             # 진단 관련 페이지
│       └── learning/              # 학습 관련 페이지
├── .env                           # 환경 변수
├── .gitignore                     # Git 무시 파일
├── index.html                     # HTML 템플릿
├── package-lock.json              # NPM 패키지 잠금 파일
├── package.json                   # NPM 패키지 설정
├── README.md                      # 프로젝트 설명
└── vite.config.js                 # Vite 설정
```

