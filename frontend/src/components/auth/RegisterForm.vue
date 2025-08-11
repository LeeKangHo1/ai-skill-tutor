<!-- src/components/auth/RegisterForm.vue -->

<template>
  <div class="register-form">
    <div class="form-header">
      <h2 class="form-title">회원가입</h2>
      <p class="form-subtitle">새 계정을 만들어 AI 학습을 시작하세요</p>
    </div>

    <form @submit.prevent="handleSubmit" class="auth-form">
      <!-- 로그인 ID 입력 -->
      <div class="form-group">
        <label for="loginId" class="form-label">
          로그인 ID
          <span class="required">*</span>
        </label>
        <div class="input-with-check">
          <input
            id="loginId"
            v-model="formData.loginId"
            type="text"
            class="form-control"
            :class="{ 
              'is-invalid': errors.loginId, 
              'is-valid': validFields.loginId && !errors.loginId 
            }"
            placeholder="4-20자의 영문, 숫자, 언더스코어"
            autocomplete="username"
            :disabled="isLoading"
            @blur="validateField('loginId')"
            @input="handleLoginIdInput"
          />
          <button
            v-if="formData.loginId.length >= 4"
            type="button"
            class="check-availability-btn"
            :class="{ 'checking': checkingLoginId }"
            @click="checkLoginIdAvailability"
            :disabled="isLoading || checkingLoginId || errors.loginId"
          >
            <span v-if="checkingLoginId" class="spinner-border spinner-border-sm"></span>
            <i v-else-if="validFields.loginId" class="fas fa-check text-success"></i>
            <span v-else>확인</span>
          </button>
        </div>
        <div v-if="errors.loginId" class="invalid-feedback">
          {{ errors.loginId }}
        </div>
        <div v-else-if="validFields.loginId" class="valid-feedback">
          사용 가능한 로그인 ID입니다
        </div>
        <div v-else-if="formData.loginId.length >= 4 && !errors.loginId && !checkingLoginId" class="check-required-feedback">
          중복 확인 버튼을 눌러주세요
        </div>
      </div>

      <!-- 사용자명 입력 -->
      <div class="form-group">
        <label for="username" class="form-label">
          사용자명
          <span class="required">*</span>
        </label>
        <input
          id="username"
          v-model="formData.username"
          type="text"
          class="form-control"
          :class="{ 
            'is-invalid': errors.username,
            'is-valid': validFields.username && !errors.username
          }"
          placeholder="표시될 사용자명을 입력하세요"
          autocomplete="name"
          :disabled="isLoading"
          @blur="validateField('username')"
          @input="clearFieldError('username')"
        />
        <div v-if="errors.username" class="invalid-feedback">
          {{ errors.username }}
        </div>
      </div>

      <!-- 이메일 입력 -->
      <div class="form-group">
        <label for="email" class="form-label">
          이메일
          <span class="required">*</span>
        </label>
        <div class="input-with-check">
          <input
            id="email"
            v-model="formData.email"
            type="email"
            class="form-control"
            :class="{ 
              'is-invalid': errors.email,
              'is-valid': validFields.email && !errors.email
            }"
            placeholder="example@domain.com"
            autocomplete="email"
            :disabled="isLoading"
            @blur="validateField('email')"
            @input="handleEmailInput"
          />
          <button
            v-if="formData.email && !errors.email"
            type="button"
            class="check-availability-btn"
            :class="{ 'checking': checkingEmail }"
            @click="checkEmailAvailability"
            :disabled="isLoading || checkingEmail || errors.email"
          >
            <span v-if="checkingEmail" class="spinner-border spinner-border-sm"></span>
            <i v-else-if="validFields.email" class="fas fa-check text-success"></i>
            <span v-else>확인</span>
          </button>
        </div>
        <div v-if="errors.email" class="invalid-feedback">
          {{ errors.email }}
        </div>
        <div v-else-if="validFields.email" class="valid-feedback">
          사용 가능한 이메일입니다
        </div>
        <div v-else-if="formData.email && !errors.email && !checkingEmail" class="check-required-feedback">
          중복 확인 버튼을 눌러주세요
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
            :class="{ 
              'is-invalid': errors.password,
              'is-valid': validFields.password && !errors.password
            }"
            placeholder="최소 8자, 영문과 숫자 포함"
            autocomplete="new-password"
            :disabled="isLoading"
            @blur="validateField('password')"
            @input="handlePasswordInput"
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
        <div v-else-if="formData.password" class="password-strength">
          <div class="strength-meter">
            <div 
              class="strength-bar"
              :class="passwordStrength.class"
              :style="{ width: passwordStrength.width }"
            ></div>
          </div>
          <span class="strength-text" :class="passwordStrength.class">
            {{ passwordStrength.text }}
          </span>
        </div>
      </div>

      <!-- 비밀번호 확인 -->
      <div class="form-group">
        <label for="passwordConfirm" class="form-label">
          비밀번호 확인
          <span class="required">*</span>
        </label>
        <div class="password-input-wrapper">
          <input
            id="passwordConfirm"
            v-model="formData.passwordConfirm"
            :type="showPasswordConfirm ? 'text' : 'password'"
            class="form-control"
            :class="{ 
              'is-invalid': errors.passwordConfirm,
              'is-valid': validFields.passwordConfirm && !errors.passwordConfirm
            }"
            placeholder="비밀번호를 다시 입력하세요"
            autocomplete="new-password"
            :disabled="isLoading"
            @blur="validateField('passwordConfirm')"
            @input="clearFieldError('passwordConfirm')"
          />
          <button
            type="button"
            class="password-toggle"
            @click="togglePasswordConfirmVisibility"
            :disabled="isLoading"
            aria-label="비밀번호 확인 표시/숨기기"
          >
            <i :class="showPasswordConfirm ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
        </div>
        <div v-if="errors.passwordConfirm" class="invalid-feedback">
          {{ errors.passwordConfirm }}
        </div>
      </div>

      <!-- 약관 동의 -->
      <div class="form-group">
        <div class="form-check">
          <input
            id="agreeTerms"
            v-model="formData.agreeTerms"
            type="checkbox"
            class="form-check-input"
            :class="{ 'is-invalid': errors.agreeTerms }"
            :disabled="isLoading"
            @change="validateField('agreeTerms')"
          />
          <label for="agreeTerms" class="form-check-label">
            <a href="#" @click.prevent="showTerms" class="terms-link">이용약관</a> 및 
            <a href="#" @click.prevent="showPrivacy" class="terms-link">개인정보처리방침</a>에 동의합니다
            <span class="required">*</span>
          </label>
        </div>
        <div v-if="errors.agreeTerms" class="invalid-feedback">
          {{ errors.agreeTerms }}
        </div>
      </div>

      <!-- 에러 메시지 표시 -->
      <div v-if="generalError" class="alert alert-danger" role="alert">
        <i class="fas fa-exclamation-circle"></i>
        {{ generalError }}
      </div>

      <!-- 회원가입 버튼 -->
      <button
        type="submit"
        class="btn btn-primary btn-block"
        :disabled="isLoading || !isFormValid"
      >
        <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        {{ isLoading ? '가입 중...' : '회원가입' }}
      </button>

      <!-- 추가 링크들 -->
      <div class="form-footer">
        <div class="link-group">
          <span class="text-muted">이미 계정이 있으신가요?</span>
          <a href="#" class="auth-link" @click.prevent="$emit('switch-to-login')">
            로그인
          </a>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import authService from '../../services/authService'

