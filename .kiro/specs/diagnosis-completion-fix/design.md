# Design Document

## Overview

진단 완료 후 대시보드 접근 시 403 에러가 발생하는 문제는 **JWT 토큰과 데이터베이스 간의 동기화 문제**입니다. 

**문제 분석:**
1. 사용자가 진단을 완료하면 데이터베이스에 `diagnosis_completed = 1`로 업데이트됩니다.
2. 하지만 이미 발급된 JWT 토큰에는 여전히 `diagnosis_completed: false`가 포함되어 있습니다.
3. 대시보드 접근 시 JWT 토큰의 `diagnosis_completed` 값을 확인하므로 403 에러가 발생합니다.
4. 로그아웃 후 재로그인하면 새로운 JWT 토큰이 발급되어 정상 작동합니다.

## Architecture

### 현재 아키텍처의 문제점

```
진단 완료 → DB 업데이트 (diagnosis_completed = 1)
     ↓
기존 JWT 토큰 (diagnosis_completed: false) ← 대시보드 접근 시 사용
     ↓
403 에러 발생
```

### 해결 방안 아키텍처

```
진단 완료 → DB 업데이트 → 새로운 JWT 토큰 발급 → 클라이언트 토큰 갱신
     ↓
대시보드 접근 시 최신 토큰 사용 → 정상 접근
```

## Components and Interfaces

### 1. 진단 완료 처리 개선

**파일:** `backend/app/routes/diagnosis/submit.py`

- `select_user_type()` 함수에서 DB 업데이트 후 새로운 JWT 토큰 발급
- 클라이언트에 새로운 `access_token` 반환

### 2. 대시보드 접근 로직 개선 (백업 방안)

**파일:** `backend/app/routes/dashboard/overview.py`

- JWT 토큰의 `diagnosis_completed`가 false인 경우 DB에서 실제 상태 재확인
- DB 상태가 true이면 접근 허용

### 3. 클라이언트 토큰 갱신

**파일:** `frontend/src/services/diagnosisService.js`

- 진단 완료 응답에서 새로운 토큰을 받아 저장소 업데이트

## Data Models

### JWT Payload 구조
```javascript
{
  user_id: number,
  login_id: string,
  user_type: string,
  diagnosis_completed: boolean,  // 이 값이 실시간으로 업데이트되어야 함
  token_type: 'access',
  iat: timestamp,
  exp: timestamp
}
```

### API 응답 구조 (진단 완료)
```javascript
{
  success: true,
  data: {
    recommended_type: string,
    recommended_description: string,
    recommended_chapters: number,
    recommended_duration: string,
    access_token: string  // 새로 추가될 필드
  },
  message: string
}
```

## Error Handling

### 현재 에러 상황
- **에러 코드:** `DIAGNOSIS_NOT_COMPLETED`
- **HTTP 상태:** 403
- **메시지:** "진단을 먼저 완료해주세요."

### 개선된 에러 처리
1. **1차 검증:** JWT 토큰의 `diagnosis_completed` 확인
2. **2차 검증:** JWT가 false인 경우 DB에서 실제 상태 확인
3. **토큰 불일치 감지:** DB는 true, JWT는 false인 경우 로그 기록
4. **자동 복구:** DB 상태에 따라 접근 허용

## Testing Strategy

### 테스트 시나리오

1. **진단 완료 후 즉시 대시보드 접근**
   - 진단 완료 → 새 토큰 발급 확인 → 대시보드 접근 성공

2. **기존 토큰으로 대시보드 접근 (백업 로직)**
   - 구 토큰 사용 → DB 재확인 → 접근 허용

3. **토큰-DB 불일치 로깅**
   - 불일치 상황 발생 → 적절한 로그 기록 확인

### 테스트 도구
- 단위 테스트: JWT 토큰 생성/검증 로직
- 통합 테스트: 진단 완료 → 대시보드 접근 플로우
- API 테스트: 각 엔드포인트별 응답 검증