# 프로젝트 구조 재정리 설계 문서

## 개요

현재 AI 활용법 학습 튜터 프로젝트는 기본적인 구조가 설정되어 있지만, 정의된 폴더 구조에 완전히 맞춰지지 않은 상태입니다. 이 설계는 기존 코드를 손실 없이 새로운 구조로 이전하고, 팀 협업을 위한 완전한 폴더 구조를 구축하는 방법을 정의합니다.

## 아키텍처

### 전체 구조 개요

```
프로젝트 루트/
├── backend/                 # Python Flask 백엔드
│   ├── app/                # 메인 애플리케이션 코드
│   │   ├── models/         # 도메인별 모델 분리
│   │   ├── routes/         # 기능별 Blueprint 분리
│   │   ├── services/       # 비즈니스 로직 서비스
│   │   ├── agents/         # LangGraph 에이전트 시스템
│   │   ├── tools/          # LangGraph 도구 함수
│   │   ├── utils/          # 유틸리티 함수
│   │   ├── core/           # 핵심 시스템 구성 요소
│   │   └── middleware/     # 미들웨어
│   └── [기타 폴더들]
└── frontend/               # Vue.js 프론트엔드
    └── src/
        ├── views/          # 페이지 컴포넌트
        ├── components/     # 재사용 컴포넌트
        ├── stores/         # Pinia 상태 관리
        ├── services/       # API 서비스
        ├── composables/    # Vue 컴포저블
        ├── utils/          # 유틸리티 함수
        └── styles/         # SCSS 스타일
```

### 마이그레이션 전략

1. **점진적 이전**: 기존 기능을 유지하면서 단계적으로 구조 변경
2. **도메인 기반 분리**: 관련 기능끼리 그룹화하여 모듈성 향상
3. **Import 경로 자동 업데이트**: 구조 변경 시 모든 참조 경로 자동 수정
4. **테스트 기반 검증**: 각 단계마다 기능 정상 작동 확인

## 컴포넌트 및 인터페이스

### 백엔드 구조 변경

#### 1. 모델 분리 (models/)

**현재 상태:**
- `backend/app/models/models.py`: 모든 모델이 하나의 파일에 정의됨

**목표 구조:**
```
backend/app/models/
├── __init__.py              # 모든 모델 import 통합
├── user/                    # 사용자 관련 모델
│   ├── __init__.py
│   ├── user.py             # User 모델
│   ├── auth_token.py       # UserAuthToken 모델
│   └── user_progress.py    # UserProgress, UserStatistics 모델
├── learning/               # 학습 관련 모델
│   ├── __init__.py
│   ├── session.py          # LearningSession 모델
│   ├── conversation.py     # SessionConversation 모델
│   └── quiz.py             # SessionQuiz 모델
└── chapter/                # 챕터 관련 모델 (향후 확장)
    ├── __init__.py
    └── chapter.py
```

#### 2. 라우트 분리 (routes/)

**현재 상태:**
- `backend/app/routes/main.py`: 기본 라우트만 정의됨

**목표 구조:**
```
backend/app/routes/
├── __init__.py              # 모든 Blueprint 등록
├── auth/                    # 인증 관련 라우트
│   ├── __init__.py
│   ├── login.py
│   ├── register.py
│   └── token.py
├── system/                  # 시스템 관리 라우트
│   ├── __init__.py
│   ├── health.py           # 기존 health_check 이전
│   └── version.py
└── [기타 도메인별 라우트]
```

#### 3. 서비스 레이어 구축 (services/)

**목표 구조:**
```
backend/app/services/
├── __init__.py
├── auth/                    # 인증 서비스
│   ├── __init__.py
│   ├── login_service.py
│   ├── register_service.py
│   └── token_service.py
└── [기타 서비스들]
```

### 프론트엔드 구조 완성

#### 1. 컴포넌트 구조 (components/)

**현재 상태:**
- 기본 폴더만 존재

**목표 구조:**
```
frontend/src/components/
├── common/                  # 공통 컴포넌트
│   ├── HeaderComponent.vue
│   ├── LoadingModal.vue
│   └── AlertMessage.vue
├── auth/                    # 인증 관련 컴포넌트
│   ├── LoginForm.vue
│   └── RegisterForm.vue
└── [기타 도메인별 컴포넌트]
```

#### 2. 서비스 레이어 (services/)

**현재 상태:**
- 기본 API 서비스만 존재

**목표 구조:**
```
frontend/src/services/
├── api.js                   # 기본 Axios 설정 (기존 유지)
├── authService.js           # 인증 관련 API
├── learningService.js       # 학습 관련 API
├── dashboardService.js      # 대시보드 관련 API
└── diagnosisService.js      # 진단 관련 API
```

## 데이터 모델

