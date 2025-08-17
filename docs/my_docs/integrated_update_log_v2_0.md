# docs/my_docs/integrated_update_log_v2_0.md

# AI 활용법 학습 튜터 프로젝트 v2.0 통합 업데이트 로그

**업데이트 날짜**: 2025년 8월 17일  
**버전**: v1.3 → v2.0  
**주요 변경 사유**: 실제 구현 완료 상태 반영 및 워크플로우 최적화

---

## 📋 전체 업데이트 개요

### 🎯 v2.0 핵심 변경사항
- **통합 워크플로우**: 모든 에이전트가 LearningSupervisor 중심으로 통합
- **하이브리드 UX**: chat/quiz 모드 자동 전환 시스템 도입
- **데이터 구조 개선**: 객관식/주관식 분리, AUTO_INCREMENT 세션 ID 도입
- **실제 구현 반영**: 이론 중심에서 완성된 기능 중심으로 문서 전환
- **성능 최적화**: 단일 API 호출, 통합 응답 구조로 효율성 향상

---

## 📄 1. PRD (Product Requirements Document) v2.0 변경사항

### 🔄 주요 구조 변경

#### 2.2 학습 진행 흐름
- **워크플로우 다이어그램 단순화**
  - 기존: 복잡한 다단계 워크플로우
  - 변경: `Start → LearningSupervisor Input → SupervisorRouter → [Agents] → LearningSupervisor Output → End`
  - 모든 에이전트가 LearningSupervisor Output으로 수렴하는 통합 구조

#### 2.3 사용자 시나리오 (1학습 세션 흐름)
- **워크플로우 표현 방식 개선**
  ```
  기존: 사용자: "AI는 인간의 지능을 모방한 기술입니다..."
  변경: 출력: "AI는 인간의 지능을 모방한 기술입니다..."
  ```

- **에이전트 처리 과정 명확화**
  ```
  3. 사용자: "2번이요" 
     → LearningSupervisor → EvaluationFeedbackAgent → 재학습 여부 판단 → LearningSupervisor 
     → 출력: "정답입니다! 다음 단계로 진행할까요?"
  
  4. 사용자: "네" (최종 재학습 여부 판단은 사용자가) 
     → SessionManager가 세션을 마무리하고 DB에 데이터 저장 → LearningSupervisor 
     → 출력: "1챕터가 완료되었습니다"
  ```

### 📚 3번 기술 요구사항 추가

#### 📦 사용 패키지 버전 신규 추가
```
- langchain==0.3.27
- langchain-core==0.3.72
- langgraph==0.6.3
- langsmith==0.4.13
```

### 📖 5번 AI 입문자 학습 챕터 구성 완전 개편

#### 신규 구조 (v2.0)
- **구체적이고 매력적인 챕터 제목**
  - "AI, 너 정체가 뭐니?" → "AI는 무엇인가?"
  - "AI 빅뱅, 세상을 바꾼 순간들" → "LLM이란 무엇인가"
  - "AI 전국시대, 누가 천하를 통일할까?" → "다양한 AI 챗봇들 소개"

- **세부 주제 불릿 포인트 방식**
  ```
  Chapter 1. AI는 무엇인가?
  - AI는 어떻게 우리 삶에 들어와 있을까?
  - AI, 머신러닝, 딥러닝 - 관계 파헤치기
  - LLM, 챗봇, 생성형 AI, GPT, 파라미터 - 핵심 용어 5분 정리
  - 챗봇과 무엇을 할 수 있을까?
  ```

### 🤖 6번 MAS 아키텍처 실제 구현 반영

#### 변경 (v2.0): 구현 완료 상태 반영
- **완성 상태 표시 시스템**
  ```
  SessionManager (✅ 완성 - 세션 생명주기 관리, DB 저장)
  └── LearningSupervisor (✅ 완성 - 워크플로우 시작점/끝점, 라우팅 및 응답 생성)
      ├── TheoryEducator (✅ 완성 - 이론 설명 대본 생성)
      ├── QuizGenerator (✅ 완성 - 퀴즈 및 힌트 동시 생성)
      ├── EvaluationFeedbackAgent (✅ 완성 - 객관식/주관식 통합 평가)
      └── QnAResolver (⚠️ 임시 구현 - "QnAResolver가 호출되었습니다" 메시지만 반환)
  ```

