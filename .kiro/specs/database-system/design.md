# Design Document

## Overview

MySQL 8.0 기반의 데이터베이스 시스템 v2.0입니다. PyMySQL을 사용하여 Flask와 연결하며, LangGraph 워크플로우와 하이브리드 UX를 지원하는 최적화된 데이터 구조를 제공합니다. AUTO_INCREMENT 세션 ID, JSON 컬럼 활용, 객관식/주관식 분리 구조로 성능과 확장성을 크게 개선했습니다.

## Architecture

### Simplified Database Architecture v2.0

```
LangGraph Workflow ←→ Flask App ←→ PyMySQL ←→ MySQL 8.0
                                    ↓
                            Connection Pool
                                    ↓
                        [Transaction Manager]
                                    ↓
                    [Query Builder] + [Schema Initializer]
```

### Connection Strategy v2.0
- 환경변수 기반 설정 관리 (.env 파일)
- 기본 연결 풀 (min_connections=5, max_connections=20)
- 트랜잭션 관리자로 데이터 무결성 보장
- 쿼리 빌더로 기본 쿼리 생성 지원
- 스키마 초기화로 빠른 DB 구축

## Components and Interfaces

### 1. Database Configuration (`db_config.py`)
- 환경변수 기반 설정 관리 (.env 파일 연동)
- 기본 연결 풀 설정 (min=5, max=20)
- 데이터베이스 초기화 및 기본 헬스체크
- 개발/테스트/운영 환경별 설정 분리

### 2. Connection Management (`connection.py`)
- PyMySQL 연결 풀 관리
- 기본 재연결 및 오류 복구
- 연결 상태 확인
- 트랜잭션 컨텍스트 관리

### 3. Query Builder (`query_builder.py`)
- 기본 SQL 쿼리 생성
- 파라미터 바인딩 및 SQL 인젝션 방지
- 기본 JOIN 쿼리 지원
- JSON 컬럼 기본 쿼리 지원

### 4. Transaction Manager (`transaction.py`)
- 기본 트랜잭션 보장
- 자동 롤백 및 커밋
- 컨텍스트 관리자 지원

### 5. Schema Initializer (`create_schema.py`)
- 기존 테이블 완전 삭제
- v2.0 구조 테이블 생성
- 인덱스 및 제약조건 적용
- 스키마 검증

### 6. Table Schema (`schema.sql`)

**Core Tables**:

#### Users Table
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    login_id VARCHAR(20) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL DEFAULT 'unassigned',
    diagnosis_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### User Auth Tokens Table
