// frontend/src/composables/useApi.js
// API 호출 관련 컴포저블 - HTTP 요청, 에러 처리, 로딩 상태 관리

import { ref, computed } from 'vue'
import api from '@/services/api'

export function useApi() {
  const isLoading = ref(false)
  const error = ref(null)
  const data = ref(null)

  // API 요청 실행 함수
  const execute = async (apiCall, options = {}) => {
    const { 
      showLoading = true, 
      resetData = true,
      onSuccess = null,
      onError = null 
    } = options

    try {
      if (showLoading) isLoading.value = true
      if (resetData) data.value = null
      error.value = null

      const response = await apiCall()
      data.value = response.data

      // 성공 콜백 실행
      if (onSuccess) {
        onSuccess(response.data)
      }

      return { success: true, data: response.data }
    } catch (err) {
      console.error('API 요청 오류:', err)
      error.value = err.response?.data?.message || err.message || 'API 요청 중 오류가 발생했습니다.'
      
      // 에러 콜백 실행
      if (onError) {
        onError(err)
      }

      return { success: false, error: error.value }
    } finally {
      if (showLoading) isLoading.value = false
    }
  }

  // GET 요청 헬퍼
  const get = async (url, config = {}) => {
    return execute(() => api.get(url, config))
  }

  // POST 요청 헬퍼
  const post = async (url, data = {}, config = {}) => {
    return execute(() => api.post(url, data, config))
  }

  // PUT 요청 헬퍼
  const put = async (url, data = {}, config = {}) => {
    return execute(() => api.put(url, data, config))
  }

  // DELETE 요청 헬퍼
  const del = async (url, config = {}) => {
    return execute(() => api.delete(url, config))
  }

  // 에러 초기화
  const clearError = () => {
    error.value = null
  }

  // 데이터 초기화
  const clearData = () => {
    data.value = null
  }

  // 전체 상태 초기화
  const reset = () => {
    isLoading.value = false
    error.value = null
    data.value = null
  }

  return {
    // 상태
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    data: computed(() => data.value),
    hasError: computed(() => !!error.value),

    // 메서드
    execute,
    get,
    post,
    put,
    delete: del,
    clearError,
    clearData,
    reset
  }
}

// 특정 리소스에 대한 CRUD 작업을 위한 컴포저블
export function useResource(baseUrl) {
  const { execute, isLoading, error, data } = useApi()

  const list = async (params = {}) => {
    return execute(() => api.get(baseUrl, { params }))
  }

  const get = async (id) => {
    return execute(() => api.get(`${baseUrl}/${id}`))
  }

  const create = async (payload) => {
    return execute(() => api.post(baseUrl, payload))
  }

  const update = async (id, payload) => {
    return execute(() => api.put(`${baseUrl}/${id}`, payload))
  }

  const remove = async (id) => {
    return execute(() => api.delete(`${baseUrl}/${id}`))
  }

  return {
    isLoading,
    error,
    data,
    list,
    get,
    create,
    update,
    remove
  }
}