export default {
  name: 'RegisterForm',
  emits: ['register-success', 'switch-to-login', 'show-terms', 'show-privacy'],
  
  setup(props, { emit }) {
    const authStore = useAuthStore()

    // 반응형 데이터
    const formData = ref({
      loginId: '',
      username: '',
      email: '',
      password: '',
      passwordConfirm: '',
      agreeTerms: false
    })

    const errors = ref({})
    const validFields = ref({})
    const generalError = ref('')
    const showPassword = ref(false)
    const showPasswordConfirm = ref(false)
    const isLoading = ref(false)
    const checkingLoginId = ref(false)
    const checkingEmail = ref(false)

    // 계산된 속성
    const isFormValid = computed(() => {
      const requiredFields = ['loginId', 'username', 'email', 'password', 'passwordConfirm']
      const allFieldsValid = requiredFields.every(field => validFields.value[field])
      const noErrors = Object.keys(errors.value).length === 0
      const termsAgreed = formData.value.agreeTerms
      
      return allFieldsValid && noErrors && termsAgreed
    })

    const passwordStrength = computed(() => {
      const password = formData.value.password
      if (!password) return { width: '0%', class: '', text: '' }

      let score = 0
      let feedback = []

      // 길이 체크
      if (password.length >= 8) score += 1
      else feedback.push('8자 이상')

      // 영문 체크
      if (/[a-zA-Z]/.test(password)) score += 1
      else feedback.push('영문 포함')

      // 숫자 체크
      if (/\d/.test(password)) score += 1
      else feedback.push('숫자 포함')

      // 특수문자 체크
      if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1

      // 대소문자 체크
      if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 1

      if (score <= 2) {
        return { width: '33%', class: 'weak', text: '약함' + (feedback.length ? ` (${feedback.join(', ')} 필요)` : '') }
      } else if (score <= 3) {
        return { width: '66%', class: 'medium', text: '보통' }
      } else {
        return { width: '100%', class: 'strong', text: '강함' }
      }
    })

    // 메서드들
    const validateField = (fieldName) => {
      const value = formData.value[fieldName]
      
      switch (fieldName) {
        case 'loginId':
          if (!value) {
            errors.value.loginId = '로그인 ID는 필수입니다'
            validFields.value.loginId = false
          } else if (value.length < 4 || value.length > 20) {
            errors.value.loginId = '로그인 ID는 4-20자 사이여야 합니다'
            validFields.value.loginId = false
          } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            errors.value.loginId = '영문, 숫자, 언더스코어만 사용 가능합니다'
            validFields.value.loginId = false
          } else {
            delete errors.value.loginId
            // 중복 확인이 완료된 경우에만 valid 표시
          }
          break

        case 'username':
          if (!value) {
            errors.value.username = '사용자명은 필수입니다'
            validFields.value.username = false
          } else if (value.length < 2 || value.length > 50) {
            errors.value.username = '사용자명은 2-50자 사이여야 합니다'
            validFields.value.username = false
          } else {
            delete errors.value.username
            validFields.value.username = true
          }
          break

        case 'email':
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
          if (!value) {
            errors.value.email = '이메일은 필수입니다'
            validFields.value.email = false
          } else if (!emailRegex.test(value)) {
            errors.value.email = '올바른 이메일 형식을 입력해주세요'
            validFields.value.email = false
          } else {
            delete errors.value.email
            // 중복 확인이 완료된 경우에만 valid 표시
          }
          break

        case 'password':
          if (!value) {
            errors.value.password = '비밀번호는 필수입니다'
            validFields.value.password = false
          } else if (value.length < 8) {
            errors.value.password = '비밀번호는 최소 8자 이상이어야 합니다'
            validFields.value.password = false
          } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(value)) {
            errors.value.password = '영문과 숫자를 모두 포함해야 합니다'
            validFields.value.password = false
          } else {
            delete errors.value.password
            validFields.value.password = true
          }
          
          // 비밀번호 확인 재검증
          if (formData.value.passwordConfirm) {
            validateField('passwordConfirm')
          }
          break

        case 'passwordConfirm':
          if (!value) {
            errors.value.passwordConfirm = '비밀번호 확인은 필수입니다'
            validFields.value.passwordConfirm = false
          } else if (value !== formData.value.password) {
            errors.value.passwordConfirm = '비밀번호가 일치하지 않습니다'
            validFields.value.passwordConfirm = false
          } else {
            delete errors.value.passwordConfirm
            validFields.value.passwordConfirm = true
          }
          break

        case 'agreeTerms':
          if (!formData.value.agreeTerms) {
            errors.value.agreeTerms = '이용약관에 동의해주세요'
          } else {
            delete errors.value.agreeTerms
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

    const handleLoginIdInput = () => {
      clearFieldError('loginId')
      validFields.value.loginId = false // 중복 확인 초기화
    }

    const handleEmailInput = () => {
      clearFieldError('email')
      validFields.value.email = false // 중복 확인 초기화
    }

    const handlePasswordInput = () => {
      clearFieldError('password')
    }

    const checkLoginIdAvailability = async () => {
      if (errors.value.loginId || !formData.value.loginId) return

      checkingLoginId.value = true
      try {
        const result = await authService.checkLoginIdAvailability(formData.value.loginId)
        
        if (result.success && result.data.login_id?.available) {
          validFields.value.loginId = true
          delete errors.value.loginId
        } else {
          errors.value.loginId = result.data.login_id?.message || '이미 사용 중인 로그인 ID입니다'
          validFields.value.loginId = false
        }
      } catch (error) {
        errors.value.loginId = error.message || '중복 확인 중 오류가 발생했습니다'
        validFields.value.loginId = false
      } finally {
        checkingLoginId.value = false
      }
    }

    const checkEmailAvailability = async () => {
      if (errors.value.email || !formData.value.email) return

      checkingEmail.value = true
      try {
        const result = await authService.checkEmailAvailability(formData.value.email)
        
        if (result.success && result.data.email?.available) {
          validFields.value.email = true
          delete errors.value.email
        } else {
          errors.value.email = result.data.email?.message || '이미 사용 중인 이메일입니다'
          validFields.value.email = false
        }
      } catch (error) {
        errors.value.email = error.message || '중복 확인 중 오류가 발생했습니다'
        validFields.value.email = false
      } finally {
        checkingEmail.value = false
      }
    }

    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value
    }

    const togglePasswordConfirmVisibility = () => {
      showPasswordConfirm.value = !showPasswordConfirm.value
    }

    const showTerms = () => {
      emit('show-terms')
    }

    const showPrivacy = () => {
      emit('show-privacy')
    }

    const handleSubmit = async () => {
      // 모든 필드 검증
      Object.keys(formData.value).forEach(field => {
        if (field !== 'agreeTerms') {
          validateField(field)
        }
      })
      validateField('agreeTerms')

      // 중복 확인 검증
      if (formData.value.loginId && !validFields.value.loginId) {
        errors.value.loginId = '로그인 ID 중복 확인을 완료해주세요'
      }
      if (formData.value.email && !validFields.value.email) {
        errors.value.email = '이메일 중복 확인을 완료해주세요'
      }

      // 에러가 있으면 제출하지 않음
      if (Object.keys(errors.value).length > 0 || !isFormValid.value) {
        return
      }

      isLoading.value = true
      generalError.value = ''

      try {
        const userData = {
          loginId: formData.value.loginId,
          username: formData.value.username,
          email: formData.value.email,
          password: formData.value.password
        }

        const result = await authStore.register(userData)
        
        if (result.success) {
          emit('register-success', {
            user: authStore.user,
            redirectTo: '/diagnosis' // 회원가입 후 진단으로 이동
          })
        } else {
          throw new Error(result.error?.message || '회원가입에 실패했습니다')
        }
      } catch (error) {
        console.error('회원가입 오류:', error)
        
        // 에러 타입에 따른 메시지 설정
        if (error.code === 'DUPLICATE_DATA') {
          generalError.value = error.message
        } else if (error.code === 'VALIDATION_ERROR') {
          generalError.value = error.message
        } else if (error.status === 0) {
          generalError.value = '서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요'
        } else {
          generalError.value = error.message || '회원가입 중 오류가 발생했습니다'
        }
      } finally {
        isLoading.value = false
      }
    }

    // 폼 초기화
    const resetForm = () => {
      formData.value = {
        loginId: '',
        username: '',
        email: '',
        password: '',
        passwordConfirm: '',
        agreeTerms: false
      }
      errors.value = {}
      validFields.value = {}
      generalError.value = ''
      showPassword.value = false
      showPasswordConfirm.value = false
    }

    return {
      formData,
      errors,
      validFields,
      generalError,
      showPassword,
      showPasswordConfirm,
      isLoading,
      checkingLoginId,
      checkingEmail,
      isFormValid,
      passwordStrength,
      validateField,
      clearFieldError,
      handleLoginIdInput,
      handleEmailInput,
      handlePasswordInput,
      checkLoginIdAvailability,
      checkEmailAvailability,
      togglePasswordVisibility,
      togglePasswordConfirmVisibility,
      showTerms,
      showPrivacy,
      handleSubmit,
      resetForm
    }
  }
}
</script>

