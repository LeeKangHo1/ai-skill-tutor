// frontend/src/stores/learningStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { learningService } from '@/services/learningService'
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'

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
export const useLearningStore = defineStore('learning', () => {
  // 의존성 스토어 및 라우터
  const authStore = useAuthStore()
  const router = useRouter()

  // ===== 상태 (State) ===== //

  // --- UI 및 로딩 상태 ---
  const isLoading = ref(false)
  const loadingMessage = ref('학습 내용을 준비하고 있습니다...')
  const currentUIMode = ref('chat') // 'chat' | 'quiz'

  // --- 세션 상태 ---
  const sessionInfo = ref({
    chapter_number: 1,
    section_number: 1,
  })
  const currentAgent = ref('session_manager')
  const sessionProgressStage = ref('session_start')

  // --- 컨텐츠 상태 ---
  // API 응답을 기반으로 한 통합 컨텐츠 객체
  const mainContent = ref({
    type: 'theory', // 'theory', 'qna', 'feedback'
    data: null,
  })
  const quizData = ref(null) // 퀴즈 데이터는 별도로 관리
  const chatHistory = ref([])

  // ===== 게터 (Getters & Computed) ===== //

  const isQuizMode = computed(() => currentUIMode.value === 'quiz')
  const isChatMode = computed(() => currentUIMode.value === 'chat')
  const hasQuiz = computed(() => quizData.value && quizData.value.question)
  const hasFeedback = computed(() => mainContent.value.type === 'feedback' && mainContent.value.data)

  // ===== 액션 (Actions) - 컴포넌트가 호출하는 공개 API ===== //

  /**
   * [ACTION] 새로운 학습 세션을 시작합니다. (HeaderComponent에서 호출)
   * authStore에서 현재 챕터/섹션 정보를 가져와 API를 호출합니다.
   */
  const startNewSession = async () => {
    isLoading.value = true
    loadingMessage.value = '새로운 학습 세션을 시작합니다...'
    console.log('ACTION: startNewSession 호출됨')

    // 이전 세션 데이터 초기화
    _resetSessionState()

    const chapterNumber = authStore.currentChapter
    const sectionNumber = authStore.currentSection
    const userMessage = `${chapterNumber}챕터 ${sectionNumber}섹션 학습을 시작합니다.`

    const result = await learningService.startLearningSession(
      chapterNumber,
      sectionNumber,
      userMessage
    )

    if (result.success && result.data?.data?.workflow_response) {
      console.log('✅ 세션 시작 API 성공', result.data)
      _processWorkflowResponse(result.data.data.workflow_response)
      // 학습 페이지로 이동
      router.push('/learning')
    } else {
      console.error('API Error in startNewSession:', result.error)
      // TODO: 사용자에게 보여줄 에러 처리 추가
      chatHistory.value.push({
        sender: '시스템',
        message: `세션 시작에 실패했습니다: ${result.error}`,
        type: 'system',
      })
    }
    isLoading.value = false
  }

  /**
   * [ACTION] 사용자 메시지 또는 퀴즈 답변을 서버로 전송합니다.
   * @param {string} message - 사용자 입력 메시지 또는 퀴즈 답변
   */
  const sendMessage = async (message) => {
    if (isLoading.value) return
    isLoading.value = true
    loadingMessage.value = '응답을 기다리고 있습니다...'
    console.log(`ACTION: sendMessage 호출됨 (Mode: ${currentUIMode.value})`, { message })

    // 사용자 메시지를 채팅 기록에 먼저 추가
    if (isChatMode.value) {
      chatHistory.value.push({ sender: '나', message, type: 'user' })
    }

    // 현재 UI 모드에 따라 다른 서비스 호출
    const result = isQuizMode.value
      ? await learningService.submitQuizAnswerV2(message)
      : await learningService.sendSessionMessage(message)

    if (result.success && result.data?.data?.workflow_response) {
      console.log('✅ 메시지/답변 API 성공', result.data)
      _processWorkflowResponse(result.data.data.workflow_response)
    } else {
      console.error('API Error in sendMessage:', result.error)
      chatHistory.value.push({
        sender: '시스템',
        message: `오류가 발생했습니다: ${result.error}`,
        type: 'system',
      })
    }
    isLoading.value = false
  }

  // ===== 내부 헬퍼 함수 (Private Helpers) ===== //

  /**
   * [HELPER] 백엔드의 워크플로우 응답을 처리하여 모든 상태를 업데이트합니다.
   * 이 함수는 모든 상태 변경의 유일한 진입점입니다.
   * @param {object} response - API 응답의 workflow_response 객체
   */
  const _processWorkflowResponse = (response) => {
    console.log('HELPER: _processWorkflowResponse 처리 시작', response)

    // 1. 핵심 상태 업데이트 (Agent, UI Mode, Progress)
    currentAgent.value = response.current_agent || 'session_manager'
    currentUIMode.value = response.ui_mode || 'chat'
    sessionProgressStage.value = response.session_progress_stage || 'unknown'

    // 2. 컨텐츠 처리
    const content = response.content
    if (!content) {
      console.warn('Workflow response에 content가 없습니다.')
      return
    }

    // 3. 컨텐츠 유형에 따라 상태 분기 처리
    switch (content.type) {
      case 'theory':
        mainContent.value = { type: 'theory', data: content }
        quizData.value = null // 이론 설명 시 퀴즈 데이터 초기화
        _addTutorMessage(
          content.refined_content || '왼쪽의 학습 내용을 확인해주세요.'
        )
        break

      case 'quiz':
        quizData.value = content
        mainContent.value = { type: 'theory', data: mainContent.value.data } // 이론 내용을 배경으로 유지
        _addTutorMessage(
          content.refined_content || '퀴즈가 준비되었습니다. 오른쪽에서 답변해주세요.'
        )
        break

      case 'qna':
        mainContent.value = { type: 'theory', data: mainContent.value.data } // 이론 내용을 배경으로 유지
        _addTutorMessage(content.answer, 'qna')
        break
        
      default:
        // 'feedback' 또는 기타 content.type이 없는 경우 (e.g., session_completion)
        if (response.evaluation_result) {
            mainContent.value = { type: 'feedback', data: response.evaluation_result.feedback }
            quizData.value = null // 평가 완료 후 퀴즈 데이터 초기화
            _addTutorMessage(
                response.evaluation_result.feedback.content || '평가가 완료되었습니다. 왼쪽 결과를 확인하고 다음 단계를 진행해주세요.'
            )
        } else if(response.session_completion) {
             _addTutorMessage(
                response.session_completion.session_summary || '세션이 완료되었습니다. 다음 학습을 시작해주세요.'
            )
            // TODO: 세션 완료 후 다음 챕터/섹션 정보 업데이트 로직 추가
        } else {
            console.warn('알 수 없는 컨텐츠 유형 또는 구조:', response)
            _addTutorMessage(content.refined_content || '알 수 없는 응답입니다. 다음 단계로 진행해주세요.')
        }
        break
    }
    console.log('HELPER: _processWorkflowResponse 처리 완료. 최종 상태:', {
        uiMode: currentUIMode.value,
        mainContent: mainContent.value,
        quizData: quizData.value,
        chatHistory: chatHistory.value
    })
  }

  /**
   * [HELPER] 튜터 메시지를 채팅 기록에 추가합니다.
   * @param {string} message - 튜터가 보낸 메시지
   * @param {string} type - 메시지 유형 ('system' | 'qna')
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
  }

  return {
    // State
    isLoading,
    loadingMessage,
    currentUIMode,
    sessionInfo,
    currentAgent,
    sessionProgressStage,
    mainContent,
    quizData,
    chatHistory,

    // Getters & Computed
    isQuizMode,
    isChatMode,
    hasQuiz,
    hasFeedback,

    // Actions
    startNewSession,
    sendMessage,
  }
})