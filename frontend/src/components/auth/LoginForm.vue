<!-- src/components/auth/LoginForm.vue -->

<template>
  <div class="login-form">
    <div class="form-header">
      <h2 class="form-title">로그인</h2>
      <p class="form-subtitle">계정에 로그인하여 학습을 계속하세요</p>
    </div>

    <form @submit.prevent="handleSubmit" class="auth-form">
      <!-- 로그인 ID 입력 -->
      <div class="form-group">
        <label for="loginId" class="form-label">
          로그인 ID
          <span class="required">*</span>
        </label>
        <input
          id="loginId"
          v-model="formData.loginId"
          type="text"
          class="form-control"
          :class="{ 'is-invalid': errors.loginId }"
          placeholder="로그인 ID를 입력하세요"
          autocomplete="username"
          :disabled="isLoading"
          @blur="validateField('loginId')"
          @input="clearFieldError('loginId')"
        />
        <div v-if="errors.loginId" class="invalid-feedback">
          {{ errors.loginId }}
        </div>
      </div>

      <!-- 비밀번호 입력 -->
      <div class="form-group">
        <label for="password" class="form-label">
          비밀번호
          <span class="required">*</span>
        </label>
        <div class="password-input-wrapper">
          <input
            id="password"
            v-model="formData.password"
            :type="showPassword ? 'text' : 'password'"
            class="form-control"
            :class="{ 'is-invalid': errors.password }"
            placeholder="비밀번호를 입력하세요"
            autocomplete="current-password"
            :disabled="isLoading"
            @blur="validateField('password')"
            @input="clearFieldError('password')"
          />
          <button
            type="button"
            class="password-toggle"
            @click="togglePasswordVisibility"
            :disabled="isLoading"
            aria-label="비밀번호 표시/숨기기"
          >
            <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
        </div>
        <div v-if="errors.password" class="invalid-feedback">
          {{ errors.password }}
        </div>
      </div>

      <!-- 로그인 유지 옵션 -->
      <div class="form-group">
        <div class="form-check">
          <input
            id="rememberMe"
            v-model="formData.rememberMe"
            type="checkbox"
            class="form-check-input"
            :disabled="isLoading"
          />
          <label for="rememberMe" class="form-check-label">
            로그인 상태 유지
          </label>
        </div>
      </div>

      <!-- 에러 메시지 표시 -->
      <div v-if="generalError" class="alert alert-danger" role="alert">
        <i class="fas fa-exclamation-circle"></i>
        {{ generalError }}
      </div>

      <!-- 로그인 버튼 -->
      <button
        type="submit"
        class="btn btn-primary btn-block"
        :disabled="isLoading || !isFormValid"
      >
        <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        {{ isLoading ? '로그인 중...' : '로그인' }}
      </button>

      <!-- 추가 링크들 -->
      <div class="form-footer">
        <div class="link-group">
          <a href="#" class="auth-link" @click.prevent="$emit('forgot-password')">
            비밀번호를 잊으셨나요?
          </a>
        </div>
        <div class="link-group">
          <span class="text-muted">계정이 없으신가요?</span>
          <a href="#" class="auth-link" @click.prevent="$emit('switch-to-register')">
            회원가입
          </a>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '../../stores/authStore'

