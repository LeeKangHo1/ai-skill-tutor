# Implementation Plan

- [x] 1. learningService.js에 v2.0 API 메서드 추가

  - startLearningSession() 메서드 구현
  - sendSessionMessage() 메서드 구현  
  - submitQuizAnswerV2() 메서드 구현
  - 기존 learningService.js 구조 유지하면서 확장
  - _Requirements: 1.1, 4.1_

- [x] 2. MainContentArea.vue 백엔드 연동

  - 컴포넌트 마운트 시 learningService.startLearningSession() 호출
  - API 응답을 기존 더미데이터 구조로 직접 매핑
  - 에러 발생 시 더미데이터 fallback 처리
  - 에이전트 변경 시 동적 컨텐츠 로드 구현
  - **작업 완료 후 반드시 ComponentTest.vue로 동작 확인**
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 3. MainContentArea 연동 테스트

  - ComponentTest.vue에서 MainContentArea API 연동 검증
  - API 성공/실패 시나리오 테스트
  - 더미데이터 fallback 동작 확인
  - **MainContentArea 작업이 완전히 완료되었는지 최종 확인**
  - _Requirements: 1.4_

- [x] 3.1 MainContentArea 컴포넌트 분리

  - MainContentArea.vue를 3개의 하위 컴포넌트로 분리
  - TheoryContent.vue: 이론 설명 파트 담당
  - QuizContent.vue: 퀴즈 문제 파트 담당  
  - FeedbackContent.vue: 평가 및 피드백 파트 담당
  - 각 컴포넌트는 props를 통해 데이터 수신
  - MainContentArea는 상위 컨테이너 역할로 변경
  - 기존 API 연동 로직은 MainContentArea에서 유지
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 3.2 ComponentTest.vue 분리된 컴포넌트 테스트 추가
  - 새로 분리된 TheoryContent, QuizContent, FeedbackContent 컴포넌트 테스트 추가
  - 각 컴포넌트별 props 전달 및 렌더링 테스트
  - 분리된 컴포넌트들의 독립적인 동작 검증
  - MainContentArea 컨테이너의 하위 컴포넌트 관리 테스트
  - **컴포넌트 분리 작업 완료 후 전체 동작 확인**
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 4. QuizContent와 QuizInteraction 컴포넌트 역할 분리 및 백엔드 연동




  - **QuizContent.vue 수정**: 메인 컨텐츠 영역에서 문제 제목과 문제 내용만 표시
  - **QuizInteraction.vue 수정**: 객관식 선택지와 제출 버튼만 포함하도록 UI 분리
  - response에서 ui_mode가 'quiz'로 변경되는 경우 QuizContent에 문제 데이터 전달
  - 답안 제출 시 QuizInteraction에서 learningService.submitQuizAnswerV2() 호출
  - API 응답을 기존 퀴즈 데이터 구조로 직접 매핑
  - 에러 발생 시 더미데이터 fallback 처리
  - **작업 완료 후 반드시 ComponentTest.vue로 동작 확인**
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 5. QuizInteraction 연동 테스트
  - ComponentTest.vue에서 QuizInteraction API 연동 검증
  - 퀴즈 로드, 답안 제출, 평가 결과 수신 테스트
  - 더미데이터 fallback 동작 확인
  - **QuizInteraction 작업이 완전히 완료되었는지 최종 확인**
  - _Requirements: 2.4_

- [x] 6. ChatInteraction.vue 백엔드 연동





  - 메시지 전송 시 learningService.sendSessionMessage() 호출
  - AI 응답을 채팅 히스토리에 실시간 추가
  - 세션 시작 시 기존 대화 기록 로드 구현
  - 에러 발생 시 더미 응답 fallback 처리
  - **작업 완료 후 반드시 ComponentTest.vue로 동작 확인**
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 7. ChatInteraction 연동 테스트
  - ComponentTest.vue에서 ChatInteraction API 연동 검증
  - 메시지 전송, AI 응답 수신, 히스토리 로드 테스트
  - 더미데이터 fallback 동작 확인
  - **ChatInteraction 작업이 완전히 완료되었는지 최종 확인**
  - _Requirements: 3.4_

- [ ] 8. 통합 테스트 및 검증
  - 모든 컴포넌트의 API 연동 통합 테스트
  - 실제 백엔드와의 end-to-end 테스트
  - 에러 시나리오 및 fallback 동작 최종 검증
  - ComponentTest.vue를 통한 전체 시스템 검증
  - _Requirements: 1.4, 2.4, 3.4, 4.4_