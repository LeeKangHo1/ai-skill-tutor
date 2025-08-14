# 구현 로그 (Implementation Log)

## 📦 사용 패키지 버전 (2025-08-13 기준)
- langchain==0.3.27
- langchain-core==0.3.72
- langgraph==0.6.3
- langsmith==0.4.13

## 📋 향후 개발 지침
**앞으로 모든 에이전트와 툴 작성 시 표준 패턴 적용:**
- **PromptTemplate**: 입력 변수 명확히 정의
- **LCEL 파이프라인**: `PromptTemplate | ChatOpenAI | OutputParser` 구조 
- **OutputParser**: JSON 출력은 `JsonOutputParser` + Pydantic 스키마, 텍스트는 `StrOutputParser`
- import는 "from langchain_core.prompts import PromptTemplate" , "from langchain_core.output_parsers import JsonOutputParser"
- db를 다루는 경우 backend/app/utils/database/connection.py, query_builder.py, transaction.py 파일의 유틸리티를 활용할 것

## 📅 2025년 8월 14일 - LangGraph 워크플로우 시스템 완성

### 🎯 주요 완성 사항
- **LangGraph 멀티에이전트 워크플로우**: 5개 핵심 에이전트 기반 완전한 학습 시스템 구축
- **StateManager 시스템**: TutorState 기반 중앙화된 상태 관리 및 검증 시스템 완성
- **워크플로우 통합**: 모든 에이전트가 LearningSupervisor를 거치는 일관된 구조 확립
- **비동기/동기 실행 시스템**: Flask API 통합을 위한 동기 래퍼 및 성능 모니터링 완성

### 🔧 핵심 구현 내용
- **Graph Builder**: agent_nodes 딕셔너리 기반 자동 노드 등록, supervisor_router 조건부 라우팅
- **Supervisor Router**: quiz_answer → evaluation_feedback 직접 연결, 의도 분석 우회 로직
- **Response Generator**: 에이전트 대본을 사용자 친화적 응답으로 정제하는 전담 시스템
- **워크플로우 최적화**: 퀴즈 답변 처리를 별도 API에서 동일 워크플로우로 통합

### 🛠️ 해결한 기술 이슈
- **아키텍처 일관성**: 초기 복잡한 다중 경로 구조 → 통일된 LearningSupervisor 중심 구조
- **책임 분리**: 각 에이전트는 순수 대본(draft)만 생성, 사용자 대면은 LearningSupervisor 전담
- **힌트 시스템**: 별도 워크플로우 → 퀴즈 생성 시점 동시 처리로 최적화
- **비동기 처리**: LangGraph 비동기 특성 + Flask 동기 환경 호환성 확보

### ✅ 완성된 워크플로우 구조
```
SessionManager → LearningSupervisor → [TheoryEducator|QuizGenerator|EvaluationFeedbackAgent] → LearningSupervisor → END
```

### 🔄 에이전트별 구현 상태
- **✅ SessionManager**: 세션 생명주기 관리, DB 저장 시스템 완성
- **✅ LearningSupervisor**: 워크플로우 시작점/끝점, 라우팅 및 응답 생성 완성
- **✅ TheoryEducator**: 이론 설명 대본 생성 시스템 완성
- **✅ QuizGenerator**: 퀴즈 및 힌트 동시 생성 시스템 완성
- **✅ EvaluationFeedbackAgent**: 객관식/주관식 통합 평가 및 피드백 완성
- **⚠️ QnAResolverAgent**: 임시 구현 상태 - "QnAResolver가 호출되었습니다" 메시지만 반환, 실제 질문 답변 로직 미구현

### 📊 성능 및 모니터링
- **실행 통계**: 총 실행 횟수, 성공/실패 비율, 평균 실행 시간 수집
- **오류 처리**: 네트워크 오류 재시도, 타임아웃 방지, State 복구 시스템
- **Runtime Config**: recursion_limit, timeout, thread_id 기반 세션 관리

### 🎯 다음 단계 준비 완료
- **API 통합 준비**: REST API 엔드포인트 구현을 위한 TutorState ↔ JSON 변환 시스템 준비
- **프론트엔드 연동**: Vue.js 컴포넌트와 실시간 UI 업데이트 시스템 연결 준비
- **테스트 가능**: `execute_tutor_workflow_sync(state)` 함수로 전체 워크플로우 테스트 가능

