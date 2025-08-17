# API 설계 v2.0 업데이트 요약

## 📋 변경사항 개요

### ✅ 변경 없는 부분 (v1.3과 동일)
- **인증 시스템**: 회원가입, 로그인, 토큰 갱신, 로그아웃
- **사용자 진단**: 진단 문항 조회, 진단 결과 제출, 사용자 유형 선택
- **대시보드**: 대시보드 개요
- **학습 기록**: 학습 기록 조회, 상세 통계, 세션 상세 조회

### 🔄 주요 변경된 부분 (학습 진행 API)

---

## 1. 🤖 학습 세션 API 변경사항

### 1.1 POST /learning/session/start (응답 구조 개편)

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

### 1.2 POST /learning/session/message (통합 워크플로우)

**변경 전 (v1.3):**
```json
{
  "session_id": "user123_ch2_session001_20250805_143052",
  "message": "LLM에 대해 설명해주세요",
  "message_type": "user"
}
```

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

### 1.3 POST /learning/quiz/submit (평가 시스템 개편)

**변경 전 (v1.3):**
```json
{
  "session_id": "user123_ch2_session001_20250805_143052",
  "question_number": 1,
  "question_type": "multiple_choice", 
  "user_answer": "2"
}
```

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

**주요 변경점:**
- 세션 정보 제거 (내부 State에서 관리)
- 통합 평가 시스템으로 변경
- 객관식/주관식 분리된 평가 구조

### 1.4 POST /learning/session/complete (신규 추가)

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

### 1.5 제거된 API

**POST /learning/quiz/hint (힌트 요청) - 제거됨**
- 이유: 퀴즈 생성 시점에 힌트 포함하여 별도 API 불필요

---

## 2. 📊 데이터 구조 변경사항

### 2.1 퀴즈 관련 필드 분리

**변경 전:**
- `is_answer_correct`: 통합 정답 여부

**변경 후:**
- `multiple_answer_correct`: 객관식 정답 여부 (boolean)
- `subjective_answer_score`: 주관식 점수 (0-100)

### 2.2 통계 정보 구조 개선

**변경 후 추가:**
```json
{
  "multiple_choice_accuracy": 88.5,
  "subjective_average_score": 76.2
}
```

### 2.3 세션 관리 구조 변경

**변경 전:**
- `session_decision_result`: proceed/retry

**변경 후:**
- `retry_decision_result`: proceed/retry (DB 필드명과 일치)

---

## 3. 🔧 시스템 API 업데이트

### 3.1 GET /system/health (모니터링 강화)

**추가된 정보:**
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

### 3.2 GET /system/version (AI 스택 정보 추가)

**추가된 정보:**
```json
{
  "ai_stack": {
    "langchain": "0.3.27",
    "langgraph": "0.6.3", 
    "langsmith": "0.4.13"
  }
}
```

---

## 4. 🚨 에러 코드 업데이트

### 4.1 새로 추가된 에러 코드

**학습 세션 관련:**
- `WORKFLOW_EXECUTION_ERROR` (500): 워크플로우 실행 중 오류
- `INVALID_QUIZ_ANSWER` (400): 퀴즈 답변 형식 오류

**시스템 관련:**
- `LANGGRAPH_COMPILATION_ERROR` (500): 워크플로우 컴파일 오류

---

## 5. 📈 성능 및 모니터링 개선

### 5.1 응답 시간 목표 조정

**변경된 목표:**
- AI 워크플로우 API: < 5000ms (기존: < 2000ms)

### 5.2 로그 포맷 개선

**추가된 정보:**
```
[2025-08-17 14:30:52] INFO [user:123] POST /learning/session/message - Agent: theory_educator - Response: 2.1s
```

---

## 6. 🎯 프론트엔드 연동 지원

### 6.1 하이브리드 UX 지원

**UI 모드 전환:**
- `ui_mode`: "chat" (자유 대화) ↔ "quiz" (퀴즈 모드)

**에이전트 정보 제공:**
- `current_agent`: 현재 활성 에이전트
- `session_progress_stage`: 세션 진행 단계

### 6.2 컨텐츠 타입 표준화

**제공되는 컨텐츠 타입:**
- `theory`: 이론 설명
- `quiz`: 퀴즈 문제
- `feedback`: 평가 피드백
- `qna`: 질문 답변

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

---

*업데이트 요약 버전: v2.0*  
*작성일: 2025.08.17*  
*주요 변경: 통합 워크플로우, 중앙집중식 라우팅, 하이브리드 UX 지원*