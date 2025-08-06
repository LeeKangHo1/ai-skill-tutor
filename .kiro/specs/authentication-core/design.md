# Design Document

## Overview

JWT 기반의 간단한 인증 시스템입니다. 사용자 회원가입, 로그인, 토큰 기반 인증을 제공하며, refresh token을 데이터베이스에 저장하여 관리합니다.

## Architecture

### Simple Authentication Flow

```
Frontend (Vue.js) ←→ Backend (Flask) ←→ Database (MySQL)
```

### Token Strategy

- **Access Token**: 1시간 만료, API 요청에 사용
- **Refresh Token**: 30일 만료, 데이터베이스에 저장
- **Single Session**: 새 로그인 시 기존 토큰 무효화

## Components and Interfaces

### 1. Backend Components

#### Authentication Service (`auth_service.py`)
- `register_user()`: 회원가입 처리
- `authenticate_user()`: 로그인 인증
- `refresh_access_token()`: 토큰 갱신
- `logout_user()`: 로그아웃 처리

#### JWT Manager (`jwt_manager.py`)
- `generate_access_token()`: Access Token 생성
- `generate_refresh_token()`: Refresh Token 생성
- `verify_token()`: 토큰 검증

#### Authentication Middleware (`auth_middleware.py`)
- `@require_auth`: 인증 필수 데코레이터
- Bearer Token 검증 및 사용자 정보 추출

#### API Routes (`auth_routes.py`)
- `POST /auth/register`: 회원가입
- `POST /auth/login`: 로그인
- `POST /auth/refresh`: 토큰 갱신
- `POST /auth/logout`: 로그아웃
- `GET /auth/me`: 현재 사용자 정보

### 2. Frontend Components

#### Authentication Store (`authStore.js` - Pinia)
- 사용자 인증 상태 관리
- 토큰 저장/복원
- 로그인/로그아웃 처리

#### HTTP Client (`httpClient.js`)
- Axios 기반 HTTP 클라이언트
- 자동 토큰 추가 및 갱신
- 401 오류 시 자동 토큰 갱신

#### Route Guards
- `requireAuth`: 로그인 필수 페이지 보호
- `requireGuest`: 비로그인 사용자만 접근
- `requireDiagnosis`: 진단 완료 후 접근

#### UI Pages
- `LoginPage.vue`: 로그인 폼
- `RegisterPage.vue`: 회원가입 폼

## Data Models

### Token Storage
- **Client**: Access Token (sessionStorage), Refresh Token (HttpOnly 쿠키)
- **Server**: Refresh Token (user_auth_tokens 테이블)

## Error Handling

### Basic Error Types
- `InvalidCredentialsError`: 잘못된 로그인 정보
- `TokenExpiredError`: 토큰 만료
- `DuplicateUserError`: 중복 사용자

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "아이디 또는 비밀번호가 올바르지 않습니다."
  }
}
```

## Testing Strategy

### Backend Tests
- JWT 토큰 생성/검증
- 비밀번호 해시화/검증
- 인증 API 엔드포인트

### Frontend Tests
- 로그인/회원가입 폼
- 자동 토큰 갱신
- 라우트 가드

## Security

### Password Security
- bcrypt 해시화 사용

### Token Security
- JWT 시크릿 키 환경변수 관리
- Access Token 1시간, Refresh Token 30일 만료
- 단일 세션 정책 (새 로그인 시 기존 토큰 무효화)
- Refresh Token: HttpOnly 쿠키 + 데이터베이스 저장으로 XSS 방지

