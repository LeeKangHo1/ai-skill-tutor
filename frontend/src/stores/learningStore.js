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
// frontend/src/stores/learningStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { learningService } from '@/services/learningService'
import { useAuthStore } from '@/stores/authStore'

export const useLearningStore = defineStore('learning', () => {
  // 의존성 스토어
  const authStore = useAuthStore()

  // ===== 상태 (State) ===== //

  // --- UI, 로딩, 에러 상태 ---
  const isContentLoading = ref(false)
  const apiError = ref(null)
  const currentUIMode = ref('chat')
  const contentMode = ref('current')

  // --- 세션 상태 ---
  // [수정] sessionInfo를 authStore와 연동되는 computed 속성으로 변경
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

  // --- 컨텐츠 상태 ---
  const mainContent = ref({
    type: 'theory',
    data: null,
  })
  const quizData = ref(null)
  const chatHistory = ref([])
  const preservedFeedback = ref(null)


  // ===== 게터 (Getters & Computed) ===== //
  const isQuizMode = computed(() => currentUIMode.value === 'quiz')
  const isChatMode = computed(() => currentUIMode.value === 'chat')


  // ===== 액션 (Actions) ===== //

  /**
   * [ACTION] 새로운 학습 세션을 시작합니다.
   */
  const startNewSession = async () => {
    isContentLoading.value = true
    apiError.value = null
    console.log('ACTION: startNewSession 호출됨')

    _resetSessionState()

    // [수정] computed 속성인 sessionInfo에서 직접 값을 가져옵니다.
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
    isContentLoading.value = false
  }

  /**
   * [ACTION] 사용자 메시지 또는 퀴즈 답변을 서버로 전송합니다.
   */
  const sendMessage = async (message) => {
    isContentLoading.value = true
    apiError.value = null
    console.log(`ACTION: sendMessage 호출됨 (Mode: ${currentUIMode.value})`, { message })

    if (isChatMode.value) {
      chatHistory.value.push({ sender: '나', message, type: 'user' })
    }

    const result = isQuizMode.value
      ? await learningService.submitQuizAnswerV2(message)
      : await learningService.sendSessionMessage(message)

    if (result.success && result.data?.data?.workflow_response) {
      console.log('✅ 메시지/답변 API 성공', result.data)
      _processWorkflowResponse(result.data.data.workflow_response)
    } else {
      const errorMessage = result.error?.message || '알 수 없는 오류가 발생했습니다.'
      console.error('API Error in sendMessage:', errorMessage)
      apiError.value = { message: `요청 처리에 실패했습니다: ${errorMessage}` };
    }
    isContentLoading.value = false
  }
  
  /**
   * [ACTION] 컨텐츠 표시 모드를 변경하는 액션
   */
  const setContentMode = (mode) => {
    console.log(`ACTION: setContentMode 호출됨. 모드 변경: ${contentMode.value} -> ${mode}`)
    contentMode.value = mode
  }


  // ===== 내부 헬퍼 함수 ===== //

  /**
   * [HELPER] 워크플로우 응답을 처리하여 모든 상태를 업데이트합니다.
   */
  const _processWorkflowResponse = (response) => {
    console.log('HELPER: _processWorkflowResponse 처리 시작', response)
    currentAgent.value = response.current_agent || 'session_manager'
    currentUIMode.value = response.ui_mode || 'chat'
    sessionProgressStage.value = response.session_progress_stage || 'unknown'
    
    switch(currentAgent.value) {
      case 'quiz_generator':
        completedSteps.value.quiz = true;
        break;
      case 'evaluation_feedback':
        completedSteps.value.feedback = true;
        break;
    }

    const content = response.content
    if (!content) {
      console.warn('Workflow response에 content가 없습니다.')
      return
    }
    
    switch (content.type) {
      case 'theory':
        mainContent.value = { type: 'theory', data: content }
        quizData.value = null
        _addTutorMessage(content.refined_content || '왼쪽의 학습 내용을 확인해주세요.')
        break
      case 'quiz':
        quizData.value = content
        mainContent.value = { type: 'theory', data: mainContent.value.data }
        _addTutorMessage(content.refined_content || '퀴즈가 준비되었습니다. 오른쪽에서 답변해주세요.')
        break
      case 'qna':
        mainContent.value = { type: 'theory', data: mainContent.value.data }
        _addTutorMessage(content.answer, 'qna')
        break
      default:
        if (response.evaluation_result) {
            mainContent.value = { type: 'feedback', data: response.evaluation_result.feedback }
            preservedFeedback.value = response.evaluation_result.feedback
            quizData.value = null
            _addTutorMessage(response.evaluation_result.feedback.content || '평가가 완료되었습니다. 왼쪽 결과를 확인하고 다음 단계를 진행해주세요.')
        } else if(response.session_completion) {
             _addTutorMessage(response.session_completion.session_summary || '세션이 완료되었습니다. 다음 학습을 시작해주세요.')
        } else {
            console.warn('알 수 없는 컨텐츠 유형 또는 구조:', response)
            _addTutorMessage(content.refined_content || '알 수 없는 응답입니다. 다음 단계로 진행해주세요.')
        }
        break
    }
  }

  /**
   * [HELPER] 튜터 메시지를 채팅 기록에 추가합니다.
   */
  const _addTutorMessage = (message, type = 'system') => {
    if (message) {
      chatHistory.value.push({ sender: '튜터', message, type })
    }
  }

  /**
   * [HELPER] 새로운 세션 시작 시 모든 관련 상태를 초기화합니다.
   */
  const _resetSessionState = () => {
    console.log('HELPER: _resetSessionState 호출됨')
    chatHistory.value = []
    mainContent.value = { type: 'theory', data: null }
    quizData.value = null
    currentUIMode.value = 'chat'
    currentAgent.value = 'session_manager'
    sessionProgressStage.value = 'session_start'
    contentMode.value = 'current'
    completedSteps.value = { theory: true, quiz: false, feedback: false }
    preservedFeedback.value = null
  }

  return {
    // State
    isContentLoading,
    apiError,
    currentUIMode,
    contentMode,
    sessionInfo,
    currentAgent,
    sessionProgressStage,
    completedSteps,
    mainContent,
    quizData,
    chatHistory,
    preservedFeedback,

    // Getters & Computed
    isQuizMode,
    isChatMode,

    // Actions
    startNewSession,
    sendMessage,
    setContentMode,
  }
})