### 🧩 8번 기능 명세서 완전 개편

#### 구현 상태 시각화
| 기능 | 구현 상태 | 
|------|-----------|
| 인증 시스템 | ✅ 완성 |
| 세션 관리 | ✅ 완성 |
| 실시간 Q&A | ⚠️ 임시 구현 |
| 하이브리드 UX | 🔄 프론트엔드 구현 예정 |

### 🤖 11번 AI 모델 운영 전략 변경

#### LLM 모델 변경
```
기존: Gemini 2.5 Flash/Pro 중심
변경: GPT-4o-mini 통일 사용
```

---

## 🗄️ 2. DB 설계 v2.0 수정내용

### 📝 주요 테이블 구조 변경사항

#### 1. learning_sessions 테이블

**변경사항:**
- **세션 ID**: `VARCHAR(100)` → `INT AUTO_INCREMENT`
- **필드명 변경**: `session_decision_result` → `retry_decision_result`
- **구조 개선**: `session_sequence` → `section_number` (의미 명확화)

#### 기존 (v1.3):
```sql
session_id VARCHAR(100) PRIMARY KEY COMMENT '고유 세션 ID',
session_sequence INT NOT NULL COMMENT '해당 챕터 내에서의 세션 순서',
session_decision_result VARCHAR(20) COMMENT 'proceed: 다음 단계 진행, retry: 재학습',
```

#### 신규 (v2.0):
```sql
session_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '자동 증가 세션 ID',
section_number INT NOT NULL COMMENT '챕터 내 섹션 번호',
retry_decision_result VARCHAR(20) COMMENT 'proceed: 다음 단계 진행, retry: 재학습',
```

#### 2. session_quizzes 테이블 완전 재설계

**신규 (v2.0):**
```sql
session_id INT NOT NULL COMMENT '세션 ID (AUTO_INCREMENT)',

-- 퀴즈 기본 정보
quiz_type VARCHAR(20) NOT NULL COMMENT 'multiple_choice: 객관식, subjective: 주관식',
quiz_content TEXT NOT NULL COMMENT '퀴즈 문제 내용',

-- 객관식 전용 필드
quiz_options JSON COMMENT '객관식 선택지 배열',
quiz_correct_answer INT COMMENT '객관식 정답 번호 (1-4)',
quiz_explanation TEXT COMMENT '객관식 정답 해설',

-- 주관식 전용 필드
quiz_sample_answer TEXT COMMENT '주관식 모범 답안 예시',
quiz_evaluation_criteria JSON COMMENT '주관식 평가 기준 배열',

-- 공통 필드
quiz_hint TEXT COMMENT '힌트 내용',
user_answer TEXT COMMENT '사용자 답변',

-- 평가 결과 분리
multiple_answer_correct BOOLEAN COMMENT '객관식 정답 여부',
subjective_answer_score INT COMMENT '주관식 점수 (0-100)',
```

#### 3. user_progress 테이블

**변경사항:**
- **새 필드 추가**: `current_section INT NOT NULL DEFAULT 1`

#### 4. user_statistics 테이블 완전 재설계

**신규 (v2.0):**
```sql
-- 객관식 통계
total_multiple_choice_count INT DEFAULT 0 COMMENT '총 객관식 문제 수',
total_multiple_choice_correct INT DEFAULT 0 COMMENT '객관식 정답 수',
multiple_choice_accuracy DECIMAL(5,2) DEFAULT 0.00 COMMENT '객관식 정답률 (%)',

-- 주관식 통계
total_subjective_count INT DEFAULT 0 COMMENT '총 주관식 문제 수',
total_subjective_score INT DEFAULT 0 COMMENT '주관식 총 점수',
subjective_average_score DECIMAL(5,2) DEFAULT 0.00 COMMENT '주관식 평균 점수',
```

### 🔧 비즈니스 로직 변경사항

#### 1. 세션 저장 프로세스 변경

**신규 (v2.0):**
```sql
-- 1. AUTO_INCREMENT로 세션 저장
INSERT INTO learning_sessions (...) VALUES (...);
SET @session_id = LAST_INSERT_ID();

-- 2. 생성된 session_id 사용
INSERT INTO session_quizzes (session_id, ...) VALUES (@session_id, ...);
```

