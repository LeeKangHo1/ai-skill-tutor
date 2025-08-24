// frontend/src/stores/learningStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useLearningStore = defineStore('learning', () => {
  // ===== 기본 상태 =====
  
  // 현재 활성 에이전트
  const currentAgent = ref('theory_educator')
  
  // UI 모드 ('chat' | 'quiz')
  const currentUIMode = ref('chat')
  
  // 컨텐츠 모드 ('current' | 'review_theory' | 'review_quiz')
  const currentContentMode = ref('current')
  
  // 사용자 의도
  const userIntent = ref('')
  
  // 세션 진행 단계
  const sessionProgressStage = ref('session_start')
  
  // 완료된 단계
  const completedSteps = ref({
    theory: true,
    quiz: false,
    feedback: false
  })
  
  // ===== 세션 정보 =====
  
  // 현재 세션 정보
  const sessionInfo = ref({
    session_id: null,
    chapter_number: 2,
    section_number: 1,
    chapter_title: 'LLM이란 무엇인가',
    section_title: 'LLM의 기본 개념',
    user_type: 'beginner'
  })
  
  // ===== 컨텐츠 데이터 =====
  
  // 메인 컨텐츠 데이터
  const mainContent = ref({
    agent_name: 'theory_educator',
    content_type: 'theory',
    title: 'LLM(Large Language Model)이란?',
    content: '',
    metadata: {}
  })
  
  // API 응답 데이터 (캐시 없이 실시간 데이터만 사용)
  const currentApiResponse = ref(null)
  
  // 채팅 히스토리 (세션별로 새로 시작, 이전 대화 저장하지 않음)
  const chatHistory = ref([])
  
  // 퀴즈 데이터 (초기값은 완전히 비워둠)
  const quizData = ref({
    question: '',
    type: '',
    options: [],
    hint: '',
    correct_answer: '',
    user_answer: ''
  })
  
  // 현재 퀴즈 상태
  const currentQuizInfo = ref({
    quiz_type: 'multiple_choice',
    is_quiz_active: false,
    is_answer_submitted: false,
    hint_usage_count: 0,
    score: null
  })
  
  // 워크플로우 응답
  const lastWorkflowResponse = ref({
    current_agent: 'theory_educator',
    session_progress_stage: 'session_start',
    ui_mode: 'chat',
    content: {},
    metadata: {}
  })
  
  // ===== 컴퓨티드 속성 =====
  
  // UI 모드 판단
  const isQuizMode = computed(() => currentUIMode.value === 'quiz')
  const isChatMode = computed(() => currentUIMode.value === 'chat')
  
  // 세션 단계 판단
  const isSessionStart = computed(() => sessionProgressStage.value === 'session_start')
  const isTheoryCompleted = computed(() => sessionProgressStage.value === 'theory_completed')
  const isQuizAndFeedbackCompleted = computed(() => sessionProgressStage.value === 'quiz_and_feedback_completed')
  
  // 사용자 액션 가능 여부
  const canAskQuestion = computed(() => {
    return ['theory_completed', 'quiz_and_feedback_completed'].includes(sessionProgressStage.value)
  })
  
  const canProceedNext = computed(() => {
    return ['theory_completed', 'quiz_and_feedback_completed'].includes(sessionProgressStage.value)
  })
  
  // 진행 단계 표시용 데이터
  const sessionSteps = computed(() => [
    {
      name: '이론',
      key: 'theory',
      active: currentAgent.value === 'theory_educator' || currentAgent.value === 'qna_resolver',
      completed: completedSteps.value.theory
    },
    {
      name: '퀴즈',
      key: 'quiz', 
      active: currentAgent.value === 'quiz_generator',
      completed: completedSteps.value.quiz
    },
    {
      name: '풀이',
      key: 'feedback',
      active: currentAgent.value === 'evaluation_feedback',
      completed: completedSteps.value.feedback
    }
  ])
  
  // ===== 액션 메서드 =====
  
  // 에이전트 업데이트
  const updateAgent = (agentName) => {
    console.log(`에이전트 업데이트: ${currentAgent.value} → ${agentName}`)
    currentAgent.value = agentName
    
    // 에이전트별 기본 설정
    switch (agentName) {
      case 'theory_educator':
        currentUIMode.value = 'chat'
        sessionProgressStage.value = 'theory_completed'
        break
      case 'quiz_generator':
        currentUIMode.value = 'quiz'
        sessionProgressStage.value = 'theory_completed'
        completedSteps.value.quiz = true
        break
      case 'evaluation_feedback':
        currentUIMode.value = 'chat'
        sessionProgressStage.value = 'quiz_and_feedback_completed'
        completedSteps.value.feedback = true
        break
      case 'qna_resolver':
        currentUIMode.value = 'chat'
        // 진행 단계는 변경하지 않음
        break
    }
  }
  
  // UI 모드 업데이트
  const updateUIMode = (mode) => {
    console.log(`UI 모드 업데이트: ${currentUIMode.value} → ${mode}`)
    currentUIMode.value = mode
  }
  
  // 컨텐츠 모드 업데이트
  const updateContentMode = (mode) => {
    console.log(`컨텐츠 모드 업데이트: ${currentContentMode.value} → ${mode}`)
    currentContentMode.value = mode
  }
  
  // 세션 진행 단계 업데이트
  const updateSessionProgress = (stage) => {
    console.log(`세션 진행 단계 업데이트: ${sessionProgressStage.value} → ${stage}`)
    sessionProgressStage.value = stage
  }
  
  // 완료된 단계 업데이트
  const updateCompletedSteps = (steps) => {
    completedSteps.value = { ...completedSteps.value, ...steps }
  }
  
  // 세션 정보 업데이트
  const updateSessionInfo = (info) => {
    sessionInfo.value = { ...sessionInfo.value, ...info }
  }
  
  // 메인 컨텐츠 업데이트
  const updateMainContent = (content) => {
    mainContent.value = { ...mainContent.value, ...content }
  }
  
  // API 응답 데이터 업데이트 (캐시 없이 현재 데이터만 저장)
  const updateCurrentApiResponse = (data) => {
    currentApiResponse.value = data
    console.log('현재 API 응답 데이터 업데이트:', data)
  }
  
  // 현재 API 응답 데이터 조회
  const getCurrentApiResponse = () => {
    return currentApiResponse.value
  }
  
  // API 응답 데이터 초기화
  const clearCurrentApiResponse = () => {
    currentApiResponse.value = null
    console.log('API 응답 데이터 초기화됨')
  }
  
  // 채팅 히스토리 업데이트 (기존 히스토리 완전 대체)
  const updateChatHistory = (history) => {
    if (Array.isArray(history)) {
      chatHistory.value = [...history] // 새로운 배열로 완전 대체
    }
  }

  // 채팅 히스토리 완전 초기화
  const clearChatHistory = () => {
    chatHistory.value = []
    console.log('채팅 히스토리 완전 초기화됨')
  }
  
  // 채팅 메시지 추가
  const addChatMessage = (message) => {
    chatHistory.value.push({
      ...message,
      timestamp: message.timestamp || new Date()
    })
  }
  
  // 퀴즈 데이터 업데이트 (기존 데이터 완전 대체)
  const updateQuizData = (quiz) => {
    // 캐시 없이 새로운 데이터로 완전 대체
    quizData.value = {
      question: quiz.question || '',
      type: quiz.type || '',
      options: quiz.options || [],
      hint: quiz.hint || '',
      correct_answer: quiz.correct_answer || '',
      user_answer: quiz.user_answer || ''
    }
  }

  // 퀴즈 데이터 완전 초기화
  const clearQuizData = () => {
    quizData.value = {
      question: '',
      type: '',
      options: [],
      hint: '',
      correct_answer: '',
      user_answer: ''
    }
    currentQuizInfo.value = {
      quiz_type: 'multiple_choice',
      is_quiz_active: false,
      is_answer_submitted: false,
      hint_usage_count: 0,
      score: null
    }
    console.log('퀴즈 데이터 완전 초기화됨')
  }

  // API 응답에서 퀴즈 데이터 저장 (캐시 없이 새로운 데이터로 대체)
  const setQuizDataFromAPI = (apiResponse) => {
    // 기존 퀴즈 데이터 완전 초기화
    clearQuizData()
    
    if (apiResponse?.workflow_response?.content) {
      const content = apiResponse.workflow_response.content
      
      // 새로운 퀴즈 데이터 매핑
      const mappedQuizData = {
        question: content.question || '',
        type: content.quiz_type || 'multiple_choice',
        options: content.options || [],
        hint: content.hint || '',
        correct_answer: content.correct_answer || '',
        user_answer: ''
      }
      
      // 새로운 퀴즈 데이터로 완전 대체
      quizData.value = mappedQuizData
      
      // 새로운 퀴즈 상태 설정
      currentQuizInfo.value = {
        quiz_type: mappedQuizData.type,
        is_quiz_active: true,
        is_answer_submitted: false,
        hint_usage_count: 0,
        score: null
      }
      
      console.log('새로운 퀴즈 데이터로 완전 대체:', mappedQuizData)
      return mappedQuizData
    }
    return null
  }
  
  // 퀴즈 상태 업데이트
  const updateQuizInfo = (info) => {
    currentQuizInfo.value = { ...currentQuizInfo.value, ...info }
  }
  
  // 사용자 답변 업데이트
  const updateUserAnswer = (answer) => {
    quizData.value.user_answer = answer
  }
  
  // 워크플로우 응답 업데이트
  const updateWorkflowResponse = (response) => {
    lastWorkflowResponse.value = { ...lastWorkflowResponse.value, ...response }
    
    // 워크플로우 응답에 따른 상태 동기화
    if (response.current_agent) {
      updateAgent(response.current_agent)
    }
    if (response.ui_mode) {
      updateUIMode(response.ui_mode)
    }
    if (response.session_progress_stage) {
      updateSessionProgress(response.session_progress_stage)
    }
  }
  
  // ===== 초기화 메서드 =====
  
  // 세션 초기화
  const initializeSession = (sessionData = {}) => {
    console.log('세션 초기화 시작')
    
    // 기본값 설정
    currentAgent.value = 'theory_educator'
    currentUIMode.value = 'chat'
    currentContentMode.value = 'current'
    sessionProgressStage.value = 'session_start'
    
    // 세션 정보 설정
    if (sessionData.chapter_number) {
      sessionInfo.value.chapter_number = sessionData.chapter_number
    }
    if (sessionData.section_number) {
      sessionInfo.value.section_number = sessionData.section_number
    }
    
    // 완료 단계 초기화
    completedSteps.value = {
      theory: true, // 이론은 기본적으로 시작 시 완료로 설정
      quiz: false,
      feedback: false
    }
    
    console.log('세션 초기화 완료', {
      agent: currentAgent.value,
      uiMode: currentUIMode.value,
      sessionInfo: sessionInfo.value
    })
  }
  
  // 세션 완전 리셋 (모든 캐시 데이터 삭제)
  const resetSession = () => {
    console.log('세션 완전 리셋 - 모든 데이터 초기화')
    
    currentAgent.value = 'theory_educator'
    currentUIMode.value = 'chat'
    currentContentMode.value = 'current'
    sessionProgressStage.value = 'session_start'
    userIntent.value = ''
    
    completedSteps.value = {
      theory: true,
      quiz: false,
      feedback: false
    }
    
    // 모든 데이터 완전 초기화
    clearChatHistory()
    clearQuizData()
    clearCurrentApiResponse()
    
    mainContent.value = {
      agent_name: 'theory_educator',
      content_type: 'theory',
      title: 'LLM(Large Language Model)이란?',
      content: '',
      metadata: {}
    }
    
    lastWorkflowResponse.value = {
      current_agent: 'theory_educator',
      session_progress_stage: 'session_start',
      ui_mode: 'chat',
      content: {},
      metadata: {}
    }
  }

  // 모든 데이터 완전 초기화
  const clearAllData = () => {
    console.log('모든 store 데이터 완전 초기화')
    clearChatHistory()
    clearQuizData()
    clearCurrentApiResponse()
    
    mainContent.value = {
      agent_name: '',
      content_type: '',
      title: '',
      content: '',
      metadata: {}
    }
  }
  
  // ===== 디버그 메서드 =====
  
  // 현재 상태 정보
  const getStateInfo = () => {
    return {
      currentAgent: currentAgent.value,
      currentUIMode: currentUIMode.value,
      currentContentMode: currentContentMode.value,
      sessionProgressStage: sessionProgressStage.value,
      completedSteps: completedSteps.value,
      sessionInfo: sessionInfo.value
    }
  }
  
  // Store 반환
  return {
    // 상태
    currentAgent,
    currentUIMode,
    currentContentMode,
    userIntent,
    sessionProgressStage,
    completedSteps,
    sessionInfo,
    mainContent,
    chatHistory,
    quizData,
    currentQuizInfo,
    lastWorkflowResponse,
    currentApiResponse,
    
    // 컴퓨티드
    isQuizMode,
    isChatMode,
    isSessionStart,
    isTheoryCompleted,
    isQuizAndFeedbackCompleted,
    canAskQuestion,
    canProceedNext,
    sessionSteps,
    
    // 액션
    updateAgent,
    updateUIMode,
    updateContentMode,
    updateSessionProgress,
    updateCompletedSteps,
    updateSessionInfo,
    updateMainContent,
    updateChatHistory,
    clearChatHistory,
    addChatMessage,
    updateQuizData,
    clearQuizData,
    setQuizDataFromAPI,
    updateQuizInfo,
    updateUserAnswer,
    updateWorkflowResponse,
    initializeSession,
    resetSession,
    clearAllData,
    getStateInfo,
    updateCurrentApiResponse,
    getCurrentApiResponse,
    clearCurrentApiResponse
  }
})