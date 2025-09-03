# 이론 생성 스트리밍 기능 요구사항 (1단계)

## 소개

AI 튜터 시스템에서 이론 스트리밍 세션을 시작하는 기능입니다. 사용자가 특정 챕터의 이론 학습을 요청하면, 시스템은 워크플로우를 실행하여 임시 세션을 생성하고 temp_session_id를 반환합니다. 이후 클라이언트는 이 ID를 사용하여 실제 스트리밍 연결을 수행할 수 있습니다.

## 요구사항

### 요구사항 1: 이론 스트리밍 엔드포인트 구현

**사용자 스토리**: 학습자로서, 특정 챕터의 이론 학습을 시작하고 스트리밍으로 받을 수 있기를 원한다.

#### 수락 기준
1. WHEN 사용자가 POST /start-theory-streaming으로 요청 THEN 시스템은 새로운 이론 스트리밍 세션을 생성해야 한다
2. WHEN 요청에 chapter_number, section_number, user_message가 포함 THEN 시스템은 이를 검증하고 처리해야 한다
3. WHEN 요청에 유효한 JWT 토큰이 포함 THEN 시스템은 사용자 인증을 수행해야 한다
4. IF 사용자가 해당 챕터에 대한 학습 권한이 없다면 THEN 시스템은 403 에러를 반환해야 한다
5. WHEN 요청 데이터가 유효하지 않다면 THEN 시스템은 400 에러를 반환해야 한다
6. WHEN 세션 생성이 성공 THEN 시스템은 temp_session_id를 포함한 응답을 반환해야 한다
7. WHEN 클라이언트가 GET /theory-stream/<temp_id>로 요청 THEN 시스템은 SSE 스트리밍을 시작해야 한다
8. WHEN theory_stream.py 파일에서 모든 로직을 처리 THEN session_service.py의 기능을 독립적으로 구현해야 한다

### 요구사항 2: TutorState 초기화 및 워크플로우 실행

**사용자 스토리**: 시스템 관리자로서, 이론 스트리밍 요청이 적절한 TutorState로 초기화되어 워크플로우가 실행되기를 원한다.

#### 수락 기준
1. WHEN 이론 스트리밍 요청이 들어옴 THEN 시스템은 user_intent를 "theory_streaming"으로 설정해야 한다
2. WHEN TutorState가 초기화 THEN 기존 TutorState 구조를 유지하면서 필요한 정보만 설정해야 한다
3. WHEN 워크플로우가 실행 THEN execute_tutor_workflow_sync 함수를 통해 동기적으로 처리되어야 한다
4. WHEN 워크플로우가 완료 THEN 최종 state에서 temp_session_id를 추출할 수 있어야 한다
5. IF TutorState에 새로운 필드 추가가 필요하다면 THEN TypedDict 제약으로 인해 추가하지 않고 다른 방식으로 처리해야 한다

### 요구사항 3: LearningSupervisor 이론 스트리밍 처리

**사용자 스토리**: 시스템 관리자로서, LearningSupervisor가 theory_streaming 의도를 감지하고 적절히 처리하기를 원한다.

#### 수락 기준
1. WHEN user_intent가 "theory_streaming" THEN LearningSupervisor는 _handle_theory_streaming_intent 메서드를 호출해야 한다
2. WHEN 이론 스트리밍 의도를 처리 THEN 고유한 temp_session_id를 생성해야 한다
3. WHEN temp_session_id가 생성 THEN 임시 스트리밍 세션 저장소에 저장해야 한다
4. WHEN temp_session_id를 대화 기록에 추가 THEN "이론 스트리밍 세션 준비 (ID: {temp_session_id})" 형태의 시스템 메시지로 저장해야 한다
5. WHEN 처리가 완료 THEN 업데이트된 state를 반환해야 한다

### 요구사항 4: Supervisor Router 워크플로우 우회

**사용자 스토리**: 시스템 관리자로서, theory_streaming 의도일 때 워크플로우가 적절히 우회되기를 원한다.

#### 수락 기준
1. WHEN user_intent가 "theory_streaming" THEN supervisor_router는 "learning_supervisor_output"을 반환해야 한다
2. WHEN 워크플로우가 우회 THEN 불필요한 에이전트 호출 없이 바로 응답 생성으로 이동해야 한다

### 요구사항 5: ResponseGenerator 스트리밍 응답 생성

**사용자 스토리**: 시스템 관리자로서, ResponseGenerator가 이론 스트리밍용 응답을 적절히 생성하기를 원한다.

#### 수락 기준
1. WHEN current_agent가 "theory_educator" THEN _create_streaming_theory_workflow_response 메서드를 호출해야 한다
2. WHEN 스트리밍 응답을 생성 THEN 대화 기록에서 temp_session_id를 추출해야 한다
3. WHEN temp_session_id를 추출 THEN "이론 스트리밍 세션 준비" 메시지에서 정규식으로 ID를 파싱해야 한다
4. WHEN 응답을 생성 THEN type이 "streaming_theory"로 설정되어야 한다
5. WHEN 응답이 완성 THEN 적절한 안내 메시지와 temp_session_id를 포함해야 한다

### 요구사항 6: 임시 세션 저장소 관리

**사용자 스토리**: 시스템 관리자로서, 이론 스트리밍 세션이 안전하게 저장되고 관리되기를 원한다.

#### 수락 기준
1. WHEN 임시 세션이 생성 THEN theory_streaming_sessions 딕셔너리에 저장되어야 한다
2. WHEN 세션 데이터를 저장 THEN 필요한 컨텍스트 정보가 포함되어야 한다
3. WHEN 세션 ID로 조회 THEN 해당 세션 데이터를 반환할 수 있어야 한다
4. WHEN 세션이 만료되거나 완료 THEN 저장소에서 제거되어야 한다