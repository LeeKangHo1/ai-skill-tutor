# Requirements Document

## Introduction

AI Skill Tutor 백엔드의 멀티에이전트 시스템을 터미널 환경에서 직접 테스트할 수 있는 대화형 테스트 도구입니다. 이 도구는 프론트엔드 없이도 백엔드 API 엔드포인트들을 순차적으로 호출하여 전체 학습 플로우를 체험할 수 있게 해줍니다.

## Requirements

### Requirement 1

**User Story:** 개발자로서, 터미널에서 백엔드 서버를 시작하고 학습 세션을 초기화할 수 있기를 원한다. 그래야 프론트엔드 개발 없이도 백엔드 로직을 검증할 수 있다.

#### Acceptance Criteria

1. WHEN 테스트 스크립트를 실행하면 THEN 시스템은 Flask 백엔드 서버를 자동으로 시작해야 한다
2. WHEN 서버가 시작되면 THEN 시스템은 LangGraph 워크플로우를 자동으로 구축해야 한다
3. WHEN 서버 준비가 완료되면 THEN 시스템은 "백엔드 서버가 실행되었습니다" 메시지를 출력해야 한다
4. WHEN 서버가 준비되면 THEN 시스템은 사용자에게 챕터 번호 입력을 요청해야 한다
5. WHEN 챕터 번호를 입력하면 THEN 시스템은 섹션 번호 입력을 요청해야 한다

### Requirement 2

**User Story:** 개발자로서, 입력한 챕터와 섹션 정보로 학습 세션을 시작할 수 있기를 원한다. 그래야 특정 학습 콘텐츠에 대한 테스트를 수행할 수 있다.

#### Acceptance Criteria

1. WHEN 챕터와 섹션 번호를 입력하면 THEN 시스템은 POST /learning/session/start 엔드포인트를 호출해야 한다
2. WHEN 세션 시작 요청을 보낼 때 THEN 요청 본문은 {"chapter_number": N, "section_number": M, "user_message": "N챕터 시작할게요"} 형태여야 한다
3. WHEN 세션이 시작되면 THEN 시스템은 user_type을 "beginner"로 고정해야 한다
4. WHEN 이론 설명이 생성되면 THEN 시스템은 터미널에 생성된 이론 내용을 출력해야 한다
5. WHEN 이론 출력이 완료되면 THEN 시스템은 "다음 메시지를 입력하세요:" 안내를 표시해야 한다

### Requirement 3

**User Story:** 개발자로서, 터미널에서 메시지를 입력하여 AI 에이전트와 상호작용할 수 있기를 원한다. 그래야 실제 사용자 경험과 유사한 테스트를 수행할 수 있다.

#### Acceptance Criteria

1. WHEN 사용자가 일반 메시지를 입력하면 THEN 시스템은 POST /learning/session/message 엔드포인트를 호출해야 한다
2. WHEN 메시지 요청을 보낼 때 THEN 요청 본문은 {"user_message": "입력메시지", "message_type": "user"} 형태여야 한다
3. WHEN AI 응답을 받으면 THEN 시스템은 응답 내용을 터미널에 출력해야 한다
4. WHEN 퀴즈가 생성되면 THEN 시스템은 퀴즈 내용을 출력하고 답변 입력을 요청해야 한다
5. WHEN 응답 출력이 완료되면 THEN 시스템은 다음 입력을 기다려야 한다

### Requirement 4

**User Story:** 개발자로서, 퀴즈 답변을 제출하고 평가 결과를 확인할 수 있기를 원한다. 그래야 평가 에이전트의 동작을 검증할 수 있다.

#### Acceptance Criteria

1. WHEN 퀴즈 상태에서 답변을 입력하면 THEN 시스템은 POST /learning/quiz/submit 엔드포인트를 호출해야 한다
2. WHEN 퀴즈 답변 요청을 보낼 때 THEN 요청 본문은 {"user_answer": "답변내용"} 형태여야 한다
3. WHEN 평가가 완료되면 THEN 시스템은 평가 결과와 피드백을 터미널에 출력해야 한다
4. WHEN 평가 결과가 출력되면 THEN 시스템은 proceed/retry 결정을 위한 안내를 표시해야 한다
5. IF 평가 점수가 기준 미달이면 THEN 시스템은 재학습을 권장하는 메시지를 출력해야 한다

