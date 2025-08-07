<!-- frontend/src/views/DiagnosisPage.vue -->
<!-- 사용자 진단 페이지 -->

<template>
  <div class="diagnosis-page">
    <div class="container">
      <!-- 페이지 헤더 -->
      <div class="page-header">
        <h1>사용자 진단</h1>
        <p>몇 가지 질문을 통해 당신에게 맞는 학습 경로를 찾아드리겠습니다.</p>
      </div>
      
      <!-- 로딩 상태 -->
      <div v-if="diagnosisStore.isLoading && !diagnosisStore.questions.length" class="loading-state">
        <div class="spinner"></div>
        <p>진단 문항을 불러오는 중...</p>
      </div>
      
      <!-- 에러 상태 -->
      <div v-else-if="diagnosisStore.error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>문제가 발생했습니다</h3>
        <p>{{ diagnosisStore.error }}</p>
        <button class="btn btn-primary" @click="retryLoad">다시 시도</button>
      </div>
      
      <!-- 진단 완료 상태 -->
      <div v-else-if="diagnosisStore.isCompleted" class="completion-state">
        <div class="completion-icon">🎉</div>
        <h2>진단이 완료되었습니다!</h2>
        
        <div class="result-card">
          <h3>당신의 유형</h3>
          <div class="user-type">
            <span class="type-badge" :class="userTypeClass">
              {{ userTypeText }}
            </span>
          </div>
          
          <div class="type-description">
            <p>{{ diagnosisStore.diagnosisResult.user_type_description }}</p>
          </div>
          
          <div class="learning-info">
            <div class="info-item">
              <strong>추천 챕터 수:</strong> 
              {{ diagnosisStore.diagnosisResult.recommended_chapters }}개
            </div>
            <div class="info-item">
              <strong>예상 학습 시간:</strong> 
              {{ diagnosisStore.diagnosisResult.estimated_duration }}
            </div>
          </div>
        </div>
        
        <div class="action-buttons">
          <button class="btn btn-secondary" @click="restartDiagnosis">
            다시 진단하기
          </button>
          <button class="btn btn-primary" @click="startLearning">
            학습 시작하기
          </button>
        </div>
      </div>
      
      <!-- 진단 진행 상태 -->
      <div v-else-if="diagnosisStore.questions.length > 0" class="diagnosis-content">
        <!-- 진행률 표시 -->
        <ProgressBar
          :current-step="diagnosisStore.currentQuestionIndex + 1"
          :total-steps="diagnosisStore.totalQuestions"
          @go-to-step="goToQuestion"
        />
        
        <!-- 현재 문항 -->
        <DiagnosisQuestion
          v-if="diagnosisStore.currentQuestion"
          :question="diagnosisStore.currentQuestion"
          :question-number="diagnosisStore.currentQuestionIndex + 1"
          :total-questions="diagnosisStore.totalQuestions"
          :existing-answer="getCurrentAnswer()"
          :is-first-question="diagnosisStore.currentQuestionIndex === 0"
          :is-last-question="diagnosisStore.isLastQuestion"
          @answer="saveAnswer"
          @next="handleNext"
          @previous="handlePrevious"
        />
        
        <!-- 완료 버튼 (마지막 문항에서 모든 답변 완료 시) -->
        <div v-if="showSubmitButton" class="submit-section">
          <div class="submit-notice">
            <p>모든 문항에 답변하셨습니다. 진단 결과를 확인해보세요!</p>
          </div>
          <button 
            class="btn btn-success btn-large"
            @click="submitDiagnosis"
            :disabled="diagnosisStore.isLoading"
          >
            <span v-if="diagnosisStore.isLoading">제출 중...</span>
            <span v-else>진단 결과 확인</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDiagnosisStore } from '@/stores/diagnosisStore'