#### 2. 통계 업데이트 로직 분리

**신규 (v2.0):**
```sql
-- 객관식 통계 업데이트
total_multiple_choice_count = total_multiple_choice_count + 1,
total_multiple_choice_correct = total_multiple_choice_correct + CASE WHEN ? = TRUE THEN 1 ELSE 0 END,
multiple_choice_accuracy = (total_multiple_choice_correct * 100.0) / total_multiple_choice_count,

-- 주관식 통계 업데이트 (별도 쿼리)
total_subjective_count = total_subjective_count + 1,
total_subjective_score = total_subjective_score + ?,
subjective_average_score = total_subjective_score / total_subjective_count,
```

---

## 🔧 3. State 설계 v2.0 업데이트 내용

### 🔄 TutorState 구조 개편

#### 퀴즈 관련 필드 완전 재설계

**기존 (v1.3):**
```python
current_question_type: str        # "multiple_choice": 객관식, "subjective": 주관식
current_question_number: int      # 문제 번호 (기본키)
current_question_content: str     # 현재 문제 내용
current_question_answer: str      # 사용자 답변
is_answer_correct: int            # 객관식: 1(정답)/0(오답), 주관식: 0~100(점수)
```

**신규 (v2.0):**
```python
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
```

#### 세션 관리 필드 수정

**기존:**
```python
session_decision_result: str  # "proceed": 다음 단계 진행, "retry": 현재 구간 재학습
current_session_count: int    # 현재 구간에서 학습 세션 횟수 (3회 제한)
```

**신규:**
```python
retry_decision_result: str  # "proceed": 다음 단계 진행, "retry": 현재 구간 재학습
current_session_count: int    # 현재 구간에서 학습 세션 횟수 (1회 제한)
```

#### 세션 ID 생성 방식 변경
**기존:** 복잡한 문자열 생성 (`user{id}_ch{chapter}_s{section}_{timestamp}`)  
**신규:** MySQL AUTO_INCREMENT 자동 생성

### 🎯 변경 사유 및 효과

1. **quiz_tools_chatgpt.py JSON 형식 연동**: ChatGPT에서 생성되는 퀴즈 JSON 구조와 State 필드 일대일 매핑
2. **평가 시스템 명확화**: `is_answer_correct` 통합 필드 → `multiple_answer_correct`(bool) + `subjective_answer_score`(int) 분리
3. **DB 연동 최적화**: `current_question_number` 삭제, 세션 ID 자동 생성으로 복잡한 로직 제거
4. **네이밍 일관성**: `current_` 접두사 제거, `session_decision_result` → `retry_decision_result` 명확한 의미 전달

---

## 🌐 4. API 설계 v2.0 업데이트 요약

### 🔄 주요 변경된 부분 (학습 진행 API)

#### 1.1 POST /learning/session/start (응답 구조 개편)

**변경 전 (v1.3):**
```json
{
  "session_id": "user123_ch2_session001_20250805_143052",
  "chapter_info": {...},
  "session_info": {...},
  "initial_message": "안녕하세요! 2챕터를 시작하겠습니다."
}
```

**변경 후 (v2.0):**
```json
{
  "session_info": {
    "chapter_number": 2,
    "section_number": 1,
    "chapter_title": "LLM이란 무엇인가",
    "estimated_duration": "15분"
  },
  "workflow_response": {
    "current_agent": "theory_educator",
    "session_progress_stage": "theory_completed",
    "ui_mode": "chat",
    "content": {
      "type": "theory",
      "title": "LLM(Large Language Model)이란?",
      "content": "...",
      "key_points": [...],
      "examples": [...]
    }
  }
}
```

**주요 변경점:**
- `session_id` 제거 (AUTO_INCREMENT로 내부 관리)
- `workflow_response` 필드 추가
- 세션 시작과 동시에 이론 설명 제공 (통합 워크플로우)

#### 1.2 POST /learning/session/message (통합 워크플로우)

**변경 후 (v2.0):**
```json
{
  "user_message": "다음 단계로 넘어가주세요",
  "message_type": "user"
}
```

