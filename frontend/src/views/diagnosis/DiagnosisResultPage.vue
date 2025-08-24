<!-- frontend/src/views/diagnosis/DiagnosisResultPage.vue -->
<!-- 사용자 진단 결과 페이지 -->

<template>
  <div class="diagnosis-result-page">
    <div class="container">
      <div class="page-header">
        <h1>진단 결과</h1>
        <p>당신에게 맞는 학습 유형을 선택해주세요.</p>
      </div>

      <div v-if="diagnosisStore.isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>결과를 처리 중입니다...</p>
      </div>

      <div v-else-if="diagnosisStore.error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>알림</h3>
        <p>{{ diagnosisStore.error }}</p>
        <button class="btn btn-primary" @click="clearError">확인</button>
      </div>

      <div v-else-if="!diagnosisStore.diagnosisResult" class="no-result-state">
        <div class="error-icon">❌</div>
        <h3>진단 결과를 찾을 수 없습니다</h3>
        <p>진단을 다시 진행해주세요.</p>
        <button class="btn btn-primary" @click="goBack">진단으로 돌아가기</button>
      </div>

      <div v-else-if="diagnosisStore.isCompleted" class="completion-state">
        <div class="completion-icon">🎉</div>
        <h2>유형 선택이 완료되었습니다!</h2>

        <div class="result-card">
          <h3>선택된 유형</h3>
          <div class="user-type">
            <span class="type-badge" :class="userTypeClass">
              {{ userTypeText }}
            </span>
          </div>
        </div>

        <div class="action-buttons">
          <button class="btn btn-primary" @click="startLearning">
            학습 시작하기
          </button>
        </div>
      </div>

      <div v-else class="type-selection-content">
        <div class="result-summary">
          <h2>진단이 완료되었습니다!</h2>
          <div class="score-info">
            <p>총 점수: <strong>{{ diagnosisStore.diagnosisResult.total_score }}점</strong></p>
          </div>
        </div>

        <div class="type-options">
          <div class="type-card" :class="{ 'selected': selectedUserType === 'beginner' }"
            @click="selectUserType('beginner')">
            <div class="type-header">
              <h3>AI 입문자</h3>
              <span class="recommended-badge">추천</span>
            </div>

            <div class="type-info">
              <div class="duration-chapters">
                <span class="chapters">8개 챕터</span>
                <span class="duration">15시간</span>
              </div>

              <ul class="features">
                <li>기초부터 차근차근 학습</li>
                <li>쉬운 용어로 설명</li>
                <li>실생활 예시 중심</li>
              </ul>
            </div>
          </div>

          <div class="type-card disabled" :class="{ 'selected': selectedUserType === 'advanced' }"
            @click="showComingSoonMessage">
            <div class="type-header">
              <h3>실무 응용형</h3>
              <span class="coming-soon-badge">개발 예정</span>
            </div>

            <div class="type-info">
              <div class="duration-chapters">
                <span class="chapters">10개 챕터</span>
                <span class="duration">20시간</span>
              </div>

              <ul class="features">
                <li>실무 중심 학습</li>
                <li>고급 기법 포함</li>
                <li>프로젝트 기반 학습</li>
              </ul>
            </div>

            <div class="disabled-overlay">
              <p>곧 출시 예정입니다!</p>
            </div>
          </div>
        </div>

        <div class="selection-actions">
          <button class="btn btn-secondary" @click="goBack">
            이전으로
          </button>
          <button class="btn btn-primary btn-large" @click="confirmUserType"
            :disabled="!selectedUserType || diagnosisStore.isLoading">
            <span v-if="diagnosisStore.isLoading">제출 중...</span>
            <span v-else>{{ selectedUserType ? `${getSelectedTypeName()} 선택하기` : '유형을 선택해주세요' }}</span>
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

