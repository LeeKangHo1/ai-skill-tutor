# 부록: API 설계 v2.0

## 1. 🏗️ API 전체 구조 개요

### 1.1 기술 스택
- **백엔드**: Python Flask
- **인증**: JWT (Access Token + Refresh Token)
- **데이터베이스**: MySQL 8.0 (PyMySQL)
- **AI 시스템**: LangChain + LangGraph + LangSmith
- **응답 형식**: JSON

### 1.2 Base URL 및 공통 헤더

```
Base URL: http://localhost:5000/api/v1
Content-Type: application/json
Authorization: Bearer {access_token}
```

### 1.3 응답 형식 통일

**성공 응답:**
```json
{
  "success": true,
  "data": { /* 실제 데이터 */ },
  "message": "요청이 성공적으로 처리되었습니다."
}
```

**실패 응답:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 올바르지 않습니다.",
    "details": { /* 상세 오류 정보 */ }
  }
}
```

---

## 2. 👤 인증/사용자 관리 API

### 2.1 POST /auth/register (회원가입)

**요청:**
```json
{
  "login_id": "user123",
  "username": "홍길동",
  "email": "user@example.com",
  "password": "password123"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "login_id": "user123",
    "username": "홍길동",
    "user_type": "unassigned",
    "diagnosis_completed": false
  },
  "message": "회원가입이 완료되었습니다."
}
```

**에러 응답:**
```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_LOGIN_ID",
    "message": "이미 사용 중인 로그인 ID입니다."
  }
}
```

### 2.2 POST /auth/login (로그인)

**요청:**
```json
{
  "login_id": "user123",
  "password": "password123"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user_info": {
      "user_id": 1,
      "login_id": "user123",
      "username": "홍길동",
      "user_type": "beginner",
      "diagnosis_completed": true,
      "current_chapter": 2,
      "current_section": 1
    }
  },
  "message": "로그인이 완료되었습니다."
}
```

### 2.3 POST /auth/refresh (토큰 갱신)

**요청:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "토큰이 갱신되었습니다."
}
```

### 2.4 POST /auth/logout (로그아웃)

**헤더:** `Authorization: Bearer {access_token}`

**응답:**
```json
{
  "success": true,
  "message": "로그아웃이 완료되었습니다."
}
```

---

## 3. 🧭 사용자 진단 API

### 3.1 GET /diagnosis/questions (진단 문항 조회)

**응답:**
```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "question_id": 1,
        "question_text": "AI 도구(ChatGPT, Bard 등) 사용 경험이 있나요?",
        "question_type": "single_choice",
        "options": [
          { "value": "option_1", "text": "전혀 없음" },
          { "value": "option_2", "text": "가끔 사용" },
          { "value": "option_3", "text": "자주 사용" }
        ]
      },
      {
        "question_id": 2,
        "question_text": "주된 학습 목적은 무엇인가요?",
        "question_type": "single_choice",
        "options": [
          { "value": "option_1", "text": "호기심" },
          { "value": "option_2", "text": "업무 효율성" },
          { "value": "option_3", "text": "자기계발" }
        ]
      }
    ],
    "total_questions": 5
  }
}
```

### 3.2 POST /diagnosis/submit (진단 결과 제출)

**요청:**
```json
{
  "answers": [
    { "question_id": 1, "answer": "option_2" },
    { "question_id": 2, "answer": "option_2" },
    { "question_id": 3, "answer": "option_1" },
    { "question_id": 4, "answer": "option_3" },
    { "question_id": 5, "answer": "option_1" }
  ]
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "user_type": "beginner",
    "user_type_description": "AI 입문자",
    "total_score": 85,
    "recommendation": "AI 입문자가 적합합니다",
    "recommended_chapters": 8,
    "estimated_duration": "15시간"
  },
  "message": "진단이 완료되었습니다."
}
```

### 3.3 POST /diagnosis/select-type (사용자 유형 선택)

