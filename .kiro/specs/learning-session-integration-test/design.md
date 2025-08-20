# 학습 세션 통합 테스트 설계 문서

## 개요

이 문서는 백엔드에서 구현된 학습 API 엔드포인트들의 통합 테스트 설계를 다룹니다. 테스트는 실제 학습 플로우를 시뮬레이션하여 전체 시스템이 올바르게 동작하는지 검증합니다.

### 테스트 대상 API 엔드포인트

1. **POST /learning/session/start** - 학습 세션 시작
2. **POST /learning/session/message** - 메시지 전송 및 처리
3. **POST /learning/quiz/submit** - 퀴즈 답변 제출
4. **POST /learning/session/complete** - 세션 완료

### 테스트 목표

- 전체 학습 플로우의 정상 동작 검증
- 데이터베이스 연동 및 트랜잭션 처리 검증
- 메모리 기반 세션 관리 검증
- 다양한 오류 상황에 대한 적절한 처리 검증

## 아키텍처

### 테스트 구조

```
backend/tests/0820/
├── conftest.py                    # 테스트 설정 및 픽스처
├── test_learning_session_flow.py  # 메인 통합 테스트
├── fixtures/
│   ├── auth_fixtures.py          # 인증 관련 픽스처
│   ├── database_fixtures.py      # 데이터베이스 픽스처
│   └── session_fixtures.py       # 세션 관련 픽스처
└── utils/
    ├── test_helpers.py           # 테스트 헬퍼 함수
    └── db_helpers.py             # 데이터베이스 검증 헬퍼
```

### 테스트 환경 설정

- **데이터베이스**: 실제 DB 서버 사용 (테스트 후 데이터 정리)
- **인증**: JWT 토큰 기반 테스트 사용자 생성
- **세션 관리**: SessionService의 메모리 상태 초기화
- **LLM 호출**: 실제 LangGraph 워크플로우 및 LLM API 사용
- **데이터 정리**: 테스트 완료 후 생성된 데이터 자동 삭제

## 컴포넌트 및 인터페이스

### 1. 테스트 픽스처 (conftest.py)

```python
@pytest.fixture(scope="session")
def test_app():
    """테스트용 Flask 앱 생성"""

@pytest.fixture(scope="function")
def test_client(test_app):
    """테스트 클라이언트 생성"""

@pytest.fixture(scope="function")
def test_user():
    """테스트 사용자 생성 및 정리"""

@pytest.fixture(scope="function")
def auth_headers(test_user):
    """인증 헤더 생성"""

@pytest.fixture(scope="function")
def clean_session_state():
    """세션 상태 초기화"""
```

### 2. 메인 통합 테스트 클래스

```python
class TestLearningSessionFlow:
    """학습 세션 전체 플로우 통합 테스트"""
    
    def test_complete_learning_flow(self):
        """완전한 학습 플로우 테스트"""
        
    def test_session_start_with_valid_data(self):
        """유효한 데이터로 세션 시작 테스트"""
        
    def test_message_processing_flow(self):
        """메시지 처리 플로우 테스트"""
        
    def test_quiz_submission_and_evaluation(self):
        """퀴즈 제출 및 평가 테스트"""
        
    def test_session_completion_and_db_storage(self):
        """세션 완료 및 DB 저장 테스트"""
```

### 3. 데이터베이스 검증 및 정리 헬퍼

```python
class DatabaseVerifier:
    """데이터베이스 상태 검증 및 정리 헬퍼"""
    
    def verify_learning_session_saved(self, user_id, chapter, section):
        """learning_sessions 테이블 저장 검증"""
        
    def verify_session_conversations_saved(self, session_id):
        """session_conversations 테이블 저장 검증"""
        
    def verify_session_quizzes_saved(self, session_id):
        """session_quizzes 테이블 저장 검증"""
        
    def verify_user_statistics_updated(self, user_id):
        """user_statistics 테이블 업데이트 검증"""
        
    def cleanup_test_data(self, user_ids):
        """테스트 데이터 정리 (CASCADE 삭제 활용)"""
        
    def get_test_data_summary(self, user_id):
        """테스트로 생성된 데이터 요약 조회"""
```

## 데이터 모델

### 테스트 데이터 구조

```python
# 테스트 사용자 데이터
TEST_USER_DATA = {
    "login_id": "test_user_001",
    "username": "테스트사용자",
    "email": "test@example.com",
    "user_type": "beginner",
    "diagnosis_completed": True
}

# 테스트 세션 데이터
TEST_SESSION_DATA = {
    "chapter_number": 1,
    "section_number": 1,
    "user_message": "1챕터 1섹션 시작할게요"
}

# 테스트 퀴즈 답변 데이터
TEST_QUIZ_ANSWERS = {
    "multiple_choice": "2",
    "subjective": "LLM은 대규모 언어 모델로서..."
}
```

