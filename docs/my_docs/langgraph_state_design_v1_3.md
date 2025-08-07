# 부록: 랭그래프 State 설계 v1.3

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
    current_agent: str  # 현재 활성화된 에이전트 이름 (스네이크 케이스)
    
    # === 학습 세션 진행 단계 ===
    session_progress_stage: str  # "session_start": 세션 시작, "theory_completed": 이론 완료, "quiz_and_feedback_completed": 퀴즈와 피드백 완료
    
    # === UI 모드 제어 ===
    ui_mode: str  # "chat": 채팅 모드, "quiz": 퀴즈 모드
    
    # === 퀴즈 관련 정보 ===
    current_question_type: str        # "multiple_choice": 객관식, "subjective": 주관식
    current_question_number: int      # 문제 번호 (기본키)
    current_question_content: str     # 현재 문제 내용
    current_question_answer: str      # 사용자 답변
    is_answer_correct: int            # 객관식: 1(정답)/0(오답), 주관식: 0~100(점수)
    evaluation_feedback: str          # 평가 및 피드백 내용
    hint_usage_count: int
    
    # === 에이전트 대본 저장 ===
    theory_draft: str                 # TheoryEducator 생성 대본
    quiz_draft: str                   # QuizGenerator 생성 대본
    feedback_draft: str               # EvaluationFeedbackAgent 생성 대본
    qna_draft: str                    # QnAResolver 생성 대본
    
    # === 라우팅 & 디버깅 ===
    previous_agent: str  # 이전 에이전트 이름 (디버깅 및 복귀 추적용)
    
    # === 학습 세션 제어 (SessionManager 활용) ===
    session_decision_result: str  # "proceed": 다음 단계 진행, "retry": 현재 구간 재학습
    current_session_count: int    # 현재 구간에서 학습 세션 횟수 (3회 제한)
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

## 2. 🔄 학습 1회(Learning Session) 정의 및 흐름

### 2.1 학습 1회 구성 (PRD v1.3 반영)

```
SessionManager → LearningSupervisor → TheoryEducator → LearningSupervisor → 
QuizGenerator → EvaluationFeedbackAgent → LearningSupervisor → SessionManager
```

**학습 1회 = 개념 설명 + 1문제 풀이 + 평가 피드백**

### 2.2 세션 진행 단계별 State 변화

| 단계 | session_progress_stage | current_agent | 설명 |
|------|----------------------|---------------|------|
| 1 | "session_start" | "session_manager" | 세션 초기화 |
| 2 | "session_start" | "learning_supervisor" | 사용자 라우팅 |
| 3 | "session_start" | "theory_educator" | 이론 설명 대본 생성 |
| 4 | "theory_completed" | "learning_supervisor" | 이론 설명 응답 생성 |
| 5 | "theory_completed" | "quiz_generator" | 문제 출제 대본 생성 |
| 6 | "quiz_and_feedback_completed" | "evaluation_feedback_agent" | 평가 피드백 대본 생성 |
| 7 | "quiz_and_feedback_completed" | "learning_supervisor" | 피드백 응답 생성 |
| 8 | "quiz_and_feedback_completed" | "session_manager" | 세션 완료 판단 |

### 2.3 QnAResolver 진입점 (유연한 질답 시스템)

`qna_resolver`는 다음 3개 지점에서 진입 가능:
- **세션 시작 후**: learning_supervisor에서 질문 의도 파악 시
- **개념 설명 후**: `session_progress_stage: "theory_completed"` 상태에서
- **평가 피드백 후**: `session_progress_stage: "quiz_and_feedback_completed"` 상태에서

**QnA 처리 흐름:**
```
LearningSupervisor → QnAResolver (대본 생성) → LearningSupervisor (응답 생성) → 원래 진행 단계로 복귀
```

## 3. 📊 대화 관리 시스템

### 3.1 current_session_conversations 구조

```python
# 각 대화 항목 구조
conversation_item = {
    "agent_name": str,      # 에이전트 이름 (스네이크 케이스)
    "message": str,         # 메시지 내용
    "timestamp": datetime,  # 메시지 시간
    "message_type": str,    # "user" | "system" | "tool"
    "session_stage": str    # 해당 메시지가 발생한 세션 진행 단계
}
```

### 3.2 대화 관리 원칙

- **학습 세션 진행 중**: 모든 대화를 `current_session_conversations`에 저장
- **학습 세션 완료 시**: DB 저장 후 요약으로 압축하여 `recent_sessions_summary`에 추가
- **퀴즈 정보**: 대화 내용과 분리하여 별도 관리하되, `session_id`로 연관관계 유지

## 4. 💾 DB 저장 및 State 초기화

### 4.1 저장 시점

- **매 학습 세션 완료 시마다** DB 저장 (SessionManager의 `session_decision_result` 결정 후)

### 4.2 저장 로직 (학습 세션 단위 통합 저장)