### 📁 주요 구현 파일
- **`state_manager.py`**: TutorState 생명주기 관리 시스템
- **`workflow.py`**: 비동기/동기 실행 및 성능 모니터링
- **`graph_builder.py`**: LangGraph 워크플로우 구성 및 노드 등록
- **`supervisor_router.py`**: 조건부 라우팅 및 의도 분석 로직
- **`response_generator.py`**: 에이전트 대본 → 사용자 응답 변환 시스템

## 📅 2025년 8월 14일 - SessionManager 구현 완성

### 🎯 주요 완성 사항
 - **SessionManager**: 세션 생명주기 관리 에이전트 완성 및 실제 DB 연동 검증
 - **SessionHandlers**: DB 저장 로직 완전 구현, 예외 처리 강화, 실제 DB 테스트 100% 성공
 - **진행 상태 관리**: session_sequence에 섹션 번호 저장, 챕터/섹션 자동 진행 로직 완성

### 🔧 핵심 구현 내용
 - **진행 로직**: `backend/data/chapters/chapter_01.json` 파일에서 섹션 수 확인, proceed/retry에 따른 챕터/섹션 자동 진행
 - **DB 저장**: learning_sessions, session_conversations, session_quizzes, user_progress, user_statistics 테이블 트랜잭션 기반 저장
 - **책임 분리**: EvaluationFeedbackAgent에서 세션 카운트 업데이트 제거, SessionManager에서 일괄 관리

#### SessionHandlers 주요 개선사항
- **예외 처리 강화**: DatabaseQueryError, DatabaseIntegrityError 적절한 catch 및 처리
- **트랜잭션 안정성**: 배치 INSERT 시 트랜잭션 기반 롤백 처리
- **사용자 통계 자동 계산**: 평균 정확도 재계산, 세션 카운트 자동 업데이트
- **데이터 무결성**: 외래키 제약 조건 순서 고려한 저장 로직
- **타임스탬프 처리**: 다양한 형태의 타임스탬프 통일 처리

#### SessionManager 주요 개선사항
- **세션 ID 생성**: `user{user_id}_ch{chapter}_s{section}_{timestamp}` 형식으로 단순화
- **session_sequence 활용**: 기존 세션 카운트 대신 섹션 번호 저장
- **세션 데이터 준비**: 학습 시간 계산, 세션 결정 결과 포함
- **진행 상태 업데이트**: proceed/retry에 따른 챕터/섹션 자동 진행

### 🔧 해결한 기술 이슈
- **DB 예외 처리**: insert_record의 return_id=False 시 None 반환 정상 처리
- **외래키 제약**: session 저장 후 conversations, quizzes 저장 순서 보장
- **message_type 호환**: enum('user','system','tool') 값 준수
- **트랜잭션 롤백**: 무결성 오류 시 자동 롤백 및 로그 출력

### ✅ 완성된 MAS 아키텍처
```
SessionManager → LearningSupervisor → TheoryEducator → QuizGenerator → EvaluationFeedbackAgent → SessionManager
```

### 📁 주요 구현 파일
- **`session_manager_agent.py`**: 세션 관리 메인 로직, 섹션 번호 기반 ID 생성
- **`session_handlers.py`**: DB 저장 및 통계 관리, 완전한 예외 처리 구현


## 📅 2025년 8월 14일 - LearningSupervisor 시스템 완성

### 🎯 주요 완성 사항
- **LearningSupervisor**: 새로운 워크플로우 기반 핵심 에이전트 완성
- **워크플로우 최적화**: 질문 받는 시점을 이론 완료 후, 피드백 완료 후로 제한
- **의도 분석 최적화**: 빠른 경로(완전 일치) + LLM 분석 2단계 시스템
- **QnA Resolver Agent** 임시 구현: 테스트용 "QnAResolver가 호출되었습니다" 메시지 반환, LangGraph 노드 등록 가능한 구조로 작성하여 다른 에이전트 테스트 완료 후 실제 질문 답변 로직 구현 예정

