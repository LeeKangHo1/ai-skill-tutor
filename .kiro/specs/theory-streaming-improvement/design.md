# 이론 생성 스트리밍 개선 설계 문서

## 개요

현재 이론 생성의 10-15초 대기 시간을 개선하기 위해 JSON 블록 단위 스트리밍 시스템을 설계합니다. QnA 스트리밍의 성공 사례를 참고하여 2단계 처리 구조를 도입하고, 기존 LangGraph 워크플로우와 완전 호환되는 시스템을 구축합니다.

## 아키텍처

### 전체 시스템 구조 (기존 이론 생성 + 스트리밍 응답)

```
기존: SessionService → TheoryEducator → ChatGPT (10-15초) → 완성된 JSON
새로운: SessionService → 스트리밍 감지 → 임시 세션 생성 → TheoryEducator 스트리밍 (3초 TTFT)
```

### 처리 구조 (기존 로직 + 스트리밍 응답만 변경)

1. **Phase 1**: JWT 인증 및 임시 세션 생성 (즉시)
   - POST `/api/v1/learning/session/start` 요청 처리
   - `user_intent: "theory_streaming"` 감지
   - 기존 TheoryEducator 컨텍스트 준비 (메타데이터 + 벡터 검색)
   - 임시 세션 생성 및 전역 저장소 저장
   - `temp_session_id` 반환

2. **Phase 2**: ChatGPT JSON 블록 스트리밍 (실시간)
   - GET `/api/v1/learning/theory-stream/<temp_id>` 연결
   - 임시 세션에서 준비된 컨텍스트 로드
   - **기존과 동일한 ChatGPT 호출이지만 JSON 블록 단위로 스트리밍**
   - 완료 후 TutorState 최종 업데이트

### 중요: TutorState 무변경 원칙

- **기존 필드만 사용**: `user_intent: "theory_streaming"` 활용
- **임시 세션 분리**: QnA 스트리밍과 동일하게 전역 저장소 사용
- **State 호환성**: 스트리밍 완료 후 기존 워크플로우와 동일한 State 구조 유지

## 컴포넌트 설계

### 1. 백엔드 컴포넌트

#### 1.1 Learning Supervisor 확장 (스트리밍 감지 및 컨텍스트 준비)

**기존 메서드 유지:**
- `process()`: 기존 워크플로우 처리

**새로운 메서드 추가:**
- `_handle_theory_streaming_intent()`: `user_intent: "theory_streaming"` 처리
- `_prepare_theory_streaming_context()`: 기존 TheoryEducator 로직으로 컨텍스트 준비

```python
class LearningSupervisor:
    def _handle_theory_streaming_intent(self, state: TutorState) -> TutorState:
        """theory_streaming 의도 처리 (기존 이론 생성 로직 재사용)"""
        # 1. 기존 TheoryEducator 로직으로 컨텍스트 준비 (GPT 호출 없음)
        #    - 메타데이터 로드: _load_section_metadata()
        #    - 벡터 검색: search_theory_materials() 
        #    - 프롬프트 준비: _prepare_vector_input_data() 또는 _prepare_fallback_input_data()
        context = self._prepare_theory_streaming_context(state)
        
        # 2. 임시 세션 생성 (준비된 컨텍스트 저장)
        temp_session_id = self._create_theory_streaming_session(state, context)
        
        # 3. 대화 기록에 temp_session_id 저장 (Response Generator가 추출)
        updated_state = state_manager.add_conversation(
            state, 
            "learning_supervisor",
            f"theory_streaming_session:{temp_session_id}",
            "system"
        )
        
        return updated_state
```

#### 1.2 TheoryEducator 분리 (스트리밍 전용)

**TutorState 건드리지 않음**: 임시 세션에서만 작업
- `process_streaming_state()`: 스트리밍 시작 시 State 관리 (QnA와 동일)
- `finalize_streaming_state()`: 스트리밍 완료 후 State 저장 (QnA와 동일)

#### 1.3 Theory Streaming Route (QnA 스트리밍과 동일한 구조)

**새로운 파일:** `backend/app/routes/learning/session/theory_stream.py`

**엔드포인트:**
- `GET /api/v1/learning/theory-stream/<temp_id>`

**QnA 스트리밍과 완전 동일한 패턴:**
- 임시 세션 검증 및 만료 체크
- TheoryEducator State 관리 호출
- SSE 스트리밍 실행
- 완료 후 자동 State 업데이트

