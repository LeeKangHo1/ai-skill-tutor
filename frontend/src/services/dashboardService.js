// frontend/src/services/dashboardService.js

/**
 * 대시보드 관련 API 서비스
 * - 학습 현황 데이터 조회
 * - UI 친화적 데이터 포맷팅
 * - 캐싱 및 에러 처리
 */

import api from './api'

class DashboardService {
  /**
   * 대시보드 개요 데이터 조회
   * GET /dashboard/overview
   */
  async getDashboardOverview() {
    try {
      const response = await api.get('/dashboard/overview')
      
      if (response.data.success) {
        return {
          success: true,
          data: response.data.data
        }
      } else {
        throw new Error(response.data.error?.message || '대시보드 데이터 조회 실패')
      }
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 대시보드 헬스 체크
   * GET /dashboard/health
   */
  async checkDashboardHealth() {
    try {
      const response = await api.get('/dashboard/health')
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 챕터 상태 정보 포맷팅 (UI 표시용 데이터 추가)
   */
  formatChapterStatus(chapterStatus) {
    if (!Array.isArray(chapterStatus)) return []

    return chapterStatus.map(chapter => ({
      ...chapter,
      // 상태 아이콘 매핑
      status_icon: this.getStatusIcon(chapter.status),
      // 완료 날짜 포맷팅
      formatted_completion_date: this.formatDate(chapter.completion_date),
      // 섹션별 포맷팅
      sections: chapter.sections?.map(section => ({
        ...section,
        formatted_completion_date: this.formatDate(section.completion_date),
        status_icon: this.getStatusIcon(section.status)
      })) || []
    }))
  }

  /**
   * 상태별 아이콘 반환
   */
  getStatusIcon(status) {
    const iconMap = {
      'completed': '✅',
      'in_progress': '⏳',
      'locked': '🔒',
      'available': '📚'
    }
    return iconMap[status] || '📚'
  }

  /**
   * 날짜 포맷팅 (YYYY-MM-DD → YYYY년 MM월 DD일)
   */
  formatDate(dateString) {
    if (!dateString) return null
    
    try {
      const date = new Date(dateString)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      
      return `${year}년 ${month}월 ${day}일`
    } catch (error) {
      console.warn('날짜 포맷팅 실패:', dateString, error)
      return dateString
    }
  }

  /**
   * 학습 통계 포맷팅
   */
  formatLearningStatistics(statistics) {
    if (!statistics) return null

    return {
      ...statistics,
      // 학습 시간을 시간:분 형식으로 변환 (초 단위를 분으로 변환)
      formatted_study_time: this.formatStudyTime(statistics.total_study_time_seconds),
      // 정확도 포맷팅
      formatted_multiple_choice_accuracy: this.formatPercentage(statistics.multiple_choice_accuracy),
      formatted_subjective_average_score: this.formatScore(statistics.subjective_average_score),
      // 마지막 학습 날짜 포맷팅
      formatted_last_study_date: this.formatDate(statistics.last_study_date)
    }
  }

  /**
   * 학습 시간 포맷팅 (초 → 시간:분)
   * 1분 미만(60초 미만)일 경우 1분으로 표시
   */
  formatStudyTime(seconds) {
    if (!seconds || seconds === 0) return '0분'
    
    const totalMinutes = Math.floor(seconds / 60)
    const hours = Math.floor(totalMinutes / 60)
    const remainingMinutes = totalMinutes % 60
    
    // 1분 미만(60초 미만)일 경우 1분으로 표시
    if (totalMinutes === 0 && seconds > 0) {
      return '1분'
    }
    
    if (hours === 0) {
      return `${remainingMinutes}분`
    } else if (remainingMinutes === 0) {
      return `${hours}시간`
    } else {
      return `${hours}시간 ${remainingMinutes}분`
    }
  }

  /**
   * 백분율 포맷팅
   */
  formatPercentage(value) {
    if (value === null || value === undefined) return '0%'
    return `${Math.round(value * 10) / 10}%`
  }

  /**
   * 점수 포맷팅
   */
  formatScore(value) {
    if (value === null || value === undefined) return '0점'
    return `${Math.round(value * 10) / 10}점`
  }

  /**
   * 진행률 포맷팅 (백엔드에서 계산된 값 그대로 사용)
   */
  formatCompletionPercentage(percentage) {
    if (percentage === null || percentage === undefined) return '0%'
    return `${Math.round(percentage * 10) / 10}%`
  }

  /**
   * 대시보드 데이터 캐싱 (옵션)
   */
  async getDashboardDataWithCache(forceRefresh = false) {
    const cacheKey = 'dashboard_data'
    const cacheTimeout = 5 * 60 * 1000 // 5분

    // 강제 새로고침이 아니고 캐시가 유효한 경우
    if (!forceRefresh) {
      const cachedData = this.getCachedData(cacheKey, cacheTimeout)
      if (cachedData) {
        return cachedData
      }
    }

    // 새 데이터 조회
    const freshData = await this.getDashboardOverview()
    
    // 캐시 저장
    this.setCachedData(cacheKey, freshData)
    
    return freshData
  }

  /**
   * 캐시 데이터 조회
   */
  getCachedData(key, timeout) {
    try {
      const cached = localStorage.getItem(key)
      if (!cached) return null

      const { data, timestamp } = JSON.parse(cached)
      
      // 캐시 만료 확인
      if (Date.now() - timestamp > timeout) {
        localStorage.removeItem(key)
        return null
      }

      return data
    } catch (error) {
      console.warn('캐시 데이터 조회 실패:', error)
      return null
    }
  }

  /**
   * 캐시 데이터 저장
   */
  setCachedData(key, data) {
    try {
      const cacheData = {
        data,
        timestamp: Date.now()
      }
      localStorage.setItem(key, JSON.stringify(cacheData))
    } catch (error) {
      console.warn('캐시 데이터 저장 실패:', error)
    }
  }

  /**
   * 대시보드 데이터 종합 처리 (백엔드 계산 결과 + UI 포맷팅)
   */
  async getFormattedDashboardData(forceRefresh = false) {
    try {
      const response = await this.getDashboardDataWithCache(forceRefresh)
      
      if (!response.success) {
        throw new Error('대시보드 데이터 조회 실패')
      }

      const { user_progress, learning_statistics, chapter_status } = response.data

      return {
        success: true,
        data: {
          // 사용자 진행 상태 (백엔드 계산 결과 + 포맷팅)
          userProgress: {
            ...user_progress,
            formatted_completion_percentage: this.formatCompletionPercentage(user_progress.completion_percentage)
          },
          // 학습 통계 (포맷팅 추가)
          learningStatistics: this.formatLearningStatistics(learning_statistics),
          // 챕터 상태 (백엔드 상태 + UI 아이콘/날짜 포맷팅)
          chapterStatus: this.formatChapterStatus(chapter_status)
        }
      }
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 에러 처리 헬퍼
   */
  handleError(error) {
    if (error.response) {
      // 서버 응답이 있는 경우
      const errorData = error.response.data
      
      if (errorData && !errorData.success) {
        return {
          message: errorData.error.message || '대시보드 조회 실패',
          code: errorData.error.code,
          details: errorData.error.details || null,
          status: error.response.status
        }
      }
    }

    // 네트워크 오류 또는 기타 오류
    return {
      message: error.message || '대시보드 데이터를 불러올 수 없습니다',
      code: 'DASHBOARD_ERROR',
      details: null,
      status: error.response?.status || 0
    }
  }
}

// 싱글톤 인스턴스 생성
const dashboardService = new DashboardService()

export default dashboardService