export default {
  name: 'DiagnosisResultPage',

  setup() {
    const router = useRouter()
    const diagnosisStore = useDiagnosisStore()
    const authStore = useAuthStore()

    // 선택된 사용자 유형
    const selectedUserType = ref(null)

    // 컴포넌트 마운트 시 진단 결과 확인
    onMounted(async () => {
      // 인증 상태 확인
      if (!authStore.isAuthenticated) {
        await authStore.initialize()
        if (!authStore.isAuthenticated) {
          router.push('/login')
          return
        }
      }

      // 진단 결과가 없으면 진단 페이지로 돌려보냄
      if (!diagnosisStore.diagnosisResult) {
        router.push('/diagnosis')
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

    /**
     * 사용자 유형 선택
     */
    const selectUserType = (type) => {
      if (type === 'advanced') {
        return // 실무 응용형은 선택 불가
      }
      selectedUserType.value = type
    }

    /**
     * 개발 예정 메시지 표시
     */
    const showComingSoonMessage = () => {
      // 더 나은 사용자 경험을 위해 에러 상태로 메시지 표시
      diagnosisStore.error = '실무 응용형은 현재 개발 중입니다. 곧 출시 예정이니 조금만 기다려주세요!'

      // 3초 후 에러 메시지 자동 제거
      setTimeout(() => {
        diagnosisStore.error = null
      }, 3000)
    }

    /**
     * 선택된 유형 이름 반환
     */
    const getSelectedTypeName = () => {
      switch (selectedUserType.value) {
        case 'beginner':
          return 'AI 입문자'
        case 'advanced':
          return '실무 응용형'
        default:
          return ''
      }
    }

    /**
     * 사용자 유형 확정 (제출 버튼 클릭 시)
     */
    const confirmUserType = async () => {
      if (!selectedUserType.value) return

      if (selectedUserType.value === 'advanced') {
        showComingSoonMessage()
        return
      }

      // /select-type API 호출하여 유형 저장
      const success = await diagnosisStore.selectUserType(selectedUserType.value)
      if (success) {
        // 완료 상태로 변경됨 (페이지 내에서 완료 메시지 표시)
      }
    }

    /**
     * 학습 시작
     */
    const startLearning = () => {
      router.push('/learning')
    }

    /**
     * 이전 페이지로 돌아가기
     */
    const goBack = () => {
      // 진단 결과만 초기화 (답변은 유지)
      diagnosisStore.clearResult()
      router.push('/diagnosis')
    }

    /**
     * 에러 메시지 제거
     */
    const clearError = () => {
      diagnosisStore.error = null
    }

    return {
      diagnosisStore,
      selectedUserType,
      userTypeClass,
      userTypeText,
      selectUserType,
      showComingSoonMessage,
      getSelectedTypeName,
      confirmUserType,
      startLearning,
      goBack,
      clearError
    }
  }
}
</script>

<style scoped lang="scss">
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.diagnosis-result-page {
  min-height: 100vh;
  background: $brand-gradient;
  padding: 2rem 0;

  .container {
    max-width: 900px;
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
  .error-state,
  .no-result-state,
  .completion-state,
  .type-selection-content {
    background: $white;
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba($black, 0.1);
  }

  .loading-state,
  .error-state,
  .no-result-state {
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

  .completion-state {
    .completion-icon {
      font-size: 4rem;
      margin-bottom: 1rem;
    }

    h2 {
      color: $success;
      margin-bottom: 2rem;
    }

    .result-card {
      background: $gray-100;
      border-radius: 8px;
      padding: 2rem;
      margin: 2rem 0;

      h3 {
        margin-bottom: 1rem;
        color: $gray-700;
      }

      .user-type .type-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: $border-radius-pill;
        font-weight: bold;
        font-size: 1.1rem;

        &.type-beginner {
          background-color: lighten($primary, 35%);
          color: darken($primary, 10%);
        }

        &.type-advanced {
          background-color: lighten($brand-purple, 35%);
          color: darken($brand-purple, 10%);
        }
      }
    }
  }

  .type-selection-content {
    padding: 2rem;

    .result-summary {
      margin-bottom: 2rem;

      h2 {
        color: $success;
        margin-bottom: 1rem;
      }

      .score-info p {
        color: $secondary;
        font-size: 1.1rem;

        strong {
          color: $gray-700;
        }
      }
    }

    .type-options {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .type-card {
      border: 2px solid $gray-200;
      border-radius: 12px;
      padding: 1.5rem;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        border-color: $primary;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba($primary, 0.15);
      }

      &.selected {
        border-color: $primary;
        background-color: lighten($primary, 40%);
        box-shadow: 0 8px 25px rgba($primary, 0.2);
      }

      .type-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;

        h3 {
          margin: 0;
          color: $gray-700;
          font-size: 1.2rem;
        }

        .recommended-badge,
        .coming-soon-badge {
          color: $white;
          padding: 0.25rem 0.75rem;
          border-radius: $border-radius-pill;
          font-size: 0.8rem;
          font-weight: 600;
        }

        .recommended-badge {
          background-color: $success;
        }

        .coming-soon-badge {
          background-color: $warning;
          color: $gray-900;
        }
      }

      .type-info {
        .duration-chapters {
          display: flex;
          gap: 1rem;
          margin-bottom: 1rem;

          .chapters,
          .duration {
            background-color: $gray-100;
            padding: 0.5rem 1rem;
            border-radius: $border-radius-pill;
            font-size: 0.9rem;
            font-weight: 500;
            color: $gray-700;
          }
        }

        .features {
          list-style: none;
          padding: 0;
          margin: 0;

          li {
            padding: 0.25rem 0;
            color: $secondary;
            font-size: 0.9rem;

            &:before {
              content: "✓";
              color: $success;
              font-weight: bold;
              margin-right: 0.5rem;
            }
          }
        }
      }

      &.disabled {
        position: relative;
        opacity: 0.7;
        cursor: not-allowed;

        &:hover {
          border-color: $gray-200;
          transform: none;
          box-shadow: none;
        }

        .disabled-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba($white, 0.8);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;

          p {
            color: $secondary;
            font-weight: 600;
            margin: 0;
            text-align: center;
          }
        }
      }
    }

    .selection-actions {
      display: flex;
      justify-content: space-between;
      gap: 1rem;

      .btn-large {
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
      }
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
      background-color: $primary;
      color: $white;

      &:hover:not(:disabled) {
        background-color: darken($primary, 10%);
      }
    }

    &.btn-secondary {
      background-color: $secondary;
      color: $white;

      &:hover:not(:disabled) {
        background-color: darken($secondary, 10%);
      }
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
  }
}
</style>