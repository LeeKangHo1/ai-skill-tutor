# Implementation Plan

- [-] 1. 진단 완료 시 새로운 JWT 토큰 발급 기능 구현



  - `backend/app/routes/diagnosis/submit.py`의 `select_user_type()` 함수 수정
  - DB 업데이트 후 최신 사용자 정보로 새로운 access_token 생성
  - 응답에 새로운 access_token 포함하여 반환
  - _Requirements: 1.1, 1.2_

- [ ] 2. 대시보드 접근 시 백업 검증 로직 추가
  - `backend/app/routes/dashboard/overview.py`의 `get_dashboard_overview()` 함수 수정
  - JWT 토큰의 diagnosis_completed가 false인 경우 DB에서 실제 상태 재확인
  - DB 상태가 true이면 접근 허용하고 토큰 불일치 로그 기록
  - _Requirements: 1.1, 1.3_

- [ ] 3. 프론트엔드 토큰 갱신 처리 구현
  - `frontend/src/services/diagnosisService.js`에서 진단 완료 응답 처리 수정
  - 새로운 access_token을 받아서 로컬 스토리지 및 axios 헤더 업데이트
  - _Requirements: 1.2, 1.3_

- [ ] 4. 통합 테스트 작성 및 검증
  - 진단 완료 → 즉시 대시보드 접근 시나리오 테스트
  - 토큰 갱신 로직 정상 작동 확인
  - 백업 검증 로직 동작 확인
  - _Requirements: 1.1, 1.2, 1.3_