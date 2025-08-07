# 프론트엔드 폴더 구조

```
ai-skill-tutor-frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
│       ├── images/
│       │   ├── logo.png
│       │   └── icons/
│       └── fonts/
├── src/
│   ├── main.js                    # Vue 앱 진입점
│   ├── App.vue                    # 루트 컴포넌트
│   ├── router/
│   │   └── index.js               # Vue Router 설정
│   ├── stores/
│   │   ├── index.js               # Pinia store 설정
│   │   ├── authStore.js           # 인증 관련 상태 관리
│   │   ├── tutorStore.js          # 학습 세션 상태 관리
│   │   └── dashboardStore.js      # 대시보드 상태 관리
│   ├── views/
│   │   ├── LoginPage.vue          # 로그인/회원가입 페이지
│   │   ├── DiagnosisPage.vue      # 사용자 진단 페이지
│   │   ├── DashboardPage.vue      # 대시보드 페이지
│   │   └── LearningPage.vue       # 학습 진행 페이지
│   ├── components/
│   │   ├── common/
│   │   │   ├── HeaderComponent.vue
│   │   │   ├── LoadingModal.vue
│   │   │   └── AlertMessage.vue
│   │   ├── auth/
│   │   │   ├── LoginForm.vue
│   │   │   └── RegisterForm.vue
│   │   ├── diagnosis/
│   │   │   ├── DiagnosisQuestion.vue
│   │   │   └── ProgressBar.vue
│   │   ├── dashboard/
│   │   │   ├── LearningStats.vue
│   │   │   ├── ChapterList.vue
│   │   │   └── ChapterCard.vue
│   │   └── learning/
│   │       ├── SessionProgressIndicator.vue
│   │       ├── MainContentArea.vue
│   │       ├── content/
│   │       │   ├── TheoryContent.vue
│   │       │   ├── QuizContent.vue
│   │       │   ├── FeedbackContent.vue
│   │       │   └── SessionCompleteContent.vue
│   │       └── chat/
│   │           ├── ChatArea.vue
│   │           ├── ChatHistory.vue
│   │           ├── ChatInput.vue
│   │           └── QuizAnswerInput.vue
│   ├── composables/
│   │   ├── useAuth.js             # 인증 관련 컴포저블
│   │   ├── useApi.js              # API 호출 컴포저블
│   │   ├── useLearning.js         # 학습 세션 컴포저블
│   │   └── useNotification.js     # 알림 컴포저블
│   ├── services/
│   │   ├── api.js                 # Axios 설정 및 기본 API 함수
│   │   ├── authService.js         # 인증 관련 API
│   │   ├── learningService.js     # 학습 관련 API
│   │   ├── dashboardService.js    # 대시보드 관련 API
│   │   └── diagnosisService.js    # 진단 관련 API
│   ├── utils/
│   │   ├── constants.js           # 상수 정의
│   │   ├── helpers.js             # 유틸리티 함수
│   │   ├── validators.js          # 입력값 검증 함수
│   │   └── formatters.js          # 데이터 포맷팅 함수
│   ├── styles/
│   │   ├── main.scss              # 메인 스타일시트
│   │   ├── variables.scss         # SCSS 변수
│   │   ├── mixins.scss            # SCSS 믹스인
│   │   ├── components/
│   │   │   ├── _buttons.scss
│   │   │   ├── _forms.scss
│   │   │   ├── _cards.scss
│   │   │   └── _modals.scss
│   │   └── pages/
│   │       ├── _login.scss
│   │       ├── _dashboard.scss
│   │       └── _learning.scss
│   └── assets/
│       ├── images/
│       └── icons/
├── .env                           # 환경 변수 (개발용)
├── .env.production                # 환경 변수 (운영용)
├── .gitignore
├── package.json
├── vite.config.js                 # Vite 설정
├── index.html
└── README.md
```

## 주요 폴더별 설명

### `/src/views/`
- 페이지 단위 컴포넌트
- 라우터와 직접 연결되는 최상위 컴포넌트들

### `/src/components/`
- 재사용 가능한 UI 컴포넌트들
- 기능별로 폴더 구분 (common, auth, diagnosis, dashboard, learning)

### `/src/stores/`
- Pinia를 사용한 상태 관리
- 기능별로 스토어 분리

### `/src/composables/`
- Vue 3 Composition API 활용
- 재사용 가능한 로직 분리

### `/src/services/`
- API 호출 관련 로직
- Axios 기반 HTTP 통신 처리

### `/src/utils/`
- 공통 유틸리티 함수들
- 상수, 검증, 포맷팅 등

### `/src/styles/`
- SCSS 기반 스타일링
- 컴포넌트별, 페이지별 스타일 분리