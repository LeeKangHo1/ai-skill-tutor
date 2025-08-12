# 구현 로그 (Implementation Log)

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