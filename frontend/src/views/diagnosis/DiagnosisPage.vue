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

      <!-- 진단 진행 상태 -->
      <div v-else-if="diagnosisStore.questions.length > 0" class="diagnosis-content">
        <!-- 진행률 표시 -->
        <ProgressBar :current-step="diagnosisStore.currentQuestionIndex + 1"
          :total-steps="diagnosisStore.totalQuestions" @go-to-step="goToQuestion" />

        <!-- 현재 문항 -->
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

  .diagnosis-content {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
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



    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
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
    .loading-state,
    .error-state {
      padding: 1.5rem 1rem;
    }
  }
}
</style>