**요청:**
```json
{
  "user_type": "beginner"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "user_type": "beginner",
    "user_type_description": "AI 입문자",
    "diagnosis_completed": true,
    "redirect_url": "/dashboard"
  },
  "message": "사용자 유형이 설정되었습니다."
}
```

---

## 4. 📊 대시보드 API

### 4.1 GET /dashboard/overview (대시보드 개요)

**응답:**
```json
{
  "success": true,
  "data": {
    "user_progress": {
      "current_chapter": 2,
      "current_section": 1,
      "total_chapters": 8,
      "completion_percentage": 25.0
    },
    "learning_statistics": {
      "total_study_time_minutes": 150,
      "total_study_sessions": 8,
      "total_completed_sessions": 6,
      "multiple_choice_accuracy": 85.5,
      "subjective_average_score": 78.2,
      "last_study_date": "2025-08-05"
    },
    "chapter_status": [
      {
        "chapter_number": 1,
        "chapter_title": "AI는 무엇인가?",
        "status": "completed",
        "completion_date": "2025-08-04"
      },
      {
        "chapter_number": 2,
        "chapter_title": "LLM이란 무엇인가",
        "status": "in_progress",
        "completion_date": null
      },
      {
        "chapter_number": 3,
        "chapter_title": "프롬프트란 무엇인가",
        "status": "locked",
        "completion_date": null
      }
    ]
  }
}
```

---

## 5. 🤖 학습 세션 API (v2.0 업데이트)

### 5.1 POST /learning/session/start (학습 세션 시작)

**요청:**
```json
{
  "chapter_number": 2,
  "section_number": 1,
  "user_message": "2챕터 시작할게요"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
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
        "content": "LLM은 대규모 언어 모델로, 방대한 텍스트 데이터를 학습하여 인간과 유사한 언어 이해와 생성 능력을 가진 AI 모델입니다...",
        "key_points": [
          "대규모 데이터 학습",
          "언어 이해 및 생성",
          "문맥 파악 능력"
        ],
        "examples": [
          "ChatGPT (OpenAI)",
          "Claude (Anthropic)",
          "Bard (Google)"
        ]
      }
    }
  },
  "message": "학습 세션이 시작되었습니다."
}
```

### 5.2 POST /learning/session/message (메시지 전송) - v2.0 통합 워크플로우

**요청:**
```json
{
  "user_message": "다음 단계로 넘어가주세요",
  "message_type": "user"
}
```

**응답 1: 퀴즈 생성**
```json
{
  "success": true,
  "data": {
    "workflow_response": {
      "current_agent": "quiz_generator",
      "session_progress_stage": "theory_completed",
      "ui_mode": "quiz",
      "content": {
        "type": "quiz",
        "quiz_type": "multiple_choice",
        "question": "다음 중 LLM의 특징이 아닌 것은?",
        "options": [
          "대규모 데이터 학습",
          "실시간 인터넷 검색",
          "언어 이해 능력",
          "텍스트 생성 능력"
        ],
        "hint": "LLM의 'L'이 무엇을 의미하는지 생각해보세요."
      }
    }
  },
  "message": "퀴즈가 준비되었습니다."
}
```

**응답 2: 질문 답변**
```json
{
  "success": true,
  "data": {
    "workflow_response": {
      "current_agent": "qna_resolver",
      "session_progress_stage": "theory_completed",
      "ui_mode": "chat",
      "content": {
        "type": "qna",
        "question": "AI와 머신러닝의 차이가 뭐예요?",
        "answer": "AI는 더 넓은 개념으로, 인간의 지능을 모방하는 모든 기술을 포함합니다. 머신러닝은 AI의 한 분야로, 데이터를 통해 학습하는 방법론입니다..."
      }
    }
  },
  "message": "질문에 대한 답변입니다."
}
```

### 5.3 POST /learning/quiz/submit (퀴즈 답변 제출) - v2.0 통합

