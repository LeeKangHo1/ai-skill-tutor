# AI 활용법 학습 튜터 - 프론트엔드

AI 입문자를 위한 개인화된 학습 플랫폼의 프론트엔드 애플리케이션입니다.

## 📋 프로젝트 개요

이 프로젝트는 Vue 3와 최신 웹 기술을 사용하여 구축된 AI 학습 튜터의 사용자 인터페이스입니다. 사용자 진단, 개인화된 학습 경험, 실시간 피드백을 제공하는 현대적이고 반응형 웹 애플리케이션입니다.

## 🛠 기술 스택

- **프레임워크**: Vue 3 (Composition API)
- **빌드 도구**: Vite
- **상태 관리**: Pinia
- **라우팅**: Vue Router
- **HTTP 클라이언트**: Axios
- **스타일링**: Sass/SCSS
- **테스팅**: Vitest
- **개발 언어**: JavaScript (ES6+)

## 📁 프로젝트 구조

```
src/
├── assets/              # 정적 자산 (이미지, 폰트 등)
├── components/          # 재사용 가능한 Vue 컴포넌트
│   ├── common/         # 공통 컴포넌트
│   ├── auth/           # 인증 관련 컴포넌트
│   ├── diagnosis/      # 진단 관련 컴포넌트
│   ├── dashboard/      # 대시보드 컴포넌트
│   └── learning/       # 학습 관련 컴포넌트
├── composables/         # Vue 3 Composition API 로직
├── router/             # Vue Router 설정
├── services/           # API 서비스 및 HTTP 통신
├── stores/             # Pinia 상태 관리
│   ├── authStore.js    # 인증 상태
│   ├── tutorStore.js   # 학습 세션 상태
│   └── dashboardStore.js # 대시보드 상태
├── styles/             # 전역 스타일 및 SCSS 파일
│   ├── main.scss       # 메인 스타일시트
│   ├── variables.scss  # SCSS 변수
│   └── mixins.scss     # SCSS 믹스인
├── utils/              # 유틸리티 함수
├── views/              # 페이지 컴포넌트
│   ├── HomeView.vue    # 홈 페이지
│   └── AboutView.vue   # 소개 페이지
├── App.vue             # 루트 컴포넌트
└── main.js             # 애플리케이션 진입점
```

## 🚀 개발 환경 설정

### 필수 요구사항

- Node.js (v18 이상)
- npm 또는 yarn

### 설치 및 실행

1. **의존성 설치**
   ```bash
   npm install
   ```

2. **개발 서버 실행**
   ```bash
   npm run dev
   ```
   브라우저에서 `http://localhost:5173`으로 접속

3. **프로덕션 빌드**
   ```bash
   npm run build
   ```

4. **빌드 결과 미리보기**
   ```bash
   npm run preview
   ```

5. **단위 테스트 실행**
   ```bash
   npm run test:unit
   ```

## 🎨 주요 기능

### 현재 구현된 기능
- ✅ 반응형 레이아웃 및 네비게이션
- ✅ Vue Router를 통한 페이지 라우팅
- ✅ Pinia를 통한 상태 관리 구조
- ✅ SCSS 기반 스타일링 시스템
- ✅ 컴포넌트 기반 아키텍처

### 향후 구현 예정
- 🔄 사용자 인증 시스템
- 🔄 AI 진단 인터페이스
- 🔄 학습 대시보드
- 🔄 실시간 학습 세션
- 🔄 진도 추적 및 통계

## 🔧 개발 가이드

### 코딩 컨벤션
- **컴포넌트**: PascalCase (예: `UserProfile.vue`)
- **파일명**: camelCase (예: `userService.js`)
- **변수/함수**: camelCase
- **상수**: UPPER_SNAKE_CASE

### 스타일 가이드
- SCSS 변수는 `variables.scss`에서 관리
- 재사용 가능한 스타일은 `mixins.scss`에서 정의
- 컴포넌트별 스타일은 `<style scoped>` 사용

### 상태 관리
- 각 기능별로 별도의 Pinia 스토어 생성
- 스토어는 `stores/` 디렉토리에서 관리
- 액션, 게터, 상태를 명확히 분리

## 🌐 API 연동

백엔드 API와의 연동을 위해 다음 설정을 사용합니다:

```javascript
// 개발 환경
const API_BASE_URL = 'http://localhost:5000'

// 프로덕션 환경
const API_BASE_URL = process.env.VITE_API_URL
```

## 📱 반응형 디자인

다음 브레이크포인트를 사용합니다:
- **모바일**: < 768px
- **태블릿**: 768px - 1024px
- **데스크톱**: > 1024px

## 🐛 문제 해결

### 일반적인 문제들

1. **개발 서버가 시작되지 않는 경우**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   npm run dev
   ```

2. **스타일이 적용되지 않는 경우**
   - `main.js`에서 스타일 import 확인
   - SCSS 문법 오류 확인

3. **라우팅이 작동하지 않는 경우**
   - `router/index.js` 설정 확인
   - 컴포넌트 import 경로 확인

## 📄 라이선스

이 프로젝트는 포트폴리오 목적으로 개발되었습니다.

## 👨‍💻 개발자

**AI 활용법 학습 튜터 프로젝트**  
개발 기간: 2025년 1월 ~ 진행중  
목적: 입사 포트폴리오용 MVP

---

더 자세한 정보는 [프로젝트 문서](../docs/)를 참조하세요.