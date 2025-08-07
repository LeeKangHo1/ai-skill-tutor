// frontend/src/utils/formatting.js
// 데이터 포맷팅 관련 함수들을 정의 (날짜, 숫자, 텍스트 등)

// 날짜 포맷팅 함수들
export const dateFormatters = {
  // 기본 날짜 형식 (YYYY-MM-DD)
  toDateString: (date) => {
    if (!date) return ''
    const d = new Date(date)
    if (isNaN(d.getTime())) return ''
    return d.toISOString().split('T')[0]
  },

  // 한국어 날짜 형식 (YYYY년 MM월 DD일)
  toKoreanDate: (date) => {
    if (!date) return ''
    const d = new Date(date)
    if (isNaN(d.getTime())) return ''
    const year = d.getFullYear()
    const month = d.getMonth() + 1
    const day = d.getDate()
    return `${year}년 ${month}월 ${day}일`
  },

  // 시간 포함 한국어 형식 (YYYY년 MM월 DD일 HH:mm)
  toKoreanDateTime: (date) => {
    if (!date) return ''
    const d = new Date(date)
    if (isNaN(d.getTime())) return ''
    const year = d.getFullYear()
    const month = d.getMonth() + 1
    const day = d.getDate()
    const hours = d.getHours().toString().padStart(2, '0')
    const minutes = d.getMinutes().toString().padStart(2, '0')
    return `${year}년 ${month}월 ${day}일 ${hours}:${minutes}`
  },

  // 상대적 시간 표시 (몇 분 전, 몇 시간 전 등)
  toRelativeTime: (date) => {
    if (!date) return ''
    const d = new Date(date)
    if (isNaN(d.getTime())) return ''
    
    const now = new Date()
    const diffInSeconds = Math.floor((now - d) / 1000)
    
    if (diffInSeconds < 60) {
      return '방금 전'
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60)
      return `${minutes}분 전`
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600)
      return `${hours}시간 전`
    } else if (diffInSeconds < 2592000) {
      const days = Math.floor(diffInSeconds / 86400)
      return `${days}일 전`
    } else if (diffInSeconds < 31536000) {
      const months = Math.floor(diffInSeconds / 2592000)
      return `${months}개월 전`
    } else {
      const years = Math.floor(diffInSeconds / 31536000)
      return `${years}년 전`
    }
  },

  // 시간만 표시 (HH:mm)
  toTimeString: (date) => {
    if (!date) return ''
    const d = new Date(date)
    if (isNaN(d.getTime())) return ''
    const hours = d.getHours().toString().padStart(2, '0')
    const minutes = d.getMinutes().toString().padStart(2, '0')
    return `${hours}:${minutes}`
  },

  // 학습 시간 포맷 (분 단위를 시간:분 형식으로)
  toStudyTime: (minutes) => {
    if (!minutes || minutes < 0) return '0분'
    if (minutes < 60) {
      return `${minutes}분`
    }
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    if (remainingMinutes === 0) {
      return `${hours}시간`
    }
    return `${hours}시간 ${remainingMinutes}분`
  }
}

// 숫자 포맷팅 함수들
export const numberFormatters = {
  // 천 단위 콤마 추가
  toCommaString: (number) => {
    if (number === null || number === undefined) return ''
    return Number(number).toLocaleString('ko-KR')
  },

  // 퍼센트 형식
  toPercent: (number, decimals = 1) => {
    if (number === null || number === undefined) return '0%'
    return `${Number(number).toFixed(decimals)}%`
  },

  // 점수 형식 (100점 만점)
  toScore: (score, maxScore = 100) => {
    if (score === null || score === undefined) return '0점'
    return `${Math.round(score)}점`
  },

  // 진행률 표시
  toProgress: (current, total) => {
    if (!total || total === 0) return '0%'
    const percentage = Math.round((current / total) * 100)
    return `${percentage}% (${current}/${total})`
  },

  // 파일 크기 포맷
  toFileSize: (bytes) => {
    if (!bytes || bytes === 0) return '0 B'
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
  },

  // 순위 표시 (1st, 2nd, 3rd 등)
  toOrdinal: (number) => {
    if (!number) return ''
    const suffixes = ['번째', '번째', '번째', '번째']
    return `${number}${suffixes[0]}`
  }
}

