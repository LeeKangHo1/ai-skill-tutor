# 구현 로그 (Implementation Log)

---

## 📅 2025-08-24: QnAResolver 에이전트 LangChain Agent 기반 완전 구현 ✅

### 🎯 작업 목표
- 임시 구현 상태였던 QnAResolver를 LangChain Agent 기반 완전한 RAG 시스템으로 구현
- Function Calling을 통한 지능형 벡터 검색 자동화
- AI 튜터 시스템의 모든 핵심 에이전트 구현 완료

### 🔧 주요 변경사항

#### 1. QnA용 메타데이터 시스템 구축 ✅
**파일**: `backend/data/qna_context_metadata.json`

**핵심 개선점**:
- 기존 34개 섹션 → 8개 챕터로 간소화
- 챕터별 핵심 키워드 + Common Topics 그룹화
- **토큰 효율성**: 150-200 토큰 (기존 300-400에서 절반 수준)

#### 2. qna_tools_chatgpt.py v3.0 - LangChain Agent 완전 전환 ✅
**LCEL 파이프라인 → Agent 구조 완전 전환:**
```python
# Before: LCEL (Function Calling 미완성)
qna_chain = prompt_template | model_with_tools | StrOutputParser

# After: LangChain Agent (Function Calling)  
agent = create_tool_calling_agent(model, tools, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

**Agent 최적화 설정:**
- `max_iterations=3`: 최대 3번의 도구 호출 허용
- `early_stopping_method="generate"`: 답변 생성 후 자동 중단
- `handle_parsing_errors=True`: 파싱 에러 자동 처리

**벡터 검색 최적화:**
- `@tool` 데코레이터로 `vector_search_qna_tool` 정의
- ChatGPT가 키워드 관련성 판단하여 필요시에만 검색 수행
- 불필요한 검색 방지로 토큰 및 응답 시간 절약

#### 3. qna_resolver_agent.py v3.0 - 필드 호환성 강화 ✅
**사용자 메시지 추출 안정성 개선:**
```python
# 필드 호환성 개선 (message_content OR message)
message_content = conv.get("message_content", "") or conv.get("message", "")

