# Implementation Plan

- [ ] 1. JWT 토큰 관리 시스템 구현
  - JWT 토큰 생성 및 검증 함수 구현 (jwt_manager.py)
  - Access Token (1시간), Refresh Token (30일) 생성 함수 구현
  - 토큰 유효성 검증 및 오류 처리 구현
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 2. 인증 서비스 로직 구현
  - 사용자 회원가입 처리 함수 구현 (auth_service.py)
  - 로그인 인증 및 토큰 발급 함수 구현
  - 토큰 갱신 및 로그아웃 처리 함수 구현
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4_

- [ ] 3. 인증 미들웨어 구현
  - @require_auth 데코레이터 구현 (auth_middleware.py)
  - Bearer Token 검증 및 사용자 정보 추출 구현
  - 401 Unauthorized 오류 처리 구현
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 4. 인증 API 엔드포인트 구현
  - 회원가입 API 구현 (POST /auth/register)
  - 로그인 API 구현 (POST /auth/login)
  - 토큰 갱신 API 구현 (POST /auth/refresh)
  - 로그아웃 API 구현 (POST /auth/logout)
  - 현재 사용자 정보 API 구현 (GET /auth/me)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 5.1, 5.2, 5.3, 5.4_

- [ ] 5. 프론트엔드 인증 스토어 구현
  - Pinia 기반 인증 상태 관리 스토어 구현 (authStore.js)
  - 로그인, 회원가입, 로그아웃 액션 구현
  - 토큰 저장 및 복원 로직 구현
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 6. HTTP 클라이언트 및 인터셉터 구현
  - Axios 기반 HTTP 클라이언트 구현 (httpClient.js)
  - 자동 토큰 추가 요청 인터셉터 구현
  - 401 오류 시 자동 토큰 갱신 응답 인터셉터 구현
  - _Requirements: 6.2, 6.3_

- [ ] 7. 라우트 가드 구현
  - requireAuth, requireGuest, requireDiagnosis 가드 구현 (router/guards.js)
  - 인증 상태에 따른 자동 리다이렉트 구현
  - Vue Router와 연동하여 라우트 보호 구현
  - _Requirements: 6.1, 6.3, 6.4_

- [ ] 8. 로그인 페이지 구현
  - 로그인 폼 UI 구현 (LoginPage.vue)
  - 폼 유효성 검사 및 오류 메시지 표시 구현
  - 로딩 상태 및 성공/실패 처리 구현
  - 진단 완료 여부에 따른 리다이렉트 구현
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 9. 회원가입 페이지 구현
  - 회원가입 폼 UI 구현 (RegisterPage.vue)
  - 실시간 유효성 검사 구현 (login_id, email 중복 검사 포함)
  - 비밀번호 확인 및 강도 검사 구현
  - 성공 시 로그인 페이지 리다이렉트 구현
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 10. 인증 시스템 통합 테스트
  - 회원가입부터 로그인까지 전체 플로우 테스트 구현
  - 토큰 갱신 및 자동 로그아웃 테스트 구현
  - 실제 페이지를 통한 인증 기능 테스트 구현
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_