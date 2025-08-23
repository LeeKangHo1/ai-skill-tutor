# 구현 계획

- [ ] 1. learningStore 생성 및 tutorStore 마이그레이션
  - tutorStore.js의 모든 내용을 learningStore.js로 이전
  - API 연동을 위한 추가 상태 및 액션 메서드 구현
  - 기존 컴포넌트에서 tutorStore 참조를 learningStore로 변경
  - tutorStore.js 파일 삭제
  - _요구사항: 1.4, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 2. learningService 클라이언트 메서드 구현
  - 기존 learningService.js에 startSession() 메서드 추가 (백엔드 POST /api/v1/learning/session/start 호출)
  - sendMessage() 메서드 추가 (백엔드 POST /api/v1/learning/session/message 호출)
  - submitQuizAnswer() 메서드 추가 (백엔드 POST /api/v1/learning/quiz/submit 호출)
  - completeSession() 메서드 추가 (백엔드 POST /api/v1/learning/session/complete 호출)
  - API 응답 데이터 파싱 및 오류 처리 로직 구현
  - _요구사항: 1.1, 2.1, 3.1, 4.1, 4.2, 6.1_

- [ ] 3. LearningPage 컴포넌트 API 연동
  - 세션 시작 로직 구현 (authStore에서 current_chapter/section 조회)
  - 라우터 파라미터 처리 및 세션 시작 API 호출
  - API 응답에 따른 learningStore 상태 업데이트
  - 로딩 상태 및 오류 처리 UI 추가
  - _요구사항: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 4. MainContentArea 컴포넌트 API 데이터 연동
  - API 응답 데이터 기반 컨텐츠 렌더링 로직 구현
  - 동적 컨텐츠 타입 처리 (theory, quiz, qna, feedback)
  - 에이전트별 테마 적용 로직 수정
  - 진행 상태 표시기 API 데이터 연동
  - _요구사항: 5.3, 5.4_

- [ ] 5. ChatInteraction 컴포넌트 메시지 전송 API 연동
  - 실제 메시지 전송 API 호출 로직 구현
  - 사용자 메시지 및 AI 응답 처리
  - 로딩 상태 표시 및 오류 처리
  - API 응답에 따른 UI 모드 전환 로직
  - _요구사항: 2.1, 2.2, 2.3, 2.5, 6.2_

- [ ] 6. QuizInteraction 컴포넌트 퀴즈 API 연동
  - 퀴즈 데이터 API 응답 기반 렌더링
  - 퀴즈 답변 제출 API 호출 구현
  - 평가 결과 표시 및 피드백 UI
  - 다음 단계 선택 옵션 (진행/재학습) 구현
  - _요구사항: 2.4, 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 7. 세션 완료 및 진행 관리 구현
  - 세션 완료 API 호출 로직 구현
  - "다음 학습 내용을 진행하시겠습니까? 아니면 대시보드로?" 선택 UI 구현
  - proceed/retry 결정에 따른 다음 액션 처리
  - 대시보드 라우팅 및 다음 세션 시작 로직
  - _요구사항: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 8. 실시간 UI 상태 동기화 구현
  - API 응답의 ui_mode에 따른 chat/quiz 모드 자동 전환
  - current_agent 변경에 따른 테마 적용
  - session_progress_stage 업데이트에 따른 진행 상태 반영
  - 세션 완료 시 completedSteps 업데이트
  - _요구사항: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 9. 학습 데이터 영속성 구현
  - learningStore에 API 응답 데이터 저장 로직 구현
  - 페이지 새로고침 시 store 데이터 기반 컨텐츠 복원
  - 브라우저 종료/로그아웃 시 정보 소실 안내 메시지 구현
  - 세션 상태 유지를 위한 localStorage 활용
  - _요구사항: 7.1, 7.2, 7.3, 7.4_

- [ ] 10. 오류 처리 및 사용자 경험 개선
  - API 오류별 구체적인 오류 메시지 표시 구현
  - 로딩 인디케이터 및 상태 표시 개선
  - 네트워크 오류 및 토큰 만료 처리
  - 사용자 친화적인 오류 메시지 및 복구 옵션 제공
  - _요구사항: 6.1, 6.2_

- [ ] 11. 컴포넌트 간 통합 테스트 및 검증
  - 전체 학습 플로우 통합 테스트 작성
  - 세션 시작부터 완료까지 전체 시나리오 검증
  - API 연동 상태에서 기존 기능 정상 동작 확인
  - 오류 상황별 처리 로직 테스트
  - _요구사항: 전체 요구사항 검증_