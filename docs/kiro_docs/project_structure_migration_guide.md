# docs/project_structure_migration_guide.md

# 프로젝트 구조 재정리 완료 가이드

## 개요

AI 활용법 학습 튜터 프로젝트의 폴더 구조가 정의된 백엔드/프론트엔드 구조에 맞게 완전히 재구성되었습니다. 이 문서는 변경된 구조와 새로운 개발 가이드라인을 설명합니다.

## 주요 변경 사항 요약

### 백엔드 구조 변경

#### 1. 모델 분리 완료
- **기존**: `backend/app/models/models.py` (모든 모델이 하나의 파일)
- **변경 후**: 도메인별 폴더 구조로 분리

```
backend/app/models/
├── __init__.py              # 모든 모델 통합 import
├── user/                    # 사용자 관련 모델
│   ├── user.py             # User 모델
│   ├── auth_token.py       # UserAuthToken 모델
│   └── user_progress.py    # UserProgress, UserStatistics 모델
├── learning/               # 학습 관련 모델
│   ├── session.py          # LearningSession 모델 + generate_session_id 함수
│   ├── conversation.py     # SessionConversation 모델
│   └── quiz.py             # SessionQuiz 모델
└── chapter/                # 챕터 관련 모델
    └── chapter.py          # Chapter 모델
```

#### 2. 라우트 Blueprint 분리 완료
- **기존**: `backend/app/routes/main.py` (기본 라우트만)
- **변경 후**: 기능별 Blueprint 구조

```
backend/app/routes/
├── __init__.py              # 모든 Blueprint 등록
├── auth/                    # 인증 관련 라우트
│   ├── login.py            # 로그인/로그아웃
│   ├── register.py         # 회원가입
│   └── token.py            # 토큰 관리
├── system/                  # 시스템 관리 라우트
│   ├── health.py           # 헬스 체크 (기존 main.py에서 이전)
│   └── version.py          # 버전 정보 (기존 index 라우트 이전)
├── dashboard/              # 대시보드 라우트
├── diagnosis/              # 진단 라우트
└── learning/               # 학습 세션 라우트
```

#### 3. 완전한 도메인 기반 구조 구축
모든 백엔드 컴포넌트가 도메인별로 체계적으로 분리되었습니다:

