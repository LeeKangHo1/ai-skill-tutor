# 프로젝트 구조 재정리 구현 계획

## Phase 1: 백엔드 폴더 구조 완성

- [ ] 1. 백엔드 도메인별 폴더 구조 생성
  - 정의된 백엔드 폴더 구조에 따라 모든 필요한 디렉토리 생성
  - 각 디렉토리에 적절한 `__init__.py` 파일과 기본 템플릿 파일 생성
  - Python 패키지 구조가 올바르게 작동하는지 확인
  - _요구사항: 1.1, 1.2, 1.3_

- [ ] 2. 사용자 관련 모델 분리 및 이전
  - `backend/app/models/models.py`에서 User, UserAuthToken, UserProgress, UserStatistics 모델을 도메인별 파일로 분리
  - `models/user/` 폴더에 각각 `user.py`, `auth_token.py`, `user_progress.py` 파일로 이전
  - 모델 간 관계 및 import 경로 정리
  - _요구사항: 3.1, 3.3_

- [ ] 3. 학습 관련 모델 분리 및 이전
  - LearningSession, SessionConversation, SessionQuiz 모델을 `models/learning/` 폴더로 이전
  - `session.py`, `conversation.py`, `quiz.py` 파일로 각각 분리
  - `generate_session_id` 함수를 `session.py`에 포함
  - _요구사항: 3.1, 3.3_

- [ ] 4. 모델 통합 import 시스템 구축
  - `models/__init__.py`에서 모든 모델을 통합 import하는 시스템 구축
  - 기존 import 경로 호환성 유지를 위한 레이어 추가
  - 새로운 import 경로와 기존 경로 모두 지원
  - _요구사항: 3.3, 3.4_

- [ ] 5. 라우트 Blueprint 분리 및 재구성
  - `routes/main.py`의 기본 라우트를 `routes/system/` 폴더로 이전
  - `health_check` 엔드포인트를 `routes/system/health.py`로 분리
  - 기본 index 라우트를 `routes/system/version.py`로 이전
  - Blueprint 등록 시스템 업데이트
  - _요구사항: 3.1, 3.2, 3.3_

- [ ] 6. Flask 애플리케이션 팩토리 업데이트
  - `app/__init__.py`에서 새로운 Blueprint 구조 반영
  - 모든 라우트가 올바르게 등록되는지 확인
  - 에러 핸들러 및 CORS 설정 유지
  - _요구사항: 3.3, 5.1_

## Phase 2: 프론트엔드 폴더 구조 완성

- [ ] 7. 프론트엔드 컴포넌트 폴더 구조 생성
  - 정의된 프론트엔드 폴더 구조에 따라 모든 컴포넌트 디렉토리 생성
  - `components/common/`, `components/auth/` 등 도메인별 폴더 생성
  - 각 폴더에 기본 템플릿 Vue 컴포넌트 파일 생성
  - _요구사항: 2.1, 2.2_

- [ ] 8. Vue 서비스 레이어 확장
  - 기존 `services/api.js` 기반으로 도메인별 서비스 파일 생성
  - `authService.js`, `learningService.js`, `dashboardService.js`, `diagnosisService.js` 생성
  - 각 서비스에 기본 API 함수 템플릿 구현
  - _요구사항: 2.1, 2.2_

- [ ] 9. Vue 스타일 구조 완성
  - `styles/` 폴더에 SCSS 변수, 믹스인, 컴포넌트별 스타일 파일 생성
  - `variables.scss`, `mixins.scss` 기본 파일 생성
  - `components/`, `pages/` 폴더에 스타일 파일 템플릿 생성
  - _요구사항: 2.1, 2.3_

- [ ] 10. Vue 컴포저블 및 유틸리티 구조 생성
  - `composables/` 폴더에 기본 컴포저블 파일들 생성
  - `useAuth.js`, `useApi.js`, `useLearning.js`, `useNotification.js` 템플릿 생성
  - `utils/` 폴더에 상수, 헬퍼, 검증, 포맷팅 함수 파일 생성
  - _요구사항: 2.1, 2.2_

## Phase 3: 기존 코드 통합 및 검증

- [ ] 11. 백엔드 import 경로 전체 업데이트
  - 모든 Python 파일에서 새로운 모델 import 경로로 업데이트
  - `run.py`, 테스트 파일, 설정 파일 등 모든 참조 경로 수정
  - 기존 기능이 정상적으로 작동하는지 확인
  - _요구사항: 3.3, 3.4_

- [ ] 12. 백엔드 기능 테스트 및 검증
  - Flask 애플리케이션이 정상적으로 실행되는지 확인
  - 모든 API 엔드포인트가 올바르게 작동하는지 테스트
  - 데이터베이스 연결 및 모델 동작 확인
  - _요구사항: 5.1, 5.4_

- [ ] 13. 프론트엔드 기능 테스트 및 검증
  - Vue.js 개발 서버가 정상적으로 실행되는지 확인
  - 기존 컴포넌트와 라우터가 올바르게 작동하는지 테스트
  - 백엔드와의 API 통신이 정상적으로 이루어지는지 확인
  - _요구사항: 5.2, 5.4_

- [ ] 14. 전체 시스템 통합 테스트
  - 백엔드와 프론트엔드가 함께 정상적으로 작동하는지 확인
  - 기존 테스트 케이스가 새로운 구조에서 통과하는지 검증
  - 개발 환경 설정이 올바르게 작동하는지 최종 확인
  - _요구사항: 5.3, 5.4_

## Phase 4: 문서화 및 정리

- [ ] 15. 구조 변경 문서 작성
  - 변경된 폴더 구조와 파일 위치에 대한 문서 작성
  - 새로운 import 경로 및 사용법 가이드 작성
  - 개발자를 위한 구조 이해 문서 생성
  - _요구사항: 4.2_

- [ ] 16. 기존 파일 정리 및 최적화
  - 더 이상 사용하지 않는 기존 파일들 정리
  - 중복 코드 제거 및 코드 품질 개선
  - 프로젝트 전체 구조 최종 점검
  - _요구사항: 3.4, 5.4_