```python
def complete_current_session(state: TutorState):
    """SessionManager에서 세션 완료 시 자동 처리"""
    
    # 고유한 세션 ID 생성 (구조화된 방식)
    session_id = generate_session_id(
        user_id=state["user_id"],
        chapter=state["current_chapter"], 
        session_count=state["current_session_count"]
    )  # 예: "user123_ch1_session001_20250805_143052"
    
    # 1. 대화 데이터 저장 (session_id 포함)
    save_conversations_to_db({
        "session_id": session_id,
        "user_id": state["user_id"],
        "chapter": state["current_chapter"],
        "conversations": state["current_session_conversations"],
        "session_start_time": state["session_start_time"],
        "session_end_time": datetime.now()
    })
    
    # 2. 퀴즈 데이터 저장 (같은 session_id 포함)
    save_quiz_to_db({
        "session_id": session_id,
        "user_id": state["user_id"],
        "chapter": state["current_chapter"],
        "question_number": state["current_question_number"],
        "question_content": state["current_question_content"],
        "question_type": state["current_question_type"],
        "user_answer": state["current_question_answer"],
        "is_correct": state["is_answer_correct"],
        "feedback": state["evaluation_feedback"],
        "hint_count": state["hint_usage_count"]
    })
    
    # 3. 학습 통계 테이블 업데이트
    update_user_learning_stats(
        user_id=state["user_id"],
        chapter=state["current_chapter"],
        learning_count=state["current_session_count"],
        correct_answer=state["is_answer_correct"],
        completion_time=calculate_completion_time(state["session_start_time"])
    )
    
    # 4. 요약 생성 후 State에 추가
    summary = create_session_summary(
        state["current_session_conversations"], 
        quiz_info
    )
    add_to_recent_summaries(state, summary)  # 최대 5개 유지
    
    # 5. SessionManager 판단에 따른 State 처리
    if state["session_decision_result"] == "proceed":  # 다음 단계 진행
        # State 초기화 (새 챕터/단계 시작)
        reset_session_state(state, new_chapter=True)
        
    elif state["session_decision_result"] == "retry":  # 재학습
        # 세션 카운트 증가 및 일부 필드만 초기화
        reset_session_state(state, new_chapter=False)
        state["current_session_count"] += 1

def reset_session_state(state: TutorState, new_chapter: bool):
    """세션 상태 초기화"""
    # 공통 초기화
    state["session_progress_stage"] = "session_start"
    state["current_session_conversations"] = []
    state["current_question_answer"] = ""
    state["evaluation_feedback"] = ""
    state["hint_usage_count"] = 0
    state["session_start_time"] = datetime.now()
    
    # 대본 필드 초기화
    state["theory_draft"] = ""
    state["quiz_draft"] = ""
    state["feedback_draft"] = ""
    state["qna_draft"] = ""
    
    if new_chapter:
        state["current_session_count"] = 0
        state["current_question_content"] = ""
```

### 4.3 세션 ID 생성 규칙

```python
def generate_session_id(user_id: int, chapter: int, session_count: int) -> str:
    """구조화된 세션 ID 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"user{user_id}_ch{chapter}_session{session_count:03d}_{timestamp}"

# 생성 예시: "user123_ch1_session001_20250805_143052"
```

## 5. 🎯 에이전트별 State 사용 패턴

### 5.1 각 에이전트가 주로 사용하는 State 필드

| 에이전트 | 주요 사용 필드 |
|---------|---------------|
| **session_manager** | `session_decision_result`, `current_session_count`, `session_progress_stage` |
| **learning_supervisor** | `current_agent`, `previous_agent`, `session_progress_stage`, `ui_mode`, 모든 draft 필드 |
| **theory_educator** | `user_type`, `current_chapter`, `recent_sessions_summary` → `theory_draft` 생성 |
| **quiz_generator** | `current_question_number`, `current_question_type`, `hint_usage_count` → `quiz_draft` 생성 |
| **evaluation_feedback_agent** | `current_question_type`, `current_question_answer`, `is_answer_correct` → `feedback_draft` 생성 |
| **qna_resolver** | `previous_agent`, `current_chapter`, `session_progress_stage` → `qna_draft` 생성 |

### 5.2 대본 전달 시스템

```python
# 1. 각 에이전트가 대본 생성 후 해당 draft 필드에 저장
def theory_educator_process(state: TutorState):
    theory_content = generate_theory_explanation(state)
    state["theory_draft"] = theory_content
    return state

# 2. LearningSupervisor가 draft를 활용해 최종 응답 생성
def learning_supervisor_response(state: TutorState):
    if state["current_agent"] == "theory_educator":
        final_response = create_user_friendly_response(state["theory_draft"])
        state["theory_draft"] = ""  # 사용 후 초기화
    return final_response
```

## 6. 🔧 특수 처리 사항

### 6.1 UI 모드 제어

```python
# QuizGenerator 활성화 시 UI 모드 전환
def update_ui_mode(state: TutorState):
    if state["current_agent"] == "quiz_generator":
        state["ui_mode"] = "quiz"
    else:
        state["ui_mode"] = "chat"
```

### 6.2 퀴즈 타입별 채점 처리