import { useAuthStore } from '@/stores/authStore'
import ProgressBar from '@/components/diagnosis/ProgressBar.vue'
import DiagnosisQuestion from '@/components/diagnosis/DiagnosisQuestion.vue'

export default {
  name: 'DiagnosisPage',
  
  components: {
    ProgressBar,
    DiagnosisQuestion
  },
  
  setup() {
    const router = useRouter()
    const diagnosisStore = useDiagnosisStore()
    const authStore = useAuthStore()
    
    // 컴포넌트 마운트 시 문항 로드
    onMounted(async () => {
      // 로그인 체크 (임시 비활성화)
      // if (!authStore.isAuthenticated) {
      //   router.push('/login')
      //   return
      // }
      
      // 이미 진단이 완료된 사용자인지 체크 (임시 비활성화)
      // if (authStore.user?.diagnosis_completed) {
      //   router.push('/dashboard')
      //   return
      // }
      
      // 문항 로드
      if (diagnosisStore.questions.length === 0) {
        await diagnosisStore.loadQuestions()
      }
    })
    
    // 사용자 유형에 따른 스타일 클래스
    const userTypeClass = computed(() => {
      switch (diagnosisStore.userType) {
        case 'beginner':
          return 'type-beginner'
        case 'advanced':
          return 'type-advanced'
        default:
          return ''
      }
    })
    
    // 사용자 유형 텍스트
    const userTypeText = computed(() => {
      switch (diagnosisStore.userType) {
        case 'beginner':
          return 'AI 입문자'
        case 'advanced':
          return '실무 응용형'
        default:
          return '미정'
      }
    })
    
    // 완료 버튼 표시 여부
    const showSubmitButton = computed(() => {
      return diagnosisStore.isLastQuestion && 
             diagnosisStore.isAllAnswered && 
             !diagnosisStore.diagnosisResult
    })
    
    /**
     * 현재 문항의 기존 답변 가져오기
     */
    const getCurrentAnswer = () => {
      const currentQuestion = diagnosisStore.currentQuestion
      if (!currentQuestion) return null
      
      const answer = diagnosisStore.answers.find(
        a => a.question_id === currentQuestion.question_id
      )
      return answer ? answer.answer : null
    }
    
    /**
     * 답변 저장
     */
    const saveAnswer = (questionId, answer) => {
      diagnosisStore.saveAnswer(questionId, answer)
    }
    
    /**
     * 다음 문항으로 이동 (자동 제출 없음)
     */
    const handleNext = () => {
      if (!diagnosisStore.isLastQuestion) {
        diagnosisStore.nextQuestion()
      }
    }
    
    /**
     * 이전 문항으로 이동
     */
    const handlePrevious = () => {
      diagnosisStore.previousQuestion()
    }
    
    /**
     * 특정 문항으로 이동
     */
    const goToQuestion = (index) => {
      diagnosisStore.goToQuestion(index)
    }
    
    /**
     * 진단 결과 제출 (완료 버튼 클릭 시)
     */
    const submitDiagnosis = async () => {
      // /submit API 호출하여 진단 결과 받기
      const success = await diagnosisStore.submitDiagnosis()
      if (success) {
        // 성공 시 결과 페이지로 이동
        router.push('/diagnosis/result')
      }
    }
    
    /**
     * 진단 다시 시작
     */
    const restartDiagnosis = () => {
      diagnosisStore.resetDiagnosis()
      diagnosisStore.loadQuestions()
    }
    
    /**
     * 학습 시작
     */
    const startLearning = () => {
      router.push('/dashboard')
    }
    
    /**
     * 문항 로드 재시도
     */
    const retryLoad = () => {
      diagnosisStore.loadQuestions()
    }
    
    return {
      diagnosisStore,
      userTypeClass,
      userTypeText,
      showSubmitButton,
      getCurrentAnswer,
      saveAnswer,
      handleNext,
      handlePrevious,
      goToQuestion,
      submitDiagnosis,
      restartDiagnosis,
      startLearning,
      retryLoad
    }
  }
}
</script>

