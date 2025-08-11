# 프론트엔드 인증 시스템 개발 일지

## 📅 개발 기간
**2025.08.11** - 프론트엔드 인증 시스템 구현 완료

---

## 🎯 개발 목표
- HttpOnly 쿠키 기반 보안 강화 인증 시스템 구현
- Vue 3 + Pinia 기반 상태 관리
- 컴포넌트 기반 모듈화된 구조
- 사용자 친화적 UI/UX 제공

---

## 📋 완료된 작업 목록

### 1️⃣ **보안 아키텍처 설계 및 구현**
- **HttpOnly 쿠키 방식 도입**: 기존 localStorage 방식에서 보안성 강화
- **토큰 관리 전략**:
  - Access Token: localStorage 저장 (1시간 만료)
  - Refresh Token: HttpOnly 쿠키 (30일 만료, JavaScript 접근 불가)
- **백엔드 API 수정**: 쿠키 설정/읽기 로직 변경

### 2️⃣ **핵심 유틸리티 구현**
#### `tokenManager.js` - 토큰 관리 유틸리티
- Access Token 저장/조회/삭제
- 토큰 파싱 및 만료 검사
- 사용자 정보 localStorage 관리
- HttpOnly 쿠키 방식에 맞는 API 설계

#### `authService.js` - API 서비스
- 회원가입, 로그인, 로그아웃 API 연동
- 중복 확인 API (로그인ID, 이메일)
- 자동 토큰 갱신 처리
- 표준화된 에러 처리

#### `api.js` - HTTP 클라이언트
- `withCredentials: true` 설정으로 쿠키 자동 전송
- 요청/응답 인터셉터 구현
- 401 에러 시 자동 토큰 갱신
- 권한 오류 시 자동 리다이렉트

### 3️⃣ **상태 관리 시스템**
#### `authStore.js` - Pinia 인증 스토어
- 사용자 정보 및 인증 상태 중앙 관리
- 로그인/회원가입/로그아웃 액션
- 권한 확인 및 진단 상태 관리
- 자동 토큰 갱신 및 상태 복원

### 4️⃣ **라우터 보안 시스템**
#### `authGuard.js` - 인증 가드
- **requireAuth**: 기본 인증 필요
- **requireDiagnosis**: 진단 완료 필요
- **requireUserType**: 특정 사용자 유형 필요
- **requireGuest**: 게스트 전용 (로그인된 사용자 차단)
- **requireLearningAccess**: 챕터별 접근 권한
- **applyMetaGuards**: 메타 정보 기반 자동 가드

#### `router/index.js` - 라우터 설정
- 페이지별 접근 권한 설정
- 자동 리다이렉트 처리
- 페이지 제목 자동 설정
- 에러 처리 및 스크롤 복원

### 5️⃣ **UI 컴포넌트 개발**
#### `LoginForm.vue` - 로그인 폼
- 실시간 입력 검증 (로그인ID 4-20자, 비밀번호 8자 이상)
- 비밀번호 표시/숨기기 토글
- 로그인 상태 유지 옵션
- 로딩 상태 및 에러 처리

#### `RegisterForm.vue` - 회원가입 폼
- 단계별 검증 (로그인ID, 사용자명, 이메일, 비밀번호)
- 실시간 중복 확인 (로그인ID, 이메일)
- 비밀번호 강도 표시
- 약관 동의 처리

#### `LoginPage.vue` - 통합 인증 페이지
- 좌우 분할 디자인 (브랜딩 + 폼)
- 탭 기반 로그인/회원가입 전환
- 성공 모달 및 결과 처리
- 약관/개인정보처리방침 모달
- 반응형 디자인

### 6️⃣ **개발자 도구**
#### `useAuth.js` - 컴포저블
- 인증 상태 및 사용자 정보 반응형 접근
- 권한 확인 헬퍼 함수
- 보호된 작업 수행 (`requireAuth`, `requireDiagnosis`)
- 이벤트 감지 및 디버깅 도구
- 리다이렉트 및 상태 업데이트 유틸리티

---

## 🏗️ 아키텍처 구조

```
Frontend Authentication System
├── 📁 utils/
│   └── tokenManager.js          # 토큰 관리
├── 📁 services/
│   ├── api.js                   # HTTP 클라이언트
│   └── authService.js           # 인증 API 서비스
├── 📁 stores/
│   └── authStore.js             # Pinia 상태 관리
├── 📁 router/
│   ├── authGuard.js             # 라우터 가드
│   └── index.js                 # 라우터 설정
├── 📁 composables/
│   └── useAuth.js               # 인증 컴포저블
├── 📁 components/auth/
│   ├── LoginForm.vue            # 로그인 폼
│   └── RegisterForm.vue         # 회원가입 폼
└── 📁 views/
    └── LoginPage.vue            # 인증 페이지
```

---

## 🔒 보안 강화 사항

### 1. **HttpOnly 쿠키 도입**
- **이전**: Refresh Token을 localStorage에 저장 (XSS 공격 취약)
- **현재**: Refresh Token을 HttpOnly 쿠키로 관리 (JavaScript 접근 불가)

### 2. **자동 토큰 갱신**
- Access Token 만료 5분 전 자동 갱신
- 갱신 실패 시 자동 로그아웃 처리
- 중복 갱신 방지 로직

### 3. **단일 세션 정책**
- 새 로그인 시 기존 토큰 무효화
- 모든 디바이스 로그아웃 기능

### 4. **입력 검증 강화**
- 클라이언트/서버 이중 검증
- 실시간 중복 확인
- 비밀번호 강도 검사
