# 부록: 랭그래프 State 설계 v2.0

## 1. 🏗️ State 구조 정의

### 1.1 TutorState 클래스

```python
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class TutorState(TypedDict):
    # === 기본 사용자 정보 ===
    user_id: int
    user_type: str   # "beginner": AI 입문자, "advanced": 실무 응용형
    
    # === 학습 진행 상태 ===
    current_chapter: int
    current_section: int  # 현재 섹션 번호 (1학습 세션 = 1섹션)
    current_agent: str  # 현재 활성화된 에이전트 이름 (스네이크 케이스)
    
    # === 학습 세션 진행 단계 ===
    session_progress_stage: str  # "session_start": 세션 시작, "theory_completed": 이론 완료, "quiz_and_feedback_completed": 퀴즈와 피드백 완료
    
    # === UI 모드 제어 ===
    ui_mode: str  # "chat": 채팅 모드, "quiz": 퀴즈 모드
    
    # === 퀴즈 관련 정보 ===
    quiz_type: str                        # "multiple_choice" 또는 "subjective"
    quiz_content: str                     # 퀴즈 문제 내용
    quiz_options: List[str]               # 객관식: ["선택지1", "선택지2", "선택지3", "선택지4"], 주관식: []
    quiz_correct_answer: Any              # 객관식: 정답 번호(int), 주관식: None
    quiz_explanation: str                 # 객관식: 정답 해설, 주관식: ""
    quiz_sample_answer: str               # 객관식: "", 주관식: 모범 답안 예시
    quiz_evaluation_criteria: List[str]   # 객관식: [], 주관식: ["평가기준1", "평가기준2", "평가기준3"]
    quiz_hint: str                        # 힌트 내용 (공통)
    user_answer: str                      # 사용자 답변
    multiple_answer_correct: bool         # 객관식 정답 여부 (True/False)
    subjective_answer_score: int          # 주관식 점수 (0~100점)
    evaluation_feedback: str              # 평가 및 피드백 내용
    hint_usage_count: int                 # 힌트 사용 횟수
    
    # === 에이전트 대본 저장 ===
    theory_draft: str                     # TheoryEducator 생성 대본
    quiz_draft: str                       # QuizGenerator 생성 대본 (JSON 문자열)
    feedback_draft: str                   # EvaluationFeedbackAgent 생성 대본
    qna_draft: str                        # QnAResolver 생성 대본
    
    # === 라우팅 & 디버깅 ===
    user_intent: str  # 사용자 의도 ("next_step", "question", "quiz_answer")
    previous_agent: str  # 이전 에이전트 이름 (디버깅 및 복귀 추적용)
    
    # === 학습 세션 제어 (SessionManager 활용) ===
    retry_decision_result: str  # "proceed": 다음 단계 진행, "retry": 현재 구간 재학습
    current_session_count: int    # 현재 구간에서 학습 세션 횟수 (1회 제한)
    session_start_time: datetime  # 학습 세션 시작 시간
    
    # === 대화 관리 ===
    current_session_conversations: List[Dict[str, Any]]  # 현재 학습 세션의 대화 내용
    recent_sessions_summary: List[Dict[str, str]]        # 최근 5개 학습 세션 요약
```

### 1.2 에이전트 이름 정의

```python
AGENT_NAMES = {
    "session_manager": "세션 관리 및 완료 판단 전담",
    "learning_supervisor": "사용자 대면 + 라우팅 + 응답 생성",
    "theory_educator": "개념 설명 대본 생성",
    "quiz_generator": "문제 출제 대본 생성",
    "evaluation_feedback_agent": "평가 및 피드백 대본 생성",
    "qna_resolver": "실시간 질문 답변 대본 생성"
}
```

---

## 2. 🔄 새로운 워크플로우 구조 (v2.0)

### 2.1 통합된 워크플로우

```
Start → LearningSupervisor Input → SupervisorRouter → [Agents] → LearningSupervisor Output → End
```

**통합 워크플로우 특징:**
- 모든 에이전트가 LearningSupervisor Output으로 수렴
- 중앙집중식 라우팅 (SupervisorRouter)
- 사용자 대면 응답 통일 (response_generator)