```sql
CREATE TABLE user_auth_tokens (
    token_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    refresh_token VARCHAR(512) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    device_info VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

#### User Progress Table
```sql
CREATE TABLE user_progress (
    progress_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    current_chapter INT NOT NULL DEFAULT 1,
    current_section INT NOT NULL DEFAULT 1,
    last_study_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_current_chapter (current_chapter),
    INDEX idx_current_section (current_section)
);
```

#### User Statistics Table
```sql
CREATE TABLE user_statistics (
    stats_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    total_study_time_minutes INT DEFAULT 0,
    total_study_sessions INT DEFAULT 0,
    total_completed_sessions INT DEFAULT 0,
    
    -- 객관식 통계
    total_multiple_choice_count INT DEFAULT 0,
    total_multiple_choice_correct INT DEFAULT 0,
    multiple_choice_accuracy DECIMAL(5,2) DEFAULT 0.00,
    
    -- 주관식 통계
    total_subjective_count INT DEFAULT 0,
    total_subjective_score INT DEFAULT 0,
    subjective_average_score DECIMAL(5,2) DEFAULT 0.00,
    
    last_study_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_multiple_choice_accuracy (multiple_choice_accuracy),
    INDEX idx_subjective_average_score (subjective_average_score)
);
```

#### Learning Sessions Table
```sql
CREATE TABLE learning_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    chapter_number INT NOT NULL,
    section_number INT NOT NULL,
    session_start_time TIMESTAMP NOT NULL,
    session_end_time TIMESTAMP NOT NULL,
    study_duration_minutes INT,
    retry_decision_result VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_chapter_section (chapter_number, section_number),
    INDEX idx_user_chapter_section (user_id, chapter_number, section_number),
    CONSTRAINT chk_retry_decision CHECK (retry_decision_result IN ('proceed', 'retry'))
);
```

#### Session Conversations Table
```sql
CREATE TABLE session_conversations (
    conversation_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    message_sequence INT NOT NULL,
    agent_name VARCHAR(50) NOT NULL,
    message_type ENUM('user', 'system', 'tool') NOT NULL,
    message_content TEXT NOT NULL,
    message_timestamp TIMESTAMP NOT NULL,
    session_progress_stage VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_message_sequence (session_id, message_sequence),
    INDEX idx_agent_name (agent_name),
    UNIQUE KEY unique_session_message_sequence (session_id, message_sequence)
);
```

#### Session Quizzes Table
```sql
CREATE TABLE session_quizzes (
    quiz_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    
    -- 퀴즈 기본 정보
    quiz_type VARCHAR(20) NOT NULL,
    quiz_content TEXT NOT NULL,
    
    -- 객관식 전용 필드
    quiz_options JSON,
    quiz_correct_answer INT,
    quiz_explanation TEXT,
    
    -- 주관식 전용 필드
    quiz_sample_answer TEXT,
    quiz_evaluation_criteria JSON,
    
    -- 공통 필드
    quiz_hint TEXT,
    user_answer TEXT,
    
    -- 평가 결과 분리
    multiple_answer_correct BOOLEAN,
    subjective_answer_score INT,
    
    evaluation_feedback TEXT,
    hint_usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_quiz_type (quiz_type),
    
    -- 퀴즈 타입별 제약 조건
    CONSTRAINT chk_quiz_type CHECK (quiz_type IN ('multiple_choice', 'subjective')),
    CONSTRAINT chk_multiple_choice_fields CHECK (
        (quiz_type = 'multiple_choice' AND quiz_options IS NOT NULL AND quiz_correct_answer IS NOT NULL)
        OR quiz_type = 'subjective'
    ),
    CONSTRAINT chk_subjective_fields CHECK (
        (quiz_type = 'subjective' AND quiz_sample_answer IS NOT NULL)
        OR quiz_type = 'multiple_choice'
    ),
    CONSTRAINT chk_score_range CHECK (
        subjective_answer_score IS NULL OR (subjective_answer_score >= 0 AND subjective_answer_score <= 100)
    )
);
```

### 3. Database Models (`models.py`)
- `User`: 사용자 기본 정보
- `UserAuthToken`: 인증 토큰
- `UserProgress`: 학습 진행 상태
- `UserStatistics`: 학습 통계
- `LearningSession`: 학습 세션
- `SessionConversation`: 세션 대화
- `SessionQuiz`: 세션 퀴즈

### 4. Database Utilities (`db_utils.py`)
- `execute_query()`: 쿼리 실행
- `fetch_one()`: 단일 레코드 조회
- `fetch_all()`: 다중 레코드 조회
- 기본 CRUD 작업 함수들

## Data Models

### Session ID Management v2.0
- **AUTO_INCREMENT**: MySQL이 자동으로 세션 ID 생성
- **LAST_INSERT_ID()**: 생성된 세션 ID 즉시 조회
- **성능 향상**: VARCHAR → INT 변환으로 인덱스 효율성 증대

### Table Relationships v2.0
```
users (1:1) user_progress, user_statistics
users (1:N) user_auth_tokens, learning_sessions
learning_sessions (1:N) session_conversations, session_quizzes
```

### Enhanced Indexes v2.0
- **users**: login_id, email (UNIQUE), username, user_type
- **user_auth_tokens**: user_id, refresh_token, expires_at
- **user_progress**: user_id, current_chapter, current_section
- **user_statistics**: user_id, multiple_choice_accuracy, subjective_average_score
- **learning_sessions**: user_id, (chapter_number, section_number), (user_id, chapter_number, section_number)
- **session_conversations**: session_id, (session_id, message_sequence), agent_name
- **session_quizzes**: session_id, quiz_type

### JSON Column Usage
- **quiz_options**: `["선택지1", "선택지2", "선택지3", "선택지4"]`
- **quiz_evaluation_criteria**: `["기준1", "기준2", "기준3"]`

### Quiz Type Differentiation
```sql
-- 객관식 퀴즈 예시
{
  "quiz_type": "multiple_choice",
  "quiz_options": ["AI", "머신러닝", "딥러닝", "모두 다름"],
  "quiz_correct_answer": 4,
  "quiz_explanation": "AI는 가장 포괄적인 개념입니다."
}