```python
@theory_stream_bp.route('/theory-stream/<temp_id>', methods=['GET'])
def stream_theory_response(temp_id: str):
    """이론 설명을 JSON 블록 단위로 스트리밍 (QnA 패턴 적용)"""
    theory_agent = None
    temp_session_data = None
    
    try:
        # 1. 임시 세션 검증 (QnA와 동일)
        temp_session_data = streaming_sessions.get(temp_id)
        if not temp_session_data or time.time() > temp_session_data["expires_at"]:
            return Response(_create_error_sse("INVALID_SESSION", "유효하지 않은 스트리밍 세션입니다."))
        
        # 2. TheoryEducator State 관리 초기화
        from app.agents.theory_educator.theory_educator_agent import TheoryEducator
        theory_agent = TheoryEducator()
        
        state_result = theory_agent.process_streaming_state(temp_session_data)
        if not state_result.get("success"):
            return Response(_create_error_sse("STATE_INIT_ERROR", "State 관리 초기화에 실패했습니다."))
        
        # 3. 세션 제거 (보안)
        streaming_sessions.pop(temp_id, None)
        
        # 4. SSE 스트리밍 시작
        return Response(
            _generate_theory_sse_stream_with_state_management(temp_session_data, theory_agent),
            mimetype='text/event-stream'
        )
    except Exception as e:
        # 오류 시에도 State 관리
        if theory_agent and temp_session_data:
            theory_agent.finalize_streaming_state(temp_session_data, f"오류: {str(e)}")
        return Response(_create_error_sse("THEORY_STREAM_ERROR", str(e)))
```

#### 1.4 Theory Streaming Tool (기존 이론 생성 도구의 스트리밍 버전)

**새로운 파일:** `backend/app/tools/content/theory_tools_chatgpt_stream.py`

**기존 theory_tools_chatgpt.py의 스트리밍 버전:**
- 동일한 프롬프트 템플릿 사용
- 동일한 입력 데이터 준비 로직
- **차이점: ChatGPT 응답을 JSON 블록 단위로 스트리밍**

```python
async def theory_streaming_generation_tool(
    section_metadata: Dict[str, Any],
    vector_materials: List[Dict[str, Any]] = None,
    user_type: str = "beginner",
    section_data: Optional[Dict[str, Any]] = None,
    is_retry_session: bool = False,
    content_source: str = "vector"
) -> AsyncGenerator[Dict[str, Any], None]:
    """기존 이론 생성과 동일한 로직 + JSON 블록 스트리밍"""
    
    try:
        # 기존과 동일한 프롬프트 준비
        model = _get_chatgpt_streaming_model()  # streaming=True로 설정
        parser = JsonOutputParser()
        prompt_template = _create_prompt_template(user_type, is_retry_session, content_source)
        
        # 기존과 동일한 입력 데이터 준비
        if content_source == "vector":
            input_data = _prepare_vector_input_data(section_metadata, vector_materials)
        else:
            input_data = _prepare_fallback_input_data(section_metadata, section_data)
        
        # 차이점: 스트리밍으로 JSON 블록 생성
        prompt = prompt_template.format(**input_data)
        current_block = ""
        block_count = 0
        
        async for chunk in model.astream([{"role": "user", "content": prompt}]):
            current_block += chunk.content
            
            # JSON 블록 완성 감지 및 전송
            if _is_complete_json_block(current_block):
                block_count += 1
                yield {
                    "block_type": _detect_block_type(current_block),
                    "block_id": block_count,
                    "data": json.loads(current_block)
                }
                current_block = ""
                
    except Exception as e:
        yield {"block_type": "error", "error": str(e)}
```

### 2. 프론트엔드 컴포넌트

#### 2.1 Learning Service 확장

**새로운 메서드:**
- `startTheoryStreaming()`: 스트리밍 시작
- `connectTheoryStream()`: SSE 연결 관리

```javascript
// learningService.js
async startTheoryStreaming(chapterNumber, sectionNumber, userMessage) {
    // 1. 일반 세션 시작 (스트리밍 감지)
    const response = await this.startSession(chapterNumber, sectionNumber, userMessage);
    
    // 2. 스트리밍 응답 감지
    if (response.data.workflow_response.streaming) {
        const tempId = response.data.workflow_response.temp_session_id;
        return this.connectTheoryStream(tempId);
    }
    
    return response;
}
```

#### 2.2 Learning Store 확장

**새로운 상태:**
- `theoryStreamingState`: 스트리밍 진행 상태
- `theoryBlocks`: 수신된 JSON 블록들

**새로운 액션:**
- `handleTheoryBlock()`: 블록 수신 처리
- `completeTheoryStreaming()`: 스트리밍 완료 처리

```javascript
// learningStore.js
const learningStore = defineStore('learning', {
    state: () => ({
        theoryStreamingState: 'idle', // idle, streaming, completed, error
        theoryBlocks: [],
        currentTheoryContent: null
    }),
    
    actions: {
        handleTheoryBlock(block) {
            this.theoryBlocks.push(block);
            this.updateTheoryContent();
        }
    }
});
```

## 데이터 모델