### 2.2 세션 진행 단계별 State 변화

| 단계 | session_progress_stage | 라우팅 | 에이전트 | 설명 |
|------|----------------------|--------|----------|------|
| 1 | "session_start" | 자동 → theory_educator | theory_educator | 세션 시작 시 의도 분석 없이 바로 이론 설명 |
| 2 | "theory_completed" | 의도 분석 | quiz_generator / qna_resolver | 퀴즈 진행 OR 질문 답변 |
| 3 | "theory_completed" | quiz_answer → evaluation_feedback | evaluation_feedback_agent | 퀴즈 답변 제출 시 의도 분석 없이 바로 평가 |
| 4 | "quiz_and_feedback_completed" | 의도 분석 | session_manager / qna_resolver | 세션 완료 OR 추가 질문 |

### 2.3 라우팅 결정 알고리즘 (SupervisorRouter)

```python
def supervisor_router(state: TutorState) -> str:
    user_intent = state.get("user_intent", "next_step")
    session_stage = state.get("session_progress_stage", "session_start")
    
    # 1. 퀴즈 답변 처리 (의도 분석 없이 바로 평가)
    if user_intent == "quiz_answer":
        return "evaluation_feedback"
    
    # 2. 질문 답변 요청  
    if user_intent == "question":
        return "qna_resolver"
    
    # 3. 세션 완료 처리 (평가 완료 후)
    if session_stage == "quiz_and_feedback_completed" and user_intent == "next_step":
        return "session_manager"
    
    # 4. 다음 단계 진행
    if user_intent == "next_step":
        if session_stage == "session_start":
            return "theory_educator"
        elif session_stage == "theory_completed":
            return "quiz_generator"
    
    # 5. 기본값 - 직접 응답 생성
    return "learning_supervisor_output"
```

---

## 3. 📊 의도 분석 시스템 강화

### 3.1 2단계 의도 분석 시스템

**1단계: 빠른 경로 (완전 일치 키워드 30-40%)**
```python
QUICK_INTENT_KEYWORDS = {
    "next_step": ["다음", "네", "계속", "진행", "시작"],
    "question": ["질문", "궁금", "설명해주세요", "차이점", "help"]
}
```

**2단계: LLM 분석 (60-70%)**
- ChatGPT 기반 맥락적 의도 분석
- 신뢰도 점수 포함 결과 반환

### 3.2 의도 분석 우회 로직

**의도 분석을 건너뛰는 경우:**
- `session_start`: 무조건 theory_educator로 진행
- `quiz_answer`: 퀴즈 답변 제출 시 evaluation_feedback로 직접 라우팅
- UI 모드가 `quiz`: 답변 입력 대기 상태

---

## 4. 💾 에이전트별 대본 시스템

### 4.1 대본 전달 흐름

```
각 에이전트 → 순수 대본 생성 → {agent_name}_draft 저장 → LearningSupervisor → response_generator → 사용자 친화적 최종 응답
```

### 4.2 대본 필드별 역할

| 대본 필드 | 생성 에이전트 | 역할 | 구현 상태 |
|-----------|---------------|------|-----------|
| `theory_draft` | TheoryEducator | 순수 이론 설명 대본 | ✅ 완성 |
| `quiz_draft` | QuizGenerator | JSON 형태 퀴즈 대본 | ✅ 완성 |
| `feedback_draft` | EvaluationFeedbackAgent | 순수 피드백 대본 | ✅ 완성 |
| `qna_draft` | QnAResolver | 질문 답변 대본 | ⚠️ 임시 구현 |

### 4.3 응답 생성 통합 시스템

**response_generator의 역할:**
1. 에이전트별 draft 분석
2. 사용자 친화적 멘트 추가
3. UI 모드별 맞춤 응답 생성
4. 진행 안내 메시지 포함

---

## 5. 🔧 세션 관리 시스템 완성

### 5.1 세션 ID 생성 규칙

```python
# 세션 ID는 MySQL AUTO_INCREMENT로 자동 생성
# learning_sessions 테이블의 session_id INT PRIMARY KEY AUTO_INCREMENT
```

### 5.2 DB 저장 시스템 (완성)

