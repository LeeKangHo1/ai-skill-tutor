# 🤖 AI 튜터 터미널 테스터

백엔드 멀티에이전트 시스템을 터미널에서 테스트할 수 있는 개발자용 도구입니다.

## 📋 목차

- [개요](#개요)
- [설치 및 설정](#설치-및-설정)
- [실행 방법](#실행-방법)
- [명령어 가이드](#명령어-가이드)
- [사용 시나리오](#사용-시나리오)
- [문제 해결](#문제-해결)
- [파일 구조](#파일-구조)

## 📖 개요

이 터미널 테스터는 AI 활용법 학습 튜터의 백엔드 API를 직접 호출하여 다음을 테스트할 수 있습니다:

- **전체 학습 플로우**: 세션 시작 → 이론 설명 → 퀴즈 → 평가 → 완료
- **에이전트 라우팅**: 사용자 입력에 따른 적절한 에이전트 호출
- **토큰 인증**: JWT 기반 인증 및 자동 토큰 갱신
- **세션 연속성**: proceed/retry 결정에 따른 다음 세션 진행
- **API 응답**: 모든 API 응답을 Raw JSON으로 확인

## 🛠️ 설치 및 설정

### 1. 필수 요구사항

- **Python 3.7 이상**
- **백엔드 서버 실행 중** (`http://localhost:5000`)
- **DB에 테스트 사용자 존재** (진단 완료된 beginner 타입)

### 2. 의존성 설치

```bash
# 터미널 테스터 디렉토리로 이동
cd backend/tests/terminal_tester_by_claude

# 필수 라이브러리 설치
pip install requests PyJWT

# 또는 requirements.txt 생성 후 설치
echo "requests>=2.28.0
PyJWT>=2.4.0" > requirements.txt
pip install -r requirements.txt
```

### 3. 백엔드 서버 실행 확인

```bash
# 다른 터미널에서 백엔드 서버 실행
cd backend
python run.py

# 서버 상태 확인 (브라우저 또는 curl)
curl http://localhost:5000/api/v1/system/health
```

## 🚀 실행 방법

### 기본 실행

```bash
python main.py
```

### 대화형 설정과 함께 실행

```bash
python main.py --setup
```

### 도움말 확인

```bash
python main.py --help
```

## 📝 명령어 가이드

### 🔐 인증 관련

| 명령어 | 설명 | 사용법 |
|--------|------|--------|
| `login` | 사용자 로그인 | `login` |
| `logout` | 로그아웃 | `logout` |
| `auth` | 인증 상태 확인 | `auth` |

### 📚 학습 세션 관련

| 명령어 | 설명 | 사용법 |
|--------|------|--------|
| `start` | 학습 세션 시작 | `start <챕터> <섹션> [메시지]` |
| `msg` | 메시지 전송 | `msg "<메시지 내용>"` |
| `quiz` | 퀴즈 답변 제출 | `quiz "<답변>"` |
| `complete` | 세션 완료 | `complete <proceed\|retry>` |

### 🔍 상태 확인

| 명령어 | 설명 | 사용법 |
|--------|------|--------|
| `state` | TutorState 조회 | `state` |
| `status` | 현재 세션 상태 | `status` |
| `reset` | 세션 상태 초기화 | `reset` |

### 🌐 시스템

| 명령어 | 설명 | 사용법 |
|--------|------|--------|
| `health` | 서버 상태 확인 | `health` |
| `version` | 서버 버전 확인 | `version` |
| `help` | 명령어 도움말 | `help` |
| `clear` | 화면 지우기 | `clear` |

### 🚪 종료

| 명령어 | 설명 |
|--------|------|
| `quit` / `exit` / `q` | 프로그램 종료 |

## 🎯 사용 시나리오

### 시나리오 1: 기본 학습 플로우 테스트

```bash
# 1. 프로그램 실행
python main.py

# 2. 로그인
AI튜터> login
로그인 ID: test_user
비밀번호: ********
✅ 환영합니다, 테스트사용자님!

# 3. 1챕터 1섹션 세션 시작
AI튜터> start 1 1
✅ 1챕터 1섹션 세션이 시작되었습니다!
📡 세션 시작 응답
{
  "success": true,
  "data": {
    "workflow_response": {
      "current_agent": "theory_educator",
      "session_progress_stage": "theory_completed",
      "ui_mode": "chat",
      "content": {
        "type": "theory",
        "title": "AI는 무엇인가?",
        "content": "AI는 인간의 지능을 모방한 기술입니다..."
      }
    }
  }
}

# 4. 다음 단계 요청 (퀴즈 진행)
AI튜터> msg "다음 단계로 가주세요"
✅ 메시지가 처리되었습니다!
📡 메시지 응답
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
        "question": "다음 중 AI의 특징이 아닌 것은?",
        "options": ["대규모 데이터 학습", "실시간 인터넷 검색", "언어 이해 능력", "텍스트 생성 능력"],
        "hint": "LLM의 'L'이 무엇을 의미하는지 생각해보세요."
      }
    }
  }
}

# 5. 퀴즈 답변 제출
AI튜터> quiz "2"
✅ 답변이 제출되고 평가되었습니다!
📡 퀴즈 평가 응답
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
          "explanation": "실시간 인터넷 검색은 LLM의 기본 기능이 아닙니다.",
          "next_step_decision": "proceed"
        }
      }
    }
  }
}

# 6. 세션 완료 (다음 섹션으로 진행)
AI튜터> complete proceed
✅ 세션이 완료되었습니다!
📡 세션 완료 응답
{
  "success": true,
  "data": {
    "workflow_response": {
      "current_agent": "session_manager",
      "session_progress_stage": "session_start",
      "ui_mode": "chat",
      "session_completion": {
        "completed_chapter": 1,
        "completed_section": 1,
        "next_chapter": 1,
        "next_section": 2,
        "session_summary": "1챕터 1섹션을 성공적으로 완료했습니다.",
        "study_time_minutes": 15
      }
    }
  }
}

# 7. 다음 세션 시작
AI튜터> start 1 2
# ... 계속 진행 ...
```

### 시나리오 2: 질문 답변 테스트

```bash
# 이론 설명 완료 후
AI튜터> msg "AI와 머신러닝의 차이가 뭐예요?"
✅ 메시지가 처리되었습니다!
📡 메시지 응답
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
        "answer": "AI는 더 넓은 개념으로, 인간의 지능을 모방하는 모든 기술을 포함합니다..."
      }
    }
  }
}
```

### 시나리오 3: 재학습 시나리오

```bash
# 퀴즈에서 틀린 후
AI튜터> complete retry
✅ 세션이 완료되었습니다!
📡 세션 완료 응답
{
  "data": {
    "workflow_response": {
      "session_completion": {
        "completed_chapter": 1,
        "completed_section": 1,
        "next_chapter": 1,
        "next_section": 1,  # 동일한 섹션으로 재학습
        "session_summary": "1챕터 1섹션 재학습이 완료되었습니다."
      }
    }
  }
}

# 동일 섹션 재시작
AI튜터> start 1 1
```

## 🔧 문제 해결

### 자주 발생하는 문제들

#### 1. 서버 연결 실패

```
❌ 서버 연결 실패
```

**해결 방법:**
- 백엔드 서버가 실행 중인지 확인
- `http://localhost:5000/api/v1/system/health` 접속 테스트
- 방화벽이나 포트 충돌 확인

#### 2. 로그인 실패

```
❌ 로그인 실패
```

**해결 방법:**
- DB에 테스트 사용자가 존재하는지 확인
- 진단이 완료된 사용자인지 확인 (`diagnosis_completed=true`)
- 사용자 타입이 `beginner`인지 확인

#### 3. 토큰 만료

```
❌ 토큰이 만료되었습니다
```

**해결 방법:**
- 자동 갱신 실패 시 `logout` 후 다시 `login`
- `auth` 명령어로 토큰 상태 확인

#### 4. 세션 상태 오류

```
❌ 활성 세션이 없습니다
```

**해결 방법:**
- `status` 명령어로 현재 상태 확인
- `reset` 명령어로 세션 상태 초기화
- `start` 명령어로 새 세션 시작

### 디버깅 명령어

```bash
# 현재 상태 확인
AI튜터> status
AI튜터> auth
AI튜터> state

# 서버 상태 확인
AI튜터> health
AI튜터> version

# 초기화
AI튜터> reset
AI튜터> logout
```

## 📁 파일 구조

```
backend/tests/terminal_tester_by_claude/
├── main.py              # 메인 실행 파일
├── config.py           # 설정 및 상수
├── display_utils.py    # 터미널 출력 유틸리티
├── api_client.py       # HTTP 요청 및 API 호출
├── auth_manager.py     # JWT 인증 및 토큰 관리
├── command_handler.py  # 명령어 처리 및 비즈니스 로직
└── README.md          # 이 파일
```

### 주요 컴포넌트 역할

- **config.py**: API 엔드포인트, 메시지, 색상 등 모든 설정 관리
- **display_utils.py**: 컬러 출력, JSON 포맷팅, 사용자 입력 처리
- **api_client.py**: HTTP 요청, 자동 토큰 갱신, 에러 처리
- **auth_manager.py**: 로그인, 로그아웃, JWT 토큰 생명주기 관리
- **command_handler.py**: 각 명령어의 비즈니스 로직 및 세션 상태 추적
- **main.py**: 전체 시스템 초기화 및 메인 실행 루프

## 🎨 출력 예시

### 성공 메시지
```
✅ 환영합니다, 테스트사용자님!
ℹ️ 사용자 타입: beginner
✅ 진단이 완료된 사용자입니다. 학습 세션을 시작할 수 있습니다.
```

### API 응답
```
=======================================
📡 세션 시작 응답
---------------------------------------
{
  "success": true,
  "data": {
    "workflow_response": {
      "current_agent": "theory_educator",
      "session_progress_stage": "theory_completed",
      "ui_mode": "chat",
      "content": {
        "type": "theory",
        "title": "AI는 무엇인가?",
        "content": "AI는 인간의 지능을 모방한 기술입니다..."
      }
    }
  }
}
=======================================
```

### 다음 액션 가이드
```
----------------------------------------
💡 다음 액션 가이드:
ℹ️ 'msg "다음 단계로 가주세요"' 로 퀴즈를 요청하거나
ℹ️ 'msg "질문 내용"' 으로 궁금한 점을 물어보세요.
----------------------------------------
```

## 📞 지원

이 터미널 테스터 사용 중 문제가 발생하면:

1. **로그 확인**: 터미널 출력에서 상세한 에러 메시지 확인
2. **상태 체크**: `health`, `auth`, `status` 명령어로 현재 상태 파악
3. **초기화 시도**: `reset`, `logout` 후 다시 시작
4. **서버 재시작**: 백엔드 서버 재시작 후 다시 시도

---

**Happy Testing! 🚀**