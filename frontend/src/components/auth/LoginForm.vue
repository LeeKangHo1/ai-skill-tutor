<!-- frontend/src/components/auth/LoginForm.vue -->
<template>
  <form @submit.prevent="handleSubmit" class="login-form">
    <div class="form-header">
      <h2 class="form-title">로그인</h2>
      <p class="form-subtitle">AI 활용법 학습을 시작해보세요</p>
    </div>

    <!-- 이메일 입력 -->
    <div class="form-group">
      <label for="email" class="form-label">이메일</label>
      <input
        id="email"
        v-model="formData.email"
        type="email"
        class="form-input"
        :class="{ 'error': errors.email }"
        placeholder="이메일을 입력하세요"
        required
        autocomplete="email"
        :disabled="isLoading"
      />
      <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
    </div>

    <!-- 비밀번호 입력 -->
    <div class="form-group">
      <label for="password" class="form-label">비밀번호</label>
      <div class="password-input-wrapper">
        <input
          id="password"
          v-model="formData.password"
          :type="showPassword ? 'text' : 'password'"
          class="form-input"
          :class="{ 'error': errors.password }"
          placeholder="비밀번호를 입력하세요"
          required
          autocomplete="current-password"
          :disabled="isLoading"
        />
        <button
          type="button"
          @click="togglePasswordVisibility"
          class="password-toggle-btn"
          :disabled="isLoading"
        >
          <svg v-if="showPassword" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
          </svg>
        </button>
      </div>
      <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
    </div>

    <!-- 로그인 유지 체크박스 -->
    <div class="form-group checkbox-group">
      <label class="checkbox-label">
        <input
          v-model="formData.rememberMe"
          type="checkbox"
          class="checkbox-input"
          :disabled="isLoading"
        />
        <span class="checkbox-custom"></span>
        <span class="checkbox-text">로그인 상태 유지</span>
      </label>
    </div>

    <!-- 에러 메시지 -->
    <div v-if="generalError" class="general-error">
      {{ generalError }}
    </div>

    <!-- 로그인 버튼 -->
    <button
      type="submit"
      class="submit-btn"
      :disabled="isLoading || !isFormValid"
    >
      <span v-if="isLoading" class="loading-spinner"></span>
      {{ isLoading ? '로그인 중...' : '로그인' }}
    </button>

    <!-- 추가 링크들 -->
    <div class="form-footer">
      <router-link to="/forgot-password" class="link">비밀번호를 잊으셨나요?</router-link>
      <div class="signup-link">
        계정이 없으신가요? 
        <router-link to="/register" class="link">회원가입</router-link>
      </div>
    </div>
  </form>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

// 라우터 및 스토어 설정
const router = useRouter()
const authStore = useAuthStore()

// 이벤트 정의
const emit = defineEmits(['success', 'error'])

// 반응형 데이터
const isLoading = ref(false)
const showPassword = ref(false)
const generalError = ref('')

// 폼 데이터
const formData = reactive({
  email: '',
  password: '',
  rememberMe: false
})

// 폼 검증 에러
const errors = reactive({
  email: '',
  password: ''
})

// 계산된 속성
const isFormValid = computed(() => {
  return formData.email.trim() !== '' && 
         formData.password.trim() !== '' && 
         !errors.email && 
         !errors.password
})

// 비밀번호 표시/숨김 토글
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// 폼 검증
const validateForm = () => {
  // 에러 초기화
  errors.email = ''
  errors.password = ''
  generalError.value = ''

  let isValid = true

  // 이메일 검증
  if (!formData.email.trim()) {
    errors.email = '이메일을 입력해주세요'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = '올바른 이메일 형식을 입력해주세요'
    isValid = false
  }

  // 비밀번호 검증
  if (!formData.password.trim()) {
    errors.password = '비밀번호를 입력해주세요'
    isValid = false
  } else if (formData.password.length < 6) {
    errors.password = '비밀번호는 최소 6자 이상이어야 합니다'
    isValid = false
  }

  return isValid
}

