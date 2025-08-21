# Implementation Plan

- [ ] 1. 기본 구조 및 핵심 클래스 구현
  - backend/tests/0821/interactive_api_tester.py 파일 생성
  - 필요한 라이브러리 import 및 기본 설정 구성
  - HTTPClient, RequestBuilder, ResponseAnalyzer 핵심 클래스 구현
  - _Requirements: 1.1, 6.1, 5.1_

- [ ] 2. 사용자 입력 및 세션 관리 구현
  - InputHandler 클래스로 사용자 입력 처리 및 명령어 파싱 구현
  - SessionManager 클래스로 세션 상태 관리 및 컨텍스트 유지 구현
  - 특수 명령어(/quit, /state, /proceed, /retry) 처리 로직 작성
  - _Requirements: 1.1, 1.4, 3.1_

- [ ] 3. 출력 및 표시 기능 구현
  - OutputHandler 클래스로 터미널 출력 및 포맷팅 구현
  - API 응답, 퀴즈, 에러 메시지별 출력 메서드 작성
  - JSON 구조화 출력 및 컬러 표시 기능 구현
  - _Requirements: 1.3, 3.2, 4.3, 4.4_

- [ ] 4. 세션 시작 및 메시지 전송 기능 구현
  - 챕터/섹션 번호와 메시지 입력 받는 인터페이스 구현
  - POST /learning/session/start 요청 생성 및 전송 로직 작성
  - POST /learning/session/message 요청 처리 및 응답 분석 구현
  - _Requirements: 1.2, 2.1, 2.2_

- [ ] 5. 퀴즈 모드 및 답변 제출 기능 구현
  - ui_mode 기반 퀴즈/채팅 모드 전환 로직 구현
  - 퀴즈 컨텐츠 표시 및 답변 입력 인터페이스 작성
  - POST /learning/quiz/submit 요청 생성 및 결과 처리 구현
  - _Requirements: 2.1, 2.3_

- [ ] 6. 세션 완료 및 상태 디버깅 기능 구현
  - /proceed, /retry 명령어로 POST /learning/session/complete 요청 처리
  - /state 명령어로 TutorState 조회 및 출력 기능 구현
  - 세션 완료 응답 처리 및 상태 정리 로직 작성
  - _Requirements: 2.3, 3.1, 3.2, 3.3, 3.4_

- [ ] 7. 메인 애플리케이션 및 실행 루프 구현
  - InteractiveAPITester 메인 클래스 및 실행 루프 구현
  - 모든 컴포넌트 초기화 및 명령어별 처리 로직 작성
  - 예외 처리 및 graceful shutdown 로직 추가
  - _Requirements: 1.1, 1.4_

- [ ] 8. 에러 처리 및 연결 관리 구현
  - 네트워크 연결 오류 처리 및 재시도 안내 로직 구현
  - API 에러 응답 파싱 및 사용자 친화적 메시지 표시 구현
  - 백엔드 서버 연결 상태 확인 기능 작성
  - _Requirements: 4.3, 5.2, 5.3_

- [ ] 9. 실행 파일 완성 및 통합 테스트
  - if __name__ == "__main__" 블록으로 직접 실행 가능하게 구현
  - 전체 워크플로우 통합 및 기능 검증 테스트 수행
  - 가상환경에서 정상 동작 확인 및 최종 검증
  - _Requirements: 6.1_

- [ ] 10. README 문서 작성
  - backend/tests/0821/README.md 파일 작성
  - 설치 방법, 실행 방법, 사용 가능한 명령어 문서화
  - 사용 예시 및 트러블슈팅 가이드 작성
  - _Requirements: 4.1, 4.2_