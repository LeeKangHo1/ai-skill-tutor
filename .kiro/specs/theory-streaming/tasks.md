# 이론 생성 스트리밍 기능 구현 계획

## 구현 작업 목록

- [ ] 1. theory_stream.py 파일 생성 및 기본 구조 구현
  - Blueprint 설정 및 임시 세션 저장소 생성
  - POST /start-theory-streaming 엔드포인트 구현 (JWT 인증, 데이터 검증 포함)
  - GET /theory-stream/<temp_id> 엔드포인트 기본 구조 구현
  - _Requirements: 1.1, 1.2, 1.3, 1.6_

- [ ] 2. theory_stream.py 세션 관리 함수 구현
  - _start_theory_streaming_session() 함수 구현 (JWT 검증, TutorState 초기화, 워크플로우 실행)
  - temp_session_id 추출 및 응답 생성 로직 구현
  - 세션 검증 및 데이터 추출 로직 구현
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 3. LearningSupervisor에 이론 스트리밍 처리 메서드 추가
  - _handle_theory_streaming_intent() 메서드 구현
  - temp_session_id 생성 및 임시 저장소 저장 로직
  - 대화 기록에 시스템 메시지 추가 ("이론 스트리밍 세션 준비 (ID: {temp_session_id})")
  - process_user_input() 메서드에서 theory_streaming 의도 처리 분기 추가
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 4. supervisor_router.py 수정
  - theory_streaming 의도 감지 시 "learning_supervisor_output" 반환하도록 수정
  - 워크플로우 우회 로직 구현
  - _Requirements: 4.1, 4.2_

- [ ] 5. ResponseGenerator에 이론 스트리밍 응답 생성 메서드 추가
  - _create_streaming_theory_workflow_response() 메서드 구현
  - 대화 기록에서 temp_session_id 추출 로직 (정규식 사용)
  - 스트리밍 응답 메타데이터 생성 ("이론 설명 준비가 되었습니다" 메시지 포함)
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 6. JSON 블록 스트리밍 Generator 구현
  - _generate_theory_json_stream() 함수 구현
  - TheoryEducator와 연동하여 JSON 블록 단위 생성
  - SSE 형식으로 완성된 JSON 블록 전송
  - 스트리밍 시작/완료/에러 이벤트 처리
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 7. 기본 에러 처리 및 세션 정리 로직 구현
  - 인증 실패, 데이터 검증 실패, 세션 오류 처리
  - 스트리밍 중 에러 발생 시 SSE 에러 이벤트 전송
  - 세션 완료 후 임시 저장소 정리
  - _Requirements: 에러 처리 관련_

- [ ] 8. Flask 앱에 Blueprint 등록
  - app/__init__.py 또는 관련 설정 파일에서 theory_stream_bp 등록
  - 라우팅 경로 확인 및 테스트
  - _Requirements: 1.7_

- [ ] 9. 기본 기능 테스트 작성
  - test_theory_stream.py 파일 생성
  - 정상적인 스트리밍 세션 시작 테스트
  - 정상적인 SSE 스트리밍 테스트
  - _Requirements: 테스트 전략 관련_

- [ ] 10. 전체 워크플로우 통합 테스트
  - test_theory_streaming_integration.py 파일 생성
  - POST → 워크플로우 → SSE 전체 흐름 테스트
  - 실제 TheoryEducator와의 연동 확인
  - _Requirements: 테스트 전략 관련_