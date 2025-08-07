<!-- frontend/src/components/auth/RegisterForm.vue -->
<template>
  <form @submit.prevent="handleSubmit" class="register-form">
    <div class="form-header">
      <h2 class="form-title">회원가입</h2>
      <p class="form-subtitle">AI 활용법 학습을 시작해보세요</p>
    </div>

    <!-- 이름 입력 -->
    <div class="form-group">
      <label for="name" class="form-label">이름</label>
      <input
        id="name"
        v-model="formData.name"
        type="text"
        class="form-input"
        :class="{ 'error': errors.name }"
        placeholder="이름을 입력하세요"
        required
        autocomplete="name"
        :disabled="isLoading"
      />
      <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
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
          autocomplete="new-password"
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
      
      <!-- 비밀번호 강도 표시 -->
      <div v-if="formData.password" class="password-strength">
        <div class="strength-bar">
          <div 
            class="strength-fill" 
            :class="`strength-${passwordStrength.level}`"
            :style="{ width: `${passwordStrength.percentage}%` }"
          ></div>
        </div>
        <span class="strength-text" :class="`strength-${passwordStrength.level}`">
          {{ passwordStrength.text }}
        </span>
      </div>
    </div>

    <!-- 비밀번호 확인 입력 -->
    <div class="form-group">
      <label for="confirmPassword" class="form-label">비밀번호 확인</label>
      <div class="password-input-wrapper">
        <input
          id="confirmPassword"
          v-model="formData.confirmPassword"
          :type="showConfirmPassword ? 'text' : 'password'"
          class="form-input"
          :class="{ 'error': errors.confirmPassword }"
          placeholder="비밀번호를 다시 입력하세요"
          required
          autocomplete="new-password"
          :disabled="isLoading"
        />
        <button
          type="button"
          @click="toggleConfirmPasswordVisibility"
          class="password-toggle-btn"
          :disabled="isLoading"
        >
          <svg v-if="showConfirmPassword" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
          </svg>
        </button>
      </div>
      <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
    </div>

    <!-- 약관 동의 체크박스 -->
    <div class="form-group checkbox-group">
      <label class="checkbox-label">
        <input
          v-model="formData.agreeToTerms"
          type="checkbox"
          class="checkbox-input"
          :disabled="isLoading"
        />
        <span class="checkbox-custom"></span>
        <span class="checkbox-text">
          <router-link to="/terms" class="link">이용약관</router-link> 및 
          <router-link to="/privacy" class="link">개인정보처리방침</router-link>에 동의합니다
        </span>
      </label>
      <span v-if="errors.agreeToTerms" class="error-message">{{ errors.agreeToTerms }}</span>
    </div>

    <!-- 에러 메시지 -->
    <div v-if="generalError" class="general-error">
      {{ generalError }}
    </div>

    <!-- 회원가입 버튼 -->
    <button
      type="submit"
      class="submit-btn"
      :disabled="isLoading || !isFormValid"
    >
      <span v-if="isLoading" class="loading-spinner"></span>
      {{ isLoading ? '가입 중...' : '회원가입' }}
    </button>

    <!-- 추가 링크들 -->
    <div class="form-footer">
      <div class="login-link">
        이미 계정이 있으신가요? 
        <router-link to="/login" class="link">로그인</router-link>
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
const showConfirmPassword = ref(false)
const generalError = ref('')

// 폼 데이터
const formData = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false
})

// 폼 검증 에러
const errors = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: ''
})

// 계산된 속성
const isFormValid = computed(() => {
  return formData.name.trim() !== '' && 
         formData.email.trim() !== '' && 
         formData.password.trim() !== '' && 
         formData.confirmPassword.trim() !== '' &&
         formData.agreeToTerms &&
         !Object.values(errors).some(error => error !== '')
})