```python
# 객관식/주관식 구분 채점
def evaluate_answer(state: TutorState):
    if state["current_question_type"] == "multiple_choice":
        # 객관식: 1(정답) 또는 0(오답)
        state["is_answer_correct"] = 1 if is_correct_answer else 0
    elif state["current_question_type"] == "subjective":
        # 주관식: 0~100점 점수
        state["is_answer_correct"] = calculate_score(answer)  # 0~100 범위
```

### 6.3 세션 진행 단계 제어

```python
# 단계별 에이전트 전환 로직
def update_session_progress(state: TutorState, completed_agent: str):
    if completed_agent == "theory_educator":
        state["session_progress_stage"] = "theory_completed"
    elif completed_agent == "evaluation_feedback_agent":
        state["session_progress_stage"] = "quiz_and_feedback_completed"
    # quiz_generator 완료 후에는 단계 변경 없음 (evaluation_feedback_agent로 자동 연결)
```

### 6.4 학습 세션 횟수 제한

```python
# SessionManager에서 강제 완료 로직
def session_completion_check(state: TutorState):
    if state["current_session_count"] >= 3:
        state["session_decision_result"] = "proceed"  # 강제 다음 단계
    else:
        # 정상적인 완료 판단 로직 수행
        state["session_decision_result"] = analyze_session_completion(state)
```

### 6.5 사용자 유형별 처리

```python
# 사용자 유형에 따른 대본 생성 분기
if state["user_type"] == "beginner":
    # AI 입문자용 설명 방식
    pass
elif state["user_type"] == "advanced":
    # 실무 응용형용 설명 방식
    pass
```

### 6.6 QnA 시스템 통합

```python
# QnA 발생 시 현재 진행 단계 보존
def handle_qna_request(state: TutorState):
    # 현재 단계 정보를 보존하고 QnA 처리
    current_stage = state["session_progress_stage"]
    
    # QnA 처리
    qna_response = process_qna(state)
    state["qna_draft"] = qna_response
    
    # 원래 단계로 복귀 (단계 변경 없음)
    state["session_progress_stage"] = current_stage
```

## 7. 🔄 워크플로우 State 변화 예시

### 7.1 정상적인 1학습 세션 흐름

```python
# 초기 상태
{
    "session_progress_stage": "session_start",
    "current_agent": "session_manager",
    "theory_draft": "",
    "quiz_draft": "",
    "feedback_draft": ""
}

# 1. 이론 설명 완료 후
{
    "session_progress_stage": "theory_completed", 
    "current_agent": "learning_supervisor",
    "theory_draft": "AI는 인간의 지능을 모방한...",
    "previous_agent": "theory_educator"
}

# 2. 문제 출제 완료 후
{
    "session_progress_stage": "quiz_and_feedback_completed",
    "current_agent": "learning_supervisor", 
    "quiz_draft": "다음 중 AI의 특징은?...",
    "previous_agent": "quiz_generator"
}

# 3. 피드백 완료 후
{
    "session_progress_stage": "quiz_and_feedback_completed",
    "current_agent": "session_manager",
    "feedback_draft": "정답입니다! 훌륭해요...",
    "session_decision_result": "proceed"
}
```

### 7.2 중간 질문 발생 시 흐름

```python
# 이론 설명 후 질문 발생
{
    "session_progress_stage": "theory_completed",  # 단계 보존
    "current_agent": "qna_resolver",
    "qna_draft": "AI와 머신러닝의 차이는...",
    "previous_agent": "learning_supervisor"
}

# 질문 답변 후 원래 흐름 복귀
{
    "session_progress_stage": "theory_completed",  # 단계 유지
    "current_agent": "learning_supervisor",
    "previous_agent": "qna_resolver"
}
```

## 8. 📋 v1.3 주요 변경사항

### 8.1 새로 추가된 필드
- `session_progress_stage`: 세션 내 진행 단계 추적
- `ui_mode`: UI 모드 제어 (채팅/퀴즈 모드 전환)
- `current_question_type`: 퀴즈 타입 구분 (객관식/주관식)
- `theory_draft`, `quiz_draft`, `feedback_draft`, `qna_draft`: 에이전트 대본 저장
- SessionManager 관련 에이전트 추가

### 8.2 변경된 워크플로우
- 모든 에이전트가 LearningSupervisor로 복귀하는 순환 구조
- 대본 기반 응답 생성 시스템
- 유연한 QnA 시스템 (언제든지 질문 가능)

### 8.3 퀴즈 시스템 강화
- 객관식/주관식 타입 구분
- is_answer_correct 필드로 통합 채점 (객관식: 0/1, 주관식: 0~100점)
- UI 모드 자동 전환 시스템

### 8.4 세션 관리 최적화
- SessionManager 전담으로 세션 생명주기 관리
- 진행 단계별 명확한 State 변화 정의
- 3회 제한 및 강제 완료 로직 유지

---

*State 설계 버전: v1.3*  
*최종 수정일: 2025.08.05*  
*연관 문서: AI 활용법 학습 튜터 PRD v1.3*