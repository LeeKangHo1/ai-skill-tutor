# 📝 QnA 스트리밍 시스템 개발일지

**개발 기간**: 2025.09.01  
**주요 작업**: 기존 가짜 스트리밍을 진짜 스트리밍으로 전환하는 대규모 리팩터링

---

## 🎯 개발 배경 및 문제점

### 기존 시스템의 한계
- **가짜 스트리밍**: LangChain Agent가 전체 답변 완성(7초) → 단어별 가짜 스트리밍
- **느린 TTFT**: Time to First Token이 실제로는 7초 (Agent 완료 시간)
- **사용자 경험 저하**: 실시간 답변 생성처럼 보이지만 실제로는 이미 완성된 답변을 분할 표시

### 기술적 문제
```python
# 기존 문제 코드
async for chunk in agent_executor.astream({"input": user_question}):
    if 'output' in chunk:  # ← Agent 전체 완료 후에만 나옴
        final_answer = chunk['output']  # 이미 완성된 전체 답변
        async for word_chunk in _split_into_words(final_answer):  # 가짜 스트리밍
            yield word_chunk
```

---

## 🚀 해결 방안 및 새로운 아키텍처

### Agent + ChatGPT 스트리밍 분리 방식 도입

**핵심 아이디어**: LLM을 2번 호출하여 각자의 역할에 충실하도록 분리

```
기존: Agent(판단+검색+답변생성) = 7초 → 가짜스트리밍
새로운: Agent(판단+검색) 2초 → ChatGPT직접스트리밍 → 진짜TTFT 2.5초
```

### 2단계 처리 구조

1. **Phase 1**: Agent가 컨텍스트 준비 (1-2초)
   - 벡터 검색 필요성 지능적 판단
   - 검색 쿼리 최적화 (최대 3개로 분할)
   - 병렬 벡터 검색 실행

2. **Phase 2**: ChatGPT 직접 스트리밍 (실시간)
   - Agent가 준비한 컨텍스트 활용
   - 실제 토큰 단위 스트리밍
   - 마크다운 실시간 제거

---

## 🛠️ 구현된 주요 기능

### 1. 기존 시스템 통합 (워크플로우 우회)

**Learning Supervisor 확장**:
- `question` 의도 감지 시 `question_streaming`으로 전환
- 스트리밍 세션 생성 및 전역 임시 저장소 관리
- 기존 LangGraph 워크플로우 우회 처리

**Supervisor Router 수정**:
```python
if user_intent == "question_streaming":
    return "learning_supervisor_output"  # 워크플로우 우회
```

### 2. Response Generator 스트리밍 지원

- 스트리밍 전용 workflow_response 생성
- temp_session_id 추출 및 전달
- Message.py에서 자동 스트리밍 응답 변환

### 3. QnA Resolver State 관리 분리

**3개 메서드로 책임 분리**:
- `process()`: 기존 LangGraph 워크플로우용
- `process_streaming_state()`: 스트리밍 시작 시 State 관리
- `finalize_streaming_state()`: 스트리밍 완료 후 최종 State 저장

### 4. 고성능 병렬 벡터 검색

**다중 쿼리 생성**:
```python
# 예시: "제프리 힌튼과 트랜스포머" 
# → ["제프리 힌튼", "트랜스포머 아키텍처"]
```

**병렬 검색 처리**:
- ThreadPoolExecutor 활용한 동시 검색
- 결과 통합 및 중복 제거
- 유사도 점수 기반 정렬

---

## 🔧 주요 파일별 수정사항

### Backend

#### `learning_supervisor_agent.py`
- `_handle_question_intent_for_streaming()` 메서드 추가
- 임시 세션 생성 및 전역 저장소 연동
- TutorState 구조 보존 (새 필드 추가 없이)

#### `supervisor_router.py`
```python
if user_intent == "question_streaming":
    return "learning_supervisor_output"
```

#### `response_generator.py`
- `_create_streaming_qna_workflow_response()` 추가
- 대화 기록에서 temp_session_id 추출
- workflow_response에 스트리밍 정보 포함

#### `qna_stream.py`
- URL 단순화: `/qna-stream/<temp_id>`
- QnA Agent State 관리 통합
- 스트리밍 완료 후 자동 State 저장

#### `qna_tools_chatgpt_stream.py`
**완전 재작성**:
- Agent + ChatGPT 분리 구조 구현
- 병렬 벡터 검색 지원
- 실제 토큰 단위 스트리밍

