# Requirements Document

## Introduction

현재 프론트엔드에서 데미데이터로 구현된 LearningPage, MainContentArea, ChatInteraction, QuizInteraction 컴포넌트들을 실제 백엔드 API와 연동하여 완전한 학습 세션 시스템을 구현합니다. API docs v2.0의 학습 세션 API 4가지 엔드포인트(session/start, session/message, quiz/submit, session/complete)의 응답을 받아 페이지에 동적으로 표시하고 사용자 인터랙션을 처리하는 시스템을 구축합니다.

## Requirements

### Requirement 1

**User Story:** 학습자로서, 챕터를 선택하여 학습 세션을 시작할 때 실제 백엔드에서 이론 설명을 받아 화면에 표시되기를 원한다.

#### Acceptance Criteria

1. WHEN 사용자가 챕터를 선택하고 학습을 시작하면 THEN 시스템은 POST /learning/session/start API를 호출해야 한다
2. WHEN API 응답이 성공적으로 수신되면 THEN MainContentArea 컴포넌트는 theory_educator 에이전트의 이론 설명 콘텐츠를 표시해야 한다
3. WHEN 이론 설명이 표시되면 THEN ChatInteraction 컴포넌트는 chat 모드로 전환되어야 한다
4. IF API 호출이 실패하면 THEN 사용자에게 적절한 오류 메시지를 표시해야 한다

### Requirement 2

**User Story:** 학습자로서, 이론 학습 후 다음 단계로 진행할 때 실제 퀴즈 문제를 받아 풀 수 있기를 원한다.

#### Acceptance Criteria

1. WHEN 사용자가 "다음 단계" 또는 유사한 메시지를 전송하면 THEN 시스템은 POST /learning/session/message API를 호출해야 한다
2. WHEN API 응답에서 quiz_generator 에이전트가 반환되면 THEN QuizInteraction 컴포넌트는 quiz 모드로 전환되어야 한다
3. WHEN 퀴즈 데이터가 수신되면 THEN 객관식/주관식 문제 형태에 맞게 UI가 렌더링되어야 한다
4. WHEN 힌트가 제공되면 THEN 사용자가 힌트 버튼을 클릭할 수 있어야 한다

### Requirement 3

**User Story:** 학습자로서, 퀴즈 답변을 제출할 때 실제 평가 결과와 피드백을 받아 확인할 수 있기를 원한다.

#### Acceptance Criteria

1. WHEN 사용자가 퀴즈 답변을 제출하면 THEN 시스템은 POST /learning/quiz/submit API를 호출해야 한다
2. WHEN 평가 결과가 수신되면 THEN evaluation_feedback_agent의 피드백이 ChatInteraction 컴포넌트에 표시되어야 한다
3. WHEN 정답/오답 결과가 표시되면 THEN 점수와 설명이 함께 제공되어야 한다
4. WHEN 피드백이 완료되면 THEN 다음 단계 진행 여부를 결정할 수 있어야 한다

### Requirement 4

**User Story:** 학습자로서, 학습 중 궁금한 점이 있을 때 질문을 하고 실시간으로 답변을 받을 수 있기를 원한다.

#### Acceptance Criteria

1. WHEN 사용자가 질문을 입력하고 전송하면 THEN 시스템은 POST /learning/session/message API를 호출해야 한다
2. WHEN qna_resolver 에이전트가 응답하면 THEN 질문과 답변이 ChatInteraction 컴포넌트에 표시되어야 한다
3. WHEN Q&A 세션이 진행되면 THEN 기존 학습 진행 상태는 유지되어야 한다
4. WHEN 질문 답변이 완료되면 THEN 원래 학습 플로우로 복귀할 수 있어야 한다

### Requirement 5

**User Story:** 학습자로서, 한 세션을 완료할 때 학습 진도가 저장되고 다음 세션으로 자동 진행되기를 원한다.

#### Acceptance Criteria

1. WHEN 사용자가 세션 완료를 결정하면 THEN 시스템은 POST /learning/session/complete API를 호출해야 한다
2. WHEN 세션 완료 응답이 수신되면 THEN 학습 진도가 tutorStore에 업데이트되어야 한다
3. WHEN 다음 섹션이 있으면 THEN 자동으로 다음 학습 세션으로 진행되어야 한다
4. IF 챕터가 완료되면 THEN 대시보드로 리다이렉트되어야 한다

### Requirement 6

**User Story:** 개발자로서, API 연동 과정에서 발생하는 오류를 적절히 처리하여 사용자 경험을 보장하고 싶다.

#### Acceptance Criteria

1. WHEN API 호출이 실패하면 THEN 사용자에게 이해하기 쉬운 오류 메시지를 표시해야 한다
2. WHEN 네트워크 오류가 발생하면 THEN 재시도 옵션을 제공해야 한다
3. WHEN 토큰이 만료되면 THEN 자동으로 토큰 갱신을 시도해야 한다
4. WHEN 세션이 중단되면 THEN 마지막 상태를 복구할 수 있어야 한다

### Requirement 7

**User Story:** 개발자로서, 기존 컴포넌트 구조를 최대한 유지하면서 API 연동을 구현하고 싶다.

#### Acceptance Criteria

1. WHEN API 연동을 구현할 때 THEN 기존 LearningPage, MainContentArea, ChatInteraction, QuizInteraction 컴포넌트 구조는 유지되어야 한다
2. WHEN 데이터 흐름을 변경할 때 THEN 기존 Props/Emits 패턴은 보존되어야 한다
3. WHEN 새로운 서비스를 추가할 때 THEN learningService.js 파일을 통해 API 호출을 중앙화해야 한다
4. WHEN 상태 관리를 수정할 때 THEN tutorStore.js의 기존 구조를 확장하는 방식으로 구현해야 한다