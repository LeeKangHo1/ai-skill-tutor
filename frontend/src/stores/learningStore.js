// frontend/src/stores/learningStore.js
/**
 * 학습 상태 관리 스토어 (PINIA V2.0 - 리팩토링)
 *
 * @description
 * 이 스토어는 학습 세션의 모든 상태와 비즈니스 로직을 중앙에서 관리합니다.
 * 컴포넌트가 액션을 호출하고, 액션이 API를 호출하며, API 응답을 기반으로 상태를 업데이트하는
 * 엄격한 단방향 데이터 흐름을 따릅니다.
 * 컴포넌트는 비즈니스 로직이나 직접적인 API 호출을 포함해서는 안 됩니다.
 *
 * @원칙
 * 1. 단일 정보 출처 (Single Source of Truth): 모든 학습 관련 데이터는 여기에 저장됩니다.
 * 2. 상태는 읽기 전용: 컴포넌트는 getters나 computed 속성을 통해 상태를 읽을 뿐, 직접 수정하지 않습니다.
 * 3. 상태 변경은 액션을 통해서만: 모든 상태 변경은 API 상호작용을 처리하는 액션을 통해 시작됩니다.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { learningService } from '@/services/learningService'
import { useAuthStore } from '@/stores/authStore'

export const useLearningStore = defineStore('learning', () => {
  // 의존성 스토어
  const authStore = useAuthStore()

  // ===== 상태 (State) ===== //

  const apiError = ref(null)
  const currentUIMode = ref('chat')
  const contentMode = ref('current')
  const sessionCompleted = ref(false)
  const sessionInfo = computed(() => ({
    chapter_number: authStore.currentChapter,
    section_number: authStore.currentSection,
  }))
  const currentAgent = ref('session_manager')
  const sessionProgressStage = ref('session_start')
  const completedSteps = ref({
    theory: false,
    quiz: false,
    feedback: false,
  })
  const theoryData = ref(null)
  const quizData = ref(null)
  const feedbackData = ref(null)
  const chatHistory = ref([])
  const streamingQnA = ref({
    isStreaming: false,
    content: '',
    messageId: null,
    eventSource: null,
  })

  // 🚀 TTFT 측정을 위한 변수 추가
  let streamingStartTime = 0;

  // ===== 게터 (Getters & Computed) ===== //
  const isQuizMode = computed(() => currentUIMode.value === 'quiz')
  const isChatMode = computed(() => currentUIMode.value === 'chat')
  const isTutorReplying = computed(() => 
    chatHistory.value.some(message => message.type === 'loading') || streamingQnA.value.isStreaming
  );

  // ===== 액션 (Actions) ===== //

  const startNewSession = async () => {
    apiError.value = null
    _resetSessionState()

    const chapterNumber = sessionInfo.value.chapter_number
    const sectionNumber = sessionInfo.value.section_number
    const userMessage = `${chapterNumber}챕터 ${sectionNumber}섹션 학습을 시작합니다.`

    const result = await learningService.startLearningSession(chapterNumber, sectionNumber, userMessage)

    if (result.success && result.data?.data?.workflow_response) {
      _processWorkflowResponse(result.data.data.workflow_response)
    } else {
      const errorMessage = result.error?.message || '알 수 없는 오류'
      apiError.value = { message: `세션 시작 실패: ${errorMessage}` };
    }
  }

  const sendMessage = async (message) => {
    apiError.value = null
    chatHistory.value.push({ sender: '나', message, type: 'user', timestamp: Date.now() })
    
    if (isChatMode.value && sessionProgressStage.value !== 'session_start') {
      await startQnAStreaming(message);
    } else {
      await _proceedWorkflow(message);
    }
  }

  const startQnAStreaming = async (userMessage) => {
    if (streamingQnA.value.isStreaming) return;
    
    const streamMessageId = `streaming-${Date.now()}`;
    streamingQnA.value = {
      isStreaming: true,
      content: '',
      messageId: streamMessageId,
      eventSource: null,
    };
    
    chatHistory.value.push({
      id: streamMessageId,
      sender: '튜터',
      message: '',
      type: 'qna-streaming',
      timestamp: Date.now(),
    });

    try {
      // 🚀 1. 요청 시작 시간 기록
      streamingStartTime = performance.now();

      const startResult = await learningService.startQnAStreamSession({
          user_message: userMessage,
          chapter: sessionInfo.value.chapter_number,
          section: sessionInfo.value.section_number,
      });

      if (!startResult.success || !startResult.data?.data?.stream_session_id) {
        throw new Error(startResult.error?.message || '스트리밍 세션을 시작할 수 없습니다.');
      }
      
      const tempId = startResult.data.data.stream_session_id;

      const eventSource = learningService.connectQnAStream({
        tempId,
        onMessage: (data) => {
          _handleStreamMessage(data);
        },
        onError: (error) => {
          console.error("SSE Error:", error);
          _stopStreaming('스트리밍 중 오류가 발생했습니다.');
        },
        onClose: () => {
           _stopStreaming();
        }
      });
      
      streamingQnA.value.eventSource = eventSource;

    } catch (error) {
      console.error("Error starting QnA stream:", error);
      _stopStreaming(error.message || '스트리밍 연결에 실패했습니다.');
    }
  };

  const setContentMode = (mode) => {
    contentMode.value = mode
  }

  const completeSession = async (decision) => {
    apiError.value = null
    const result = await learningService.completeSession(decision)

    if (result.success) {
      await authStore.updateUserInfo()
      sessionCompleted.value = true
    } else {
      const errorMessage = result.error?.message || '알 수 없는 오류'
      apiError.value = { message: `세션 완료 처리 실패: ${errorMessage}` };
    }
  }

  // ===== 내부 헬퍼 함수 ===== //

  const _proceedWorkflow = async (message) => {
    const loadingMessage = { id: `loading-${Date.now()}`, sender: '튜터', message: '...', type: 'loading', timestamp: Date.now() };
    if (isChatMode.value) {
      chatHistory.value.push(loadingMessage);
    }

    const result = isQuizMode.value
      ? await learningService.submitQuizAnswerV2(message)
      : await learningService.sendSessionMessage(message);

    if (isChatMode.value) {
      const loadingIndex = chatHistory.value.findIndex(m => m.id === loadingMessage.id);
      if (loadingIndex !== -1) chatHistory.value.splice(loadingIndex, 1);
    }

    if (result.success && result.data?.data?.workflow_response) {
      _processWorkflowResponse(result.data.data.workflow_response);
    } else {
      const errorMessage = result.error?.message || '알 수 없는 오류';
      apiError.value = { message: `요청 처리 실패: ${errorMessage}` };
      _addTutorMessage(`오류: ${errorMessage}`, 'system');
    }
  }
  
  const _handleStreamMessage = (data) => {
    const streamingMessage = chatHistory.value.find(m => m.id === streamingQnA.value.messageId);
    if (!streamingMessage) return;

    switch (data.type) {
      case 'content_chunk':
        // 🚀 2. 첫 번째 청크 수신 시에만 시간 계산 및 출력
        if (streamingStartTime > 0) {
          const ttft = performance.now() - streamingStartTime;
          console.log(`🚀 TTFT (Time to First Token): ${ttft.toFixed(2)} ms`);
          streamingStartTime = 0; // 중복 측정을 방지하기 위해 리셋
        }
        
        streamingMessage.message += data.chunk;
        break;
      case 'stream_complete':
        streamingMessage.type = 'qna';
        console.log('Streaming complete.');
        _stopStreaming();
        break;
      case 'stream_error':
         _stopStreaming(data.message || '서버에서 스트리밍 오류가 발생했습니다.');
        break;
    }
  }
  
  const _stopStreaming = (errorMessage = null) => {
      if (!streamingQnA.value.isStreaming) return;

      if (errorMessage) {
          const streamingMessage = chatHistory.value.find(m => m.id === streamingQnA.value.messageId);
          if (streamingMessage) {
              streamingMessage.message = errorMessage;
              streamingMessage.type = 'system';
          } else {
              _addTutorMessage(errorMessage, 'system');
          }
      }

      if (streamingQnA.value.eventSource) {
          streamingQnA.value.eventSource.close();
      }

      streamingQnA.value.isStreaming = false;
      streamingQnA.value.eventSource = null;
      streamingQnA.value.messageId = null;
  }
  
  const _processWorkflowResponse = (response) => {
    if (response.current_agent !== 'qna_resolver') {
      currentAgent.value = response.current_agent || 'session_manager'
    }
    currentUIMode.value = response.ui_mode || 'chat'
    sessionProgressStage.value = response.session_progress_stage || 'unknown'
    
    switch(currentAgent.value) {
      case 'theory_educator': completedSteps.value.theory = true; break
      case 'quiz_generator': completedSteps.value.quiz = true; break
      case 'evaluation_feedback_agent':
      case 'evaluation_feedback': completedSteps.value.feedback = true; break
    }
    if (response.evaluation_result) {
      feedbackData.value = response.evaluation_result.feedback; return;
    }
    if (response.session_completion) {
      _addTutorMessage(response.session_completion.session_summary || '세션이 완료되었습니다.'); return;
    }
    const content = response.content; if (!content) return;
    if (content.type === 'theory') theoryData.value = content
    else if (content.type === 'quiz') { quizData.value = content; _addTutorMessage('퀴즈가 생성되었습니다.') }
    else if (content.type === 'qna') _addTutorMessage(content.answer, 'qna')
  }

  const _addTutorMessage = (message, type = 'system') => {
    if (message) chatHistory.value.push({ sender: '튜터', message, type, timestamp: Date.now() })
  }

  const _resetSessionState = () => {
    _stopStreaming();
    theoryData.value = null; quizData.value = null; feedbackData.value = null;
    chatHistory.value = []; currentUIMode.value = 'chat';
    currentAgent.value = 'session_manager'; sessionProgressStage.value = 'session_start';
    contentMode.value = 'current';
    completedSteps.value = { theory: false, quiz: false, feedback: false };
    sessionCompleted.value = false;
    _addTutorMessage('🎓 학습을 시작합니다! 이론 내용을 불러오겠습니다.');
  }

  return {
    apiError, currentUIMode, contentMode, sessionCompleted, sessionInfo, currentAgent,
    sessionProgressStage, completedSteps, theoryData, quizData, feedbackData, chatHistory,
    isQuizMode, isChatMode, isTutorReplying, streamingQnA,
    startNewSession, sendMessage, setContentMode, completeSession, startQnAStreaming,
  }
})