**요청:**
```json
{
  "user_answer": "2"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "workflow_response": {
      "current_agent": "evaluation_feedback_agent",
      "session_progress_stage": "quiz_and_feedback_completed",
      "ui_mode": "chat",
      "evaluation_result": {
        "quiz_type": "multiple_choice",
        "is_answer_correct": true,
        "score": 100,
        "feedback": {
          "type": "feedback",
          "title": "정답입니다! 🎉",
          "content": "훌륭합니다. LLM의 핵심 특징을 정확히 이해하고 계시네요.",
          "explanation": "실시간 인터넷 검색은 LLM의 기본 기능이 아닙니다. LLM은 학습된 데이터를 바탕으로 응답을 생성합니다.",
          "next_step_decision": "proceed"
        }
      }
    }
  },
  "message": "답변이 평가되었습니다."
}
```

### 5.4 POST /learning/session/complete (세션 완료) - v2.0 신규

**요청:**
```json
{
  "proceed_decision": "proceed"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
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
  },
  "message": "세션이 완료되었습니다."
}
```

---

## 6. 📈 학습 기록 및 통계 API

### 6.1 GET /learning/history (학습 기록 조회)

**파라미터:**
- `page`: 페이지 번호 (기본값: 1)
- `limit`: 페이지당 개수 (기본값: 10)
- `chapter`: 특정 챕터 필터 (선택사항)

**응답:**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": 12,
        "chapter_number": 2,
        "section_number": 1,
        "chapter_title": "LLM이란 무엇인가",
        "session_start_time": "2025-08-05T14:30:52Z",
        "session_end_time": "2025-08-05T14:45:30Z",
        "study_duration_minutes": 15,
        "retry_decision_result": "proceed",
        "quiz_info": {
          "quiz_type": "multiple_choice",
          "multiple_answer_correct": true,
          "subjective_answer_score": null,
          "hint_usage_count": 0
        }
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_sessions": 25,
      "limit": 10
    }
  }
}
```

### 6.2 GET /learning/statistics (상세 통계)

**응답:**
```json
{
  "success": true,
  "data": {
    "overall_stats": {
      "total_study_time_minutes": 450,
      "total_study_sessions": 25,
      "total_completed_sessions": 20,
      "study_streak_days": 7
    },
    "chapter_progress": [
      {
        "chapter_number": 1,
        "chapter_title": "AI는 무엇인가?",
        "completion_status": "completed",
        "sections_count": 4,
        "completed_sections": 4,
        "average_score": 90.0,
        "total_time_minutes": 60
      },
      {
        "chapter_number": 2,
        "chapter_title": "LLM이란 무엇인가",
        "completion_status": "in_progress",
        "sections_count": 4,
        "completed_sections": 1,
        "average_score": 85.0,
        "total_time_minutes": 15
      }
    ],
    "quiz_performance": {
      "multiple_choice_accuracy": 88.5,
      "subjective_average_score": 76.2,
      "total_hints_used": 12
    },
    "recent_activity": [
      {
        "date": "2025-08-05",
        "sessions_count": 2,
        "study_time_minutes": 30
      },
      {
        "date": "2025-08-04",
        "sessions_count": 3,
        "study_time_minutes": 45
      }
    ]
  }
}
```

### 6.3 GET /learning/session/{session_id}/details (세션 상세 조회)

**응답:**
```json
{
  "success": true,
  "data": {
    "session_info": {
      "session_id": 12,
      "chapter_number": 2,
      "section_number": 1,
      "chapter_title": "LLM이란 무엇인가",
      "session_start_time": "2025-08-05T14:30:52Z",
      "session_end_time": "2025-08-05T14:45:30Z",
      "study_duration_minutes": 15,
      "retry_decision_result": "proceed"
    },
    "conversations": [
      {
        "conversation_id": 1,
        "message_sequence": 1,
        "agent_name": "user",
        "message_type": "user",
        "message_content": "2챕터 시작할게요",
        "message_timestamp": "2025-08-05T14:30:52Z",
        "session_progress_stage": "session_start"
      },
      {
        "conversation_id": 2,
        "message_sequence": 2,
        "agent_name": "theory_educator",
        "message_type": "system",
        "message_content": "LLM은 대규모 언어 모델로...",
        "message_timestamp": "2025-08-05T14:30:55Z",
        "session_progress_stage": "theory_completed"
      }
    ],
    "quiz_info": {
      "quiz_type": "multiple_choice",
      "quiz_content": "다음 중 LLM의 특징이 아닌 것은?",
      "quiz_options": ["대규모 데이터 학습", "실시간 인터넷 검색", "언어 이해 능력", "텍스트 생성 능력"],
      "quiz_correct_answer": 2,
      "user_answer": "2",
      "multiple_answer_correct": true,
      "evaluation_feedback": "정답입니다! 훌륭합니다...",
      "hint_usage_count": 0
    }
  }
}
```

---

## 7. 🔧 시스템 관리 API

### 7.1 GET /system/health (헬스 체크)

**응답:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-08-17T14:30:52Z",
    "services": {
      "database": "connected",
      "langchain": "active",
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
}
```

