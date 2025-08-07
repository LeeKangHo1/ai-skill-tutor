// frontend/src/utils/helpers.js
// 범용적으로 사용되는 헬퍼 함수들을 정의

// 딥 클론 함수
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (typeof obj === 'object') {
    const clonedObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
}

// 디바운스 함수
export const debounce = (func, wait, immediate = false) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    if (callNow) func(...args)
  }
}

// 스로틀 함수
export const throttle = (func, limit) => {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// 랜덤 ID 생성
export const generateId = (length = 8) => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

// UUID v4 생성
export const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

// 배열을 청크 단위로 분할
export const chunk = (array, size) => {
  const chunks = []
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size))
  }
  return chunks
}

// 배열에서 중복 제거
export const unique = (array, key = null) => {
  if (key) {
    const seen = new Set()
    return array.filter(item => {
      const value = item[key]
      if (seen.has(value)) {
        return false
      }
      seen.add(value)
      return true
    })
  }
  return [...new Set(array)]
}

// 배열 셔플
export const shuffle = (array) => {
  const shuffled = [...array]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}

// 객체에서 빈 값 제거
export const removeEmpty = (obj) => {
  const cleaned = {}
  for (const key in obj) {
    if (obj[key] !== null && obj[key] !== undefined && obj[key] !== '') {
      if (typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
        const nested = removeEmpty(obj[key])
        if (Object.keys(nested).length > 0) {
          cleaned[key] = nested
        }
      } else {
        cleaned[key] = obj[key]
      }
    }
  }
  return cleaned
}

// 객체 키를 카멜케이스로 변환
export const camelCaseKeys = (obj) => {
  if (Array.isArray(obj)) {
    return obj.map(item => camelCaseKeys(item))
  } else if (obj !== null && typeof obj === 'object') {
    const camelCased = {}
    for (const key in obj) {
      const camelKey = key.replace(/_([a-z])/g, (match, letter) => letter.toUpperCase())
      camelCased[camelKey] = camelCaseKeys(obj[key])
    }
    return camelCased
  }
  return obj
}

// 객체 키를 스네이크케이스로 변환
export const snakeCaseKeys = (obj) => {
  if (Array.isArray(obj)) {
    return obj.map(item => snakeCaseKeys(item))
  } else if (obj !== null && typeof obj === 'object') {
    const snakeCased = {}
    for (const key in obj) {
      const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
      snakeCased[snakeKey] = snakeCaseKeys(obj[key])
    }
    return snakeCased
  }
  return obj
}

// 문자열을 케밥케이스로 변환
export const kebabCase = (str) => {
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase()
}

// 문자열을 파스칼케이스로 변환
export const pascalCase = (str) => {
  return str
    .replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => word.toUpperCase())
    .replace(/\s+/g, '')
}

// 문자열 자르기 (말줄임표 추가)
export const truncate = (str, length, suffix = '...') => {
  if (str.length <= length) return str
  return str.substring(0, length) + suffix
}

// 숫자를 한국어 단위로 변환
export const formatNumberToKorean = (num) => {
  const units = ['', '만', '억', '조']
  const result = []
  let unitIndex = 0

  while (num > 0) {
    const chunk = num % 10000
    if (chunk > 0) {
      result.unshift(chunk + units[unitIndex])
    }
    num = Math.floor(num / 10000)
    unitIndex++
  }

  return result.join(' ') || '0'
}

// 파일 크기를 읽기 쉬운 형태로 변환
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 색상 밝기 계산
export const getColorBrightness = (hex) => {
  const r = parseInt(hex.substr(1, 2), 16)
  const g = parseInt(hex.substr(3, 2), 16)
  const b = parseInt(hex.substr(5, 2), 16)
  return (r * 299 + g * 587 + b * 114) / 1000
}

// 어두운 색상인지 판단
export const isDarkColor = (hex) => {
  return getColorBrightness(hex) < 128
}

// 쿼리 파라미터를 객체로 변환
export const parseQueryParams = (queryString) => {
  const params = {}
  const urlParams = new URLSearchParams(queryString)
  for (const [key, value] of urlParams) {
    params[key] = value
  }
  return params
}

// 객체를 쿼리 파라미터 문자열로 변환
export const stringifyQueryParams = (params) => {
  const searchParams = new URLSearchParams()
  for (const key in params) {
    if (params[key] !== null && params[key] !== undefined) {
      searchParams.append(key, params[key])
    }
  }
  return searchParams.toString()
}

// 프로미스 지연 실행
export const delay = (ms) => {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 재시도 로직
export const retry = async (fn, maxAttempts = 3, delayMs = 1000) => {
  let lastError
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      if (attempt === maxAttempts) break
      await delay(delayMs * attempt) // 지수 백오프
    }
  }
  
  throw lastError
}