**응답 구조 통합:**
```json
{
  "workflow_response": {
    "current_agent": "quiz_generator",
    "session_progress_stage": "theory_completed", 
    "ui_mode": "quiz",
    "content": {
      "type": "quiz",
      "quiz_type": "multiple_choice",
      "question": "다음 중 LLM의 특징이 아닌 것은?",
      "options": [...],
      "hint": "LLM의 'L'이 무엇을 의미하는지 생각해보세요."
    }
  }
}
```

**주요 변경점:**
- 모든 학습 진행이 하나의 엔드포인트로 통합
- `workflow_response`로 표준화된 응답 구조
- 에이전트 정보 및 UI 모드 실시간 제공

#### 1.3 POST /learning/quiz/submit (평가 시스템 개편)

**변경 후 (v2.0):**
```json
{
  "user_answer": "2"
}
```

**응답 구조 개편:**
```json
{
  "workflow_response": {
    "current_agent": "evaluation_feedback_agent",
    "session_progress_stage": "quiz_and_feedback_completed",
    "ui_mode": "chat",
    "evaluation_result": {
      "quiz_type": "multiple_choice",
      "is_answer_correct": true,
      "score": 100,
      "feedback": {
        "title": "정답입니다! 🎉",
        "content": "훌륭합니다...",
        "explanation": "...",
        "next_step_decision": "proceed"
      }
    }
  }
}
```

#### 1.4 POST /learning/session/complete (신규 추가)

**v2.0 신규 API:**
```json
// 요청
{
  "proceed_decision": "proceed"
}

// 응답
{
  "workflow_response": {
    "current_agent": "session_manager",
    "session_progress_stage": "session_start",
    "ui_mode": "chat",
    "session_completion": {
      "completed_chapter": 2,
      "completed_section": 1,
      "next_chapter": 2,
      "next_section": 2,
      "session_summary": "2챕터 1섹션을 성공적으로 완료했습니다.",
      "study_time_minutes": 15
    }
  }
}
```

### 📊 데이터 구조 변경사항

#### 2.1 퀴즈 관련 필드 분리

**변경 후:**
- `multiple_answer_correct`: 객관식 정답 여부 (boolean)
- `subjective_answer_score`: 주관식 점수 (0-100)

#### 2.2 통계 정보 구조 개선

**변경 후 추가:**
```json
{
  "multiple_choice_accuracy": 88.5,
  "subjective_average_score": 76.2
}
```

### 🚨 에러 코드 업데이트

#### 새로 추가된 에러 코드

**학습 세션 관련:**
- `WORKFLOW_EXECUTION_ERROR` (500): 워크플로우 실행 중 오류
- `INVALID_QUIZ_ANSWER` (400): 퀴즈 답변 형식 오류

**시스템 관련:**
- `LANGGRAPH_COMPILATION_ERROR` (500): 워크플로우 컴파일 오류

### 🎯 프론트엔드 연동 지원

#### 하이브리드 UX 지원

**UI 모드 전환:**
- `ui_mode`: "chat" (자유 대화) ↔ "quiz" (퀴즈 모드)

**에이전트 정보 제공:**
- `current_agent`: 현재 활성 에이전트
- `session_progress_stage`: 세션 진행 단계

**제공되는 컨텐츠 타입:**
- `theory`: 이론 설명
- `quiz`: 퀴즈 문제
- `feedback`: 평가 피드백
- `qna`: 질문 답변

---

## 🎨 5. UI 설계 v2.0 수정 내용

### 🔄 주요 변경사항

#### 1. 통합 워크플로우 기반 UI 시스템

**변경 (v2.0):**
- **단일 API**: `POST /learning/session/message`로 모든 상호작용 통합
- **SupervisorRouter 기반**: 사용자 의도에 따른 자동 에이전트 라우팅
- **통합 응답 구조**: `workflow_response` 필드로 에이전트 정보, UI 모드, 컨텐츠 통합 제공

#### 2. 하이브리드 UX 시스템 도입

**신규 추가:**
- **chat 모드**: 자유 대화 (이론 설명, 피드백, QnA 시)
- **quiz 모드**: 퀴즈 풀이 (객관식/주관식 통합)
- **자동 모드 전환**: 에이전트 응답에 따른 실시간 UI 모드 변경