### 테스트 데이터 추적 구조

```python
# 테스트 실행 중 생성된 데이터 추적
TEST_DATA_TRACKER = {
    "created_users": [],      # 생성된 테스트 사용자 ID 목록
    "created_sessions": [],   # 생성된 세션 ID 목록
    "test_start_time": None,  # 테스트 시작 시간
    "test_end_time": None     # 테스트 종료 시간
}

# 실제 LLM 응답 검증을 위한 기대값
EXPECTED_RESPONSE_PATTERNS = {
    "theory_content": ["LLM", "언어 모델", "인공지능"],
    "quiz_content": ["문제", "선택지", "정답"],
    "feedback_content": ["평가", "피드백", "설명"]
}
```

## 오류 처리

### 테스트할 오류 시나리오

1. **인증 오류**
   - 유효하지 않은 JWT 토큰
   - 만료된 토큰
   - 토큰 없이 요청

2. **권한 오류**
   - 진단 미완료 사용자
   - 접근 권한 없는 챕터/섹션

3. **세션 상태 오류**
   - 활성 세션 없이 메시지 전송
   - 퀴즈 없이 답변 제출
   - 완료 불가능한 상태에서 세션 완료

4. **데이터베이스 오류**
   - 연결 실패
   - 트랜잭션 롤백
   - 제약 조건 위반

### 오류 처리 검증 방법

```python
def test_error_scenarios(self):
    """다양한 오류 시나리오 테스트"""
    
    # 인증 오류 테스트
    response = self.client.post('/learning/session/start', 
                               headers={'Authorization': 'Bearer invalid_token'})
    assert response.status_code == 401
    
    # 권한 오류 테스트  
    response = self.client.post('/learning/session/start',
                               json={'chapter_number': 999},
                               headers=self.auth_headers)
    assert response.status_code == 403
```

## 테스트 전략

### 1. 통합 테스트 시나리오

**시나리오 1: 정상적인 학습 플로우**
```
1. 세션 시작 → 이론 설명 반환
2. "다음 단계" 메시지 → 퀴즈 출제
3. 퀴즈 답변 제출 → 평가 및 피드백
4. "proceed" 결정 → 세션 완료 및 DB 저장
```

**시나리오 2: 재학습 플로우**
```
1. 세션 시작 → 이론 설명
2. 퀴즈 답변 제출 → 낮은 점수
3. "retry" 결정 → 동일 섹션 재시작
```

**시나리오 3: 질문-답변 플로우**
```
1. 세션 시작 → 이론 설명
2. 질문 메시지 → QnA 에이전트 응답
3. "다음 단계" 메시지 → 퀴즈 출제
```

### 2. 데이터베이스 검증 전략

```python
def verify_complete_db_storage(self, user_id, session_data):
    """완전한 DB 저장 검증"""
    
    # 1. learning_sessions 테이블 검증
    session = self.db_verifier.get_latest_session(user_id)
    assert session is not None
    assert session['chapter_number'] == session_data['chapter_number']
    
    # 2. session_conversations 테이블 검증
    conversations = self.db_verifier.get_session_conversations(session['session_id'])
    assert len(conversations) > 0
    
    # 3. session_quizzes 테이블 검증
    quizzes = self.db_verifier.get_session_quizzes(session['session_id'])
    assert len(quizzes) > 0
    
    # 4. user_statistics 테이블 업데이트 검증
    stats = self.db_verifier.get_user_statistics(user_id)
    assert stats['total_study_sessions'] > 0
```

### 3. 메모리 세션 관리 검증

```python
def test_session_memory_management(self):
    """세션 메모리 관리 테스트"""
    
    # 세션 시작 후 메모리 상태 확인
    self.start_session()
    assert session_service.get_active_sessions_count() == 1
    
    # 세션 완료 후 메모리 정리 확인
    self.complete_session()
    assert session_service.get_active_sessions_count() == 0
```

### 4. 성능 및 동시성 테스트

```python
def test_concurrent_sessions(self):
    """동시 세션 처리 테스트"""
    
    # 여러 사용자 동시 세션 시작
    users = [self.create_test_user(f"user_{i}") for i in range(5)]
    
    # 동시 요청 처리 검증
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(self.run_complete_flow, user) 
                  for user in users]
        results = [future.result() for future in futures]
    
    # 모든 세션이 정상 처리되었는지 확인
    assert all(result['success'] for result in results)
```

## 테스트 데이터 관리

### 테스트 데이터 생성 및 정리

