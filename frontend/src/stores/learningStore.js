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

  // --- UI, 에러 상태 ---
  const apiError = ref(null)
  const currentUIMode = ref('chat')
  const contentMode = ref('current')
  const sessionCompleted = ref(false)

  // --- 세션 상태 ---
  // sessionInfo를 authStore와 연동되는 computed 속성으로 변경
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

  // --- 컨텐츠 상태 (분리 관리) ---
  const theoryData = ref(null)    // 이론 데이터 전용
  const quizData = ref(null)      // 퀴즈 데이터 전용  
  const feedbackData = ref(null)  // 피드백 데이터 전용

  const chatHistory = ref([])

  // ===== 게터 (Getters & Computed) ===== //
  const isQuizMode = computed(() => currentUIMode.value === 'quiz')
  const isChatMode = computed(() => currentUIMode.value === 'chat')

  // ===== 액션 (Actions) ===== //

  /**
   * [ACTION] 새로운 학습 세션을 시작합니다.
   */
  const startNewSession = async () => {
    apiError.value = null
    console.log('ACTION: startNewSession 호출됨')

    _resetSessionState()

    const chapterNumber = sessionInfo.value.chapter_number
    const sectionNumber = sessionInfo.value.section_number
    const userMessage = `${chapterNumber}챕터 ${sectionNumber}섹션 학습을 시작합니다.`

    const result = await learningService.startLearningSession(
      chapterNumber,
      sectionNumber,
      userMessage
    )

    if (result.success && result.data?.data?.workflow_response) {
      console.log('✅ 세션 시작 API 성공', result.data)
      _processWorkflowResponse(result.data.data.workflow_response)
    } else {
      const errorMessage = result.error?.message || '알 수 없는 오류가 발생했습니다.'
      console.error('API Error in startNewSession:', errorMessage)
      apiError.value = { message: `세션 시작에 실패했습니다: ${errorMessage}` };
    }
  }

  /**
   * [ACTION] 사용자 메시지 또는 퀴즈 답변을 서버로 전송합니다.
   */
  const sendMessage = async (message) => {
    apiError.value = null
    let loadingMessageId = null // 로딩 메시지를 식별할 ID

    // 채팅 모드일 때만 사용자 메시지 추가 및 로딩 시작
    if (isChatMode.value) {
      // 1. 사용자 메시지를 채팅 기록에 추가
      chatHistory.value.push({ sender: '나', message, type: 'user', timestamp: Date.now() })
      
      // 2. 키워드 검사 없이 무조건 로딩 메시지 추가
      const loadingMessage = {
        id: `loading-${Date.now()}`,
        sender: '튜터',
        message: '...',
        type: 'loading',
        timestamp: Date.now()
      };
      loadingMessageId = loadingMessage.id
      chatHistory.value.push(loadingMessage)
    }

    // API 호출 (퀴즈 모드 또는 채팅 모드)
    const result = isQuizMode.value
      ? await learningService.submitQuizAnswerV2(message)
      : await learningService.sendSessionMessage(message)

    // 3. API 응답 후 로딩 메시지가 있었다면 제거
    if (loadingMessageId) {
      const loadingIndex = chatHistory.value.findIndex(m => m.id === loadingMessageId)
      if (loadingIndex !== -1) {
        chatHistory.value.splice(loadingIndex, 1)
      }
    }

    // 4. 실제 API 결과 처리
    if (result.success && result.data?.data?.workflow_response) {
      console.log('✅ 메시지/답변 API 성공', result.data)
      _processWorkflowResponse(result.data.data.workflow_response)
    } else {
      const errorMessage = result.error?.message || '알 수 없는 오류가 발생했습니다.'
      console.error('API Error in sendMessage:', errorMessage)
      apiError.value = { message: `요청 처리에 실패했습니다: ${errorMessage}` };
      // 오류 발생 시 사용자에게도 알려주는 메시지 추가
      _addTutorMessage(`오류가 발생했습니다. 잠시 후 다시 시도해주세요: ${errorMessage}`, 'system');
    }
  }
  
  /**
   * [ACTION] 컨텐츠 표시 모드를 변경하는 액션
   */
  const setContentMode = (mode) => {
    console.log(`ACTION: setContentMode 호출됨. 모드 변경: ${contentMode.value} -> ${mode}`)
    contentMode.value = mode
  }

  /**
   * [ACTION] 학습 세션을 완료(다음으로 진행 또는 재학습) 처리합니다.
   * @param {'proceed' | 'retry'} decision - 사용자의 결정
   */
  const completeSession = async (decision) => {
    apiError.value = null
    console.log(`ACTION: completeSession 호출됨 (decision: ${decision})`)

    const result = await learningService.completeSession(decision)

    if (result.success) {
      console.log('✅ 세션 완료 API 성공', result.data)
      await authStore.updateUserInfo()
      sessionCompleted.value = true
    } else {
      const errorMessage = result.error?.message || '알 수 없는 오류가 발생했습니다.'
      console.error('API Error in completeSession:', errorMessage)
      apiError.value = { message: `세션 완료 처리에 실패했습니다: ${errorMessage}` };
    }
  }

  // ===== 내부 헬퍼 함수 ===== //

  /**
   * [HELPER] 워크플로우 응답을 처리하여 모든 상태를 업데이트합니다.
   */
  const _processWorkflowResponse = (response) => {
    console.log('HELPER: _processWorkflowResponse 처리 시작', response)

    if (response.current_agent !== 'qna_resolver') {
      currentAgent.value = response.current_agent || 'session_manager'
    }
    
    currentUIMode.value = response.ui_mode || 'chat'
    sessionProgressStage.value = response.session_progress_stage || 'unknown'
    
    switch(currentAgent.value) {
      case 'theory_educator':
        completedSteps.value.theory = true
        break
      case 'quiz_generator':
        completedSteps.value.quiz = true
        break
      case 'evaluation_feedback_agent':
      case 'evaluation_feedback':
        completedSteps.value.feedback = true
        break
    }

    if (response.evaluation_result) {
      feedbackData.value = response.evaluation_result.feedback
      console.log('HELPER: feedbackData 업데이트됨 (evaluation_result)', response.evaluation_result.feedback)
      return
    }

    if (response.session_completion) {
      _addTutorMessage(response.session_completion.session_summary || '세션이 완료되었습니다. 다음 학습을 시작해주세요.')
      console.log('HELPER: 세션 완료 메시지 추가됨')
      return
    }

    const content = response.content
    if (!content) {
      console.warn('Workflow response에 content가 없고 evaluation_result나 session_completion도 없습니다.')
      return
    }
    
    if (content.type === 'theory') {
      theoryData.value = content
      console.log('HELPER: theoryData 업데이트됨', content)
    } else if (content.type === 'quiz') {
      quizData.value = content
      _addTutorMessage('퀴즈가 생성되었습니다.')
      console.log('HELPER: quizData 업데이트됨', content)
    } else if (content.type === 'qna') {
      _addTutorMessage(content.answer, 'qna')
      console.log('HELPER: QnA 응답 채팅에 추가됨', content.answer)
    } else {
      console.warn('알 수 없는 컨텐츠 유형:', content.type, response)
    }
  }

  /**
   * [HELPER] 튜터 메시지를 채팅 기록에 추가합니다.
   */
  const _addTutorMessage = (message, type = 'system') => {
    if (message) {
      chatHistory.value.push({ sender: '튜터', message, type, timestamp: Date.now() })
    }
  }

  /**
   * [HELPER] 새로운 세션 시작 시 모든 관련 상태를 초기화합니다.
   */
  const _resetSessionState = () => {
    console.log('HELPER: _resetSessionState 호출됨')
    
    theoryData.value = null
    quizData.value = null
    feedbackData.value = null
    chatHistory.value = []
    
    currentUIMode.value = 'chat'
    currentAgent.value = 'session_manager'
    sessionProgressStage.value = 'session_start'
    contentMode.value = 'current'
    completedSteps.value = { theory: false, quiz: false, feedback: false }
    sessionCompleted.value = false

    _addTutorMessage('🎓 학습을 시작합니다! 이론 내용을 불러오겠습니다.')
  }

  return {
    apiError,
    currentUIMode,
    contentMode,
    sessionCompleted,
    sessionInfo,
    currentAgent,
    sessionProgressStage,
    completedSteps,
    theoryData,
    quizData,
    feedbackData,
    chatHistory,
    isQuizMode,
    isChatMode,
    startNewSession,
    sendMessage,
    setContentMode,
    completeSession,
  }
})