export default {
  name: 'LoginForm',
  emits: ['login-success', 'switch-to-register', 'forgot-password'],
  
  setup(props, { emit }) {
    const authStore = useAuthStore()

    // 반응형 데이터
    const formData = ref({
      loginId: '',
      password: '',
      rememberMe: false
    })

    const errors = ref({})
    const generalError = ref('')
    const showPassword = ref(false)
    const isLoading = ref(false)

    // 계산된 속성
    const isFormValid = computed(() => {
      return formData.value.loginId.length >= 4 && 
             formData.value.password.length >= 8 && 
             Object.keys(errors.value).length === 0
    })

    // 메서드들
    const validateField = (fieldName) => {
      const value = formData.value[fieldName]
      
      switch (fieldName) {
        case 'loginId':
          if (!value) {
            errors.value.loginId = '로그인 ID는 필수입니다'
          } else if (value.length < 4 || value.length > 20) {
            errors.value.loginId = '로그인 ID는 4-20자 사이여야 합니다'
          } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            errors.value.loginId = '영문, 숫자, 언더스코어만 사용 가능합니다'
          } else {
            delete errors.value.loginId
          }
          break

        case 'password':
          if (!value) {
            errors.value.password = '비밀번호는 필수입니다'
          } else if (value.length < 8) {
            errors.value.password = '비밀번호는 최소 8자 이상이어야 합니다'
          } else {
            delete errors.value.password
          }
          break
      }
    }

    const clearFieldError = (fieldName) => {
      if (errors.value[fieldName]) {
        delete errors.value[fieldName]
      }
      if (generalError.value) {
        generalError.value = ''
      }
    }

    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value
    }

    const handleSubmit = async () => {
      // 모든 필드 검증
      Object.keys(formData.value).forEach(field => {
        if (field !== 'rememberMe') {
          validateField(field)
        }
      })

      // 에러가 있으면 제출하지 않음
      if (Object.keys(errors.value).length > 0) {
        return
      }

      isLoading.value = true
      generalError.value = ''

      try {
        const credentials = {
          loginId: formData.value.loginId,
          password: formData.value.password,
          rememberMe: formData.value.rememberMe  // 로그인 상태 유지 옵션 추가
        }

        const result = await authStore.login(credentials)
        
        if (result.success) {
          emit('login-success', {
            user: authStore.user,
            redirectTo: authStore.isDiagnosisCompleted ? '/dashboard' : '/diagnosis'
          })
        } else {
          throw new Error(result.error?.message || '로그인에 실패했습니다')
        }
      } catch (error) {
        console.error('로그인 오류:', error)
        
        // 에러 타입에 따른 메시지 설정
        if (error.code === 'AUTH_INVALID_CREDENTIALS') {
          generalError.value = '로그인 ID 또는 비밀번호가 올바르지 않습니다'
        } else if (error.code === 'VALIDATION_ERROR') {
          generalError.value = error.message
        } else if (error.status === 0) {
          generalError.value = '서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요'
        } else {
          generalError.value = error.message || '로그인 중 오류가 발생했습니다'
        }
      } finally {
        isLoading.value = false
      }
    }

    // 폼 초기화
    const resetForm = () => {
      formData.value = {
        loginId: '',
        password: '',
        rememberMe: false
      }
      errors.value = {}
      generalError.value = ''
      showPassword.value = false
    }

    // 로그인 ID 변경 시 에러 초기화
    watch(() => formData.value.loginId, () => {
      clearFieldError('loginId')
    })

    watch(() => formData.value.password, () => {
      clearFieldError('password')
    })

    return {
      formData,
      errors,
      generalError,
      showPassword,
      isLoading,
      isFormValid,
      validateField,
      clearFieldError,
      togglePasswordVisibility,
      handleSubmit,
      resetForm
    }
  }
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  color: #6c757d;
  margin-bottom: 0;
}

.auth-form {
  width: 100%;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.required {
  color: #dc3545;
}

.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
  outline: none;
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.form-control.is-invalid {
  border-color: #dc3545;
}

.form-control:disabled {
  background-color: #f8f9fa;
  opacity: 0.65;
}

.password-input-wrapper {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.15s ease-in-out;
}

.password-toggle:hover:not(:disabled) {
  color: #333;
}

.password-toggle:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.form-check {
  display: flex;
  align-items: center;
}

.form-check-input {
  margin-right: 0.5rem;
}

.form-check-label {
  color: #6c757d;
  cursor: pointer;
  margin-bottom: 0;
}

.invalid-feedback {
  display: block;
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  text-align: center;
  text-decoration: none;
  border-radius: 0.375rem;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.btn-primary {
  color: #fff;
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0b5ed7;
  border-color: #0a58ca;
}

.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-block {
  width: 100%;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.form-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.link-group {
  margin-bottom: 0.75rem;
}

.link-group:last-child {
  margin-bottom: 0;
}

.auth-link {
  color: #0d6efd;
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.5rem;
}

.auth-link:hover {
  color: #0b5ed7;
  text-decoration: underline;
}

.text-muted {
  color: #6c757d;
}

.me-2 {
  margin-right: 0.5rem;
}

/* 반응형 디자인 */
@media (max-width: 576px) {
  .login-form {
    padding: 1rem;
  }
  
  .form-title {
    font-size: 1.5rem;
  }
}
</style>