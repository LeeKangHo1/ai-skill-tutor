<!-- frontend/src/views/diagnosis/DiagnosisPage.vue -->
<!-- 사용자 진단 페이지 -->

<template>
  <div class="diagnosis-page">
    <div class="container">
      <div class="page-header">
        <h1>사용자 진단</h1>
        <p>몇 가지 질문을 통해 당신에게 맞는 학습 경로를 찾아드리겠습니다.</p>
      </div>

      <div v-if="diagnosisStore.isLoading && !diagnosisStore.questions.length" class="loading-state">
        <div class="spinner"></div>
        <p>진단 문항을 불러오는 중...</p>
      </div>

      <div v-else-if="diagnosisStore.error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>문제가 발생했습니다</h3>
        <p>{{ diagnosisStore.error }}</p>
        <button class="btn btn-primary" @click="retryLoad">다시 시도</button>
      </div>

      <div v-else-if="diagnosisStore.questions.length > 0" class="diagnosis-content">
        <ProgressBar :current-step="diagnosisStore.currentQuestionIndex + 1"
          :total-steps="diagnosisStore.totalQuestions" @go-to-step="goToQuestion" />

        <DiagnosisQuestion v-if="diagnosisStore.currentQuestion" :question="diagnosisStore.currentQuestion"
          :total-questions="diagnosisStore.totalQuestions" :existing-answer="getCurrentAnswer()"
          :is-first-question="diagnosisStore.currentQuestionIndex === 0"
          :is-last-question="diagnosisStore.isLastQuestion" @answer="saveAnswer" @next="handleNext"
          @previous="handlePrevious" @complete="handleComplete" />
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDiagnosisStore } from '@/stores/diagnosisStore'
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

    // 컴포넌트 마운트 시 문항 로드
    onMounted(async () => {
      if (diagnosisStore.questions.length === 0) {
        await diagnosisStore.loadQuestions()
      }
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
     * 다음 문항으로 이동
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
     * 진단 완료 처리 (마지막 문항 답변 완료 시)
     */
    const handleComplete = async () => {
      const success = await diagnosisStore.submitDiagnosis()
      if (success) {
        router.push('/diagnosis/result')
      }
    }

    /**
     * 문항 로드 재시도
     */
    const retryLoad = () => {
      diagnosisStore.loadQuestions()
    }

    return {
      diagnosisStore,
      getCurrentAnswer,
      saveAnswer,
      handleNext,
      handlePrevious,
      goToQuestion,
      handleComplete,
      retryLoad
    }
  }
}
</script>

<style scoped lang="scss">
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.diagnosis-page {
  min-height: 100vh;
  background: $brand-gradient;
  padding: 2rem 0;

  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  .page-header {
    text-align: center;
    color: $white;
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
    background: $white;
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba($black, 0.1);

    .spinner {
      width: 40px;
      height: 40px;
      border: 4px solid $gray-200;
      border-top-color: $primary;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 1rem;
    }

    .error-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
    }

    h3 {
      color: $danger;
      margin-bottom: 1rem;
    }

    p {
      color: $secondary;
      margin-bottom: 2rem;
    }
  }

  .diagnosis-content {
    background: $white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba($black, 0.1);
  }

  .btn {
    padding: 0.75rem 2rem;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;

    &.btn-primary {
      background-color: $primary;
      color: $white;

      &:hover:not(:disabled) {
        background-color: darken($primary, 10%);
      }
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}
</style>