// 비밀번호 강도 계산
const passwordStrength = computed(() => {
  const password = formData.password
  if (!password) return { level: 'none', percentage: 0, text: '' }

  let score = 0
  let feedback = []

  // 길이 체크
  if (password.length >= 8) score += 25
  else feedback.push('8자 이상')

  // 대소문자 체크
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 25
  else feedback.push('대소문자 포함')

  // 숫자 체크
  if (/\d/.test(password)) score += 25
  else feedback.push('숫자 포함')

  // 특수문자 체크
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 25
  else feedback.push('특수문자 포함')

  if (score < 50) {
    return { level: 'weak', percentage: score, text: '약함' }
  } else if (score < 75) {
    return { level: 'medium', percentage: score, text: '보통' }
  } else {
    return { level: 'strong', percentage: score, text: '강함' }
  }
})

// 비밀번호 표시/숨김 토글
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const toggleConfirmPasswordVisibility = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}

// 폼 검증
const validateForm = () => {
  // 에러 초기화
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
  generalError.value = ''

  let isValid = true

  // 이름 검증
  if (!formData.name.trim()) {
    errors.name = '이름을 입력해주세요'
    isValid = false
  } else if (formData.name.trim().length < 2) {
    errors.name = '이름은 최소 2자 이상이어야 합니다'
    isValid = false
  }

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
  } else if (formData.password.length < 8) {
    errors.password = '비밀번호는 최소 8자 이상이어야 합니다'
    isValid = false
  }

  // 비밀번호 확인 검증
  if (!formData.confirmPassword.trim()) {
    errors.confirmPassword = '비밀번호 확인을 입력해주세요'
    isValid = false
  } else if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = '비밀번호가 일치하지 않습니다'
    isValid = false
  }

  // 약관 동의 검증
  if (!formData.agreeToTerms) {
    errors.agreeToTerms = '이용약관 및 개인정보처리방침에 동의해주세요'
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
    // 회원가입 시도
    await authStore.register({
      name: formData.name,
      email: formData.email,
      password: formData.password
    })

    // 성공 이벤트 발생
    emit('success')

    // 진단 페이지로 리다이렉트
    router.push('/diagnosis')
  } catch (error) {
    console.error('회원가입 실패:', error)
    
    // 에러 메시지 설정
    if (error.response?.status === 409) {
      generalError.value = '이미 사용 중인 이메일입니다'
    } else if (error.response?.status === 422) {
      generalError.value = '입력 정보를 다시 확인해주세요'
    } else {
      generalError.value = '회원가입 중 오류가 발생했습니다. 다시 시도해주세요'
    }

    // 에러 이벤트 발생
    emit('error', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style lang="scss" scoped>
.register-form {
  max-width: 450px;
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

    .password-strength {
      margin-top: 0.5rem;

      .strength-bar {
        width: 100%;
        height: 4px;
        background-color: #e9ecef;
        border-radius: 2px;
        overflow: hidden;
        margin-bottom: 0.25rem;

        .strength-fill {
          height: 100%;
          border-radius: 2px;
          transition: all 0.3s ease;

          &.strength-weak {
            background-color: #ef4444;
          }

          &.strength-medium {
            background-color: #f59e0b;
          }

          &.strength-strong {
            background-color: #10b981;
          }
        }
      }

      .strength-text {
        font-size: 0.75rem;
        font-weight: 500;

        &.strength-weak {
          color: #ef4444;
        }

        &.strength-medium {
          color: #f59e0b;
        }

        &.strength-strong {
          color: #10b981;
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
        align-items: flex-start;
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
          margin-top: 0.125rem;
          flex-shrink: 0;
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
          font-size: 0.875rem;
          color: var(--text-secondary);
          line-height: 1.4;

          .link {
            color: var(--primary-color);
            text-decoration: none;

            &:hover {
              text-decoration: underline;
            }
          }
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

    .login-link {
      color: var(--text-secondary);
      font-size: 0.9rem;

      .link {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 500;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 반응형 디자인
@media (max-width: 480px) {
  .register-form {
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