```python
class TestDataManager:
    """테스트 데이터 생성 및 정리 관리"""
    
    def setup_test_data(self):
        """테스트 데이터 생성"""
        # 테스트 사용자 생성 (실제 DB에 저장)
        # 초기 진행 상태 설정
        # 챕터 메타데이터 준비
        # 생성된 데이터 추적 시작
        
    def cleanup_test_data(self):
        """테스트 데이터 정리"""
        # CASCADE 삭제를 활용한 관련 데이터 일괄 삭제
        # users 테이블에서 테스트 사용자 삭제 시 관련 모든 데이터 자동 삭제
        # 세션 상태 초기화
        # 데이터 정리 결과 로깅
        
    def create_test_user_with_cleanup_tracking(self, user_data):
        """정리 추적이 가능한 테스트 사용자 생성"""
        
    def get_cleanup_summary(self):
        """정리된 데이터 요약 반환"""
```

### 테스트 격리 전략

- **사용자 레벨 격리**: 각 테스트마다 고유한 테스트 사용자 생성
- **세션 상태 초기화**: 테스트 간 SessionService 메모리 상태 초기화  
- **데이터 보존**: 테스트 완료 후 데이터 보존하여 수동 확인 가능
- **타임스탬프 기반 추적**: 테스트 시작/종료 시간으로 데이터 범위 확인
- **수동 정리**: 사용자 지시에 따른 선택적 데이터 삭제

## 실제 시스템 통합 전략

### 실제 시스템 통합 테스트

```python
class IntegrationTestRunner:
    """실제 시스템 통합 테스트 실행"""
    
    def run_complete_learning_flow(self, test_user):
        """완전한 학습 플로우 실행"""
        # API 문서 규칙에 따른 엔드포인트 호출
        # 실제 에이전트 및 LLM 응답 처리
        # 각 단계별 응답 검증
        
    def validate_api_response_format(self, response, expected_format):
        """API 응답 형식 검증"""
        # API 문서에 정의된 응답 구조 확인
        # 필수 필드 존재 여부 검증
        # 데이터 타입 일치성 확인
```

### 테스트 데이터 관리

```python
class TestDataManager:
    """테스트 데이터 생성 및 관리"""
    
    def create_test_user_with_prefix(self, prefix="test_"):
        """테스트 식별 가능한 사용자 생성"""
        # login_id에 test_ 접두사 추가
        # 생성 시간 기록으로 추적 가능하게 설정
        # 생성된 사용자 정보 로깅
        
    def log_created_test_data(self, user_id, session_data):
        """생성된 테스트 데이터 로깅"""
        # 테스트로 생성된 사용자 및 세션 정보 기록
        # 나중에 수동 삭제를 위한 정보 제공
        
    def get_test_data_summary(self):
        """테스트 데이터 요약 조회"""
        # test_ 접두사가 있는 모든 사용자 목록
        # 각 사용자별 생성된 세션, 퀴즈, 대화 수
        # 생성 시간 및 데이터 크기 정보
        
    def manual_cleanup_test_data(self, user_ids_to_delete):
        """수동 지시에 따른 테스트 데이터 삭제"""
        # 지정된 사용자 ID들의 데이터 삭제
        # CASCADE 제약조건으로 관련 테이블 자동 정리
        # 삭제 결과 상세 로깅
```

### 테스트 실행 시간 고려사항

- **LLM 응답 대기**: 실제 API 호출로 인한 응답 시간 (5-30초)
- **데이터베이스 처리**: 실제 DB 트랜잭션 처리 시간
- **전체 플로우 테스트**: 완전한 학습 세션 (2-5분 소요 예상)
- **타임아웃 설정**: 각 단계별 적절한 타임아웃 설정

### 테스트 데이터 추적

```python
@pytest.fixture(scope="function")
def test_data_tracker():
    """테스트 데이터 추적"""
    tracker = {
        "created_users": [],
        "test_start_time": datetime.now(),
        "test_name": None
    }
    
    yield tracker
    
    # 테스트 완료 후 생성된 데이터 로깅
    data_manager = TestDataManager()
    data_manager.log_created_test_data(
        tracker["created_users"], 
        tracker["test_name"]
    )
    
    print(f"\n=== 테스트 완료: {tracker['test_name']} ===")
    print(f"생성된 테스트 사용자: {tracker['created_users']}")
    print("수동 삭제가 필요한 경우 TestDataManager.manual_cleanup_test_data() 사용")
```

이 설계는 MVP 완성을 위한 실제 시스템 동작 검증에 중점을 두며, 실제 LLM 응답과 DB 저장을 통해 전체 시스템의 안정성을 확인합니다.