### 7.2 GET /system/version (버전 정보)

**응답:**
```json
{
  "success": true,
  "data": {
    "api_version": "2.0.0",
    "build_date": "2025-08-17",
    "python_version": "3.9.0",
    "framework": "Flask 2.3.0",
    "ai_stack": {
      "langchain": "0.3.27",
      "langgraph": "0.6.3",
      "langsmith": "0.4.13"
    }
  }
}
```

---

## 8. 🚨 에러 코드 정의

### 8.1 인증 관련 에러

| 코드 | HTTP 상태 | 메시지 |
|------|-----------|--------|
| AUTH_INVALID_CREDENTIALS | 401 | 로그인 정보가 올바르지 않습니다. |
| AUTH_TOKEN_EXPIRED | 401 | 토큰이 만료되었습니다. |
| AUTH_TOKEN_INVALID | 401 | 유효하지 않은 토큰입니다. |
| AUTH_REFRESH_TOKEN_EXPIRED | 401 | 리프레시 토큰이 만료되었습니다. |

### 8.2 검증 관련 에러

| 코드 | HTTP 상태 | 메시지 |
|------|-----------|--------|
| VALIDATION_ERROR | 400 | 입력값이 올바르지 않습니다. |
| DUPLICATE_LOGIN_ID | 409 | 이미 사용 중인 로그인 ID입니다. |
| DUPLICATE_EMAIL | 409 | 이미 사용 중인 이메일입니다. |
| PASSWORD_TOO_WEAK | 400 | 비밀번호가 너무 약합니다. |

### 8.3 진단 관련 에러

| 코드 | HTTP 상태 | 메시지 |
|------|-----------|--------|
| DIAGNOSIS_NOT_COMPLETED | 403 | 진단을 먼저 완료해주세요. |
| INVALID_USER_TYPE | 400 | 유효하지 않은 사용자 유형입니다. |
| DIAGNOSIS_ALREADY_COMPLETED | 409 | 이미 진단을 완료했습니다. |

### 8.4 학습 세션 관련 에러

| 코드 | HTTP 상태 | 메시지 |
|------|-----------|--------|
| CHAPTER_ACCESS_DENIED | 403 | 해당 챕터에 접근할 수 없습니다. |
| SESSION_NOT_FOUND | 404 | 세션을 찾을 수 없습니다. |
| WORKFLOW_EXECUTION_ERROR | 500 | 워크플로우 실행 중 오류가 발생했습니다. |
| INVALID_QUIZ_ANSWER | 400 | 퀴즈 답변 형식이 올바르지 않습니다. |

### 8.5 시스템 에러