-- 주관식 퀴즈 예시
{
  "quiz_type": "subjective",
  "quiz_sample_answer": "AI는 인간의 지능을 모방하는 기술로...",
  "quiz_evaluation_criteria": ["개념 이해도", "설명 논리성", "예시 활용"]
}
```

## Error Handling

### Enhanced Error Types v2.0
- `DatabaseConnectionError`: 연결 실패 및 풀 고갈
- `DatabaseQueryError`: 쿼리 실행 실패
- `DatabaseIntegrityError`: 제약조건 위반
- `DatabaseTransactionError`: 트랜잭션 롤백 실패
- `DatabaseMigrationError`: 스키마 마이그레이션 실패
- `DatabaseJSONError`: JSON 컬럼 파싱 오류
- `DatabaseConstraintError`: 퀴즈 타입별 제약조건 위반

### Error Recovery Strategies
- **연결 오류**: 자동 재연결 (최대 3회 시도)
- **트랜잭션 오류**: 자동 롤백 및 상태 복구
- **제약조건 위반**: 상세 오류 메시지 제공
- **JSON 오류**: 스키마 검증 및 기본값 적용

## Testing Strategy

### Simplified Test Categories v2.0
- **연결 테스트**: 기본 데이터베이스 연결 확인
- **CRUD 테스트**: 각 테이블별 생성/조회/수정/삭제 기본 작업
- **AUTO_INCREMENT 테스트**: 세션 ID 자동 생성 및 조회
- **JSON 컬럼 테스트**: 기본 JSON 데이터 저장/조회
- **통계 테스트**: 객관식/주관식 분리 통계 기본 작업

## Security

### Data Protection v2.0
- **비밀번호**: bcrypt 해시 저장 (salt rounds: 12)
- **환경변수**: .env 파일에서 관리, .gitignore 포함
- **토큰**: 데이터베이스에 안전하게 저장, 만료 시간 관리
- **SQL 인젝션**: 파라미터 바인딩 강제 사용
- **JSON 검증**: 스키마 검증으로 악성 데이터 차단
- **접근 제어**: 사용자별 데이터 격리

### Database Security
- **최소 권한 원칙**: 애플리케이션 전용 DB 사용자
- **연결 암호화**: SSL/TLS 연결 강제
- **감사 로그**: 중요 작업 로깅
- **백업 암호화**: 데이터 덤프 암호화

## Performance Optimization

### Index Strategy v2.0
- **복합 인덱스**: (user_id, chapter_number, section_number)
- **JSON 인덱스**: quiz_type 필드 인덱싱
- **통계 인덱스**: accuracy, score 필드 인덱싱
- **시간 인덱스**: created_at, updated_at 인덱싱

### Query Optimization
- **AUTO_INCREMENT**: VARCHAR → INT 변환으로 JOIN 성능 향상
- **JSON 컬럼**: 정규화 오버헤드 없이 구조화된 데이터 저장
- **연결 풀**: 연결 재사용으로 오버헤드 감소
- **배치 처리**: 통계 업데이트 배치 실행

## Database Initialization Strategy

### Fresh Installation Plan (기존 DB 완전 삭제 후 재생성)
1. **기존 테이블 삭제**: DROP TABLE IF EXISTS로 모든 테이블 제거
2. **스키마 생성**: v2.0 구조의 새 테이블 생성
3. **인덱스 생성**: 성능 최적화 인덱스 적용
4. **제약조건 적용**: 데이터 무결성 보장
5. **구조 검증**: 테이블 생성 확인
6. **기본 테스트**: CRUD 작업 검증

### Initialization Scripts
- `drop_all_tables.sql`: 기존 모든 테이블 삭제
- `create_schema_v2.sql`: v2.0 구조 테이블 생성
- `verify_schema.sql`: 테이블 구조 검증