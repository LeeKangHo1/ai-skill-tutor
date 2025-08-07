// frontend/src/composables/useLearning.js
// 학습 관련 컴포저블 - 학습 세션, 진행 상태, 퀴즈 등의 학습 로직을 담당

import { ref, computed } from 'vue'
import { learningService } from '@/services/learningService'
import { useNotification } from './useNotification'

export function useLearning() {
  const { showSuccess, showError } = useNotification()

  // 학습 상태
  const currentSession = ref(null)
  const learningProgress = ref(null)
  const isSessionActive = ref(false)
  const isLoading = ref(false)

  // 현재 학습 단계 (theory, quiz, feedback)
  const currentStep = ref('theory')
  const stepProgress = ref(0)

  // 퀴즈 관련 상태
  const currentQuiz = ref(null)
  const userAnswer = ref('')
  const quizResult = ref(null)

  // 계산된 속성
  const sessionProgress = computed(() => {
    if (!currentSession.value) return 0
    return Math.round((stepProgress.value / 3) * 100)
  })

  const canProceedToNext = computed(() => {
    switch (currentStep.value) {
      case 'theory':
        return true // 이론 학습은 항상 다음 단계로 진행 가능
      case 'quiz':
        return !!quizResult.value // 퀴즈 결과가 있어야 진행 가능
      case 'feedback':
        return true // 피드백 확인 후 세션 완료
      default:
        return false
    }
  })

  // 새 학습 세션 시작
  const startSession = async (chapterId) => {
    try {
      isLoading.value = true
      const response = await learningService.startSession(chapterId)
      
      if (response.success) {
        currentSession.value = response.session
        isSessionActive.value = true
        currentStep.value = 'theory'
        stepProgress.value = 1
        showSuccess('새로운 학습 세션이 시작되었습니다.')
        return { success: true, session: response.session }
      } else {
        showError(response.message || '세션 시작에 실패했습니다.')
        return { success: false, error: response.message }
      }
    } catch (error) {
      console.error('세션 시작 오류:', error)
      showError('세션 시작 중 오류가 발생했습니다.')
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  // 다음 단계로 진행
  const proceedToNext = async () => {
    if (!canProceedToNext.value) return

    try {
      isLoading.value = true

      switch (currentStep.value) {
        case 'theory':
          // 이론 학습 완료 후 퀴즈로 이동
          const quizResponse = await learningService.getQuiz(currentSession.value.id)
          if (quizResponse.success) {
            currentQuiz.value = quizResponse.quiz
            currentStep.value = 'quiz'
            stepProgress.value = 2
          }
          break

        case 'quiz':
          // 퀴즈 완료 후 피드백으로 이동
          currentStep.value = 'feedback'
          stepProgress.value = 3
          break

        case 'feedback':
          // 피드백 확인 후 세션 완료
          await completeSession()
          break
      }
    } catch (error) {
      console.error('단계 진행 오류:', error)
      showError('다음 단계로 진행하는 중 오류가 발생했습니다.')
    } finally {
      isLoading.value = false
    }
  }

  // 퀴즈 답안 제출
  const submitQuizAnswer = async (answer) => {
    if (!currentQuiz.value || !currentSession.value) return

    try {
      isLoading.value = true
      userAnswer.value = answer

      const response = await learningService.submitQuizAnswer(
        currentSession.value.id,
        currentQuiz.value.id,
        answer
      )

      if (response.success) {
        quizResult.value = response.result
        showSuccess('답안이 제출되었습니다.')
        return { success: true, result: response.result }
      } else {
        showError(response.message || '답안 제출에 실패했습니다.')
        return { success: false, error: response.message }
      }
    } catch (error) {
      console.error('답안 제출 오류:', error)
      showError('답안 제출 중 오류가 발생했습니다.')
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  // 학습 세션 완료
  const completeSession = async () => {
    if (!currentSession.value) return

    try {
      isLoading.value = true
      const response = await learningService.completeSession(currentSession.value.id)

      if (response.success) {
        // 학습 진행 상태 업데이트
        learningProgress.value = response.progress
        showSuccess('학습 세션이 완료되었습니다!')
        
        // 상태 초기화
        resetSession()
        
        return { success: true, progress: response.progress }
      } else {
        showError(response.message || '세션 완료 처리에 실패했습니다.')
        return { success: false, error: response.message }
      }
    } catch (error) {
      console.error('세션 완료 오류:', error)
      showError('세션 완료 중 오류가 발생했습니다.')
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  // 학습 진행 상태 조회
  const loadLearningProgress = async () => {
    try {
      isLoading.value = true
      const response = await learningService.getLearningProgress()

      if (response.success) {
        learningProgress.value = response.progress
        return { success: true, progress: response.progress }
      } else {
        return { success: false, error: response.message }
      }
    } catch (error) {
      console.error('학습 진행 상태 조회 오류:', error)
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  // 세션 상태 초기화
  const resetSession = () => {
    currentSession.value = null
    isSessionActive.value = false
    currentStep.value = 'theory'
    stepProgress.value = 0
    currentQuiz.value = null
    userAnswer.value = ''
    quizResult.value = null
  }

  // 질문하기 (QnA)
  const askQuestion = async (question) => {
    if (!currentSession.value) return

    try {
      isLoading.value = true
      const response = await learningService.askQuestion(currentSession.value.id, question)

      if (response.success) {
        return { success: true, answer: response.answer }
      } else {
        showError(response.message || '질문 처리에 실패했습니다.')
        return { success: false, error: response.message }
      }
    } catch (error) {
      console.error('질문 처리 오류:', error)
      showError('질문 처리 중 오류가 발생했습니다.')
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  return {
    // 상태
    currentSession: computed(() => currentSession.value),
    learningProgress: computed(() => learningProgress.value),
    isSessionActive: computed(() => isSessionActive.value),
    isLoading: computed(() => isLoading.value),
    currentStep: computed(() => currentStep.value),
    sessionProgress,
    currentQuiz: computed(() => currentQuiz.value),
    userAnswer: computed(() => userAnswer.value),
    quizResult: computed(() => quizResult.value),
    canProceedToNext,

    // 메서드
    startSession,
    proceedToNext,
    submitQuizAnswer,
    completeSession,
    loadLearningProgress,
    resetSession,
    askQuestion
  }
}