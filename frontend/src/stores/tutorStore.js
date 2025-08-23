// frontend/src/stores/tutorStore.js
// UI 상태 관리 전용 Pinia Store
// learningStore와 분리하여 UI 관련 상태만 관리하고 learningStore와 연동

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useLearningStore } from './learningStore.js'

export const useTutorStore = defineStore('tutor', () => {
  // learningStore 인스턴스 (연동용)
  const learningStore = useLearningStore()
  
  // ===== UI 상태 관리 =====
  
  // 현재 활성 에이전트 (UI 표시용)
  const currentAgent = ref('theory_educator')
  
  // UI 모드 ('chat' | 'quiz')
  const currentUIMode = ref('chat')
  
  // 컨텐츠 모드 ('current' | 'review_theory' | 'review_quiz')
  const currentContentMode = ref('current')
  
  // 사용자 의도
  const userIntent = ref('')
  
  // 세션 진행 단계 (UI 표시용)
  const sessionProgressStage = ref('session_start')
  
  // 완료된 단계 (UI 진행률 표시용)
  const completedSteps = ref({
    theory: true,
    quiz: false,
    feedback: false
  })
  
  // ===== UI 컨텐츠 데이터 =====
  
  // 메인 컨텐츠 데이터 (UI 표시용)
  const mainContent = ref({
    agent_name: 'theory_educator',
    content_type: 'theory',
    title: 'LLM(Large Language Model)이란?',
    content: '',
    metadata: {}
  })
  
  // 채팅 히스토리 (UI 표시용)
  const chatHistory = ref([
    {
      sender: '튜터',
      message: 'LLM에 대해 학습해보겠습니다. 위 내용을 확인해주세요!',
      type: 'system',
      timestamp: new Date()
    }
  ])
  
  // 퀴즈 데이터 (UI 표시용)
  const quizData = ref({
    question: '',
    type: 'multiple_choice',
    options: [],
    hint: '',
    correct_answer: '',
    user_answer: ''
  })
  
  // 현재 퀴즈 상태 (UI 상태용)
  const currentQuizInfo = ref({
    quiz_type: 'multiple_choice',
    is_quiz_active: false,
    is_answer_submitted: false,
    hint_usage_count: 0,
    score: null
  })
  
  // ===== learningStore 연동 메서드 (watch 이전에 정의) =====
  
  /**
   * learningStore의 워크플로우 응답을 받아서 UI 상태 업데이트
   * @param {Object} workflowResponse - learningStore의 워크플로우 응답
   */
  const updateFromWorkflowResponse = (workflowResponse) => {
    if (!workflowResponse) return
    
    console.log('워크플로우 응답으로 UI 상태 업데이트:', workflowResponse)
    
    // 에이전트 상태 동기화
    if (workflowResponse.current_agent) {
      updateAgent(workflowResponse.current_agent)
    }
    
    // UI 모드 동기화
    if (workflowResponse.ui_mode) {
      updateUIMode(workflowResponse.ui_mode)
    }
    
    // 세션 진행 단계 동기화
    if (workflowResponse.session_progress_stage) {
      updateSessionProgress(workflowResponse.session_progress_stage)
    }
    
    // 컨텐츠 처리
    if (workflowResponse.content) {
      processWorkflowContent(workflowResponse.content)
    }
    
    // 평가 결과 처리
    if (workflowResponse.evaluation_result) {
      processEvaluationResult(workflowResponse.evaluation_result)
    }
  }

  // ===== learningStore 연동 감시자 =====
  
  // learningStore의 워크플로우 상태 변화 감시 및 UI 상태 동기화
  watch(
    () => learningStore.workflowState,
    (newWorkflowState) => {
      if (newWorkflowState && Object.keys(newWorkflowState).length > 0) {
        console.log('learningStore 워크플로우 상태 변화 감지:', newWorkflowState)
        updateFromWorkflowResponse(newWorkflowState)
      }
    },
    { deep: true, immediate: true }
  )
  
  // learningStore의 세션 상태 변화 감시
  watch(
    () => learningStore.sessionState,
    (newSessionState) => {
      if (newSessionState && newSessionState.is_active) {
        console.log('learningStore 세션 상태 변화 감지:', newSessionState)
        // 세션 정보가 변경되면 UI 초기화
        if (newSessionState.chapter_number && newSessionState.section_number) {
          initializeSessionUI(newSessionState)
        }
      }
    },
    { deep: true, immediate: true }
  )
  
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
  
  // 세션 완료 조건 확인
  const isSessionReadyToComplete = computed(() => {
    // 모든 단계가 완료되었고, 피드백 단계까지 도달한 경우
    return completedSteps.value.theory && 
           completedSteps.value.quiz && 
           completedSteps.value.feedback &&
           sessionProgressStage.value === 'quiz_and_feedback_completed'
  })
  
  // learningStore 연동 상태 확인
  const isConnectedToLearningStore = computed(() => {
    return learningStore.isSessionActive && learningStore.workflowState.current_agent !== null
  })
  
  // 통합 세션 정보 (learningStore 우선)
  const sessionInfo = computed(() => {
    if (learningStore.isSessionActive) {
      return {
        session_id: learningStore.sessionState.session_id,
        chapter_number: learningStore.sessionState.chapter_number,
        section_number: learningStore.sessionState.section_number,
        chapter_title: learningStore.sessionState.chapter_title,
        section_title: learningStore.sessionState.section_title,
        estimated_duration: learningStore.sessionState.estimated_duration,
        is_active: learningStore.sessionState.is_active
      }
    }
    return {
      session_id: null,
      chapter_number: null,
      section_number: null,
      chapter_title: '',
      section_title: '',
      estimated_duration: '',
      is_active: false
    }
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
      active: currentAgent.value === 'evaluation_feedback_agent',
      completed: completedSteps.value.feedback
    }
  ])
  
  // ===== UI 액션 메서드 =====
  
  // 에이전트 업데이트 (UI 상태만)
  const updateAgent = (agentName) => {
    console.log(`UI 에이전트 업데이트: ${currentAgent.value} → ${agentName}`)
    currentAgent.value = agentName
    
    // 에이전트별 UI 기본 설정
    switch (agentName) {
      case 'theory_educator':
        currentUIMode.value = 'chat'
        break
      case 'quiz_generator':
        currentUIMode.value = 'quiz'
        completedSteps.value.theory = true
        break
      case 'evaluation_feedback_agent':
        currentUIMode.value = 'chat'
        completedSteps.value.quiz = true
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
  
  // 세션 진행 단계 업데이트 (UI 표시용)
  const updateSessionProgress = (stage) => {
    console.log(`UI 세션 진행 단계 업데이트: ${sessionProgressStage.value} → ${stage}`)
    sessionProgressStage.value = stage
  }
  
  // 완료된 단계 업데이트
  const updateCompletedSteps = (steps) => {
    completedSteps.value = { ...completedSteps.value, ...steps }
  }
  
  // 메인 컨텐츠 업데이트
  const updateMainContent = (content) => {
    mainContent.value = { ...mainContent.value, ...content }
  }
  
  // 채팅 히스토리 업데이트
  const updateChatHistory = (history) => {
    if (Array.isArray(history)) {
      chatHistory.value = history
    }
  }
  
  // 채팅 메시지 추가
  const addChatMessage = (message) => {
    chatHistory.value.push({
      ...message,
      timestamp: message.timestamp || new Date()
    })
  }
  
  // 퀴즈 데이터 업데이트
  const updateQuizData = (quiz) => {
    quizData.value = { ...quizData.value, ...quiz }
  }
  
  // 퀴즈 상태 업데이트
  const updateQuizInfo = (info) => {
    currentQuizInfo.value = { ...currentQuizInfo.value, ...info }
  }
  
  // 사용자 답변 업데이트
  const updateUserAnswer = (answer) => {
    quizData.value.user_answer = answer
  }
  
  // ===== learningStore 연동 메서드 (중복 제거됨) =====
  
  /**
   * 워크플로우 컨텐츠를 UI에 맞게 처리
   * @param {Object} content - 워크플로우 컨텐츠
   */
  const processWorkflowContent = (content) => {
    if (!content || !content.type) return
    
    console.log('워크플로우 컨텐츠 처리:', content)
    
    switch (content.type) {
      case 'theory':
        // 이론 컨텐츠를 메인 컨텐츠와 채팅에 추가
        updateMainContent({
          agent_name: currentAgent.value,
          content_type: 'theory',
          title: content.title || '이론 학습',
          content: content.content || '',
          metadata: content
        })
        
        if (content.content) {
          addChatMessage({
            sender: '튜터',
            message: content.content,
            type: 'theory',
            metadata: content
          })
        }
        break
        
      case 'quiz':
        // 퀴즈 데이터 업데이트
        updateQuizData({
          question: content.question || '',
          type: content.quiz_type || 'multiple_choice',
          options: content.options || [],
          hint: content.hint || '',
          correct_answer: content.correct_answer || '',
          user_answer: ''
        })
        
        updateQuizInfo({
          quiz_type: content.quiz_type || 'multiple_choice',
          is_quiz_active: true,
          is_answer_submitted: false,
          hint_usage_count: 0,
          score: null
        })
        break
        
      case 'feedback':
        // 피드백을 채팅에 추가
        if (content.content) {
          addChatMessage({
            sender: '튜터',
            message: content.content,
            type: 'feedback',
            metadata: content
          })
        }
        break
        
      case 'qna':
        // Q&A 응답을 채팅에 추가
        if (content.content) {
          addChatMessage({
            sender: '튜터',
            message: content.content,
            type: 'qna',
            metadata: content
          })
        }
        break
        
      default:
        console.warn('알 수 없는 컨텐츠 타입:', content.type)
    }
  }
  
  /**
   * 평가 결과를 UI에 반영
   * @param {Object} evaluationResult - 평가 결과
   */
  const processEvaluationResult = (evaluationResult) => {
    if (!evaluationResult) return
    
    console.log('평가 결과 처리:', evaluationResult)
    
    // 퀴즈 상태 업데이트
    updateQuizInfo({
      is_answer_submitted: true,
      score: evaluationResult.score || 0
    })
    
    // 피드백 메시지 추가
    if (evaluationResult.feedback) {
      addChatMessage({
        sender: '튜터',
        message: evaluationResult.feedback,
        type: 'evaluation',
        metadata: {
          is_correct: evaluationResult.is_correct,
          score: evaluationResult.score,
          explanation: evaluationResult.explanation
        }
      })
    }
  }
  
  /**
   * learningStore 세션 시작 시 UI 초기화
   * @param {Object} sessionState - learningStore의 세션 상태
   */
  const initializeSessionUI = (sessionState) => {
    console.log('세션 시작으로 UI 초기화:', sessionState)
    
    // UI 상태 초기화
    currentAgent.value = 'theory_educator'
    currentUIMode.value = 'chat'
    currentContentMode.value = 'current'
    sessionProgressStage.value = 'session_start'
    userIntent.value = ''
    
    // 완료 단계 초기화
    completedSteps.value = {
      theory: false,
      quiz: false,
      feedback: false
    }
    
    // 채팅 히스토리 초기화
    chatHistory.value = [
      {
        sender: '튜터',
        message: `${sessionState.chapter_title} - ${sessionState.section_title} 학습을 시작합니다!`,
        type: 'system',
        timestamp: new Date()
      }
    ]
    
    // 퀴즈 데이터 초기화
    quizData.value = {
      question: '',
      type: 'multiple_choice',
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
  }
  
  // ===== UI 초기화 메서드 =====
  
  /**
   * UI 상태 초기화 (learningStore와 독립적)
   * @param {Object} sessionData - 세션 데이터 (선택적)
   */
  const initializeSession = (sessionData = {}) => {
    console.log('UI 세션 초기화 시작')
    
    // 기본 UI 상태 설정
    currentAgent.value = 'theory_educator'
    currentUIMode.value = 'chat'
    currentContentMode.value = 'current'
    sessionProgressStage.value = 'session_start'
    userIntent.value = ''
    
    // 완료 단계 초기화
    completedSteps.value = {
      theory: false,
      quiz: false,
      feedback: false
    }
    
    // 채팅 히스토리 초기화
    const welcomeMessage = sessionData.chapter_title 
      ? `${sessionData.chapter_title} 학습을 시작합니다!`
      : 'LLM에 대해 학습해보겠습니다. 위 내용을 확인해주세요!'
    
    chatHistory.value = [
      {
        sender: '튜터',
        message: welcomeMessage,
        type: 'system',
        timestamp: new Date()
      }
    ]
    
    // 퀴즈 데이터 초기화
    resetQuizData()
    
    console.log('UI 세션 초기화 완료', {
      agent: currentAgent.value,
      uiMode: currentUIMode.value
    })
  }
  
  /**
   * UI 상태 완전 리셋
   */
  const resetSession = () => {
    console.log('UI 세션 리셋')
    
    currentAgent.value = 'theory_educator'
    currentUIMode.value = 'chat'
    currentContentMode.value = 'current'
    sessionProgressStage.value = 'session_start'
    userIntent.value = ''
    
    completedSteps.value = {
      theory: false,
      quiz: false,
      feedback: false
    }
    
    chatHistory.value = [
      {
        sender: '튜터',
        message: 'LLM에 대해 학습해보겠습니다. 위 내용을 확인해주세요!',
        type: 'system',
        timestamp: new Date()
      }
    ]
    
    resetQuizData()
  }
  
  /**
   * 퀴즈 데이터 초기화
   */
  const resetQuizData = () => {
    quizData.value = {
      question: '',
      type: 'multiple_choice',
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
  }
  
  // ===== 디버그 및 유틸리티 메서드 =====
  
  /**
   * 현재 UI 상태 정보 반환
   */
  const getStateInfo = () => {
    return {
      currentAgent: currentAgent.value,
      currentUIMode: currentUIMode.value,
      currentContentMode: currentContentMode.value,
      sessionProgressStage: sessionProgressStage.value,
      completedSteps: completedSteps.value,
      sessionInfo: sessionInfo.value,
      isConnectedToLearningStore: isConnectedToLearningStore.value,
      learningStoreStatus: {
        isSessionActive: learningStore.isSessionActive,
        isLoading: learningStore.isLoading,
        hasError: learningStore.hasError
      }
    }
  }
  
  /**
   * learningStore와의 연동 상태 확인
   */
  const checkLearningStoreConnection = () => {
    const connection = {
      isConnected: isConnectedToLearningStore.value,
      sessionActive: learningStore.isSessionActive,
      currentAgent: learningStore.workflowState.current_agent,
      uiMode: learningStore.workflowState.ui_mode,
      syncStatus: {
        agentSync: currentAgent.value === learningStore.workflowState.current_agent,
        uiModeSync: currentUIMode.value === learningStore.workflowState.ui_mode,
        progressSync: sessionProgressStage.value === learningStore.workflowState.session_progress_stage
      }
    }
    
    console.log('learningStore 연동 상태:', connection)
    return connection
  }
  
  // ===== Store 반환 =====
  
  return {
    // UI 상태
    currentAgent,
    currentUIMode,
    currentContentMode,
    userIntent,
    sessionProgressStage,
    completedSteps,
    mainContent,
    chatHistory,
    quizData,
    currentQuizInfo,
    
    // 컴퓨티드 (UI 관련)
    isQuizMode,
    isChatMode,
    isSessionStart,
    isTheoryCompleted,
    isQuizAndFeedbackCompleted,
    canAskQuestion,
    canProceedNext,
    isSessionReadyToComplete,
    sessionSteps,
    
    // learningStore 연동 컴퓨티드
    isConnectedToLearningStore,
    sessionInfo,
    
    // UI 액션
    updateAgent,
    updateUIMode,
    updateContentMode,
    updateSessionProgress,
    updateCompletedSteps,
    updateMainContent,
    updateChatHistory,
    addChatMessage,
    updateQuizData,
    updateQuizInfo,
    updateUserAnswer,
    
    // learningStore 연동 액션
    updateFromWorkflowResponse,
    updateWorkflowResponse: updateFromWorkflowResponse, // 별칭 추가
    processWorkflowContent,
    processEvaluationResult,
    initializeSessionUI,
    
    // 초기화 액션
    initializeSession,
    resetSession,
    resetQuizData,
    
    // 에러 처리
    setError: (error) => {
      console.error('tutorStore 에러 설정:', error)
      // 에러를 채팅 히스토리에 추가
      addChatMessage({
        sender: '시스템',
        message: typeof error === 'string' ? error : '오류가 발생했습니다.',
        type: 'system',
        timestamp: new Date()
      })
    },
    
    // 디버그 및 유틸리티
    getStateInfo,
    checkLearningStoreConnection
  }
})