### JSON 블록 구조

#### Block 1: Header
```json
{
    "block_type": "header",
    "block_id": 1,
    "data": {
        "chapter_info": "📚 2챕터 1섹션",
        "title": "LLM(Large Language Model)이란? 🤖"
    }
}
```

#### Block 2: Introduction
```json
{
    "block_type": "section",
    "block_id": 2,
    "data": {
        "type": "introduction",
        "content": "안녕하세요! 오늘은 AI의 핵심 기술 중 하나인 LLM에 대해 알아보겠습니다..."
    }
}
```

#### Block 3: Definition
```json
{
    "block_type": "section", 
    "block_id": 3,
    "data": {
        "type": "definition",
        "title": "LLM이 뭔가요? 🔍",
        "content": "LLM은 Large Language Model의 줄임말로...",
        "analogy": {
            "concept": "LLM",
            "comparison": "도서관의 박학다식한 사서",
            "details": ["수많은 책을 읽고 기억하는 사서처럼..."]
        }
    }
}
```

#### Block 4: Examples
```json
{
    "block_type": "section",
    "block_id": 4,
    "data": {
        "type": "examples",
        "title": "실생활 LLM 예시들 💡",
        "items": [
            {
                "category": "대화형 AI 🗣️",
                "description": "ChatGPT, Claude, Bard 같은 챗봇들",
                "benefit": "자연스러운 대화로 정보를 얻고 문제를 해결할 수 있어요"
            }
        ]
    }
}
```

### SSE 이벤트 타입

```javascript
// SSE 이벤트 타입 정의
const SSE_EVENTS = {
    STREAM_START: 'stream_start',
    THEORY_BLOCK: 'theory_block', 
    STREAM_COMPLETE: 'stream_complete',
    STREAM_ERROR: 'stream_error'
};
```

## 인터페이스 설계

### 1. TheoryEducator Interface (QnA Resolver와 동일한 패턴)

```python
class TheoryEducatorInterface:
    def process(self, state: TutorState) -> TutorState:
        """기존 동기 방식 (폴백용)"""
        pass
    
    def process_streaming_state(self, temp_session_data: Dict) -> Dict[str, Any]:
        """스트리밍 시작 시 State 관리 (QnA Resolver와 동일)"""
        pass
    
    def finalize_streaming_state(self, temp_session_data: Dict, final_content: Dict) -> Dict[str, Any]:
        """스트리밍 완료 후 State 최종 업데이트 (QnA Resolver와 동일)"""
        pass
```

### 2. Theory Streaming API Interface (QnA 스트리밍과 동일한 구조)

```python
# Request: POST /api/v1/learning/session/start (기존과 동일)
{
    "chapter_number": 2,
    "section_number": 1,
    "user_message": "2챕터 시작할게요"
}

# Response: user_intent가 "theory_streaming"으로 감지된 경우
{
    "success": true,
    "data": {
        "session_info": {...},
        "workflow_response": {
            "current_agent": "learning_supervisor",
            "session_progress_stage": "theory_streaming",
            "ui_mode": "streaming",
            "streaming": true,
            "temp_session_id": "theory_stream_123456",
            "estimated_blocks": 4
        }
    }
}

# SSE Endpoint: GET /api/v1/learning/theory-stream/<temp_id>
# QnA 스트리밍과 동일한 SSE 이벤트 구조
```

### 3. Frontend Streaming Interface (QnA 스트리밍과 동일한 구조)

```javascript
// learningService.js - QnA 스트리밍과 동일한 패턴
async startTheoryStreaming(chapterNumber, sectionNumber, userMessage) {
    // 1. 일반 세션 시작 (스트리밍 감지)
    const response = await this.startSession(chapterNumber, sectionNumber, userMessage);
    
    // 2. 스트리밍 응답 감지 (QnA와 동일)
    if (response.data.workflow_response.streaming) {
        const tempId = response.data.workflow_response.temp_session_id;
        return this.connectTheoryStream(tempId);
    }
    
    return response;
}

connectTheoryStream(tempSessionId) {
    // QnA 스트리밍과 동일한 SSE 연결 로직
    const eventSource = new EventSource(`/api/v1/learning/theory-stream/${tempSessionId}`);
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleTheoryStreamEvent(data);
    };
    
    return eventSource;
}
```

```javascript
// learningStore.js - QnA 스트리밍 상태 관리 패턴 적용
const learningStore = defineStore('learning', {
    state: () => ({
        // 기존 상태 유지
        theoryStreamingState: 'idle', // QnA와 동일한 상태 관리
        theoryBlocks: [],
        streamingEventSource: null
    }),
    
    actions: {
        // QnA 스트리밍과 동일한 패턴
        async startTheoryStreamingIfDetected(response) {
            if (response.data.workflow_response.streaming) {
                const tempId = response.data.workflow_response.temp_session_id;
                this.connectTheoryStream(tempId);
                return true;
            }
            return false;
        }
    }
});
```

