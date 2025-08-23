# Requirements Document

## Introduction

현재 프론트엔드 학습 시스템(LearningPage, MainContentArea, ChatInteraction, QuizInteraction 컴포넌트)이 더미 데이터로 구현되어 있습니다. 이 기능을 실제 백엔드 API와 연동하여 완전한 학습 워크플로우를 구현해야 합니다. API 문서 v2.0에 정의된 4가지 핵심 학습 세션 API(start, message, submit, complete)와 프론트엔드 시스템을 완전히 통합하고, 필요한 store 파일들을 새로 생성하는 것이 목표입니다.

## Requirements

### Requirement 1

**User Story:** 개발자로서, 기존 더미 데이터 기반 학습 시스템을 실제 백엔드 API와 연동하기 위해 learningService.js를 완전히 개편하고 새로운 learningStore.js를 생성하고 싶습니다.

#### Acceptance Criteria

1. WHEN learningService.js를 수정하면 THEN 기존 시뮬레이션 기반 메서드들을 실제 axios HTTP 호출로 교체해야 합니다
2. WHEN API 호출 메서드를 구현하면 THEN startLearningSession, sendSessionMessage, submitQuizAnswer, completeSession 4가지 핵심 메서드를 포함해야 합니다
3. WHEN learningStore.js를 새로 생성하면 THEN sessionInfo, currentWorkflow, apiStatus, errorHandling 상태를 포함해야 합니다
4. WHEN learningStore 액션을 정의하면 THEN startSession, sendMessage, submitQuiz, completeSession 메서드를 구현해야 합니다
5. WHEN 기존 tutorStore와 연동하면 THEN 중복되는 상태는 제거하고 명확한 역할 분담을 해야 합니다
6. IF HTTP 요청을 구성하면 THEN JWT 토큰 인증, 요청 헤더 설정, 자동 토큰 갱신 로직을 포함해야 합니다

### Requirement 2

**User Story:** 사용자로서, 학습 세션의 전체 워크플로우(시작→메시지→퀴즈→완료)가 실제 백엔드 API와 연동되어 원활하게 동작하기를 원합니다.

#### Acceptance Criteria

1. WHEN 사용자가 특정 챕터/섹션 학습을 시작하면 THEN POST /learning/session/start API를 호출하고 세션 정보를 저장해야 합니다
2. WHEN 사용자가 채팅에서 메시지를 입력하면 THEN POST /learning/session/message API를 호출하고 workflow_response를 처리해야 합니다
3. WHEN 사용자가 퀴즈 답안을 제출하면 THEN POST /learning/quiz/submit API를 호출하고 evaluation_result를 표시해야 합니다
4. WHEN 세션 완료 조건이 충족되면 THEN POST /learning/session/complete API를 호출하고 진행 상황을 업데이트해야 합니다
5. WHEN workflow_response를 받으면 THEN current_agent와 ui_mode에 따라 적절한 UI 컴포넌트를 활성화해야 합니다
6. IF API 호출이 실패하면 THEN 적절한 오류 메시지를 반환하고 사용자에게 표시해야 합니다

### Requirement 3

**User Story:** 사용자로서, 학습 진행 중 실시간으로 변화하는 UI 상태와 컨텐츠를 명확하게 인지하고 원활한 사용자 경험을 얻고 싶습니다.

#### Acceptance Criteria

1. WHEN current_agent가 변경되면 THEN MainContentArea SHALL 에이전트별 테마 색상과 아이콘을 즉시 업데이트해야 합니다
2. WHEN ui_mode가 "quiz"로 변경되면 THEN QuizInteraction 컴포넌트를 활성화하고 "chat"이면 ChatInteraction을 활성화해야 합니다
3. WHEN theory 타입 컨텐츠를 받으면 THEN ChatInteraction에서 이론 설명을 채팅 형태로 표시해야 합니다
4. WHEN qna 타입 응답을 받으면 THEN ChatInteraction에서 질문-답변 형태로 컨텐츠를 표시해야 합니다
5. WHEN evaluation_result를 받으면 THEN QuizInteraction에서 정답/오답 표시와 함께 피드백을 ChatInteraction에 표시해야 합니다
6. WHEN 새로운 메시지가 추가되면 THEN ChatInteraction SHALL 자동으로 최신 메시지로 스크롤해야 합니다

