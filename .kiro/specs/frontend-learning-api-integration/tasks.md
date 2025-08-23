# Implementation Plan

- [x] 1. learningStore.js 새로 생성하여 학습 세션 전용 상태 관리 구현





  - Pinia store 기본 구조 생성 (sessionState, apiState, workflowState, errorState)
  - 4가지 핵심 액션 메서드 구현 (startSession, sendMessage, submitQuiz, completeSession)
  - 에러 처리 및 상태 초기화 메서드 구현
  - _Requirements: 1.3, 1.4_

- [x] 2. learningService.js 완전 개편하여 실제 HTTP API 호출 구조로 변경





  - 기존 더미 데이터 기반 메서드들을 실제 axios HTTP 호출로 교체
  - 4가지 핵심 API 메서드 구현 (startLearningSession, sendSessionMessage, submitQuizAnswer, completeSession)
  - JWT 토큰 인증, 요청 헤더 설정, 자동 토큰 갱신 로직 구현
  - 공통 HTTP 요청 처리 및 에러 분류 로직 구현
  - _Requirements: 1.1, 1.2, 1.6_

- [x] 3. tutorStore.js 리팩토링하여 UI 상태 관리에 집중하도록 정리





  - API 관련 상태를 learningStore로 이관하고 중복 제거
  - UI 상태 관리 액션들 유지 및 learningStore와의 연동 로직 구현
  - 명확한 역할 분담을 위한 상태 구조 정리
  - _Requirements: 1.5_

- [x] 4. LearningPage.vue에서 learningStore와 tutorStore 연동 구현






  - 두 store를 모두 import하고 적절한 역할 분담으로 사용
  - 세션 시작 시 learningStore.startSession 호출 및 결과를 tutorStore에 반영
  - API 응답의 workflow_response를 tutorStore.updateWorkflowResponse로 처리
  - _Requirements: 2.1, 2.5_

- [x] 5. ChatInteraction.vue에서 메시지 전송 API 연동 구현





  - 사용자 메시지 입력 시 learningStore.sendMessage 호출
  - API 응답에 따른 채팅 히스토리 업데이트 및 UI 상태 반영
  - qna 타입 응답을 질문-답변 형태로 표시하는 로직 구현
  - _Requirements: 2.2, 3.4_

- [x] 6. QuizInteraction.vue에서 퀴즈 제출 API 연동 구현





  - 퀴즈 답안 제출 시 learningStore.submitQuiz 호출
  - evaluation_result에 따른 정답/오답 표시 및 피드백 처리
  - 퀴즈 완료 후 ChatInteraction으로 피드백 메시지 전달
  - _Requirements: 2.3, 3.5_

- [x] 7. MainContentArea.vue에서 실시간 UI 상태 반영 구현










  - current_agent 변경에 따른 에이전트별 테마 색상과 아이콘 업데이트
  - ui_mode 전환에 따른 ChatInteraction/QuizInteraction 컴포넌트 활성화
  - session_progress_stage 업데이트에 따른 진행률 표시기 실시간 반영
  - _Requirements: 3.1, 3.2, 3.6_

- [x] 8. 세션 완료 처리 및 다음 단계 안내 기능 구현





  - 세션 완료 조건 충족 시 learningStore.completeSession 호출
  - session_completion 데이터를 통한 진행 상황 업데이트
  - 다음 학습 단계 안내 및 대시보드/계속하기 옵션 제공
  - _Requirements: 2.4_

- [x] 9. API 오류 처리 및 사용자 친화적 메시지 표시 구현





  - 네트워크 오류, 인증 오류, 서버 오류에 대한 적절한 오류 메시지 반환
  - learningService에서 에러 분류 및 기본값 대체 로직 구현
  - 사용자에게 오류 상황을 명확히 알리는 UI 구현
  - _Requirements: 2.6_

- [x] 10. ComponentTest.vue 파일 수정하여 실제 API 연동 테스트 지원





  - 기존 시뮬레이션 기반 테스트를 실제 learningStore 및 API 호출 기반으로 변경
  - learningStore와 tutorStore 연동 상태를 실시간으로 모니터링하는 기능 추가
  - API 호출 성공/실패 상황을 테스트할 수 있는 시나리오 추가
  - 실제 백엔드 연동 후 테스트 검증을 위한 디버깅 도구 기능 구현
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 11. 통합 테스트 및 전체 워크플로우 검증





  - 세션 시작부터 완료까지 전체 학습 워크플로우 테스트
  - 에이전트 전환, UI 모드 변경, 컨텐츠 표시가 올바르게 동작하는지 검증
  - API 연동 후 ComponentTest.vue를 통한 실제 시나리오 테스트
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3_