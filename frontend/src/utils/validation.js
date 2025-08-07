// frontend/src/utils/validation.js
// 폼 검증 및 데이터 유효성 검사 함수들을 정의

import { ref, computed } from 'vue'
import { VALIDATION_RULES } from './constants'

// 기본 검증 함수들
export const validators = {
  // 필수 입력 검증
  required: (value, message = '필수 입력 항목입니다.') => {
    if (value === null || value === undefined || value === '') {
      return message
    }
    return null
  },

  // 이메일 검증
  email: (value, message = VALIDATION_RULES.EMAIL.MESSAGE) => {
    if (!value) return null // 빈 값은 required에서 처리
    if (!VALIDATION_RULES.EMAIL.PATTERN.test(value)) {
      return message
    }
    return null
  },

  // 비밀번호 검증
  password: (value, message = VALIDATION_RULES.PASSWORD.MESSAGE) => {
    if (!value) return null
    if (value.length < VALIDATION_RULES.PASSWORD.MIN_LENGTH) {
      return `비밀번호는 최소 ${VALIDATION_RULES.PASSWORD.MIN_LENGTH}자 이상이어야 합니다.`
    }
    if (!VALIDATION_RULES.PASSWORD.PATTERN.test(value)) {
      return message
    }
    return null
  },

  // 비밀번호 확인 검증
  passwordConfirm: (value, originalPassword, message = '비밀번호가 일치하지 않습니다.') => {
    if (!value) return null
    if (value !== originalPassword) {
      return message
    }
    return null
  },

  // 사용자명 검증
  username: (value, message = VALIDATION_RULES.USERNAME.MESSAGE) => {
    if (!value) return null
    if (value.length < VALIDATION_RULES.USERNAME.MIN_LENGTH || 
        value.length > VALIDATION_RULES.USERNAME.MAX_LENGTH) {
      return `사용자명은 ${VALIDATION_RULES.USERNAME.MIN_LENGTH}-${VALIDATION_RULES.USERNAME.MAX_LENGTH}자 사이여야 합니다.`
    }
    if (!VALIDATION_RULES.USERNAME.PATTERN.test(value)) {
      return message
    }
    return null
  },

  // 최소 길이 검증
  minLength: (minLength, message) => (value) => {
    if (!value) return null
    if (value.length < minLength) {
      return message || `최소 ${minLength}자 이상 입력해주세요.`
    }
    return null
  },

  // 최대 길이 검증
  maxLength: (maxLength, message) => (value) => {
    if (!value) return null
    if (value.length > maxLength) {
      return message || `최대 ${maxLength}자까지 입력 가능합니다.`
    }
    return null
  },

  // 숫자 검증
  numeric: (value, message = '숫자만 입력 가능합니다.') => {
    if (!value) return null
    if (!/^\d+$/.test(value)) {
      return message
    }
    return null
  },

  // 최소값 검증
  min: (minValue, message) => (value) => {
    if (!value) return null
    const numValue = Number(value)
    if (isNaN(numValue) || numValue < minValue) {
      return message || `${minValue} 이상의 값을 입력해주세요.`
    }
    return null
  },

  // 최대값 검증
  max: (maxValue, message) => (value) => {
    if (!value) return null
    const numValue = Number(value)
    if (isNaN(numValue) || numValue > maxValue) {
      return message || `${maxValue} 이하의 값을 입력해주세요.`
    }
    return null
  },

  // 정규식 패턴 검증
  pattern: (regex, message) => (value) => {
    if (!value) return null
    if (!regex.test(value)) {
      return message || '올바른 형식이 아닙니다.'
    }
    return null
  },

  // 한국어 이름 검증
  koreanName: (value, message = '한글 이름을 입력해주세요.') => {
    if (!value) return null
    if (!/^[가-힣]{2,10}$/.test(value)) {
      return message
    }
    return null
  },

  // 전화번호 검증
  phoneNumber: (value, message = '올바른 전화번호 형식을 입력해주세요.') => {
    if (!value) return null
    const phoneRegex = /^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$/
    if (!phoneRegex.test(value.replace(/\s/g, ''))) {
      return message
    }
    return null
  },

  // URL 검증
  url: (value, message = '올바른 URL 형식을 입력해주세요.') => {
    if (!value) return null
    try {
      new URL(value)
      return null
    } catch {
      return message
    }
  }
}