### Requirement 5

**User Story:** 개발자로서, 특정 패턴의 명령어로 세션을 완료하고 다음 단계로 진행할 수 있기를 원한다. 그래야 전체 학습 플로우의 연속성을 테스트할 수 있다.

#### Acceptance Criteria

1. WHEN "/retry" 또는 "/proceed" 패턴의 메시지를 입력하면 THEN 시스템은 POST /learning/session/complete 엔드포인트를 호출해야 한다
2. WHEN 세션 완료 요청을 보낼 때 THEN 요청 본문은 {"proceed_decision": "retry" 또는 "proceed"} 형태여야 한다
3. WHEN proceed 결정이면 THEN 시스템은 다음 섹션으로 자동 진행해야 한다
4. WHEN retry 결정이면 THEN 시스템은 현재 섹션을 다시 시작해야 한다
5. WHEN 세션이 완료되면 THEN 시스템은 학습 기록이 DB에 저장되었음을 확인하는 메시지를 출력해야 한다

### Requirement 6

**User Story:** 개발자로서, 테스트 중 발생하는 오류와 API 응답을 상세히 확인할 수 있기를 원한다. 그래야 디버깅과 문제 해결을 효율적으로 수행할 수 있다.

#### Acceptance Criteria

1. WHEN API 요청을 보낼 때 THEN 시스템은 요청 URL과 본문을 터미널에 로깅해야 한다
2. WHEN API 응답을 받을 때 THEN 시스템은 응답 상태 코드와 본문을 터미널에 로깅해야 한다
3. WHEN 오류가 발생하면 THEN 시스템은 상세한 오류 메시지와 스택 트레이스를 출력해야 한다
4. WHEN JWT 토큰이 필요하면 THEN 시스템은 테스트용 토큰을 자동으로 생성하고 사용해야 한다
5. WHEN 테스트가 종료되면 THEN 시스템은 백엔드 서버를 자동으로 종료해야 한다

### Requirement 7

**User Story:** 개발자로서, 테스트 진행 중 현재 TutorState의 상태를 실시간으로 확인할 수 있기를 원한다. 그래야 에이전트 간 상태 전환과 데이터 흐름을 정확히 모니터링할 수 있다.

#### Acceptance Criteria

1. WHEN "/state" 명령어를 입력하면 THEN 시스템은 현재 활성화된 TutorState의 모든 내용을 출력해야 한다
2. WHEN 상태를 출력할 때 THEN 시스템은 session_progress_stage, current_agent, ui_mode를 포함한 모든 필드를 표시해야 한다
3. WHEN 테스트 진행 중 THEN 시스템은 session_progress_stage, current_agent, ui_mode 내용을 항상 확인 가능하게 해야 한다
4. WHEN 상태가 변경될 때마다 THEN 시스템은 변경된 필드를 하이라이트하여 표시해야 한다
5. WHEN 상태 출력 후 THEN 시스템은 일반 입력 모드로 돌아가야 한다

### Requirement 8

**User Story:** 개발자로서, 테스트 실행 중 언제든지 안전하게 종료할 수 있기를 원한다. 그래야 테스트 중단 시에도 리소스가 정리된다.

#### Acceptance Criteria

1. WHEN Ctrl+C를 입력하면 THEN 시스템은 현재 세션을 안전하게 종료해야 한다
2. WHEN 종료 신호를 받으면 THEN 시스템은 백엔드 서버 프로세스를 정리해야 한다
3. WHEN "/quit" 또는 "/exit" 명령을 입력하면 THEN 시스템은 정상적으로 종료해야 한다
4. WHEN 종료 시 THEN 시스템은 "테스트가 종료되었습니다" 메시지를 출력해야 한다
5. WHEN 예상치 못한 오류로 종료되면 THEN 시스템은 오류 로그를 파일에 저장해야 한다