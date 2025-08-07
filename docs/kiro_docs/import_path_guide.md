# docs/import_path_guide.md

# Import 경로 및 사용법 가이드

## 개요

프로젝트 구조 재정리에 따라 모든 모듈의 import 경로가 변경되었습니다. 이 문서는 새로운 import 경로와 올바른 사용법을 상세히 설명합니다.

## 백엔드 Import 가이드

### 1. 모델 Import

#### 기본 Import 방식
```python
# 도메인별 직접 import (권장)
from app.models.user.user import User
from app.models.user.auth_token import UserAuthToken
from app.models.user.user_progress import UserProgress, UserStatistics

from app.models.learning.session import LearningSession, generate_session_id
from app.models.learning.conversation import SessionConversation
from app.models.learning.quiz import SessionQuiz

from app.models.chapter.chapter import Chapter
```

#### 도메인별 통합 Import
```python
# 도메인 단위로 import
from app.models.user import User, UserAuthToken, UserProgress, UserStatistics
from app.models.learning import LearningSession, SessionConversation, SessionQuiz, generate_session_id
from app.models.chapter import Chapter
```

#### 전체 통합 Import (호환성 유지)
```python
# 기존 코드와의 호환성을 위한 통합 import
from app.models import (
    User, UserAuthToken, UserProgress, UserStatistics,
    LearningSession, SessionConversation, SessionQuiz,
    Chapter, generate_session_id
)
```

### 2. 서비스 Import

#### 인증 서비스
```python
# 개별 서비스 import
from app.services.auth.login_service import LoginService
from app.services.auth.register_service import RegisterService
from app.services.auth.token_service import TokenService

# 도메인별 통합 import
from app.services.auth import LoginService, RegisterService, TokenService
```

#### 학습 서비스
```python
# 개별 서비스 import
from app.services.learning.session_service import SessionService
from app.services.learning.content_service import ContentService
from app.services.learning.quiz_service import QuizService

# 도메인별 통합 import
from app.services.learning import SessionService, ContentService, QuizService
```

#### 사용자 서비스
```python
# 개별 서비스 import
from app.services.user.profile_service import ProfileService
from app.services.user.progress_service import ProgressService

# 도메인별 통합 import
from app.services.user import ProfileService, ProgressService
```

### 3. 에이전트 Import

#### 개별 에이전트 Import
```python
# 각 에이전트의 메인 클래스
from app.agents.session_manager.agent import SessionManagerAgent
from app.agents.learning_supervisor.agent import LearningSupervisorAgent
from app.agents.theory_educator.agent import TheoryEducatorAgent
from app.agents.quiz_generator.agent import QuizGeneratorAgent
from app.agents.evaluation_feedback.agent import EvaluationFeedbackAgent
from app.agents.qna_resolver.agent import QnAResolverAgent
```

#### 에이전트 구성 요소 Import
```python
# 에이전트 내부 구성 요소
from app.agents.learning_supervisor.router import SupervisorRouter
from app.agents.learning_supervisor.response_generator import ResponseGenerator

from app.agents.theory_educator.content_generator import ContentGenerator
from app.agents.quiz_generator.question_generator import QuestionGenerator
from app.agents.quiz_generator.hint_generator import HintGenerator
```

### 4. 도구(Tools) Import

#### 컨텐츠 생성 도구
```python
from app.tools.content.theory_tools import generate_theory_content
from app.tools.content.quiz_tools import generate_quiz_question
from app.tools.content.feedback_tools import generate_feedback
```

#### 외부 연동 도구
```python
from app.tools.external.chatgpt_tools import call_chatgpt_api
from app.tools.external.vector_search_tools import search_vector_db
from app.tools.external.web_search_tools import search_web
```

#### 분석 도구
```python
from app.tools.analysis.evaluation_tools import evaluate_answer
from app.tools.analysis.intent_analysis_tools import analyze_intent
from app.tools.analysis.context_tools import build_context
```

### 5. 유틸리티 Import

#### 인증 유틸리티
```python
from app.utils.auth.jwt_handler import JWTHandler
from app.utils.auth.password_handler import PasswordHandler
```

#### 데이터베이스 유틸리티
```python
from app.utils.database.connection import get_db_connection
from app.utils.database.query_builder import QueryBuilder
from app.utils.database.transaction import TransactionManager
```

#### 응답 처리 유틸리티
```python
from app.utils.response.formatter import format_success_response, format_error_response
from app.utils.response.error_formatter import format_validation_error
```

### 6. 라우트 Import

#### Blueprint Import
```python
# Flask 애플리케이션에서 Blueprint 등록
from app.routes.auth import auth_bp
from app.routes.system import system_bp
from app.routes.dashboard import dashboard_bp
from app.routes.diagnosis import diagnosis_bp
from app.routes.learning import learning_bp

# 애플리케이션에 등록
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(system_bp, url_prefix='/api/system')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(diagnosis_bp, url_prefix='/api/diagnosis')
app.register_blueprint(learning_bp, url_prefix='/api/learning')
```