<style scoped>
.register-form {
  max-width: 450px;
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

.form-control.is-valid {
  border-color: #198754;
}

.form-control:disabled {
  background-color: #f8f9fa;
  opacity: 0.65;
}

.input-with-check {
  position: relative;
}

.check-availability-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  padding: 0.25rem 0.5rem;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.check-availability-btn:hover:not(:disabled) {
  background: #e9ecef;
}

.check-availability-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.check-availability-btn.checking {
  background: #e3f2fd;
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

.password-strength {
  margin-top: 0.5rem;
}

.strength-meter {
  height: 4px;
  background-color: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.strength-bar {
  height: 100%;
  transition: width 0.3s ease-in-out;
}

.strength-bar.weak {
  background-color: #dc3545;
}

.strength-bar.medium {
  background-color: #ffc107;
}

.strength-bar.strong {
  background-color: #198754;
}

.strength-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.strength-text.weak {
  color: #dc3545;
}

.strength-text.medium {
  color: #ffc107;
}

.strength-text.strong {
  color: #198754;
}

.form-check {
  display: flex;
  align-items: flex-start;
}

.form-check-input {
  margin-right: 0.5rem;
  margin-top: 0.25rem;
}

.form-check-input.is-invalid {
  border-color: #dc3545;
}

.form-check-label {
  color: #6c757d;
  cursor: pointer;
  margin-bottom: 0;
  line-height: 1.5;
}

.terms-link {
  color: #0d6efd;
  text-decoration: none;
}

.terms-link:hover {
  color: #0b5ed7;
  text-decoration: underline;
}

.invalid-feedback {
  display: block;
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.valid-feedback {
  display: block;
  color: #198754;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.check-required-feedback {
  display: block;
  color: #fd7e14;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  font-weight: 500;
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

.text-success {
  color: #198754;
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
  .register-form {
    padding: 1rem;
  }
  
  .form-title {
    font-size: 1.5rem;
  }
}
</style>