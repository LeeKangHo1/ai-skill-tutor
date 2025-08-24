# Requirements Document

## Introduction

이 기능은 AI 활용법 학습 튜터 프로젝트의 퀴즈 생성 에이전트와 QnA 에이전트를 개선하여 벡터 DB 기반 시스템으로 전환하는 것입니다. 현재 퀴즈 에이전트는 JSON 파일 데이터를 직접 사용하고 있으며, QnA 에이전트는 임시 구현 상태입니다. 이론 생성 에이전트가 이미 벡터 DB 통합을 완료한 것을 참고하여 동일한 패턴으로 개선합니다.

## Requirements

### Requirement 1

**User Story:** 개발자로서, 퀴즈 생성 에이전트의 퀴즈 생성 로직만 수정하여 theory_draft를 우선 참고하고 chapters_metadata.json에서 메타데이터를 가져와 더 일관성 있는 퀴즈를 생성하기를 원합니다.

#### Acceptance Criteria

1. WHEN 퀴즈 생성 에이전트가 호출되면 THEN 시스템은 State의 theory_draft 내용을 우선적으로 참고해야 합니다
2. WHEN theory_draft가 존재하면 THEN 시스템은 해당 내용과 chapters_metadata.json의 챕터/섹션 제목을 결합하여 퀴즈를 생성해야 합니다
3. WHEN theory_draft가 없거나 부족하면 THEN 시스템은 기존 JSON 파일을 폴백 전략으로 사용해야 합니다
4. WHEN 퀴즈 생성이 완료되면 THEN 시스템은 생성된 퀴즈를 State에 올바르게 파싱하여 저장해야 합니다
5. WHEN 에이전트의 다른 기능들은 THEN 시스템은 기존 구조를 그대로 유지해야 합니다

### Requirement 2

**User Story:** 개발자로서, QnA 에이전트를 이론 생성 에이전트의 워크플로우를 참고하여 완전히 새로 구현하고, 벡터 DB 검색 기반 답변 생성 기능을 추가하기를 원합니다.

#### Acceptance Criteria

1. WHEN QnA 에이전트가 호출되면 THEN 시스템은 이론 생성 에이전트와 동일한 구조로 process() 메서드를 구현해야 합니다
2. WHEN 사용자 질문을 분석하면 THEN 시스템은 질문 내용에서 검색 쿼리를 추출해야 합니다
3. WHEN 검색 쿼리가 생성되면 THEN 시스템은 search_qna_materials() 함수를 사용하여 벡터 DB를 검색해야 합니다
4. WHEN 벡터 검색 결과가 존재하면 THEN 시스템은 검색된 자료를 참고하여 답변을 생성해야 합니다
5. WHEN 벡터 검색 결과가 없으면 THEN 시스템은 LLM의 일반 지식을 활용하여 답변을 생성해야 합니다
6. WHEN 답변 생성이 완료되면 THEN 시스템은 state_manager.update_agent_draft()로 qna_draft에 답변을 저장해야 합니다
7. WHEN State 업데이트가 필요하면 THEN 시스템은 update_agent_transition()과 add_conversation()을 순서대로 호출해야 합니다

### Requirement 3

**User Story:** 개발자로서, QnA 에이전트가 LangChain function calling을 활용하여 벡터 검색을 자동으로 수행하고 효율적인 답변을 생성하기를 원합니다.

#### Acceptance Criteria

1. WHEN QnA 도구를 구현하면 THEN 시스템은 벡터 검색 함수를 LangChain tool로 등록해야 합니다
2. WHEN 사용자 질문이 입력되면 THEN ChatGPT가 필요에 따라 자동으로 벡터 검색 tool을 function calling으로 호출해야 합니다
3. WHEN ChatGPT가 검색이 필요하다고 판단하면 THEN 시스템은 search_qna_materials() 함수를 자동 실행해야 합니다
4. WHEN 벡터 검색 결과가 반환되면 THEN ChatGPT가 해당 결과를 바탕으로 답변을 생성해야 합니다
5. WHEN 검색이 불필요하거나 결과가 없으면 THEN ChatGPT가 일반 지식으로 답변을 생성해야 합니다

### Requirement 4

**User Story:** 개발자로서, 두 에이전트의 개선된 기능이 기존 LangGraph 워크플로우와 완벽하게 호환되기를 원합니다.

#### Acceptance Criteria

1. WHEN 기존 API 엔드포인트에서 에이전트를 호출하면 THEN 시스템은 기존과 동일한 방식으로 동작해야 합니다
2. WHEN State 구조가 변경되면 THEN 시스템은 기존 State 필드와의 호환성을 유지해야 합니다
3. WHEN 에이전트 간 전환이 발생하면 THEN 시스템은 올바른 라우팅을 수행해야 합니다
4. WHEN 오류가 발생하면 THEN 시스템은 적절한 폴백 메커니즘을 제공해야 합니다
5. WHEN 성능 테스트를 수행하면 THEN 시스템은 기존 대비 응답 품질이 향상되어야 합니다