// 폼 제출 처리
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  generalError.value = ''

  try {
    // 로그인 시도
    await authStore.login({
      email: formData.email,
      password: formData.password,
      rememberMe: formData.rememberMe
    })

    // 성공 이벤트 발생
    emit('success')

    // 대시보드로 리다이렉트
    router.push('/dashboard')
  } catch (error) {
    console.error('로그인 실패:', error)
    
    // 에러 메시지 설정
    if (error.response?.status === 401) {
      generalError.value = '이메일 또는 비밀번호가 올바르지 않습니다'
    } else if (error.response?.status === 429) {
      generalError.value = '너무 많은 로그인 시도입니다. 잠시 후 다시 시도해주세요'
    } else {
      generalError.value = '로그인 중 오류가 발생했습니다. 다시 시도해주세요'
    }

    // 에러 이벤트 발생
    emit('error', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);

  .form-header {
    text-align: center;
    margin-bottom: 2rem;

    .form-title {
      font-size: 1.75rem;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0 0 0.5rem 0;
    }

    .form-subtitle {
      color: var(--text-secondary);
      margin: 0;
    }
  }

  .form-group {
    margin-bottom: 1.5rem;

    .form-label {
      display: block;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 0.5rem;
    }

    .form-input {
      width: 100%;
      padding: 0.75rem;
      border: 2px solid var(--border-color);
      border-radius: 8px;
      font-size: 1rem;
      transition: all 0.2s ease;

      &:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.1);
      }

      &.error {
        border-color: var(--error-color);
      }

      &:disabled {
        background-color: var(--bg-disabled);
        cursor: not-allowed;
      }
    }

    .password-input-wrapper {
      position: relative;

      .password-toggle-btn {
        position: absolute;
        right: 0.75rem;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 0.25rem;
        width: 20px;
        height: 20px;

        &:hover {
          color: var(--text-primary);
        }

        &:disabled {
          cursor: not-allowed;
          opacity: 0.5;
        }

        svg {
          width: 100%;
          height: 100%;
        }
      }
    }

    .error-message {
      display: block;
      color: var(--error-color);
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }

    &.checkbox-group {
      .checkbox-label {
        display: flex;
        align-items: center;
        cursor: pointer;
        user-select: none;

        .checkbox-input {
          display: none;

          &:checked + .checkbox-custom {
            background-color: var(--primary-color);
            border-color: var(--primary-color);

            &::after {
              opacity: 1;
            }
          }
        }

        .checkbox-custom {
          width: 18px;
          height: 18px;
          border: 2px solid var(--border-color);
          border-radius: 4px;
          margin-right: 0.5rem;
          position: relative;
          transition: all 0.2s ease;

          &::after {
            content: '';
            position: absolute;
            left: 2px;
            top: -1px;
            width: 6px;
            height: 10px;
            border: solid white;
            border-width: 0 2px 2px 0;
            transform: rotate(45deg);
            opacity: 0;
            transition: opacity 0.2s ease;
          }
        }

        .checkbox-text {
          font-size: 0.9rem;
          color: var(--text-secondary);
        }
      }
    }
  }

  .general-error {
    background-color: #fef2f2;
    color: #991b1b;
    padding: 0.75rem;
    border-radius: 6px;
    font-size: 0.875rem;
    margin-bottom: 1rem;
    border-left: 4px solid #ef4444;
  }

  .submit-btn {
    width: 100%;
    padding: 0.875rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;

    &:hover:not(:disabled) {
      background-color: var(--primary-color-dark);
      transform: translateY(-1px);
    }

    &:disabled {
      background-color: var(--bg-disabled);
      cursor: not-allowed;
      transform: none;
    }

    .loading-spinner {
      width: 16px;
      height: 16px;
      border: 2px solid transparent;
      border-top: 2px solid currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  }

  .form-footer {
    margin-top: 1.5rem;
    text-align: center;

    .link {
      color: var(--primary-color);
      text-decoration: none;
      font-weight: 500;

      &:hover {
        text-decoration: underline;
      }
    }

    .signup-link {
      margin-top: 1rem;
      color: var(--text-secondary);
      font-size: 0.9rem;
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 반응형 디자인
@media (max-width: 480px) {
  .login-form {
    padding: 1.5rem;
    margin: 1rem;

    .form-header {
      .form-title {
        font-size: 1.5rem;
      }
    }
  }
}
</style>