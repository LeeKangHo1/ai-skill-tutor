# Requirements Document

## Introduction

백엔드 API 개발 과정에서 실시간으로 API 엔드포인트를 테스트하고 디버깅할 수 있는 대화형 터미널 테스터 도구입니다. 개발자가 터미널에서 직접 사용자 입력을 받아 적절한 API 요청으로 변환하여 로컬 백엔드 서버에 전송하고, 응답을 확인할 수 있는 기능을 제공합니다. 특히 AI 학습 세션 API의 복잡한 워크플로우를 효율적으로 테스트할 수 있도록 설계됩니다.

## Requirements

### Requirement 1

**User Story:** 개발자로서, 터미널에서 대화형으로 API를 테스트할 수 있는 도구를 사용하여, 백엔드 개발 과정에서 빠르게 API 동작을 확인하고 디버깅할 수 있다.

#### Acceptance Criteria

1. WHEN 개발자가 테스트 파일을 실행하면 THEN 시스템은 대화형 터미널 인터페이스를 시작해야 한다
2. WHEN 개발자가 챕터 번호, 섹션 번호, 메시지를 입력하면 THEN 시스템은 POST /learning/session/start 요청을 생성하여 전송해야 한다
3. WHEN 시스템이 API 응답을 받으면 THEN 응답 내용을 읽기 쉬운 형태로 터미널에 출력해야 한다
4. WHEN 개발자가 "/quit" 명령을 입력하면 THEN 시스템은 테스트 세션을 종료해야 한다

### Requirement 2

**User Story:** 개발자로서, AI 학습 세션의 다양한 상호작용 패턴을 자동으로 처리하는 테스터를 사용하여, 복잡한 워크플로우를 효율적으로 테스트할 수 있다.

#### Acceptance Criteria

1. WHEN API 응답의 ui_mode가 "quiz"이고 content.type이 "quiz"이면 THEN 시스템은 사용자 입력을 {"user_answer": "답변"} 형태로 POST /learning/quiz/submit 요청으로 변환해야 한다
2. WHEN 개발자가 일반 메시지를 입력하면 THEN 시스템은 POST /learning/session/message 요청으로 변환해야 한다
3. WHEN 개발자가 "/proceed" 또는 "/retry" 명령을 입력하면 THEN 시스템은 POST /learning/session/complete 요청을 생성해야 한다

### Requirement 3

**User Story:** 개발자로서, 현재 세션의 상태 정보를 실시간으로 확인할 수 있는 디버깅 기능을 사용하여, API 동작을 정확히 파악하고 문제를 해결할 수 있다.

#### Acceptance Criteria

1. WHEN 개발자가 "/state" 명령을 입력하면 THEN 시스템은 현재 활성화된 TutorState의 모든 정보를 조회하여 출력해야 한다
2. WHEN 상태 정보를 출력할 때 THEN 시스템은 JSON 형태로 구조화된 데이터를 읽기 쉽게 포맷팅해야 한다
3. WHEN 상태 조회 요청이 실패하면 THEN 시스템은 오류 메시지를 명확히 표시해야 한다
4. WHEN 상태 정보가 없으면 THEN 시스템은 "활성 세션이 없습니다" 메시지를 출력해야 한다

### Requirement 4

**User Story:** 개발자로서, README 문서를 통해 테스터 도구의 사용법을 쉽게 이해하고, 필요한 정보를 빠르게 얻을 수 있다.

#### Acceptance Criteria

1. WHEN README 파일을 확인하면 THEN 시스템은 설치 방법과 실행 방법을 명시해야 한다
2. WHEN README 파일을 확인하면 THEN 시스템은 사용 가능한 명령어와 사용 예시를 제공해야 한다
3. WHEN API 요청이 실패하면 THEN 시스템은 오류 상태 코드와 메시지를 명확히 표시해야 한다
4. WHEN 각 요청을 전송할 때 THEN 시스템은 요청 URL과 메서드를 표시하여 어떤 API가 호출되는지 알려야 한다

### Requirement 5

**User Story:** 개발자로서, 로컬 백엔드 서버와 안정적으로 통신하는 테스터를 사용하여, 네트워크 연결 문제 없이 API 테스트를 수행할 수 있다.

#### Acceptance Criteria

1. WHEN 테스터가 시작되면 THEN 시스템은 기본 Base URL을 http://localhost:5000/api/v1로 설정해야 한다
2. WHEN 백엔드 서버가 응답하지 않으면 THEN 시스템은 연결 오류 메시지를 표시하고 재시도 안내를 제공해야 한다
3. WHEN HTTP 요청을 전송할 때 THEN 시스템은 적절한 Content-Type 헤더를 설정해야 한다
4. WHEN JWT 토큰이 필요한 요청의 경우 THEN 시스템은 토큰 입력을 요청하거나 기본 테스트 토큰을 사용해야 한다

### Requirement 6

**User Story:** 개발자로서, 테스트 파일이 지정된 위치에 생성되어, 프로젝트 구조를 유지하면서 효율적으로 테스트할 수 있다.

#### Acceptance Criteria

1. WHEN 테스트 파일을 생성할 때 THEN 시스템은 backend/tests/0821 폴더에 파일을 생성해야 한다