### 모델 분리 매핑

| 기존 모델 | 새로운 위치 | 설명 |
|-----------|-------------|------|
| `User` | `models/user/user.py` | 사용자 기본 정보 |
| `UserAuthToken` | `models/user/auth_token.py` | 인증 토큰 관리 |
| `UserProgress` | `models/user/user_progress.py` | 사용자 진행 상태 |
| `UserStatistics` | `models/user/user_progress.py` | 사용자 통계 (관련성으로 인해 같은 파일) |
| `LearningSession` | `models/learning/session.py` | 학습 세션 |
| `SessionConversation` | `models/learning/conversation.py` | 대화 기록 |
| `SessionQuiz` | `models/learning/quiz.py` | 퀴즈 정보 |
| `generate_session_id` | `models/learning/session.py` | 세션 ID 생성 함수 |

### Import 경로 변경

**기존:**
```python
from app.models.models import User, UserAuthToken
```

**변경 후:**
```python
from app.models.user import User, UserAuthToken
# 또는
from app.models import User, UserAuthToken  # __init__.py에서 통합 관리
```

## 에러 처리

### 마이그레이션 중 에러 처리

1. **Import 에러 방지**
   - 기존 import 경로를 유지하는 호환성 레이어 제공
   - 단계적으로 새로운 경로로 변경

2. **기능 중단 방지**
   - 각 단계마다 기능 테스트 실행
   - 문제 발생 시 롤백 가능한 구조

3. **의존성 관리**
   - 순환 import 방지를 위한 의존성 그래프 분석
   - 모듈 간 결합도 최소화

### 에러 복구 전략

```python
# 호환성 레이어 예시 (models/__init__.py)
try:
    # 새로운 구조에서 import
    from .user.user import User
    from .user.auth_token import UserAuthToken
    from .learning.session import LearningSession
except ImportError:
    # 기존 구조에서 import (fallback)
    from .models import User, UserAuthToken, LearningSession
```

## 테스트 전략

### 구조 변경 검증

1. **기능 테스트**
   - 기존 API 엔드포인트 정상 작동 확인
   - 데이터베이스 연결 및 모델 동작 확인

2. **Import 테스트**
   - 모든 모듈이 올바르게 import되는지 확인
   - 순환 import 없음을 확인

3. **통합 테스트**
   - 백엔드-프론트엔드 연동 확인
   - 전체 애플리케이션 실행 확인

### 테스트 자동화

```python
# 구조 검증 테스트 예시
def test_model_imports():
    """모든 모델이 올바르게 import되는지 테스트"""
    from app.models import User, UserAuthToken, LearningSession
    assert User is not None
    assert UserAuthToken is not None
    assert LearningSession is not None

def test_api_endpoints():
    """기본 API 엔드포인트가 작동하는지 테스트"""
    response = client.get('/')
    assert response.status_code == 200
    
    response = client.get('/health')
    assert response.status_code == 200
```

## 협업 가이드라인 업데이트

### 프로젝트 컨텍스트 추가 내용

1. **폴더 구조 준수 규칙**
   - 새로운 파일 생성 시 정의된 구조 따르기
   - 도메인별 분리 원칙 유지

2. **파일 명명 규칙**
   - 모델: `snake_case.py` (예: `user_progress.py`)
   - 컴포넌트: `PascalCase.vue` (예: `LoginForm.vue`)
   - 서비스: `camelCase.js` (예: `authService.js`)

3. **VSCode-Kiro 협업 규칙**
   - 같은 도메인 폴더 내에서는 충돌 방지를 위해 작업 영역 분리
   - 구조 변경 시 사전 조율 필수

### 개발 워크플로우

1. **새 기능 개발 시**
   - 해당 도메인 폴더에 파일 생성
   - 관련 `__init__.py` 파일에 import 추가
   - 테스트 파일도 같은 구조로 생성

2. **기존 코드 수정 시**
   - 새로운 구조의 파일에서 수정
   - 기존 파일은 deprecation 경고 추가 후 점진적 제거

## 구현 순서

### Phase 1: 백엔드 구조 재정리
1. 모델 분리 및 이전
2. 라우트 분리 및 Blueprint 재구성
3. Import 경로 업데이트
4. 기능 테스트

### Phase 2: 프론트엔드 구조 완성
1. 컴포넌트 폴더 구조 생성
2. 서비스 레이어 확장
3. 스타일 구조 정리
4. 통합 테스트

### Phase 3: 프로젝트 컨텍스트 업데이트
1. 협업 가이드라인 추가
2. 폴더 구조 준수 규칙 명시
3. 개발 워크플로우 문서화

### Phase 4: 검증 및 최적화
1. 전체 시스템 테스트
2. 성능 확인
3. 문서 업데이트
4. 팀 공유 및 교육