# 상세한 디버깅 로그 추가
print(f"[{self.agent_name}] 대화 기록 확인 - agent: '{agent_name}', type: '{message_type}'")
```

**구조 간소화:**
- `_is_valid_user_question()` 검증 로직 제거 (ChatGPT 판단 위임)
- conversations에서 최근 사용자 메시지 단순 추출
- TheoryEducator와 동일한 State 관리 패턴 적용

### 🚀 완전한 Function Calling 실행 흐름

**1. 사용자 질문 분석:**
- ChatGPT Agent가 질문의 키워드 관련성 판단
- 메타데이터 기반으로 벡터 검색 필요성 자동 결정

**2. 지능형 벡터 검색:**
- Agent가 `vector_search_qna_tool` 자동 호출
- 사용자 자연어 → 최적화된 검색 쿼리 변환
- 벡터 DB에서 관련 학습 자료 검색 실행

**3. 검색 결과 기반 답변 생성:**
- 벡터 검색 결과를 바탕으로 정확한 답변 생성
- 학습 맥락을 고려한 개인화된 설명 제공

### 📊 기술적 해결 성과

#### 프롬프트 변수 문제 해결 ✅
**문제**: `KeyError: Input to ChatPromptTemplate is missing variables`
**해결**: 프롬프트 생성 시점에 메타데이터 완전 문자열화
```python
# 메타데이터 이스케이프 처리로 ChatPromptTemplate 변수 충돌 해결
learning_context_str = learning_context_str.replace("{", "{{").replace("}", "}}")
```

#### Function Calling 완전 구현 ✅
- **기존**: ChatGPT가 tool_call만 생성, 실제 실행 안됨
- **개선**: AgentExecutor가 도구 실행 → 결과 전달 → 최종 답변 생성

**Function Calling 최적화:**
- 1회 호출로 질문 분석 + 벡터 검색 + 답변 생성
- vs 2단계 분리 호출 대비 속도/비용 모두 우수

### 🎯 시스템 개선 효과

**✅ RAG 시스템 완성:**
- LLM 기반 쿼리 최적화 + 벡터 검색 + 맥락적 답변 생성
- 필요시에만 검색하는 지능형 시스템 (토큰 효율성)

**✅ 사용자 시나리오 최적화:**
```
"질문" → "네, 질문해주세요! 😊" (검색 없음)
"ChatGPT와 클로드 차이는?" → 벡터 검색 + 상세 비교 설명
"AI와 머신러닝 차이는?" → ChatGPT: 벡터 검색 + 상세 답변
"프롬프트 작성법" → 벡터 검색 + 실용적 가이드 제공
```

---

---

# 구현 로그 - 벡터 DB 기반 이론 생성 시스템 통합

## 📅 2025-08-24: TheoryEducator 벡터 DB 통합 및 폴백 전략 구현 ✅

### 🎯 작업 목표
- 이론 생성 에이전트를 벡터 DB 기반으로 전환
- 벡터 검색 실패 시 기존 JSON 파일 폴백 전략 구현
- `chapters_metadata.json` 기반 메타데이터 활용

### 🔧 주요 변경사항

#### 1. TheoryEducator 에이전트 v2.0 구현 ✅
**파일**: `backend/app/agents/theory_educator/theory_educator_agent.py`

**핵심 변경점**:
- **데이터 소스 우선순위 변경**:
  - 1순위: `chapters_metadata.json` (제목) + 벡터 DB 검색 결과
  - 2순위: 기존 `chapter_xx.json` 상세 데이터 (폴백 전략)

**새로운 메서드**:
- `_load_section_metadata()`: 메타데이터에서 챕터/섹션 제목만 추출
- `_load_section_data_fallback()`: 기존 JSON 파일 폴백 로드  
- `get_content_source_info()`: 디버깅용 콘텐츠 소스 정보 반환

**벡터 검색 통합**:
- `vector_search_tools.search_theory_materials()` 함수 활용
- 벡터 검색 결과 > 0개 → 벡터 데이터 우선 사용
- 벡터 검색 실패/결과 없음 → 자동 폴백 to JSON 파일

#### 2. 이론 생성 도구 v2.0 구현 ✅
**파일**: `backend/app/tools/content/theory_tools_chatgpt.py`

**프롬프트 템플릿 분기**:
- **벡터 기반**: 여러 자료 종합한 체계적 설명 생성
- **폴백 기반**: 기존 JSON 데이터 활용 (기존 방식 유지)

**벡터 데이터 처리**:
- 청크 타입별 한글 설명 매핑 (`core_concept` → `핵심 개념`)
- 품질 점수, 키워드, 콘텐츠를 구조화하여 ChatGPT에 전달
- 여러 벡터 자료를 하나의 텍스트로 결합

#### 3. 벡터 검색 도구 준비 ✅
**파일**: `backend/app/tools/external/vector_search_tools.py`

**이론 생성용 검색 함수**:
- `search_theory_materials()`: 이론 생성에 최적화된 벡터 검색
- `core_concept` 청크 우선 (최대 3개, 품질점수 90점 이상)
- 기타 청크 타입 보완 (최대 2개, 품질점수 높은 순)

### 🚀 새로운 동작 흐름

```
1. chapters_metadata.json → 챕터/섹션 제목 추출
2. vector_search_tools.search_theory_materials() 호출
3. IF 벡터 결과 > 0개:
   → 메타데이터 + 벡터 데이터로 이론 생성 (content_source="vector")
4. ELSE:
   → chapter_xx.json 폴백 데이터로 이론 생성 (content_source="fallback")
5. ChatGPT 프롬프트 템플릿 분기 처리
6. 최종 이론 설명 대본 생성
```

### 📊 시스템 장점

- **확장성**: 새로운 벡터 데이터 추가 시 즉시 반영
- **안정성**: 벡터 DB 장애 시에도 기존 JSON 방식으로 동작
- **유연성**: 콘텐츠 품질에 따라 자동으로 최적 소스 선택
- **추적성**: 로그에서 어떤 소스를 사용했는지 명확히 확인 가능
- **호환성**: 기존 LangGraph 워크플로우와 완전 호환

### 🔍 디버깅 지원

**터미널 로그 개선**:
```python
# 벡터 검색 성공 시
print(f"[theory_educator] 벡터 검색 성공 - {len(vector_materials)}개 자료 발견")