### 7. 코어 시스템 Import

#### LangGraph 관련
```python
from app.core.langraph.workflow import TutorWorkflow
from app.core.langraph.state_manager import StateManager
from app.core.langraph.graph_builder import GraphBuilder
```

#### 데이터베이스 관련
```python
from app.core.database.mysql_client import MySQLClient
from app.core.database.migration_runner import MigrationRunner
```

#### 외부 서비스 관련
```python
from app.core.external.vector_db import ChromaDBClient
from app.core.external.chatgpt_client import ChatGPTClient
```

## 프론트엔드 Import 가이드

### 1. 컴포넌트 Import

#### 공통 컴포넌트
```javascript
// 공통 컴포넌트
import HeaderComponent from '@/components/common/HeaderComponent.vue'
import LoadingModal from '@/components/common/LoadingModal.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
```

#### 도메인별 컴포넌트
```javascript
// 인증 관련 컴포넌트
import LoginForm from '@/components/auth/LoginForm.vue'
import RegisterForm from '@/components/auth/RegisterForm.vue'

// 대시보드 컴포넌트
import LearningStats from '@/components/dashboard/LearningStats.vue'
import ChapterList from '@/components/dashboard/ChapterList.vue'
import ChapterCard from '@/components/dashboard/ChapterCard.vue'

// 진단 컴포넌트
import DiagnosisQuestion from '@/components/diagnosis/DiagnosisQuestion.vue'
import ProgressBar from '@/components/diagnosis/ProgressBar.vue'

// 학습 컴포넌트
import SessionProgressIndicator from '@/components/learning/SessionProgressIndicator.vue'
import MainContentArea from '@/components/learning/MainContentArea.vue'
```

### 2. 서비스 Import

#### 개별 함수 Import (권장)
```javascript
// 인증 서비스
import { login, logout, register, refreshToken } from '@/services/authService'

// 학습 서비스
import { 
  startSession, 
  sendMessage, 
  submitQuizAnswer, 
  getSessionHistory 
} from '@/services/learningService'

// 대시보드 서비스
import { 
  getDashboardStats, 
  getChapterList, 
  getChapterProgress 
} from '@/services/dashboardService'

// 진단 서비스
import { 
  getDiagnosisQuestions, 
  submitDiagnosisAnswers 
} from '@/services/diagnosisService'
```

#### 전체 서비스 Import
```javascript
// 전체 서비스 객체 import
import authService from '@/services/authService'
import learningService from '@/services/learningService'
import dashboardService from '@/services/dashboardService'
import diagnosisService from '@/services/diagnosisService'

// 사용 예시
const loginResult = await authService.login(credentials)
const sessionData = await learningService.startSession(chapterId)
```

### 3. 컴포저블 Import

```javascript
// 컴포저블 import
import { useAuth } from '@/composables/useAuth'
import { useApi } from '@/composables/useApi'
import { useLearning } from '@/composables/useLearning'
import { useNotification } from '@/composables/useNotification'

// 컴포넌트에서 사용
export default {
  setup() {
    const { user, login, logout, isAuthenticated } = useAuth()
    const { loading, error, request } = useApi()
    const { currentSession, startSession, sendMessage } = useLearning()
    const { showSuccess, showError, showWarning } = useNotification()
    
    return {
      user,
      login,
      logout,
      isAuthenticated,
      loading,
      error,
      currentSession,
      startSession,
      sendMessage,
      showSuccess,
      showError,
      showWarning
    }
  }
}
```

### 4. 스토어 Import

```javascript
// Pinia 스토어 import
import { useAuthStore } from '@/stores/authStore'
import { useTutorStore } from '@/stores/tutorStore'
import { useDashboardStore } from '@/stores/dashboardStore'

// 컴포넌트에서 사용
export default {
  setup() {
    const authStore = useAuthStore()
    const tutorStore = useTutorStore()
    const dashboardStore = useDashboardStore()
    
    return {
      authStore,
      tutorStore,
      dashboardStore
    }
  }
}
```

### 5. 유틸리티 Import

```javascript
// 유틸리티 함수 import
import { 
  formatDate, 
  formatTime, 
  formatDuration 
} from '@/utils/formatting'

import { 
  validateEmail, 
  validatePassword, 
  validateRequired 
} from '@/utils/validation'

import { 
  debounce, 
  throttle, 
  deepClone 
} from '@/utils/helpers'

import { 
  API_ENDPOINTS, 
  ERROR_MESSAGES, 
  SUCCESS_MESSAGES 
} from '@/utils/constants'
```

### 6. 스타일 Import

#### SCSS 변수 및 믹스인
```scss
// 컴포넌트 스타일에서 변수 import
@import '@/styles/variables';
@import '@/styles/mixins';

// 사용 예시
.my-component {
  color: $primary-color;
  @include flex-center;
  @include responsive-font-size;
}
```

