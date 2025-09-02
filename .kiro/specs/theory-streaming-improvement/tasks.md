# 이론 생성 스트리밍 개선 구현 계획

## 구현 개요

기존 이론 생성 로직을 유지하면서 ChatGPT 응답만 JSON 블록 단위로 스트리밍하는 시스템을 구현합니다. QnA 스트리밍의 임시 세션 패턴을 적용하되, GPT 호출은 1번만 수행합니다.

## 구현 작업

- [ ] 1. Learning Supervisor 스트리밍 감지 기능 추가
  - Learning Supervisor에 `_handle_theory_streaming_intent()` 메서드 구현
  - 기존 TheoryEducator 로직을 재사용하여 컨텍스트 준비 (메타데이터 + 벡터 검색)
  - 임시 세션 생성 및 전역 저장소 저장 로직 구현
  - Response Generator가 추출할 수 있도록 대화 기록에 temp_session_id 저장
  - _Requirements: 1.1, 3.1_

- [ ] 2. Theory Streaming Route 구현
  - `backend/app/routes/learning/session/theory_stream.py` 파일 생성
  - QnA 스트리밍과 동일한 패턴으로 SSE 엔드포인트 구현
  - GET `/api/v1/learning/theory-stream/<temp_id>` 라우트 추가
  - 임시 세션 검증, 만료 체크, 보안 처리 구현
  - TheoryEducator State 관리 메서드 호출 구조 구현
  - _Requirements: 1.1, 1.2, 3.3_

- [ ] 3. TheoryEducator State 관리 메서드 추가
  - `process_streaming_state()` 메서드 구현 (QnA Resolver 패턴 적용)
  - `finalize_streaming_state()` 메서드 구현 (스트리밍 완료 후 State 저장)
  - 기존 `process()` 메서드는 폴백용으로 유지
  - TutorState 무변경 원칙 준수
  - _Requirements: 3.1, 3.3_

- [ ] 4. Theory Streaming Tool 구현
  - `backend/app/tools/content/theory_tools_chatgpt_stream.py` 파일 생성
  - 기존 `theory_tools_chatgpt.py`의 프롬프트 템플릿과 입력 데이터 준비 로직 재사용
  - ChatGPT 스트리밍 API 호출 구현 (streaming=True)
  - JSON 블록 단위 파싱 및 실시간 전송 로직 구현
  - 블록 타입 감지 로직 구현 (header, introduction, definition, examples)
  - _Requirements: 1.2, 2.1, 2.2_

- [ ] 5. Response Generator 스트리밍 응답 지원 (1단계에서만 사용)
  - `_create_theory_streaming_workflow_response()` 메서드 추가
  - 대화 기록에서 temp_session_id 추출 로직 구현
  - 스트리밍 응답 형식으로 workflow_response 생성 (temp_session_id 포함)
  - GET `/theory-stream/<temp_id>`는 Response Generator 경유하지 않고 직접 SSE 처리
  - _Requirements: 1.1, 3.1_

- [ ] 6. Blueprint 등록 및 라우팅 설정
  - `backend/app/__init__.py`에 theory_stream_bp Blueprint 등록
  - URL 프리픽스 설정: `/api/v1/learning`
  - 기존 라우팅 구조와 일관성 유지
  - _Requirements: 3.1_

- [ ] 7. 백엔드 스트리밍 응답 및 JSON 블록 순서 테스트
  - `backend/tests/0902/test_theory_streaming_response.py` 파일 생성
  - POST `/session/start` 요청 시 스트리밍 응답 감지 테스트
  - `workflow_response.streaming = true` 및 `temp_session_id` 반환 확인
  - GET `/theory-stream/<temp_id>` SSE 연결 테스트
  - JSON 블록이 올바른 순서로 스트리밍되는지 확인 (header → introduction → definition → examples)
  - 각 블록이 수신될 때마다 터미널에 실시간으로 출력하여 순차 전송 확인
  - 블록별 수신 시간 측정 및 출력 (TTFT 및 블록 간 간격 확인)
  - 터미널에서 실행 가능한 테스트 작성 (수동 로그인 ID/Password 입력)
  - _Requirements: 1.1, 1.2, 2.1, 3.1_

- [ ] 8. 프론트엔드 스트리밍 감지 및 연결
  - learningService.js에 이론 스트리밍 감지 로직 추가
  - QnA 스트리밍과 동일한 패턴으로 SSE 연결 구현
  - `connectTheoryStream()` 메서드 구현
  - 자동 스트리밍 감지 및 연결 로직 구현
  - _Requirements: 1.1, 4.1_

- [ ] 9. 프론트엔드 JSON 블록 처리
  - learningStore.js에 이론 블록 상태 관리 추가
  - JSON 블록 수신 및 누적 처리 로직 구현
  - 기존 이론 UI 컴포넌트와 호환되는 데이터 구조 유지
  - 블록별 실시간 렌더링 지원
  - _Requirements: 1.2, 2.3, 4.2_

- [ ] 10. 에러 처리 및 폴백 시스템
  - Learning Supervisor에서 스트리밍 실패 시 기존 플로우로 폴백
  - Theory Streaming Route에서 스트리밍 실패 시 동기 방식 폴백
  - 프론트엔드에서 네트워크 오류 시 재연결 및 폴백 처리
  - 임시 세션 만료 및 정리 로직 구현
  - _Requirements: 3.2, 4.3_

- [ ] 11. 통합 테스트 및 성능 검증
  - 전체 스트리밍 플로우 통합 테스트 작성
  - TTFT (Time to First Token) 성능 측정
  - 기존 워크플로우와의 호환성 테스트
  - 동시 다중 사용자 스트리밍 테스트
  - 폴백 시나리오 테스트
  - _Requirements: 1.5, 3.4, 4.4_