# 벡터 DB 데이터 내용 상세 출력 (추가)
print(f"[theory_educator] === 벡터 DB 검색 결과 상세 ===")
for i, material in enumerate(vector_materials, 1):
    chunk_type = material.get('chunk_type', 'unknown')
    quality_score = material.get('content_quality_score', 0)
    keywords = material.get('primary_keywords', [])
    content = material.get('content', '')[:200]  # 처음 200자만
    
    print(f"[theory_educator] 자료 {i}:")
    print(f"  - 타입: {chunk_type}")
    print(f"  - 품질점수: {quality_score}")
    print(f"  - 키워드: {', '.join(keywords) if keywords else '없음'}")
    print(f"  - 내용: {content}...")

# 폴백 활성화 시
print(f"[theory_educator] 벡터 검색 실패 또는 결과 없음 - 폴백 전략 활성화")

# 최종 소스 확인
source_info = f"벡터 DB ({len(vector_materials)}개 자료)" if content_source == "vector" else "폴백 JSON 파일"
print(f"[theory_educator] 이론 설명 생성 완료 (출처: {source_info})")
```

---


## 📅 2025-08-24: ChromaDB 벡터 데이터베이스 구축 완료 ✅

### 구현 완료 항목

#### 1. ChromaDB 인프라 구축
- ✅ **chroma_client.py**: ChromaDB 연결 관리, 싱글톤 패턴
- ✅ **vector_db_setup.py**: JSON 데이터 → 벡터DB 삽입 시스템
- ✅ **vector_search_tools.py**: 3가지 벡터 검색 함수 완성
  - `search_theory_materials()`: 이론 생성용 (core_concept 3개 + 기타 2개)
  - `search_quiz_materials()`: 퀴즈 생성용 (core_concept 제외, 최대 3개)
  - `search_qna_materials()`: QnA용 (유사도 검색, confidence 0.9 이상)

#### 2. 데이터 처리 시스템
- ✅ **JSON → 벡터 변환**: `backend/data/chapters_vec/*.json` 파일들 자동 로드
- ✅ **OpenAI 임베딩**: `text-embedding-3-large` 모델 사용
- ✅ **메타데이터 처리**: 리스트 타입을 쉼표 구분 문자열로 변환
- ✅ **삽입 기록**: `vector_insertion_log.json` 자동 생성

#### 3. 경로 및 설정 최적화
- ✅ **절대경로 시스템**: `backend/data/chroma_db` 정확한 경로 설정
- ✅ **Python 경로 추가**: `sys.path.insert()` 모듈 인식 해결
- ✅ **__init__.py 업데이트**: 외부 서비스 모듈 통합 export

#### 4. 벡터 DB 구축 결과
- ✅ **총 청크 수**: 157개 (성공적으로 삽입)
- ✅ **청크 타입별 분포**: core_concept, analogy, practical_example, technical_detail
- ✅ **품질 필터링**: content_quality_score 90점 이상만 활용

### 해결한 기술적 이슈
- **ChromaDB 메타데이터 타입 제한**: 리스트 → 문자열 변환
- **상대/절대 경로 혼재**: 모든 경로를 절대경로로 통일
- **Collection.count() API 변경**: get() + len() 방식으로 우회
- **모듈 import 오류**: sys.path 동적 추가로 해결

---

## 🎯 다음 구현 목표 (우선순위)

### Phase 1: 이론 생성 벡터 검색 통합 🔄
- **theory_educator_agent.py**: 벡터 검색 호출 추가
- **theory_tools_chatgpt.py**: 벡터 자료를 프롬프트에 통합
- **폴백 전략**: core_concept 0개 시 기존 JSON 데이터 사용
- **테스트**: 챕터1 섹션1 이론 생성 품질 비교

### Phase 2: 퀴즈 생성 벡터 검색 통합
- **quiz_generator_agent.py**: 벡터 검색 호출 추가  
- **quiz_tools_chatgpt.py**: 벡터 자료 활용 로직 추가

### Phase 3: QnA 에이전트 완전 구현
- **qna_resolver_agent.py**: 임시 구현 → 실제 RAG 시스템
- **질문 분석**: 사용자 질문에서 검색 쿼리 추출
- **답변 생성**: 벡터 검색 결과 + ChatGPT 통합

### Phase 4: 성능 최적화 및 테스트
- **응답 품질 측정**: 벡터 검색 전후 비교
- **LangSmith 모니터링**: 성능 지표 추적
- **사용자 테스트**: 실제 학습 시나리오 검증

---

## 📅 2025-08-23: DB 컬럼명 변경 (시간 단위 통일) ✅

### 변경된 컬럼
- `learning_sessions.study_duration_minutes` → `study_duration_seconds`
- `user_statistics.total_study_time_minutes` → `total_study_time_seconds`

### 수정 완료된 부분
- ✅ DB 설계 문서 (`docs/my_docs/db_design_v2_0.md`)
- ✅ 실제 데이터베이스 구조 (마이그레이션 스크립트 실행)

### 추가 수정 필요한 부분
- 🔄 **백엔드 코드**: 시간 관련 컬럼명 사용하는 모든 파일
  - `app/services/learning/` 폴더의 세션 관련 서비스
  - `app/models/` 폴더의 모델 클래스들
  - `app/routes/learning/` 폴더의 API 라우트들
- 🔄 **프론트엔드 코드**: API 응답에서 시간 데이터 처리하는 부분
  - 대시보드 컴포넌트의 학습 시간 표시
  - 세션 완료 후 시간 데이터 처리
- 🔄 **테스트 코드**: 시간 관련 테스트 케이스들

---

## 🔧 구현 상세

### Phase 1: DashboardService 구현 ✅

#### 1.1 주요 메서드 구현
- `get_dashboard_overview()`: 통합 대시보드 데이터 조회
- `_get_user_progress()`: user_progress 테이블 조회 (QueryBuilder)
- `_get_learning_statistics()`: user_statistics 테이블 조회 (QueryBuilder)
- `_get_completed_sessions()`: learning_sessions 테이블 조회 (proceed만)
- `_get_chapter_status()`: JSON 메타데이터 + DB 조합 처리

#### 1.2 JSON 메타데이터 시스템
- `_load_chapters_metadata()`: `backend/data/chapters/chapters_metadata.json` 로드
- 하드코딩된 챕터 구조 제거하고 동적 로드 구현
- `metadata.total_sections` 활용한 정확한 진행률 계산

#### 1.3 완료 날짜 추적 시스템
- `_get_chapter_completion_date()`: 챕터의 마지막 섹션 완료 날짜
- `_get_section_completion_date()`: 섹션별 정확한 완료 날짜
- DB session_end_time 기반 실제 완료 날짜 반환

### Phase 2: API 라우트 구현 ✅

#### 2.1 `backend/app/routes/dashboard/overview.py` 작성
- **GET /dashboard/overview**: 메인 대시보드 API
- **GET /dashboard/health**: 헬스 체크 엔드포인트
- **JWT 인증**: @token_required 데코레이터 적용
- **진단 검증**: diagnosis_completed 체크 후 접근 제어

#### 2.2 에러 처리 시스템
- Blueprint 레벨 에러 핸들러 (404, 405, 500)
- DIAGNOSIS_NOT_COMPLETED 커스텀 에러 코드
- ErrorFormatter 활용한 일관된 에러 응답


---


## **2025년 8월 18일** - SessionService 및 학습 API 엔드포인트 구현 완료

## 🎯 주요 구현 성과

### 1. SessionService 클래스 완전 구현
- **파일 위치**: `backend/app/services/learning/session_service.py`
- **핵심 기능**: 사용자별 TutorState 메모리 관리 및 LangGraph 워크플로우 실행 통합
- **메모리 기반 세션 관리**: JWT 토큰 기반 단일 세션 정책 구현
- **State 만료 시스템**: 1시간 비활성 시 자동 State 정리

### 2. 학습 API 엔드포인트 4개 완전 구현 ✅

#### 2.1 POST /learning/session/start (학습 세션 시작)
- **기능**: 새로운 학습 세션 초기화 및 워크플로우 시작
- **JWT 인증**: 토큰에서 user_id, user_type 추출 및 검증
- **접근 권한 검증**: 사용자 진행 상태 기반 챕터/섹션 접근 제어
- **TutorState 초기화**: state_manager를 통한 초기 상태 생성
- **워크플로우 실행**: TheoryEducator로 자동 라우팅되어 이론 설명 시작

#### 2.2 POST /learning/session/message (메시지 전송)
- **기능**: 사용자 메시지를 받아 LangGraph 워크플로우 실행
- **의도 분석**: LearningSupervisor가 사용자 의도 파악 후 적절한 에이전트로 라우팅
- **State 연속성**: 메모리 저장된 State를 활용한 세션 연속성 보장
- **통합 처리**: 이론 질문, 다음 단계 요청 등 모든 상호작용 처리

#### 2.3 POST /learning/quiz/submit (퀴즈 답변 제출)
- **기능**: 퀴즈 답변을 State에 직접 설정 후 평가 에이전트 호출
- **의도 명시**: user_intent를 "quiz_answer"로 설정하여 정확한 라우팅 보장
- **평가 처리**: EvaluationFeedbackAgent가 객관식/주관식 통합 평가 수행
- **재학습 판단**: 점수 기반 proceed/retry 결정 로직 포함

#### 2.4 POST /learning/session/complete (세션 완료)
- **기능**: 사용자 결정(proceed/retry)에 따른 세션 마무리 처리
- **DB 저장**: SessionManager가 학습 기록을 DB에 트랜잭션 저장
- **진행 상태 업데이트**: user_progress 테이블 자동 업데이트
- **State 정리**: 세션 완료 후 메모리 State 자동 정리

---

## **2025년 8월 18일** - StateManager v1.3 → v2.0 대규모 리팩토링

### 기존 구조
```
state_manager.py (500+ lines)
├── TutorState 정의
├── State 생성/초기화
├── 퀴즈 관련 로직 (100+ lines)
├── 세션 진행 로직 (80+ lines)
├── 대화 관리 로직 (60+ lines)
├── 에이전트 전환 로직 (50+ lines)
├── 검증 로직 (40+ lines)
└── 유틸리티 메서드들
```

### 새로운 구조
```
backend/app/core/langraph/
├── state/                         # State 정의 및 기본 관리
│   ├── __init__.py               # 모든 State 관련 export
│   ├── state_definition.py       # TutorState TypedDict 정의
│   ├── state_factory.py          # State 생성 및 초기화
│   └── state_validator.py        # State 유효성 검증
├── managers/                      # 도메인별 State 관리자
│   ├── __init__.py               # 모든 관리자 export
│   ├── quiz_manager.py           # 퀴즈 관련 State 관리
│   ├── session_manager.py        # 세션 진행 State 관리
│   ├── conversation_manager.py   # 대화 관리
│   └── agent_manager.py          # 에이전트 전환 관리
└── state_manager.py              # 통합 래퍼 클래스 (호환성)
```

---

## 🔧 구현 상세

### Phase 1: State 정의 분리 ✅

#### 1.1 `state_definition.py` 작성
- **TutorState TypedDict** 완전 정의
- **필드별 상세 독스트링** 추가
- **v2.0 퀴즈 시스템** 완전 반영 (객관식/주관식 분리)
- **필드 그룹 분류** 시스템 구축
- **검증용 상수** 정의 (`REQUIRED_FIELDS`, `VALID_VALUES`, `DEFAULT_VALUES`)

```python
# 주요 개선사항
- hint_usage_count 필드 추가 (기존 누락 필드 발견 및 수정)
- 객관식/주관식 완전 분리된 필드 구조
- 명확한 타입 힌팅 및 문서화
```

#### 1.2 `state_factory.py` 작성
- **State 생성 메서드**: `create_new_state()`, `create_session_state()`, `create_quiz_state()`
- **State 초기화**: `reset_session_state()`, `clear_agent_drafts()`, `clear_quiz_data()`
- **직렬화/역직렬화**: `to_dict()`, `from_dict()`, `to_json()`, `from_json()`
- **State 조작 유틸리티**: `copy_state()`, `merge_states()`, `prepare_next_session()`

#### 1.3 `state_validator.py` 작성
- **다양한 검증 레벨**: `quick_validate()`, `validate_state()`, `get_validation_report()`
- **세분화된 검증**: 필수 필드, 필드값, 비즈니스 룰, 퀴즈 일관성, 타입 검증
- **퀴즈 타입별 전용 검증**: 객관식/주관식 각각의 필드 일관성 체크
- **커스텀 예외**: `StateValidationError` 클래스로 상세한 오류 정보 제공

### Phase 2: 도메인별 관리자 분리 ✅

#### 2.1 `quiz_manager.py` 작성 (가장 복잡한 로직)
- **퀴즈 타입 관리**: 섹션 데이터 기반 타입 추출 및 동기화
- **ChatGPT JSON 파싱**: `parse_quiz_from_json()`, `parse_quiz_from_draft()`
- **사용자 답변 처리**: `update_user_answer()`, `evaluate_multiple_choice()`
- **평가 결과 관리**: `update_evaluation_result()` (객관식/주관식 분리)
- **힌트 시스템**: `increment_hint_usage()`, `reset_hint_usage()`
- **UI 모드 전환**: `prepare_quiz_mode()`, `finish_quiz_mode()`
- **퀴즈 상태 조회**: `get_quiz_summary()`, `is_quiz_completed()`, `get_quiz_score()`

#### 2.2 `session_manager.py` 작성
- **세션 진행 단계**: `update_session_progress()`, `update_session_decision()`
- **챕터/섹션 진행**: `update_section_progress()`, `calculate_next_progress()`
- **세션 상태 관리**: `reset_session_state()`, `prepare_next_session()`
- **세션 제한 추적**: `is_session_limit_reached()`, `increment_session_count()`
- **진행률 관리**: `get_progress_percentage()`, `get_remaining_content()`
- **세션 전환 요약**: `create_session_transition_summary()`

#### 2.3 `conversation_manager.py` 작성
- **대화 기록 관리**: `add_conversation()`, `add_user_message()`, `add_system_message()`
- **대화 검색**: `get_conversations_by_agent()`, `find_conversations_by_keyword()`
- **에이전트 대본**: `update_agent_draft()`, `get_agent_draft()`, `clear_agent_drafts()`
- **세션 요약**: `add_recent_session_summary()`, `get_recent_session_summaries()`
- **통계 분석**: `create_conversation_summary()`, `get_conversation_statistics()`
- **DB 연동**: `export_conversations_for_db()` (메시지 순서, 타임스탬프 처리)

#### 2.4 `agent_manager.py` 작성
- **에이전트 전환**: `update_agent_transition()`, `update_agent_with_ui_mode()`
- **UI 모드 제어**: `update_ui_mode()`, `transition_to_quiz_mode()`, `transition_to_chat_mode()`
- **라우팅 로직**: `handle_intent_routing()`, `get_recommended_next_agent()`
- **워크플로우 관리**: `update_workflow_response()`, `create_agent_workflow_context()`
- **상태 추적**: `get_agent_status()`, `get_agent_transition_history()`, `get_agent_statistics()`
- **오류 처리**: `handle_agent_error()`, `reset_agent_state()`

### Phase 3: 통합 시스템 구축 ✅

#### 3.1 모듈 Export 시스템
- **`state/__init__.py`**: State 정의 및 기본 관리자 export
- **`managers/__init__.py`**: 모든 도메인 관리자 export
- **명확한 import 경로** 및 **전역 인스턴스** 제공

#### 3.2 통합 StateManager 래퍼 클래스
```python
class StateManager:
    def __init__(self):
        self.factory = state_factory          # State 생성/초기화
        self.validator = state_validator      # State 검증
        self.quiz = quiz_manager             # 퀴즈 관리
        self.session = session_manager       # 세션 관리  
        self.conversation = conversation_manager  # 대화 관리
        self.agent = agent_manager           # 에이전트 관리
```

- **완벽한 하위 호환성**: 기존 API 100% 유지
- **새로운 통합 메서드**: `get_comprehensive_summary()`, `process_quiz_answer()`, `export_for_database()`
- **향상된 개발 지원**: `debug_state_info()`, `validate_and_fix_state()`


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

