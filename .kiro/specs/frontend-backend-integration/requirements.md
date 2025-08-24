# Requirements Document

## Introduction

더미데이터로 구현된 프론트엔드 컴포넌트들을 백엔드 API와 연동합니다. MainContentArea → QuizInteraction → ChatInteraction 순서로 파일별 작업하며, 각 파일 완료 후 ComponentTest.vue로 검증합니다. 성능 최적화나 복잡한 기능은 제외하고 기본 동작만 구현합니다.

## Requirements

### Requirement 1

**User Story:** 개발자로서 MainContentArea.vue를 백엔드 API와 연동하고 싶습니다. 그래야 실제 학습 컨텐츠를 표시할 수 있습니다.

#### Acceptance Criteria

1. WHEN MainContentArea가 마운트될 때 THEN 백엔드에서 학습 컨텐츠를 가져와야 합니다
2. WHEN API 응답을 받을 때 THEN 기존 더미데이터 구조와 동일하게 바인딩해야 합니다
3. WHEN API 요청이 실패할 때 THEN 더미데이터로 fallback해야 합니다
4. WHEN 작업 완료 후 THEN ComponentTest.vue에서 정상 동작을 확인해야 합니다

### Requirement 2

**User Story:** 개발자로서 QuizInteraction.vue를 백엔드 API와 연동하고 싶습니다. 그래야 실제 퀴즈 데이터를 사용할 수 있습니다.

#### Acceptance Criteria

1. WHEN 퀴즈 모드가 활성화될 때 THEN 백엔드에서 퀴즈 데이터를 가져와야 합니다
2. WHEN 답안을 제출할 때 THEN 백엔드로 전송하고 결과를 받아야 합니다
3. WHEN API 요청이 실패할 때 THEN 더미데이터로 fallback해야 합니다
4. WHEN 작업 완료 후 THEN ComponentTest.vue에서 정상 동작을 확인해야 합니다

### Requirement 3

**User Story:** 개발자로서 ChatInteraction.vue를 백엔드 API와 연동하고 싶습니다. 그래야 실제 AI 에이전트와 대화할 수 있습니다.

#### Acceptance Criteria

1. WHEN 메시지를 전송할 때 THEN 백엔드 AI 에이전트로 전송해야 합니다
2. WHEN AI 응답을 받을 때 THEN 채팅 히스토리에 추가해야 합니다
3. WHEN API 요청이 실패할 때 THEN 더미 응답으로 fallback해야 합니다
4. WHEN 작업 완료 후 THEN ComponentTest.vue에서 정상 동작을 확인해야 합니다

### Requirement 4

**User Story:** 개발자로서 기존 컴포넌트 구조를 유지하면서 API 연동을 구현하고 싶습니다. 그래야 기존 코드를 최대한 보존할 수 있습니다.

#### Acceptance Criteria

1. WHEN API 연동을 구현할 때 THEN 기존 props/emits 구조를 유지해야 합니다
2. WHEN 데이터를 바인딩할 때 THEN 기존 UI 디자인을 변경하지 않아야 합니다
3. WHEN 에러가 발생할 때 THEN 더미데이터로 fallback해야 합니다
4. WHEN 각 파일 작업 후 THEN ComponentTest.vue로 검증해야 합니다