# 부록: API 설계 v1.3

## 1. 🏗️ API 전체 구조 개요

### 1.1 기술 스택
- **백엔드**: Python Flask
- **인증**: JWT (Access Token + Refresh Token)
- **데이터베이스**: MySQL 8.0 (PyMySQL)
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
      "current_chapter": 2
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
          { "value": "none", "text": "전혀 없음" },
          { "value": "occasional", "text": "가끔 사용" },
          { "value": "frequent", "text": "자주 사용" }
        ]
      },
      {
        "question_id": 2,
        "question_text": "주된 학습 목적은 무엇인가요?",
        "question_type": "single_choice",
        "options": [
          { "value": "curiosity", "text": "호기심" },
          { "value": "work_efficiency", "text": "업무 효율성" },
          { "value": "self_development", "text": "자기계발" }
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
    { "question_id": 1, "answer": "occasional" },
    { "question_id": 2, "answer": "work_efficiency" },
    { "question_id": 3, "answer": "document_work" },
    { "question_id": 4, "answer": "medium" },
    { "question_id": 5, "answer": "practical" }
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
    "recommended_chapters": 8,
    "estimated_duration": "15시간"
  },
  "message": "진단이 완료되었습니다."
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
      "total_chapters": 8,
      "completion_percentage": 25.0
    },
    "learning_statistics": {
      "total_study_time_minutes": 150,
      "total_study_sessions": 8,
      "total_completed_sessions": 6,
      "average_accuracy": 85.5,
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

## 5. 🤖 학습 세션 API

### 5.1 POST /learning/session/start (학습 세션 시작)

**요청:**
```json
{
  "chapter_number": 2
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "session_id": "user123_ch2_session001_20250805_143052",
    "chapter_info": {
      "chapter_number": 2,
      "chapter_title": "LLM이란 무엇인가",
      "estimated_duration": "15분"
    },
    "session_info": {
      "session_sequence": 1,
      "session_progress_stage": "session_start",
      "ui_mode": "chat"
    },
    "initial_message": "안녕하세요! 2챕터 'LLM이란 무엇인가'를 시작하겠습니다."
  },
  "message": "학습 세션이 시작되었습니다."
}
```

### 5.2 POST /learning/session/message (메시지 전송)

**요청:**
```json
{
  "session_id": "user123_ch2_session001_20250805_143052",
  "message": "LLM에 대해 설명해주세요",
  "message_type": "user"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "agent_response": {
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
    },
    "conversation_history": [
      {
        "message_sequence": 1,
        "agent_name": "user",
        "message_type": "user",
        "message_content": "LLM에 대해 설명해주세요",
        "timestamp": "2025-08-05T14:30:52Z"
      },
      {
        "message_sequence": 2,
        "agent_name": "theory_educator",
        "message_type": "system",
        "message_content": "LLM은 대규모 언어 모델로...",
        "timestamp": "2025-08-05T14:30:55Z"
      }
    ]
  },
  "message": "응답이 생성되었습니다."
}
```

### 5.3 POST /learning/quiz/submit (퀴즈 답변 제출)

**요청:**
```json
{
  "session_id": "user123_ch2_session001_20250805_143052",
  "question_number": 1,
  "question_type": "multiple_choice",
  "user_answer": "2"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "evaluation_result": {
      "is_answer_correct": 1,
      "score": 100,
      "feedback": {
        "type": "feedback",
        "title": "정답입니다! 🎉",
        "content": "훌륭합니다. LLM의 핵심 특징을 정확히 이해하고 계시네요.",
        "explanation": "LLM은 대규모 데이터를 학습하여 언어를 이해하고 생성하는 능력을 가지고 있습니다.",
        "additional_tips": [
          "다음 단계에서는 프롬프트 작성법에 대해 배워보겠습니다.",
          "LLM의 한계점도 함께 알아두시면 좋겠습니다."
        ]
      }
    },
    "session_info": {
      "session_progress_stage": "quiz_and_feedback_completed",
      "ui_mode": "chat"
    }
  },
  "message": "답변이 평가되었습니다."
}
```

### 5.4 POST /learning/quiz/hint (힌트 요청)

**요청:**
```json
{
  "session_id": "user123_ch2_session001_20250805_143052",
  "question_number": 1
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "hint": {
      "level": 1,
      "content": "LLM의 'L'이 무엇을 의미하는지 생각해보세요.",
      "remaining_hints": 2
    },
    "hint_usage_count": 1
  },
  "message": "힌트가 제공되었습니다."
}
```

### 5.5 GET /learning/session/status (세션 상태 조회)

**파라미터:** `session_id`

**응답:**
```json
{
  "success": true,
  "data": {
    "session_info": {
      "session_id": "user123_ch2_session001_20250805_143052",
      "chapter_number": 2,
      "session_sequence": 1,
      "session_progress_stage": "theory_completed",
      "ui_mode": "chat",
      "session_start_time": "2025-08-05T14:30:52Z"
    },
    "current_quiz": {
      "question_number": 1,
      "question_type": "multiple_choice",
      "question_content": "다음 중 LLM의 특징이 아닌 것은?",
      "options": [
        "대규모 데이터 학습",
        "실시간 인터넷 검색",
        "언어 이해 능력",
        "텍스트 생성 능력"
      ],
      "hint_usage_count": 0
    }
  }
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
        "session_id": "user123_ch2_session001_20250805_143052",
        "chapter_number": 2,
        "chapter_title": "LLM이란 무엇인가",
        "session_sequence": 1,
        "session_start_time": "2025-08-05T14:30:52Z",
        "session_end_time": "2025-08-05T14:45:30Z",
        "study_duration_minutes": 15,
        "session_decision_result": "proceed",
        "quiz_info": {
          "question_number": 1,
          "question_type": "multiple_choice",
          "is_answer_correct": 1,
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
      "average_accuracy": 82.5,
      "study_streak_days": 7
    },
    "chapter_progress": [
      {
        "chapter_number": 1,
        "chapter_title": "AI는 무엇인가?",
        "completion_status": "completed",
        "sessions_count": 3,
        "average_score": 90.0,
        "total_time_minutes": 45
      },
      {
        "chapter_number": 2,
        "chapter_title": "LLM이란 무엇인가",
        "completion_status": "in_progress",
        "sessions_count": 1,
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
      "session_id": "user123_ch2_session001_20250805_143052",
      "chapter_number": 2,
      "chapter_title": "LLM이란 무엇인가",
      "session_sequence": 1,
      "session_start_time": "2025-08-05T14:30:52Z",
      "session_end_time": "2025-08-05T14:45:30Z",
      "study_duration_minutes": 15,
      "session_decision_result": "proceed"
    },
    "conversations": [
      {
        "message_sequence": 1,
        "agent_name": "user",
        "message_type": "user",
        "message_content": "LLM에 대해 설명해주세요",
        "message_timestamp": "2025-08-05T14:30:52Z",
        "session_progress_stage": "session_start"
      },
      {
        "message_sequence": 2,
        "agent_name": "theory_educator",
        "message_type": "system",
        "message_content": "LLM은 대규모 언어 모델로...",
        "message_timestamp": "2025-08-05T14:30:55Z",
        "session_progress_stage": "theory_completed"
      }
    ],
    "quiz_info": {
      "question_number": 1,
      "question_type": "multiple_choice",
      "question_content": "다음 중 LLM의 특징이 아닌 것은?",
      "user_answer": "2",
      "is_answer_correct": 1,
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
    "timestamp": "2025-08-05T14:30:52Z",
    "services": {
      "database": "connected",
      "langchain": "active",
      "chromadb": "connected"
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
    "api_version": "1.3.0",
    "build_date": "2025-08-05",
    "python_version": "3.9.0",
    "framework": "Flask 2.3.0"
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

### 8.3 비즈니스 로직 에러

| 코드 | HTTP 상태 | 메시지 |
|------|-----------|--------|
| DIAGNOSIS_NOT_COMPLETED | 403 | 진단을 먼저 완료해주세요. |
| CHAPTER_ACCESS_DENIED | 403 | 해당 챕터에 접근할 수 없습니다. |
| SESSION_NOT_FOUND | 404 | 세션을 찾을 수 없습니다. |
| SESSION_ALREADY_COMPLETED | 409 | 이미 완료된 세션입니다. |

### 8.4 시스템 에러

| 코드 | HTTP 상태 | 메시지 |
|------|-----------|--------|
| DATABASE_ERROR | 500 | 데이터베이스 오류가 발생했습니다. |
| LANGCHAIN_ERROR | 500 | AI 처리 중 오류가 발생했습니다. |
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
| 학습 세션 API | < 2000ms |
| AI 처리 API | < 5000ms |

### 10.2 로깅 정책

**로그 레벨:**
- `ERROR`: 시스템 오류, 예외 상황
- `WARN`: 비정상적이지만 처리 가능한 상황
- `INFO`: 주요 비즈니스 로직 실행
- `DEBUG`: 상세 디버깅 정보

**로그 포맷:**
```
[2025-08-05 14:30:52] INFO [user:123] POST /learning/session/message - Response: 200ms
```

---

*API 설계 버전: v1.3*  
*최종 수정일: 2025.08.05*  
*연관 문서: AI 활용법 학습 튜터 PRD v1.3, DB 설계 v1.3, UI 설계 v1.3*