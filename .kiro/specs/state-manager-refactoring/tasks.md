# Implementation Plan

- [ ] 1. 폴더 구조 생성 및 기본 파일 설정
  - `backend/app/core/langraph/state/` 폴더 생성
  - 빈 파일들 생성: `__init__.py`, `state_definition.py`, `quiz_manager.py`, `session_manager.py`, `state_serializer.py`
  - 각 파일에 기본 헤더 주석과 import 구문 추가
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2. TutorState 정의 분리
  - 기존 `state_manager.py`에서 `TutorState` TypedDict 클래스를 `state_definition.py`로 이동
  - 관련 상수들 (valid_user_types, valid_progress_stages 등)도 함께 이동
  - 필드별 상세 주석 추가하여 문서화 개선
  - _Requirements: 2.1_

- [ ] 3. 퀴즈 관리 로직 분리
  - 퀴즈 관련 메서드들을 `quiz_manager.py`로 이동: `update_quiz_info`, `parse_quiz_from_json`, `update_evaluation_result`, `clear_quiz_data`, `get_quiz_type_from_section`, `update_quiz_type_from_section`, `sync_quiz_types`, `update_user_answer`
  - QuizManager 클래스 생성하여 메서드들을 그룹화
  - TutorState import 추가
  - _Requirements: 2.2_

- [ ] 4. 세션 관리 로직 분리
  - 세션 관련 메서드들을 `session_manager.py`로 이동: `update_section_progress`, `update_agent_transition`, `update_session_progress`, `update_ui_mode`, `reset_session_state`, `add_conversation`, `clear_agent_drafts`, `update_agent_draft`, `update_session_decision`, `prepare_next_session`, `get_current_section_data`
  - SessionManager 클래스 생성하여 메서드들을 그룹화
  - TutorState import 추가
  - _Requirements: 2.2_

- [ ] 5. 직렬화 및 검증 로직 분리
  - 직렬화 관련 메서드들을 `state_serializer.py`로 이동: `to_dict`, `from_dict`, `validate_state`
  - StateSerializer 클래스 생성하여 메서드들을 그룹화
  - TutorState import 추가
  - _Requirements: 2.4_

- [ ] 6. 통합 StateManager 클래스 구현
  - `__init__.py`에서 통합 StateManager 클래스 구현
  - 분리된 모듈들을 조합하여 기존과 동일한 인터페이스 제공
  - `initialize_state`, `_create_default_state` 등 핵심 메서드 구현
  - 전역 `state_manager` 인스턴스 생성
  - _Requirements: 2.1, 2.2, 2.4_

- [ ] 7. 기존 파일 호환성 업데이트
  - 기존 `state_manager.py` 파일을 새로운 모듈 구조를 사용하도록 수정
  - 기존 import 경로 유지하면서 새로운 구조로 리다이렉트
  - 호환성 보장을 위한 fallback 로직 추가
  - _Requirements: 3.1, 3.3_

- [ ] 8. 테스트 코드 작성 및 검증
  - 기존 테스트 `backend/tests/0812/test_state_manager.py` 실행하여 호환성 확인
  - 분리된 모듈별 단위 테스트 작성: `backend/tests/0817/test_state_refactoring.py`
  - 모든 메서드가 기존과 동일하게 동작하는지 검증
  - _Requirements: 3.3_