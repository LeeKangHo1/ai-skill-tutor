# 이론 생성 스트리밍 개선 요구사항

## 소개

현재 이론 생성은 10-15초의 긴 대기 시간으로 인해 사용자 경험이 저하되고 있습니다. JSON 형식 출력의 특성상 단어 단위 스트리밍은 어렵지만, JSON 블록 단위로 순차적 스트리밍을 구현하여 TTFT(Time to First Token)를 대폭 개선하고자 합니다.

## 요구사항

### Requirement 1: 이론 생성 스트리밍 시스템

**User Story:** 사용자로서, 학습 세션을 시작할 때 이론 설명이 블록 단위로 실시간 스트리밍되어 빠르게 내용을 확인하고 싶습니다.

#### Acceptance Criteria

1. WHEN 사용자가 학습 세션을 시작하면 THEN 시스템은 이론 생성을 스트리밍 방식으로 처리해야 합니다
2. WHEN 이론 생성이 시작되면 THEN 첫 번째 JSON 블록(chapter_info, title)이 3초 이내에 화면에 표시되어야 합니다
3. WHEN JSON 블록이 생성되면 THEN 각 블록(introduction, definition, examples)이 순차적으로 스트리밍되어야 합니다
4. WHEN 스트리밍이 진행되면 THEN 사용자는 이미 생성된 블록을 즉시 읽을 수 있어야 합니다
5. WHEN 스트리밍이 완료되면 THEN 기존 워크플로우와 동일하게 다음 단계(퀴즈 생성)로 진행되어야 합니다

### Requirement 2: JSON 블록 단위 스트리밍 구조

**User Story:** 개발자로서, JSON 구조를 유지하면서도 블록 단위로 스트리밍할 수 있는 시스템을 구현하고 싶습니다.

#### Acceptance Criteria

1. WHEN 이론 생성이 시작되면 THEN 시스템은 JSON을 다음 블록으로 분할해야 합니다:
   - Block 1: `chapter_info`, `title`
   - Block 2: `sections[0]` (introduction)
   - Block 3: `sections[1]` (definition + analogy)
   - Block 4: `sections[2]` (examples)
2. WHEN 각 블록이 생성되면 THEN 완전한 JSON 구조로 클라이언트에 전송되어야 합니다
3. WHEN 블록이 수신되면 THEN 프론트엔드는 기존 UI 컴포넌트를 재사용하여 렌더링해야 합니다
4. WHEN 모든 블록이 완성되면 THEN 최종 완전한 JSON이 State에 저장되어야 합니다

### Requirement 3: 기존 시스템과의 호환성

**User Story:** 시스템 관리자로서, 새로운 스트리밍 기능이 기존 워크플로우를 방해하지 않고 통합되기를 원합니다.

#### Acceptance Criteria

1. WHEN 스트리밍 기능이 활성화되면 THEN 기존 LangGraph 워크플로우와 완전히 호환되어야 합니다
2. WHEN 스트리밍이 실패하면 THEN 기존 동기 방식으로 자동 폴백되어야 합니다
3. WHEN 스트리밍이 완료되면 THEN TutorState가 기존과 동일한 구조로 업데이트되어야 합니다
4. WHEN 다음 단계로 진행하면 THEN 퀴즈 생성 등 후속 프로세스가 정상 작동해야 합니다

### Requirement 4: 사용자 경험 개선

**User Story:** 사용자로서, 이론 생성 과정을 시각적으로 확인하고 진행 상황을 알고 싶습니다.

#### Acceptance Criteria

1. WHEN 스트리밍이 시작되면 THEN 진행 상황을 나타내는 UI가 표시되어야 합니다
2. WHEN 각 블록이 생성되면 THEN 해당 블록이 하이라이트되거나 애니메이션 효과가 적용되어야 합니다
3. WHEN 스트리밍 중 오류가 발생하면 THEN 사용자에게 명확한 오류 메시지가 표시되어야 합니다
4. WHEN 스트리밍이 완료되면 THEN 사용자가 다음 단계로 진행할 수 있는 버튼이 활성화되어야 합니다