**저장 테이블:**
1. `learning_sessions`: 세션 기본 정보
2. `session_conversations`: 대화 기록
3. `session_quizzes`: 퀴즈 정보
4. `user_progress`: 사용자 진행 상태
5. `user_statistics`: 학습 통계 (자동 업데이트)

**트랜잭션 저장 순서:**
```python
# SessionManager에서 세션 완료 시 자동 처리
1. learning_sessions 저장 (session_id는 AUTO_INCREMENT로 자동 생성)
2. session_conversations 배치 저장 (생성된 session_id 사용)
3. session_quizzes 저장 (퀴즈가 있는 경우)
4. user_progress 업데이트 (챕터/섹션 진행)
5. user_statistics 자동 계산 업데이트
```

### 5.3 섹션 진행 로직

```python
def update_progress_for_next_session(state: TutorState, decision_result: str):
    if decision_result == "proceed":
        max_sections = get_max_sections_from_json(current_chapter, user_type)
        
        if current_section < max_sections:
            # 같은 챕터 내 다음 섹션
            next_chapter = current_chapter
            next_section = current_section + 1
        else:
            # 다음 챕터의 첫 번째 섹션
            next_chapter = current_chapter + 1
            next_section = 1
    
    elif decision_result == "retry":
        # 현재 섹션 유지, 세션 카운트 증가
        next_chapter = current_chapter
        next_section = current_section
        current_session_count += 1
```



---

## 6. 🔧 기술적 최적화 성과

### 9.1 라우팅 안정성 확보

**해결된 핵심 버그:**
- **문제**: "질문" 입력 시 의도는 `question`이지만 라우터에서 `next_step`으로 읽혀 quiz_generator로 잘못 라우팅
- **원인**: `TutorState`에 `user_intent` 필드 미정의
- **해결**: 필드 정의 + 기본값 `"next_step"` 설정

### 9.2 State 일관성 보장

**개선 사항:**
- TutorState 모든 필드 명시적 정의
- 에이전트 인스턴스 통일 (단일 인스턴스 패턴)
- State 검증 시스템 구축

### 9.3 성능 최적화

**의도 분석 최적화:**
- 1단계: 완전 일치 키워드 (빠른 처리)
- 2단계: LLM 분석 (정확도 향상)
- 우회 로직: 불필요한 분석 건너뛰기

**ChatGPT 호출 최적화:**
- 퀴즈 + 힌트 동시 생성 (QuizGenerator)
- 채점 + 피드백 동시 처리 (EvaluationFeedback)

---

## 7. 📋 v2.0 주요 변경사항

### 7.1 워크플로우 구조 개편
- **기존**: 복잡한 다중 경로 구조
- **v2.0**: 통합된 LearningSupervisor 중심 구조
- **장점**: 라우팅 일관성, 응답 품질 향상, 디버깅 용이성

### 7.2 의도 분석 시스템 강화
- **2단계 분석**: 빠른 경로 + LLM 백업
- **우회 로직**: 불필요한 분석 제거
- **키워드 확장**: 25개 의도 분석 키워드 추가

### 7.3 세션 관리 완전 구현
- **SessionManager**: 세션 생명주기 완전 관리
- **DB 저장**: 5개 테이블 트랜잭션 저장 시스템
- **자동 진행**: MySQL AUTO_INCREMENT 기반 세션 관리

### 7.4 대본 기반 응답 시스템
- **분리**: 에이전트 대본 생성 ↔ 사용자 응답 생성
- **통합**: response_generator로 일관된 응답 품질
- **유연성**: 에이전트별 특성 유지하면서 사용자 친화적 변환

### 7.5 QnA 시스템 준비
- **노드 등록**: LangGraph 워크플로우 통합 완료
- **임시 구현**: 기본 메시지 응답 시스템
- **확장 준비**: Vector DB + 웹 검색 인터페이스 준비

---

*State 설계 버전: v1.3 → v2.0*  
*최종 수정일: 2025.08.17*  
*주요 변경 사유: 워크플로우 통합, 라우팅 안정성 확보, 실제 구현 완료 상태 반영*  
*연관 문서: AI 활용법 학습 튜터 PRD v2.0, 구현 로그 2025.08.16*