// 텍스트 포맷팅 함수들
export const textFormatters = {
  // 첫 글자 대문자
  capitalize: (text) => {
    if (!text) return ''
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
  },

  // 각 단어의 첫 글자 대문자
  titleCase: (text) => {
    if (!text) return ''
    return text.replace(/\w\S*/g, (txt) => 
      txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    )
  },

  // 텍스트 자르기 (말줄임표 추가)
  truncate: (text, length = 50, suffix = '...') => {
    if (!text) return ''
    if (text.length <= length) return text
    return text.substring(0, length) + suffix
  },

  // 단어 단위로 자르기
  truncateWords: (text, wordCount = 10, suffix = '...') => {
    if (!text) return ''
    const words = text.split(' ')
    if (words.length <= wordCount) return text
    return words.slice(0, wordCount).join(' ') + suffix
  },

  // HTML 태그 제거
  stripHtml: (html) => {
    if (!html) return ''
    return html.replace(/<[^>]*>/g, '')
  },

  // 줄바꿈을 <br> 태그로 변환
  nl2br: (text) => {
    if (!text) return ''
    return text.replace(/\n/g, '<br>')
  },

  // 이메일 마스킹 (일부 문자를 * 로 대체)
  maskEmail: (email) => {
    if (!email) return ''
    const [username, domain] = email.split('@')
    if (!domain) return email
    const maskedUsername = username.length > 2 
      ? username.substring(0, 2) + '*'.repeat(username.length - 2)
      : username
    return `${maskedUsername}@${domain}`
  },

  // 전화번호 마스킹
  maskPhone: (phone) => {
    if (!phone) return ''
    const cleaned = phone.replace(/\D/g, '')
    if (cleaned.length === 11) {
      return cleaned.replace(/(\d{3})(\d{4})(\d{4})/, '$1-****-$3')
    }
    return phone
  },

  // 이름 마스킹 (가운데 글자를 * 로 대체)
  maskName: (name) => {
    if (!name || name.length < 2) return name
    if (name.length === 2) {
      return name.charAt(0) + '*'
    }
    const first = name.charAt(0)
    const last = name.charAt(name.length - 1)
    const middle = '*'.repeat(name.length - 2)
    return first + middle + last
  }
}

// 학습 관련 포맷팅 함수들
export const learningFormatters = {
  // 학습 단계 한글 변환
  toStepName: (step) => {
    const stepNames = {
      'theory': '이론 학습',
      'quiz': '퀴즈',
      'feedback': '피드백'
    }
    return stepNames[step] || step
  },

  // 사용자 레벨 표시
  toUserLevel: (level) => {
    const levels = {
      'beginner': '초급자',
      'intermediate': '중급자',
      'advanced': '고급자'
    }
    return levels[level] || level
  },

  // 퀴즈 타입 한글 변환
  toQuizType: (type) => {
    const types = {
      'multiple_choice': '객관식',
      'true_false': 'O/X',
      'short_answer': '단답형'
    }
    return types[type] || type
  },

  // 세션 상태 한글 변환
  toSessionStatus: (status) => {
    const statuses = {
      'active': '진행 중',
      'completed': '완료',
      'paused': '일시정지'
    }
    return statuses[status] || status
  },

  // 진행 상태 한글 변환
  toProgressStatus: (status) => {
    const statuses = {
      'not_started': '시작 전',
      'in_progress': '진행 중',
      'completed': '완료'
    }
    return statuses[status] || status
  },

  // 학습 통계 포맷
  toStudyStats: (stats) => {
    if (!stats) return {}
    return {
      totalSessions: `${stats.totalSessions || 0}회`,
      totalTime: dateFormatters.toStudyTime(stats.totalTime || 0),
      averageScore: `${Math.round(stats.averageScore || 0)}점`,
      completionRate: numberFormatters.toPercent(stats.completionRate || 0)
    }
  }
}

// 통합 포맷터 객체
export const formatters = {
  date: dateFormatters,
  number: numberFormatters,
  text: textFormatters,
  learning: learningFormatters
}

// 기본 포맷팅 함수들을 직접 export
export const {
  toDateString,
  toKoreanDate,
  toKoreanDateTime,
  toRelativeTime,
  toTimeString,
  toStudyTime
} = dateFormatters

export const {
  toCommaString,
  toPercent,
  toScore,
  toProgress,
  toFileSize,
  toOrdinal
} = numberFormatters

export const {
  capitalize,
  titleCase,
  truncate,
  truncateWords,
  stripHtml,
  nl2br,
  maskEmail,
  maskPhone,
  maskName
} = textFormatters