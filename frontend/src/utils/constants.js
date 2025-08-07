// frontend/src/utils/constants.js
// 애플리케이션 전체에서 사용되는 상수들을 정의

// API 관련 상수
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    VALIDATE: '/auth/validate',
    REFRESH: '/auth/refresh'
  },
  USER: {
    PROFILE: '/user/profile',
    PROGRESS: '/user/progress',
    STATISTICS: '/user/statistics'
  },
  LEARNING: {
    SESSIONS: '/learning/sessions',
    START_SESSION: '/learning/sessions/start',
    COMPLETE_SESSION: '/learning/sessions/complete',
    QUIZ: '/learning/quiz',
    SUBMIT_ANSWER: '/learning/quiz/submit',
    ASK_QUESTION: '/learning/qna'
  },
  CHAPTERS: {
    LIST: '/chapters',
    DETAIL: '/chapters'
  }
}

// 사용자 유형 상수
export const USER_TYPES = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced'
}

// 학습 단계 상수
export const LEARNING_STEPS = {
  THEORY: 'theory',
  QUIZ: 'quiz',
  FEEDBACK: 'feedback'
}

// 퀴즈 타입 상수
export const QUIZ_TYPES = {
  MULTIPLE_CHOICE: 'multiple_choice',
  TRUE_FALSE: 'true_false',
  SHORT_ANSWER: 'short_answer'
}

// 세션 상태 상수
export const SESSION_STATUS = {
  ACTIVE: 'active',
  COMPLETED: 'completed',
  PAUSED: 'paused'
}

// 알림 타입 상수
export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
}

// 로컬 스토리지 키 상수
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  LEARNING_PROGRESS: 'learning_progress',
  THEME: 'theme_preference',
  LANGUAGE: 'language_preference'
}

// 라우트 이름 상수
export const ROUTE_NAMES = {
  HOME: 'Home',
  LOGIN: 'Login',
  REGISTER: 'Register',
  DASHBOARD: 'Dashboard',
  LEARNING: 'Learning',
  PROFILE: 'Profile',
  DIAGNOSIS: 'Diagnosis'
}

// 테마 상수
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto'
}

// 언어 상수
export const LANGUAGES = {
  KO: 'ko',
  EN: 'en'
}

// 챕터 카테고리 상수
export const CHAPTER_CATEGORIES = {
  BASICS: 'basics',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced',
  PRACTICAL: 'practical'
}

// 진행 상태 상수
export const PROGRESS_STATUS = {
  NOT_STARTED: 'not_started',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed'
}

// HTTP 상태 코드 상수
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500
}

// 폼 검증 규칙 상수
export const VALIDATION_RULES = {
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    MESSAGE: '올바른 이메일 형식을 입력해주세요.'
  },
  PASSWORD: {
    MIN_LENGTH: 8,
    PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    MESSAGE: '비밀번호는 8자 이상이며, 대소문자, 숫자, 특수문자를 포함해야 합니다.'
  },
  USERNAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 20,
    PATTERN: /^[a-zA-Z0-9_]+$/,
    MESSAGE: '사용자명은 3-20자의 영문, 숫자, 언더스코어만 사용 가능합니다.'
  }
}

// 애니메이션 지속 시간 상수
export const ANIMATION_DURATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500
}

// 페이지네이션 상수
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100
}

// 파일 업로드 상수
export const FILE_UPLOAD = {
  MAX_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif'],
  ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.gif']
}