- **agents/**: 각 에이전트별 독립적인 폴더 구조
- **services/**: 도메인별 비즈니스 로직 분리
- **tools/**: 기능별 LangGraph 도구 분류
- **utils/**: 목적별 유틸리티 함수 분리
- **core/**: 시스템 핵심 구성 요소 분리
- **middleware/**: 처리 단계별 미들웨어 분리

### 프론트엔드 구조 완성

#### 1. 컴포넌트 구조 완성
정의된 구조에 따라 모든 컴포넌트 폴더와 기본 파일들이 생성되었습니다:

```
frontend/src/components/
├── common/                  # 공통 컴포넌트
│   ├── HeaderComponent.vue
│   ├── LoadingModal.vue
│   └── AlertMessage.vue
├── auth/                    # 인증 관련 컴포넌트
│   ├── LoginForm.vue
│   └── RegisterForm.vue
├── dashboard/              # 대시보드 컴포넌트
├── diagnosis/              # 진단 컴포넌트
└── learning/               # 학습 컴포넌트
```

#### 2. 서비스 레이어 확장
기존 `api.js` 기반으로 도메인별 서비스 파일들이 생성되었습니다:

```
frontend/src/services/
├── api.js                   # 기본 Axios 설정 (기존 유지)
├── authService.js           # 인증 관련 API
├── learningService.js       # 학습 관련 API
├── dashboardService.js      # 대시보드 관련 API
└── diagnosisService.js      # 진단 관련 API
```

#### 3. 스타일 구조 완성
SCSS 기반의 체계적인 스타일 구조가 구축되었습니다:

```
frontend/src/styles/
├── main.scss                # 메인 스타일시트
├── variables.scss           # SCSS 변수
├── mixins.scss             # SCSS 믹스인
├── components/             # 컴포넌트별 스타일
└── pages/                  # 페이지별 스타일
```

## 새로운 Import 경로 가이드

### 백엔드 Import 경로

#### 모델 Import
```python
# 새로운 방식 (권장)
from app.models.user import User, UserAuthToken
from app.models.learning import LearningSession, SessionConversation
from app.models.chapter import Chapter

# 통합 Import (호환성 유지)
from app.models import User, UserAuthToken, LearningSession, SessionConversation, Chapter
```

#### 서비스 Import
```python
# 도메인별 서비스 Import
from app.services.auth import LoginService, RegisterService
from app.services.learning import SessionService, ContentService
from app.services.user import ProfileService, ProgressService
```

#### 에이전트 Import
```python
# 에이전트 Import
from app.agents.session_manager import SessionManagerAgent
from app.agents.learning_supervisor import LearningSupervisorAgent
from app.agents.theory_educator import TheoryEducatorAgent
```

### 프론트엔드 Import 경로

#### 컴포넌트 Import
```javascript
// 공통 컴포넌트
import HeaderComponent from '@/components/common/HeaderComponent.vue'
import LoadingModal from '@/components/common/LoadingModal.vue'

// 도메인별 컴포넌트
import LoginForm from '@/components/auth/LoginForm.vue'
import ChapterCard from '@/components/dashboard/ChapterCard.vue'
```

#### 서비스 Import
```javascript
// 도메인별 서비스
import { login, logout } from '@/services/authService'
import { startSession, sendMessage } from '@/services/learningService'
import { getDashboardStats } from '@/services/dashboardService'
```

#### 컴포저블 Import
```javascript
// 컴포저블
import { useAuth } from '@/composables/useAuth'
import { useLearning } from '@/composables/useLearning'
import { useNotification } from '@/composables/useNotification'
```

## 개발 가이드라인

### 1. 파일 생성 규칙

#### 백엔드 파일 생성
- **모델**: 도메인별 폴더에 생성 (`models/domain/model_name.py`)
- **라우트**: 기능별 폴더에 생성 (`routes/domain/feature.py`)
- **서비스**: 도메인별 폴더에 생성 (`services/domain/service_name.py`)
- **에이전트**: 에이전트별 폴더에 생성 (`agents/agent_name/component.py`)

#### 프론트엔드 파일 생성
- **컴포넌트**: 도메인별 폴더에 생성 (`components/domain/ComponentName.vue`)
- **페이지**: views 폴더에 생성 (`views/PageName.vue`)
- **서비스**: services 폴더에 생성 (`services/domainService.js`)
- **스타일**: 컴포넌트/페이지별 폴더에 생성

### 2. 명명 규칙

#### 백엔드
- **파일명**: `snake_case.py` (예: `user_progress.py`, `login_service.py`)
- **클래스명**: `PascalCase` (예: `UserProgress`, `LoginService`)
- **함수명**: `snake_case` (예: `generate_session_id`, `validate_user`)

#### 프론트엔드
- **컴포넌트**: `PascalCase.vue` (예: `LoginForm.vue`, `ChapterCard.vue`)
- **서비스**: `camelCase.js` (예: `authService.js`, `learningService.js`)
- **함수명**: `camelCase` (예: `getUserProfile`, `startLearningSession`)

### 3. 폴더 구조 준수 원칙

#### 단일 책임 원칙
- 각 파일은 하나의 명확한 책임을 가져야 합니다
- 파일 크기는 100-200줄 내외로 유지합니다
- 복잡한 로직은 별도 파일로 분리합니다

#### 도메인 기반 분리
- 관련 기능끼리 같은 도메인 폴더에 그룹화합니다
- 도메인 간 의존성을 최소화합니다
- 공통 기능은 common 또는 shared 폴더에 배치합니다

#### 계층별 분리
- 프레젠테이션 계층 (routes, components)
- 비즈니스 로직 계층 (services, agents)
- 데이터 계층 (models, repositories)
- 인프라 계층 (core, utils, middleware)

### 4. 새 기능 개발 워크플로우

#### 백엔드 기능 추가
1. **모델 정의**: 해당 도메인 폴더에 모델 생성
2. **서비스 구현**: 비즈니스 로직을 서비스 계층에 구현
3. **라우트 추가**: API 엔드포인트를 라우트에 추가
4. **테스트 작성**: `tests/` 폴더에 테스트 코드 작성
5. **Import 업데이트**: `__init__.py` 파일에 새 모듈 추가

#### 프론트엔드 기능 추가
1. **컴포넌트 생성**: 해당 도메인 폴더에 Vue 컴포넌트 생성
2. **서비스 구현**: API 호출 로직을 서비스에 구현
3. **스토어 업데이트**: 필요시 Pinia 스토어에 상태 추가
4. **라우트 추가**: Vue Router에 새 페이지 라우트 추가
5. **스타일 추가**: 컴포넌트별 SCSS 스타일 작성

## 호환성 및 마이그레이션

### 기존 코드 호환성
- 기존 import 경로는 `models/__init__.py`의 호환성 레이어를 통해 계속 작동합니다
- 점진적으로 새로운 import 경로로 변경하는 것을 권장합니다

### 마이그레이션 체크리스트
- [ ] 모든 기존 기능이 정상 작동하는지 확인
- [ ] 새로운 import 경로로 점진적 변경
- [ ] 테스트 코드 업데이트
- [ ] 문서 업데이트

## 협업 가이드라인

### VSCode와 Kiro 동시 작업 시 주의사항
1. **작업 영역 분리**: 같은 도메인 폴더 내에서는 충돌 방지를 위해 작업 영역을 분리합니다
2. **구조 변경 사전 조율**: 폴더 구조나 파일 이동 시 사전에 팀원과 조율합니다
3. **Import 경로 일관성**: 팀 내에서 일관된 import 경로 스타일을 유지합니다

### 코드 리뷰 포인트
1. **구조 준수**: 정의된 폴더 구조를 따르고 있는지 확인
2. **명명 규칙**: 파일명과 함수명이 규칙을 따르고 있는지 확인
3. **단일 책임**: 각 파일이 명확한 단일 책임을 가지고 있는지 확인
4. **의존성 관리**: 순환 import나 불필요한 의존성이 없는지 확인

## 문제 해결

### 자주 발생하는 문제

#### Import 에러
```python
# 문제: ModuleNotFoundError
from app.models.models import User  # 기존 경로

# 해결: 새로운 경로 사용
from app.models.user import User
# 또는
from app.models import User  # 통합 import
```

#### 순환 Import
```python
# 문제: 순환 import 발생
# models/user/user.py에서 models/learning/session.py import
# models/learning/session.py에서 models/user/user.py import

# 해결: 타입 힌트에서만 import 사용
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.learning import LearningSession
```

### 성능 최적화
- 필요한 모듈만 import하여 메모리 사용량 최적화
- 지연 import를 활용하여 초기 로딩 시간 단축
- 캐싱을 활용하여 반복적인 import 비용 절약

## 다음 단계

### 추가 개선 사항
1. **API 문서 자동화**: OpenAPI/Swagger 문서 생성
2. **테스트 커버리지 향상**: 각 도메인별 테스트 강화
3. **모니터링 시스템**: 로깅 및 메트릭 수집 체계 구축
4. **CI/CD 파이프라인**: 자동화된 배포 시스템 구축

### 지속적인 개선
- 정기적인 구조 리뷰 및 리팩토링
- 새로운 기능 추가 시 구조 일관성 유지
- 팀 피드백을 통한 가이드라인 개선

---

이 문서는 프로젝트 구조 재정리 완료 후 개발팀이 새로운 구조에서 효율적으로 협업할 수 있도록 작성되었습니다. 