# QnA 스트리밍 구현 전체 계획

## 🎯 최종 목표
- QnA 답변을 단어 단위로 실시간 스트리밍 표시
- **기존 채팅창에 채팅 메시지로 표시** (별도 영역 아님)
- **완전히 별도 기능으로 구현** (기존 `/session/message`와 통합은 나중에)

## 🔧 구현 단계별 계획

### 1단계: 백엔드 기본 엔드포인트 (테스트용)
**파일**: `backend/app/routes/learning/session/message_qna.py`
- POST /learning/message-qna
- 일반 QnA 응답 (스트리밍 아님) - 동작 확인용
- 기존 qna_resolver_agent.py 로직 재사용

### 2단계: QnA 스트리밍 도구
**파일**: `backend/app/tools/content/qna_tools_chatgpt_stream.py`
- LangChain Agent의 astream 메서드 활용
- 단어 단위 스트리밍 Generator 반환
- 기존 qna_tools_chatgpt.py 구조 참고

### 3단계: SSE 스트리밍 엔드포인트
**파일**: `backend/app/routes/learning/session/qna_stream.py`
- GET /learning/qna-stream/{session_id}
- Server-Sent Events로 실시간 스트리밍
- Flask의 Response + stream_template 사용

### 4단계: 프론트엔드 서비스 확장
**파일**: `frontend/src/services/learningService.js`
- sendQnAMessage(): 1단계 테스트용 함수
- startQnAStreaming(): EventSource 연결 함수

### 5단계: 프론트엔드 스토어 확장
**파일**: `frontend/src/stores/learningStore.js`
- streamingQnA 상태 추가 (옵션 B)
```javascript
const streamingQnA = ref({
  isStreaming: false,
  content: '',
  messageId: null
})
```
- 스트리밍 시작/중단/완료 관리 함수
- **기존 chatHistory 배열에 스트리밍 메시지 추가/업데이트**

### 6단계: UI 컴포넌트 수정
**파일**: `frontend/src/components/learning/ChatInteraction.vue`
- **기존 채팅 메시지 표시 로직 활용**
- 스트리밍 중인 메시지 식별 (type: 'qna-streaming')
- 전송 버튼 임시 변경 (테스트용)
- 스트리밍 중 전송 버튼 비활성화
- formatMessage 함수에서 마크다운 제거 (## → '', ** → '')

## 📱 UI/UX 설계

### 스트리밍 메시지 표시 방식
1. **스트리밍 시작**: 빈 튜터 메시지를 chatHistory에 추가
```javascript
chatHistory.value.push({
  id: `streaming-${Date.now()}`,
  sender: '튜터',
  message: '',
  type: 'qna-streaming',
  timestamp: Date.now()
})
```

2. **스트리밍 중**: 해당 메시지의 content 실시간 업데이트
```javascript
const streamingMessage = chatHistory.value.find(m => m.id === streamingMessageId)
streamingMessage.message += cleanedChunk
```

3. **스트리밍 완료**: type을 'qna'로 변경
```javascript
streamingMessage.type = 'qna'
```

### 채팅창 렌더링
- 기존 `.qna-message` 스타일 활용
- 스트리밍 중에는 타이핑 커서 애니메이션 추가
- 기존 스크롤 및 메시지 정렬 로직 그대로 사용

## ⏱️ 구현 우선순위

### 우선 구현 (기능 동작 확인)
1. **1단계**: 기본 엔드포인트 - 동작 테스트
2. **6단계**: UI 임시 연결 - 호출 확인
3. **2단계**: 스트리밍 도구 - AI 응답 확인

### 이후 구현 (실제 스트리밍)
4. **3단계**: SSE 엔드포인트
5. **4단계**: 프론트엔드 서비스  
6. **5단계**: 프론트엔드 스토어 (채팅 통합)

### 최종 테스트
- 새로운 스트리밍 기능이 기존 채팅창에 정상 표시 확인
- 에러 상황 처리 확인
- **기존 기능과의 통합은 별도 작업으로 진행**

## 🎯 핵심 설계 결정사항
- ✅ 옵션 B: 별도 스트리밍 상태 관리 + 기존 chatHistory 통합
- ✅ 프론트엔드 마크다운 제거 (formatMessage 활용)
- ✅ 스트리밍 중 전송 버튼만 비활성화
- ✅ **완전히 독립적인 QnA 스트리밍 기능**
- ✅ **기존 기능과의 통합은 향후 작업**

## 🔄 기존 채팅 통합 상세 설계

### chatHistory 구조 활용
```javascript
// 일반 QnA 메시지
{ sender: '튜터', message: '완성된 답변', type: 'qna' }

// 스트리밍 중 QnA 메시지  
{ sender: '튜터', message: '실시간 업데이트 내용', type: 'qna-streaming' }

// 스트리밍 완료 후
{ sender: '튜터', message: '완성된 답변', type: 'qna' }
```

### CSS 스타일 확장
```scss
.qna-streaming {
  // 기존 .qna-message 스타일 상속
  // + 타이핑 커서 애니메이션 추가
}
```