### 🔧 핵심 구현 내용
- **learning_supervisor_agent.py**: 워크플로우 시작점/끝점, 단계별 분기 처리
- **supervisor_router.py**: LangGraph conditional_edges용 라우터 함수
- **response_generator.py**: 에이전트 대본을 사용자 친화적 응답으로 정제
- **intent_analysis_tools.py**: 완전 일치 키워드(30-40%) + LLM 분석(60-70%)
- **chat_logger.py**: 사용자별 JSON 대화 로그 저장 시스템

### 🛠️ 해결한 기술 이슈
- **워크플로우 단순화**: session_start → 의도 분석 없이 바로 이론 설명
- **중복 제거**: EvaluationFeedbackAgent와 ResponseGenerator 역할 분담
- **성능 최적화**: "다음", "네" 등 명확한 키워드는 LLM 호출 없이 즉시 처리
- **오판 방지**: 포함 검색 → 완전 일치 방식으로 변경

### 🎯 새로운 워크플로우
```
session_start → theory_educator (자동)
theory_completed → question? qna_resolver : quiz_generator  
quiz_and_feedback_completed → question? qna_resolver : session_manager
```

## 📅 2025년 8월 13일 - EvaluationFeedbackAgent 완성 및 평가 시스템 구축

### 🎯 주요 완성 사항
- **EvaluationFeedbackAgent**: 객관식/주관식 통합 평가 및 피드백 생성 에이전트 완성
- **평가 도구 시스템**: evaluation_tools.py, feedback_tools_chatgpt.py 구현
- **ChatGPT 통합**: 1회 호출로 채점+피드백 동시 처리 (비용 최적화)

### 🔧 핵심 구현 내용
- **객관식 평가**: 로컬 채점 + ChatGPT 피드백 생성
- **주관식 평가**: ChatGPT 1회 호출로 0-100점 채점 + 상세 피드백
- **세션 관리**: 최대 1회 재학습 제한, 60점 기준 proceed/retry 판단
- **사용자 맞춤**: beginner(친근함)/advanced(효율성) 톤 차별화

### 🛠️ 해결한 기술 이슈
- **LangChain JSON 이스케이프**: PromptTemplate에서 `{}`를 `{{}}`로 처리
- **State 구조 최적화**: 복잡한 evaluation_detail 딕셔너리 → 필요한 값만 반환
- **코드 간소화**: 함수별 단일 책임 원칙 적용, 불필요한 중간 데이터 제거

### 🧪 테스트 시스템 구축
- **객관식 테스트**: 챕터 1 섹션 2 기준 정답/오답 케이스
- **주관식 테스트**: 챕터 5 섹션 1,2 기준 다양한 품질 답변 평가
- **사용자 유형별**: beginner vs advanced 피드백 차이 검증

### 📊 완성된 아키텍처
```
QuizGenerator → EvaluationFeedbackAgent → LearningSupervisor
                ↓
        evaluation_tools.py (로컬 채점)
        feedback_tools_chatgpt.py (ChatGPT 피드백)
```

## 📅 2025년 8월 13일 - 퀴즈 생성 시스템 LangChain LCEL 파이프라인 전환

### 🎯 주요 작업
- **퀴즈 생성 에이전트 간소화**: 불필요한 기능 제거, 핵심 로직만 유지
- **LangChain LCEL 파이프라인 도입**: `quiz_tools_chatgpt.py`와 `theory_tools_chatgpt.py`를 LCEL 패턴으로 전환
- **JSON 출력 구조 최적화**: 기존 데이터 템플릿 구조 그대로 활용하여 프론트엔드 호환성 보장

### 🛠️ 주요 수정 파일
- **quiz_generator_agent.py**: 불필요한 기능 제거, 특정 섹션 로드 로직 구현
- **theory_educator_agent.py**: 불필요한 기능 제거, 특정 섹션 로드 로직 구현
- **quiz_tools_chatgpt.py**: `PromptTemplate | ChatOpenAI | JsonOutputParser` LCEL 파이프라인 전환, Pydantic 스키마 도입
- **theory_tools_chatgpt.py**: `PromptTemplate | ChatOpenAI | StrOutputParser` LCEL 파이프라인 전환

### 🗑️ 삭제된 파일
- **ai_client_manager.py**: LangChain 직접 사용으로 인한 중간 관리자 레이어 불필요
- **gemini_client.py**: LangChain ChatGoogleGenerativeAI로 대체
- **chatgpt_client.py**: LangChain ChatOpenAI로 대체  
- **langsmith_client.py**: LangChain 자동 추적으로 수동 추적 불필요