<style scoped lang="scss">
.diagnosis-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
  
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 1rem;
  }
  
  .page-header {
    text-align: center;
    color: white;
    margin-bottom: 3rem;
    
    h1 {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 1rem;
    }
    
    p {
      font-size: 1.1rem;
      opacity: 0.9;
      margin: 0;
    }
  }
  
  .loading-state,
  .error-state {
    background: white;
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    
    .spinner {
      width: 40px;
      height: 40px;
      border: 4px solid #f3f3f3;
      border-top: 4px solid #007bff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 1rem;
    }
    
    .error-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
    }
    
    h3 {
      color: #dc3545;
      margin-bottom: 1rem;
    }
    
    p {
      color: #6c757d;
      margin-bottom: 2rem;
    }
  }
  
  .completion-state {
    background: white;
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    
    .completion-icon {
      font-size: 4rem;
      margin-bottom: 1rem;
    }
    
    h2 {
      color: #28a745;
      margin-bottom: 2rem;
    }
    
    .result-card {
      background: #f8f9fa;
      border-radius: 8px;
      padding: 2rem;
      margin: 2rem 0;
      text-align: left;
      
      h3 {
        text-align: center;
        margin-bottom: 1rem;
        color: #495057;
      }
      
      .user-type {
        text-align: center;
        margin-bottom: 1.5rem;
        
        .type-badge {
          display: inline-block;
          padding: 0.5rem 1.5rem;
          border-radius: 25px;
          font-weight: bold;
          font-size: 1.1rem;
          
          &.type-beginner {
            background-color: #e3f2fd;
            color: #1976d2;
          }
          
          &.type-advanced {
            background-color: #f3e5f5;
            color: #7b1fa2;
          }
        }
      }
      
      .type-description {
        text-align: center;
        margin-bottom: 1.5rem;
        
        p {
          color: #6c757d;
          line-height: 1.6;
        }
      }
      
      .learning-info {
        .info-item {
          display: flex;
          justify-content: space-between;
          padding: 0.5rem 0;
          border-bottom: 1px solid #dee2e6;
          
          &:last-child {
            border-bottom: none;
          }
        }
      }
    }
    
    .action-buttons {
      display: flex;
      gap: 1rem;
      justify-content: center;
      flex-wrap: wrap;
    }
  }
  
  .diagnosis-content {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  }
  
  .submit-section {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 2px solid #e9ecef;
    
    .submit-notice {
      margin-bottom: 1.5rem;
      
      p {
        color: #28a745;
        font-weight: 600;
        font-size: 1.1rem;
      }
    }
    
    .btn-large {
      padding: 1rem 3rem;
      font-size: 1.1rem;
      font-weight: 600;
    }
  }
  
  .btn {
    padding: 0.75rem 2rem;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &.btn-primary {
      background-color: #007bff;
      color: white;
      
      &:hover:not(:disabled) {
        background-color: #0056b3;
      }
    }
    
    &.btn-secondary {
      background-color: #6c757d;
      color: white;
      
      &:hover:not(:disabled) {
        background-color: #5a6268;
      }
    }
    
    &.btn-success {
      background-color: #28a745;
      color: white;
      
      &:hover:not(:disabled) {
        background-color: #1e7e34;
      }
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 반응형 디자인
@media (max-width: 768px) {
  .diagnosis-page {
    padding: 1rem 0;
    
    .page-header {
      margin-bottom: 2rem;
      
      h1 {
        font-size: 2rem;
      }
      
      p {
        font-size: 1rem;
      }
    }
    
    .diagnosis-content,
    .completion-state,
    .loading-state,
    .error-state {
      padding: 1.5rem 1rem;
    }
    
    .completion-state .action-buttons {
      flex-direction: column;
      
      .btn {
        width: 100%;
      }
    }
  }
}
</style>