#### `vector_search_tools.py`
- `search_qna_materials_parallel()` 추가
- 병렬 검색 및 결과 통합 로직

#### `message.py`
- 스트리밍 응답 자동 감지 및 변환
- temp_session_id 추출 후 클라이언트 전달

### Frontend

#### `learningService.js`
- URL 단순화: `/qna-stream/<temp_id>`
- EventSource 연결 및 에러 처리

#### `learningStore.js`
- 자동 스트리밍 감지 로직 추가
- `_startStreamingWithTempId()` 함수 구현
- TTFT 측정 기능

---

## 📊 성능 개선 결과

### TTFT (Time to First Token) 개선
```
기존: Agent 완료(7초) → 가짜 스트리밍
새로운: Agent 분석(2초) → 실제 ChatGPT 첫 토큰(0.5초) = 2.5초
```
**개선율**: 약 65% 단축

### 벡터 검색 성능
```
기존: 단일 검색(3초)
새로운: 병렬 검색(1.5초) + 더 정확한 다중 쿼리
```
**개선율**: 50% 단축 + 품질 향상

### 사용자 경험
- **진짜 스트리밍**: 실제 토큰 단위 실시간 생성
- **빠른 응답**: 체감 속도 대폭 개선
- **정확한 답변**: 다중 쿼리로 검색 품질 향상

---

## 🎯 핵심 설계 결정사항

### 1. "2번 LLM 호출" 선택 이유
- **1번 호출의 한계**: Agent 내부 처리 완료 후 output 반환 (스트리밍 불가)
- **현실적 선택**: 실제 서비스들(ChatGPT, Claude)도 단계별 처리 사용
- **성능 향상**: 각 역할에 최적화된 처리로 전체 속도 개선

### 2. 워크플로우 통합 vs 독립
- **통합 선택**: 기존 시스템과 완전 호환
- **State 관리**: QnA Resolver가 여전히 책임 유지
- **사용자 경험**: 기존 채팅창에서 자연스럽게 작동

### 3. 병렬 처리 도입
- **벡터 검색**: I/O 바운드가 아닌 CPU 바운드로 병렬 가능
- **서버 부하**: 3개 동시 검색은 acceptable
- **품질 vs 성능**: 둘 다 개선하는 win-win 선택

---

## 🚨 해결한 기술적 과제

### 1. TutorState TypedDict 제약
**문제**: 새로운 필드 추가 시 타입 에러  
**해결**: 기존 필드 활용 + 전역 임시 저장소 분리

### 2. JWT 인증 + SSE 스트리밍
**문제**: SSE는 헤더 인증 불가  
**해결**: 2단계 요청 (JWT로 temp_id 발급 → SSE 연결)

### 3. Agent 스트리밍의 근본적 한계
**문제**: Agent는 의사결정 도구이지 스트리밍 도구가 아님  
**해결**: Agent와 ChatGPT 역할 분리

### 4. 벡터 검색 품질 저하
**문제**: 복합 질문을 하나의 쿼리로 처리  
**해결**: 지능적 쿼리 분할 + 병렬 검색

---

## 🔮 향후 개선 계획

### 1. 캐싱 시스템 도입
- Agent 분석 결과 캐싱
- 벡터 검색 결과 캐싱
- 동일한 질문 재요청 시 즉시 응답

### 2. 검색 품질 최적화
- 쿼리 생성 알고리즘 개선
- 검색 결과 re-ranking 도입
- 사용자 피드백 기반 학습

### 3. 모니터링 강화
- 실시간 TTFT 측정
- 검색 성공률 추적
- 사용자 만족도 지표

---

## 📈 결론

이번 리팩터링을 통해 **가짜 스트리밍을 진짜 스트리밍으로 전환**하는 데 성공했습니다. 

**주요 성과**:
- TTFT 65% 개선 (7초 → 2.5초)
- 벡터 검색 50% 단축 + 품질 향상  
- 실제 토큰 단위 스트리밍 구현
- 기존 시스템과 완전 호환

**기술적 교훈**:
- Agent의 한계를 인정하고 적절한 역할 분리가 중요
- "완벽한 1번 호출"보다 "효율적인 단계별 처리"가 현실적
- 사용자 경험 개선을 위해서는 때로 아키텍처 재설계가 필요

이제 사용자들이 **진짜 실시간 AI 답변**을 경험할 수 있게 되었습니다! 🎉