**UI 모드 전환 흐름:**
```
session_start → chat (이론 설명)
theory_completed → quiz (퀴즈) OR chat (질문)
quiz_answer → chat (피드백)
quiz_and_feedback_completed → chat (세션 완료) OR chat (추가 질문)
```

#### 3. 에이전트별 UI 패턴 정의

**새로 추가된 에이전트별 UI 디자인:**

- **TheoryEducator**: 이론 설명 + 핵심 포인트 + 대표 예시 + 사용자 액션 가이드
- **QuizGenerator**: 문제 표시 + 선택지/입력창 + 힌트 버튼 + 제출 버튼
- **EvaluationFeedbackAgent**: 점수 표시 + 상세 피드백 + 다음 단계 결정 + 사용자 선택
- **QnAResolver**: 질문 표시 + 답변 + 관계도/시각화 + 관련 학습 연결
- **SessionManager**: 세션 결과 요약 + 다음 학습 안내 + 학습 기록 저장 확인

#### 4. 세션 진행 단계 시각화

**신규 컴포넌트**: `SessionProgressIndicator.vue`
- 4단계 진행 표시: 📖 이론 설명 → 📝 퀴즈 진행 → ✅ 완료 → ❓ 질문하기
- 활성/완료/비활성 상태 시각적 구분
- 연결선과 아이콘으로 직관적인 진행 상황 제공

#### 5. 상태 관리 시스템 v2.0

**Vue Pinia Store 확장:**
```javascript
// 신규 추가된 주요 상태
currentAgent: 현재 활성 에이전트
sessionProgressStage: 세션 진행 단계
userIntent: 사용자 의도
lastWorkflowResponse: 최근 워크플로우 응답
sessionInfo: 세션 관리 정보

// 신규 추가된 주요 액션
sendMessage(): 통합 메시지 전송
updateFromWorkflowResponse(): 워크플로우 응답 처리
submitQuizAnswer(): 퀴즈 답변 제출
startSession(): 세션 시작
completeSession(): 세션 완료

// 신규 추가된 게터
sessionSteps: 진행 단계 표시용 데이터
canAskQuestion: 질문 가능 여부
canProceedNext: 다음 단계 진행 가능 여부
```

#### 6. 컴포넌트 구조 재편

**새로 추가된 핵심 컴포넌트:**
- `SessionProgressIndicator.vue`: 진행 단계 시각화
- `InteractionArea.vue`: chat/quiz 모드 통합 상호작용 영역
- `MainContentArea.vue`: 에이전트별 동적 컨텐츠 표시
- `TheoryContent.vue`, `QuizContent.vue`, `FeedbackContent.vue` 등: 에이전트별 전용 컴포넌트

#### 7. 대시보드 페이지 개선

**변경:**
- **섹션별 진행 상태**: 챕터 내 섹션 단위 진행 표시
- **분리된 통계**: 객관식 정답률 / 주관식 평균 점수 분리 표시
- **연속 학습일**: 사용자 학습 습관 추적
- **상세 성과 정보**: 챕터별 평균 점수, 학습 시간 등

#### 8. 스타일링 시스템 강화

**에이전트별 테마 시스템:**
- 각 에이전트별 고유 색상 및 배경 테마
- 왼쪽 테두�� 색상으로 에이전트 구분
- 그라데이션 배경으로 시각적 차별화

**애니메이션 시스템:**
- 에이전트 전환 시 애니메이션 효과
- slideInLeft, slideInRight, fadeIn, bounceIn, zoomIn 등
- 부드러운 UI 전환으로 사용자 경험 향상

### 🗑️ 제거된 내용

#### 1. 모바일 관련 내용 전체 제거
- 반응형 디자인 섹션
- 모바일 우선 설계
- 태블릿/데스크톱 브레이크포인트
- 터치 친화적 UI 언급

#### 2. 기술적 구현 세부사항 제거
- 성능 최적화 전략 (API 캐싱, 가상 스크롤링 등)
- 개발자 도구 및 디버깅
- 테스트 전략
- 문서화 및 가이드

---

## 📋 마이그레이션 가이드

### 기존 프론트엔드 코드 수정 필요 사항