### 🔄 기술적 개선사항
- **LangChain 네이티브 활용**: ChatOpenAI 모델 직접 사용, 자동 LangSmith 추적
- **출력 파서 최적화**: 퀴즈는 JsonOutputParser + Pydantic, 이론은 StrOutputParser + 자연어
- **프롬프트 템플릿 체계화**: 사용자 유형별 분기 처리, 재학습 모드 지원

### ✅ 달성 효과
- **코드 간소화**: 복잡한 AI Client Manager 의존성 제거
- **유지보수성 향상**: LCEL 파이프라인으로 가독성 개선
- **프론트엔드 호환성**: 기존 JSON 구조 유지

## 📅 2025년 8월 12일 - LangChain 모델 전환 및 LangSmith 자동 추적 통합

### 🎯 주요 문제 해결
- **LangSmith pending 상태 문제**: 모든 run이 pending으로 남아있던 문제 해결
- **중복 추적 제거**: 수동 LangSmith 추적과 LangChain 자동 추적 간 충돌 해결
- **코드 간소화**: 복잡한 수동 추적 로직을 LangChain 자동 추적으로 대체

### LangChain 모델 전환
- **Gemini 클라이언트**: `google.generativeai` → `ChatGoogleGenerativeAI` 전환
- **OpenAI 클라이언트**: 직접 API 호출 → `ChatOpenAI` + `OpenAIEmbeddings` 전환
- **자동 추적**: 모든 LLM 호출이 LangChain을 통해 자동으로 LangSmith에 추적됨

### 🛠️ 주요 수정 파일
- **theory_tools.py / quiz_tools.py**: 중복 LangSmith 추적 코드 제거, AI Client Manager만 호출
- **gemini_client.py / openai_client.py**: LangChain 모델로 전환, JsonOutputParser 통합
- **ai_client_manager.py**: 수동 추적 로직 제거, 클라이언트 직접 호출로 간소화
- **langsmith_client.py**: 환경변수 관리만 담당, 수동 추적 관련 메서드 제거

### 🔄 State 구조 개선
- **섹션 번호 추가**: State에 `section_number` 필드 추가하여 챕터 내 세부 구간 관리
- **퀴즈 유형 명시**: `quiz_type` 필드로 객관식/주관식 문제 유형 구분 강화

### 💡 힌트 시스템 최적화  
- **힌트 생성 방식 변경**: 퀴즈 생성과 동시에 힌트를 1번만 생성하여 사용

### 🔄 개발 전략 수정
 - BaseAgent 사용 중단: 개별 에이전트 직접 구현 후 공통 패턴 파악하여 리팩터링 시점에 BaseAgent 도입 예정

## 2025.08.11 - 로그인 상태 유지 및 사용자 정보 표시 개선

### 🎯 개선된 동작 방식

- **로그인 상태 유지 체크 시**: 30일 만료 쿠키 + DB 토큰, 브라우저 재시작해도 로그인 유지
- **일반 로그인 시**: 세션 쿠키 + 12시간 DB 토큰, 브라우저 종료 시 로그아웃
- **새로고침 시 사용자 정보**: localStorage에서 즉시 복원, 백그라운드에서 서버 최신 정보 동기화
- **로딩 상태 처리**: 초기화 완료 전까지 '로딩 중...' 표시로 사용자 경험 개선

### 🔧 추가 수정사항

- **쿠키 정책 수정**: 일반 로그인 시 세션 쿠키 사용으로 브라우저 종료 시 자동 로그아웃
- **토큰 만료 시간 조정**: 일반 로그인 시 DB 토큰 12시간으로 단축
- **refresh API 개선**: 기존 쿠키 속성 유지하여 일관성 보장

---

## 2025.08.11 - 인증 시스템 완성 및 UI 개선

### ✅ 백엔드 인증 시스템 구현 완료

- **JWT 기반 인증**: Access Token(1시간) + Refresh Token(30일) 구조
- **HttpOnly 쿠키**: Refresh Token을 HttpOnly 쿠키로 보안 강화
- **인증 서비스**: 회원가입, 로그인, 토큰 갱신, 로그아웃 완전 구현
- **보안 강화**: bcrypt 비밀번호 해시화, 단일 세션 정책, 트랜잭션 기반 데이터 무결성
- **미들웨어**: JWT 검증 미들웨어로 보호된 라우트 구현

