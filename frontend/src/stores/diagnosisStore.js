// frontend/src/stores/diagnosisStore.js
// 진단 관련 상태 관리

import { defineStore } from 'pinia'
import { getDiagnosisQuestions, submitDiagnosisAnswers } from '@/services/diagnosisService'

export const useDiagnosisStore = defineStore('diagnosis', {
  state: () => ({
    // 진단 문항 관련
    questions: [],
    totalQuestions: 0,
    
    // 진행 상태
    currentQuestionIndex: 0,
    answers: [],
    
    // 결과
    diagnosisResult: null,
    userType: null,
    
    // UI 상태
    isLoading: false,
    error: null,
    isCompleted: false
  }),

  getters: {
    // 현재 문항
    currentQuestion: (state) => {
      return state.questions[state.currentQuestionIndex] || null
    },
    
    // 진행률 계산
    progressPercentage: (state) => {
      if (state.totalQuestions === 0) return 0
      return Math.round((state.currentQuestionIndex / state.totalQuestions) * 100)
    },
    
    // 마지막 문항 여부
    isLastQuestion: (state) => {
      return state.currentQuestionIndex === state.totalQuestions - 1
    },
    
    // 모든 문항 답변 완료 여부
    isAllAnswered: (state) => {
      return state.answers.length === state.totalQuestions
    }
  },

  actions: {
    /**
     * 진단 문항 로드
     */
    async loadQuestions() {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await getDiagnosisQuestions()
        
        if (response.success) {
          this.questions = response.data.questions
          this.totalQuestions = response.data.total_questions
        } else {
          throw new Error(response.error?.message || '문항 로드 실패')
        }
      } catch (error) {
        this.error = error.message
        console.error('문항 로드 실패:', error)
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 답변 저장
     * @param {number} questionId - 문항 ID
     * @param {string} answer - 답변 값
     */
    saveAnswer(questionId, answer) {
      const existingIndex = this.answers.findIndex(a => a.question_id === questionId)
      
      if (existingIndex >= 0) {
        // 기존 답변 업데이트
        this.answers[existingIndex].answer = answer
      } else {
        // 새 답변 추가
        this.answers.push({ question_id: questionId, answer })
      }
    },

    /**
     * 다음 문항으로 이동
     */
    nextQuestion() {
      if (this.currentQuestionIndex < this.totalQuestions - 1) {
        this.currentQuestionIndex++
      }
    },

    /**
     * 이전 문항으로 이동
     */
    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
      }
    },

    /**
     * 특정 문항으로 이동
     * @param {number} index - 문항 인덱스
     */
    goToQuestion(index) {
      if (index >= 0 && index < this.totalQuestions) {
        this.currentQuestionIndex = index
      }
    },

    /**
     * 진단 결과 제출
     */
    async submitDiagnosis() {
      if (!this.isAllAnswered) {
        this.error = '모든 문항에 답변해주세요.'
        return false
      }

      this.isLoading = true
      this.error = null

      try {
        const response = await submitDiagnosisAnswers(this.answers)
        
        if (response.success) {
          this.diagnosisResult = response.data
          // 여기서는 완료 상태로 설정하지 않음 (유형 선택 필요)
          return true
        } else {
          throw new Error(response.error?.message || '진단 제출 실패')
        }
      } catch (error) {
        this.error = error.message
        console.error('진단 제출 실패:', error)
        return false
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 사용자 유형 선택
     * @param {string} selectedType - 선택한 유형 ('beginner' | 'advanced')
     */
    async selectUserType(selectedType) {
      this.isLoading = true
      this.error = null

      try {
        const response = await selectUserType(selectedType)
        
        if (response.success) {
          this.userType = selectedType
          this.isCompleted = true
          return true
        } else {
          throw new Error(response.error?.message || '유형 선택 실패')
        }
      } catch (error) {
        this.error = error.message
        console.error('유형 선택 실패:', error)
        return false
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 진단 결과만 초기화 (답변은 유지)
     */
    clearResult() {
      this.diagnosisResult = null
      this.isCompleted = false
      // 답변은 유지 - isAllAnswered getter에서 diagnosisResult 존재 시 false 반환
    },

    /**
     * 진단 상태 초기화
     */
    resetDiagnosis() {
      this.questions = []
      this.totalQuestions = 0
      this.currentQuestionIndex = 0
      this.answers = []
      this.diagnosisResult = null
      this.userType = null
      this.isLoading = false
      this.error = null
      this.isCompleted = false
    }
  }
})