1. **세션 시작**: `session_id` 관리 제거
2. **메시지 전송**: `workflow_response` 구조로 응답 처리 변경
3. **퀴즈 제출**: 간소화된 요청 구조 적용
4. **UI 모드**: `ui_mode` 필드로 chat/quiz 전환 구현
5. **힌트 시스템**: 별도 API 호출 → 퀴즈 응답에서 직접 확인

### 백엔드 구현 필요 사항

1. **LangGraph 워크플로우** 통합
2. **SupervisorRouter** 기반 라우팅 시스템
3. **response_generator** 응답 생성 시스템
4. **SessionManager** 세션 완료 처리
5. **AUTO_INCREMENT** 기반 세션 ID 관리

### 데이터베이스 마이그레이션

1. **세션 ID 변경**: 기존 VARCHAR 세션 ID → INT AUTO_INCREMENT
2. **퀴즈 데이터 구조 변경**: 기존 단일 필드 → 타입별 분리 필드
3. **통계 데이터 재계산**: 기존 통합 통계 → 객관식/주관식 분리 통계

---

## 🎯 핵심 개선 효과

### 1. 사용자 경험 향상
- 일관된 워크플로우로 혼란 최소화
- 자동 UI 모드 전환으로 자연스러운 상호작용
- 진행 단계 시각화로 현재 위치 명확화

### 2. 개발 효율성 증대
- 단일 API로 복잡도 감소
- 통합된 상태 관리로 버그 최소화
- 컴포넌트 재사용성 향상

### 3. 확장성 확보
- 에이전트별 독립적인 UI 컴포넌트
- 새로운 에이전트 추가 시 기존 구조 재사용 가능
- 일관된 디자인 패턴으로 유지보수성 향상

### 4. 성능 개선
- AUTO_INCREMENT 도입으로 세션 ID 생성 오버헤드 제거
- 외래키 참조 성능 향상 (INT vs VARCHAR)
- JSON 컬럼 활용으로 배열 데이터 효율적 저장

### 5. 데이터 무결성 향상
- 객관식/주관식 성과 독립 추적
- 더 정확한 학습 분석 가능
- 제약 조건 강화로 데이터 품질 향상

---

## 📅 구현 단계

### Phase 1 (즉시 구현)
- `LearningPage.vue`: v2.0 통합 워크플로우 기반
- `InteractionArea.vue`: chat/quiz 모드 통합
- `MainContentArea.vue`: 에이전트별 동적 컨텐츠
- `SessionProgressIndicator.vue`: 진행 단계 시각화

### Phase 2 (단계별 구현)
- 에이전트별 컨텐츠 컴포넌트 개발
- `DashboardPage.vue` API 연동
- 스타일링 시스템 및 애니메이션 적용

### Phase 3 (고도화)
- 애니메이션 시스템 완성
- 상태 관리 최적화
- UI/UX 개선

---

## 🔄 호환성 유지

### 기존 시스템과의 연계
- 완성된 인증/진단 시스템은 그대로 유지
- 기존 API (`/auth/*`, `/diagnosis/*`) 호환성 보장
- authStore, diagnosisStore 등 기존 상태 관리 유지
- 라우터 가드 시스템 연동

### 점진적 마이그레이션
- 새로운 tutorStore 추가로 기존 시스템과 병행 운영
- 학습 관련 기능만 v2.0 시스템으로 전환
- 단계별 이주로 안정성 확보

---

## 📈 성능 및 모니터링 개선

### 응답 시간 목표 조정
- AI 워크플로우 API: < 5000ms (기존: < 2000ms)

### 로그 포맷 개선
```
[2025-08-17 14:30:52] INFO [user:123] POST /learning/session/message - Agent: theory_educator - Response: 2.1s
```

### 시스템 모니터링 강화
```json
{
  "services": {
    "langgraph": "compiled",
    "langsmith": "tracking"
  },
  "workflow_stats": {
    "total_executions": 150,
    "successful_executions": 145,
    "failed_executions": 5,
    "success_rate": 96.67
  }
}
```

---

*통합 업데이트 로그 버전: v2.0*  
*작성일: 2025.08.17*  
*주요 변경: 통합 워크플로우, 중앙집중식 라우팅, 하이브리드 UX 지원, 데이터 구조 개선*  
*문서 통합: PRD, DB 설계, State 설계, API 설계, UI 설계 v2.0 업데이트 내용 종합*