// 폼 검증 클래스
export class FormValidator {
  constructor(rules = {}) {
    this.rules = rules
    this.errors = {}
  }

  // 단일 필드 검증
  validateField(fieldName, value) {
    const fieldRules = this.rules[fieldName]
    if (!fieldRules) return null

    for (const rule of fieldRules) {
      const error = rule(value)
      if (error) {
        this.errors[fieldName] = error
        return error
      }
    }

    delete this.errors[fieldName]
    return null
  }

  // 전체 폼 검증
  validate(data) {
    this.errors = {}
    let isValid = true

    for (const fieldName in this.rules) {
      const error = this.validateField(fieldName, data[fieldName])
      if (error) {
        isValid = false
      }
    }

    return {
      isValid,
      errors: { ...this.errors }
    }
  }

  // 에러 초기화
  clearErrors() {
    this.errors = {}
  }

  // 특정 필드 에러 초기화
  clearFieldError(fieldName) {
    delete this.errors[fieldName]
  }

  // 에러 존재 여부 확인
  hasErrors() {
    return Object.keys(this.errors).length > 0
  }

  // 특정 필드 에러 존재 여부 확인
  hasFieldError(fieldName) {
    return !!this.errors[fieldName]
  }

  // 에러 메시지 가져오기
  getFieldError(fieldName) {
    return this.errors[fieldName] || null
  }
}

// 일반적인 폼 검증 규칙 세트
export const commonValidationRules = {
  // 로그인 폼
  loginForm: {
    email: [validators.required, validators.email],
    password: [validators.required]
  },

  // 회원가입 폼
  registerForm: {
    username: [validators.required, validators.username],
    email: [validators.required, validators.email],
    password: [validators.required, validators.password],
    passwordConfirm: [validators.required]
  },

  // 프로필 수정 폼
  profileForm: {
    username: [validators.required, validators.username],
    email: [validators.required, validators.email],
    name: [validators.koreanName],
    phone: [validators.phoneNumber]
  },

  // 비밀번호 변경 폼
  passwordChangeForm: {
    currentPassword: [validators.required],
    newPassword: [validators.required, validators.password],
    newPasswordConfirm: [validators.required]
  }
}

// 실시간 검증을 위한 컴포저블 스타일 함수
export const useFormValidation = (rules) => {
  const validator = new FormValidator(rules)
  const errors = ref({})
  const isValid = ref(true)

  const validateField = (fieldName, value) => {
    const error = validator.validateField(fieldName, value)
    errors.value = { ...validator.errors }
    return error
  }

  const validateForm = (data) => {
    const result = validator.validate(data)
    errors.value = result.errors
    isValid.value = result.isValid
    return result
  }

  const clearErrors = () => {
    validator.clearErrors()
    errors.value = {}
    isValid.value = true
  }

  const clearFieldError = (fieldName) => {
    validator.clearFieldError(fieldName)
    errors.value = { ...validator.errors }
  }

  return {
    errors: computed(() => errors.value),
    isValid: computed(() => isValid.value),
    validateField,
    validateForm,
    clearErrors,
    clearFieldError,
    hasErrors: computed(() => validator.hasErrors()),
    getFieldError: (fieldName) => validator.getFieldError(fieldName)
  }
}

// 파일 검증 함수들
export const fileValidators = {
  // 파일 크기 검증
  maxSize: (maxSizeInBytes, message) => (file) => {
    if (!file) return null
    if (file.size > maxSizeInBytes) {
      return message || `파일 크기는 ${Math.round(maxSizeInBytes / 1024 / 1024)}MB 이하여야 합니다.`
    }
    return null
  },

  // 파일 타입 검증
  allowedTypes: (allowedTypes, message) => (file) => {
    if (!file) return null
    if (!allowedTypes.includes(file.type)) {
      return message || `허용된 파일 형식: ${allowedTypes.join(', ')}`
    }
    return null
  },

  // 이미지 파일 검증
  imageFile: (file, message = '이미지 파일만 업로드 가능합니다.') => {
    if (!file) return null
    const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (!imageTypes.includes(file.type)) {
      return message
    }
    return null
  }
}