| 코드 | HTTP 상태 | 메시지 |
|------|-----------|--------|
| DATABASE_ERROR | 500 | 데이터베이스 오류가 발생했습니다. |
| LANGCHAIN_ERROR | 500 | AI 처리 중 오류가 발생했습니다. |
| LANGGRAPH_COMPILATION_ERROR | 500 | 워크플로우 컴파일 오류가 발생했습니다. |
| EXTERNAL_API_ERROR | 503 | 외부 서비스 연결에 실패했습니다. |

---

## 9. 🔐 보안 및 인증

### 9.1 JWT 토큰 구조

**Access Token (1시간 만료):**
```json
{
  "user_id": 123,
  "login_id": "user123",
  "user_type": "beginner",
  "exp": 1691234567,
  "iat": 1691230967
}
```

**Refresh Token (30일 만료):**
```json
{
  "user_id": 123,
  "token_type": "refresh",
  "exp": 1693826567,
  "iat": 1691234567
}
```

### 9.2 API 보안 정책

- **CORS**: 허용된 도메인만 접근 가능
- **Rate Limiting**: 분당 60회 요청 제한
- **Input Validation**: 모든 입력값 검증
- **SQL Injection 방지**: 파라미터화된 쿼리 사용
- **XSS 방지**: 출력 데이터 이스케이프 처리

---

## 10. 📊 API 성능 및 모니터링

### 10.1 응답 시간 목표

| API 유형 | 목표 응답 시간 |
|----------|---------------|
| 인증 API | < 200ms |
| 조회 API | < 500ms |
| 학습 세션 API | < 3000ms |
| AI 워크플로우 API | < 5000ms |

### 10.2 로깅 정책

**로그 레벨:**
- `ERROR`: 시스템 오류, 예외 상황
- `WARN`: 비정상적이지만 처리 가능한 상황
- `INFO`: 주요 비즈니스 로직 실행
- `DEBUG`: 상세 디버깅 정보

**로그 포맷:**
```
[2025-08-17 14:30:52] INFO [user:123] POST /learning/session/message - Agent: theory_educator - Response: 2.1s
```

---

## 📋 v2.0 주요 변경사항

### 🆕 새로 추가된 API
- **POST /learning/session/complete**: 세션 완료 처리 API 추가
- **통합 워크플로우**: 모든 학습 진행이 하나의 `/session/message` 엔드포인트로 통합

### 🔧 수정된 API 응답 형식
- **POST /learning/session/message**: LangGraph 워크플로우 통합으로 응답 구조 개편
- **모든 학습 API**: `workflow_response` 필드로 에이전트 정보 및 UI 모드 통합 제공
- **퀴즈 관련**: 객관식/주관식 통합 구조로 변경

### 🚀 성능 최적화
- **라우팅 시스템**: SupervisorRouter 기반 중앙집중식 라우팅
- **응답 생성**: response_generator를 통한 일관된 사용자 친화적 응답
- **세션 관리**: AUTO_INCREMENT 기반 세션 ID 관리로 성능 향상

### ✅ 구현 완료된 API
- GET /diagnosis/questions (진단 문항 조회)
- POST /diagnosis/submit (진단 결과 제출)  
- POST /diagnosis/select-type (사용자 유형 선택)
- POST /learning/session/start (학습 세션 시작)
- POST /learning/session/message (통합 메시지 처리)
- POST /learning/quiz/submit (퀴즈 답변 제출)
- POST /learning/session/complete (세션 완료)
- GET /system/health (헬스 체크)
- GET /system/version (버전 정보)

### 🔄 프론트엔드 연동 준비
- **하이브리드 UX**: `ui_mode` 필드로 chat/quiz 모드 전환 지원
- **실시간 UI 업데이트**: 에이전트별 응답에 따른 동적 UI 변경 지원
- **상태 관리**: TutorState와 Vue Pinia store 간 동기화 구조 완성

---

*API 설계 버전: v1.3 → v2.0*  
*최종 수정일: 2025.08.17*  
*연관 문서: AI 활용법 학습 튜터 PRD v2.0, DB 설계 v2.0, LangGraph State 설계 v2.0*