#### 컴포넌트별 스타일
```scss
// 메인 스타일시트에서 컴포넌트 스타일 import
@import 'components/buttons';
@import 'components/forms';
@import 'components/cards';
@import 'components/modals';

@import 'pages/auth';
@import 'pages/dashboard';
@import 'pages/learning';
```

## Import 최적화 가이드

### 1. 트리 셰이킹 최적화

#### 백엔드 (Python)
```python
# 좋은 예: 필요한 것만 import
from app.models.user import User
from app.services.auth import LoginService

# 피해야 할 예: 전체 모듈 import
import app.models  # 모든 모델을 메모리에 로드
import app.services  # 모든 서비스를 메모리에 로드
```

#### 프론트엔드 (JavaScript)
```javascript
// 좋은 예: 필요한 함수만 import
import { login, logout } from '@/services/authService'

// 피해야 할 예: 전체 객체 import (번들 크기 증가)
import * as authService from '@/services/authService'
```

### 2. 지연 Import (Lazy Loading)

#### 백엔드
```python
# 지연 import를 통한 성능 최적화
def get_learning_service():
    from app.services.learning import SessionService
    return SessionService()

# 조건부 import
if feature_enabled:
    from app.agents.advanced_tutor import AdvancedTutorAgent
```

#### 프론트엔드
```javascript
// 라우트 레벨 코드 스플리팅
const LoginPage = () => import('@/views/LoginPage.vue')
const DashboardPage = () => import('@/views/DashboardPage.vue')
const LearningPage = () => import('@/views/LearningPage.vue')

// 컴포넌트 레벨 지연 로딩
export default {
  components: {
    HeavyComponent: () => import('@/components/HeavyComponent.vue')
  }
}
```

### 3. 순환 Import 방지

#### 백엔드
```python
# 문제가 되는 순환 import
# models/user/user.py
from app.models.learning.session import LearningSession  # 순환 참조

# 해결 방법 1: 타입 힌트에서만 사용
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.learning.session import LearningSession

# 해결 방법 2: 지연 import
def get_user_sessions(self):
    from app.models.learning.session import LearningSession
    return LearningSession.query.filter_by(user_id=self.id).all()
```

#### 프론트엔드
```javascript
// 문제가 되는 순환 import
// services/authService.js
import { getUserProfile } from '@/services/userService'

// services/userService.js  
import { refreshToken } from '@/services/authService'  // 순환 참조

// 해결 방법: 공통 유틸리티로 분리
// utils/apiUtils.js
export const makeAuthenticatedRequest = (config) => {
  // 인증이 필요한 요청 처리 로직
}
```

## 마이그레이션 체크리스트

### 백엔드 마이그레이션
- [ ] 모든 모델 import 경로 업데이트
- [ ] 서비스 import 경로 업데이트  
- [ ] 라우트에서 모델/서비스 import 경로 업데이트
- [ ] 테스트 파일의 import 경로 업데이트
- [ ] `run.py`의 import 경로 업데이트
- [ ] 설정 파일의 import 경로 업데이트

### 프론트엔드 마이그레이션
- [ ] 컴포넌트 import 경로 업데이트
- [ ] 서비스 import 경로 업데이트
- [ ] 스토어에서 서비스 import 경로 업데이트
- [ ] 라우터 설정의 컴포넌트 import 경로 업데이트
- [ ] 테스트 파일의 import 경로 업데이트

### 검증 단계
- [ ] 애플리케이션이 정상적으로 시작되는지 확인
- [ ] 모든 API 엔드포인트가 작동하는지 확인
- [ ] 프론트엔드 페이지가 정상적으로 로드되는지 확인
- [ ] 기존 테스트가 통과하는지 확인

## 문제 해결

### 자주 발생하는 Import 에러

#### ModuleNotFoundError
```python
# 에러: ModuleNotFoundError: No module named 'app.models.models'
from app.models.models import User

# 해결: 새로운 경로 사용
from app.models.user import User
```

#### ImportError
```python
# 에러: ImportError: cannot import name 'generate_session_id'
from app.models.learning import generate_session_id

# 해결: 함수가 포함된 정확한 모듈에서 import
from app.models.learning.session import generate_session_id
```

#### 순환 Import 에러
```python
# 에러: ImportError: cannot import name 'X' from partially initialized module
# 해결: 타입 힌트나 지연 import 사용 (위의 순환 Import 방지 섹션 참조)
```

### 성능 최적화 팁

1. **필요한 것만 Import**: 전체 모듈보다는 필요한 클래스/함수만 import
2. **지연 Import 활용**: 조건부로 사용되는 모듈은 지연 import 사용
3. **Import 순서 최적화**: 표준 라이브러리 → 서드파티 → 로컬 모듈 순서로 import
4. **캐싱 활용**: 반복적으로 사용되는 import는 모듈 레벨에서 캐싱

---

이 가이드를 통해 새로운 프로젝트 구조에서 올바른 import 경로를 사용하여 효율적으로 개발할 수 있습니다. 추가 질문이나 특정 상황에 대한 가이드가 필요하면 언제든지 문의해 주세요.