### ✅ 프론트엔드 인증 시스템 구현 완료

- **Vue 3 + Pinia**: 인증 상태 관리 및 자동 토큰 갱신
- **라우터 가드**: 페이지별 접근 권한 제어 (인증, 진단 완료, 사용자 유형별)
- **인증 컴포넌트**: LoginForm, RegisterForm 실시간 검증 및 중복 확인
- **API 인터셉터**: 401 에러 시 자동 토큰 갱신, 쿠키 기반 인증 처리

### ✅ UI/UX 개선

- **HeaderComponent**: 로그인/로그아웃 상태별 메뉴 표시, FontAwesome 아이콘 적용
- **자동 페이지 전환**: 회원가입/로그인/로그아웃 후 홈으로 이동
- **사용자 안내**: 중복 확인 버튼 미클릭 시 안내 메시지 표시
- **CORS 해결**: `supports_credentials=True` 설정으로 쿠키 기반 인증 지원

### 🔧 기술적 해결

- **쿠키 보안 설정**: 개발/운영 환경별 `secure`, `samesite` 설정 분리
- **토큰 갱신 로직**: 중복 갱신 방지 및 실패 시 자동 로그아웃
- **HTML 구문 오류**: HeaderComponent Vue 템플릿 구문 수정
- **초기 로드 오류**: 쿠키 존재 여부 확인 후 토큰 갱신 시도

### 📁 주요 구현 파일

- **백엔드**: `routes/auth/`, `services/auth/`, `utils/auth/`, `middleware/auth/`
- **프론트엔드**: `stores/authStore.js`, `components/auth/`, `utils/cookieUtils.js`

---

## 2025.08.08 - 사용자 진단 시스템 완성

### ✅ 구현 완료

- **백엔드**: 진단 API 3개 구현 완료 (`/questions`, `/submit`, `/select-type`)
    - `questions`: `diagnosis_questions.json` 파일에서 문항 목록을 조회
    - `submit`: 사용자 답변을 받아 점수 계산 후 추천 유형 및 선택지를 반환
    - `select-type`: 사용자가 선택한 최종 유형을 DB에 업데이트
- **프론트엔드**: Vue.js 기반 진단 플로우 3단계 페이지 및 컴포넌트 구현 완료
    - `DiagnosisPage`: 문항 진행 및 답변 제출
    - `DiagnosisQuestion`: 개별 문항 UI
    - `DiagnosisResultPage`: 점수 기반 결과 확인 및 최종 유형 선택
- **상태 관리**: Pinia `diagnosisStore`를 통해 진단 상태(문항, 답변, 결과)를 전역으로 관리하고 API 연동 로직 구현

### 🔧 기술적 해결

- Blueprint 구조 개선 (충돌 해결)
- 데이터 형식 통일 (`option_1` 문자열 형식)
- 복귀 상태 추적으로 UI 동기화 문제 해결
- API 연동: 백엔드-프론트엔드 완전 연동

### 📁 폴더 구조 업데이트

- 백엔드: `routes/diagnosis/`, `services/diagnosis_service.py` 추가
- 프론트엔드: `views/DiagnosisResultPage.vue`, `stores/diagnosisStore.js` 추가

### 📝 문서 업데이트

- API 설계 v1.3: `/select-type` API 추가, 응답 형식 수정

---

## 2025.08.08 - 코어 데이터베이스 모듈 구현

### ✅ 구현 완료

- **`db_config.py`**: 환경 변수 기반 DB 설정, 커넥션 풀 및 단일 연결 통로(`get_db_connection`) 구현
- **`connection.py`**: `db_config`를 사용하여 기본적인 SQL 실행기(`fetch_one`, `fetch_all` 등) 구현
- **`query_builder.py`**: 동적 쿼리 생성을 위한 `QueryBuilder` 및 CRUD 헬퍼 함수 구현
- **`transaction.py`**: 데이터 무결성을 위한 `TransactionManager` 및 'All or Nothing' 원칙의 트랜잭션 실행 함수 구현

### 📝 문서 업데이트

- 4개 모듈의 역할을 정의하고 계층적 아키텍처 확립