## 에러 처리

### 1. 백엔드 에러 처리 (QnA 스트리밍과 동일한 패턴)

**스트리밍 실패 시 폴백:**
```python
# Learning Supervisor에서 처리
if user_intent == "theory_streaming":
    try:
        return self._handle_theory_streaming_intent(state)
    except Exception as e:
        logger.warning(f"이론 스트리밍 준비 실패, 일반 이론 생성으로 폴백: {e}")
        # user_intent를 "next_step"으로 변경하여 기존 TheoryEducator 플로우로 진행
        state["user_intent"] = "next_step"
        return self._route_to_theory_educator(state)

# Theory Streaming Route에서도 폴백 처리
try:
    # 스트리밍 시도
    async for block in theory_streaming_generation_tool(...):
        yield _format_sse_data(block)
except Exception as e:
    # 스트리밍 실패 시 기존 동기 방식으로 폴백
    fallback_result = theory_generation_tool(...)  # 기존 동기 함수
    yield _format_sse_data({"block_type": "complete", "data": fallback_result})
```

**임시 세션 관리:**
```python
# QnA 스트리밍과 동일한 전역 저장소 사용
theory_streaming_sessions: Dict[str, Dict[str, Any]] = {}

# 세션 만료 및 정리 (QnA와 동일)
def cleanup_expired_theory_sessions():
    current_time = time.time()
    expired_sessions = [
        session_id for session_id, session_data in theory_streaming_sessions.items()
        if current_time > session_data.get("expires_at", 0)
    ]
    for expired_id in expired_sessions:
        theory_streaming_sessions.pop(expired_id, None)
```

### 2. 프론트엔드 에러 처리

**네트워크 연결 실패:**
```javascript
eventSource.onerror = (error) => {
    if (retryCount < MAX_RETRIES) {
        setTimeout(() => this.reconnect(), RETRY_DELAY);
    } else {
        this.fallbackToSync();
    }
};
```

**스트리밍 타임아웃:**
```javascript
const streamingTimeout = setTimeout(() => {
    this.eventSource.close();
    this.fallbackToSync();
}, STREAMING_TIMEOUT);
```

## 테스트 전략

### 1. 단위 테스트

**백엔드:**
- `TheoryEducator.process_streaming()` 테스트
- JSON 블록 파싱 테스트
- SSE 이벤트 생성 테스트

**프론트엔드:**
- 블록 수신 처리 테스트
- UI 업데이트 테스트
- 에러 처리 테스트

### 2. 통합 테스트

**스트리밍 플로우:**
- 세션 시작 → 스트리밍 감지 → SSE 연결 → 블록 수신 → 완료
- 에러 발생 시 폴백 동작 확인
- 동시 다중 사용자 스트리밍 테스트

### 3. 성능 테스트

**TTFT 측정:**
- 첫 번째 블록 수신 시간
- 전체 스트리밍 완료 시간
- 기존 동기 방식과 비교

## 배포 전략

### 1. 점진적 배포

**Phase 1:** 백엔드 스트리밍 인프라 구축
- TheoryEducator 확장
- 스트리밍 라우트 추가
- 기본 SSE 구현

**Phase 2:** 프론트엔드 스트리밍 UI
- 스트리밍 감지 로직
- 블록 단위 렌더링
- 진행 상황 표시

**Phase 3:** 최적화 및 안정화
- 에러 처리 강화
- 성능 튜닝
- 사용자 피드백 반영

### 2. 기능 플래그 (QnA 스트리밍과 동일한 방식)

```python
# Learning Supervisor에서 스트리밍 기능 제어
THEORY_STREAMING_ENABLED = os.getenv('THEORY_STREAMING_ENABLED', 'true').lower() == 'true'

def _should_use_theory_streaming(self, state: TutorState) -> bool:
    """이론 스트리밍 사용 여부 결정 (QnA와 동일한 패턴)"""
    if not THEORY_STREAMING_ENABLED:
        return False
    
    # 사용자 의도가 명시적으로 스트리밍인 경우
    if state.get("user_intent") == "theory_streaming":
        return True
    
    # 기본적으로는 일반 플로우 사용
    return False
```

### 3. 모니터링

**핵심 지표:**
- TTFT (Time to First Token)
- 스트리밍 성공률
- 폴백 발생률
- 사용자 만족도

## 결론

이 설계는 QnA 스트리밍의 성공 패턴을 이론 생성에 적용하여 사용자 경험을 크게 개선할 것입니다. JSON 블록 단위 스트리밍을 통해 TTFT를 대폭 단축하면서도 기존 시스템과의 완전한 호환성을 유지합니다.