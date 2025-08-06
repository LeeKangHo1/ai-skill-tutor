# Design Document

## Overview

MySQL 8.0 기반의 간단한 데이터베이스 시스템입니다. PyMySQL을 사용하여 Flask와 연결하며, 사용자 정보, 인증 토큰, 학습 기록을 저장합니다.

## Architecture

### Simple Database Architecture

```
Flask App ←→ PyMySQL ←→ MySQL 8.0
```

### Connection Strategy
- 환경변수 기반 설정 관리
- 기본 연결 풀 사용
- 간단한 오류 처리

## Components and Interfaces

### 1. Database Configuration (`db_config.py`)
- 환경변수 기반 설정 관리
- 연결 풀 설정
- 데이터베이스 초기화

### 2. Table Schema (`schema.sql`)

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
    last_study_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
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
    total_correct_answers INT DEFAULT 0,
    average_accuracy DECIMAL(5,2) DEFAULT 0.00,
    last_study_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

#### Learning Sessions Table
```sql
CREATE TABLE learning_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_id INT NOT NULL,
    chapter_number INT NOT NULL,
    session_sequence INT NOT NULL,
    session_start_time TIMESTAMP NOT NULL,
    session_end_time TIMESTAMP NOT NULL,
    study_duration_minutes INT,
    session_decision_result VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

#### Session Conversations Table
```sql
CREATE TABLE session_conversations (
    conversation_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(100) NOT NULL,
    message_sequence INT NOT NULL,
    agent_name VARCHAR(50) NOT NULL,
    message_type ENUM('user', 'system', 'tool') NOT NULL,
    message_content TEXT NOT NULL,
    message_timestamp TIMESTAMP NOT NULL,
    session_progress_stage VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id) ON DELETE CASCADE
);
```

#### Session Quizzes Table
```sql
CREATE TABLE session_quizzes (
    quiz_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    question_number INT,
    question_type VARCHAR(20),
    question_content TEXT,
    user_answer TEXT,
    is_answer_correct INT,
    evaluation_feedback TEXT,
    hint_usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id) ON DELETE CASCADE
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

### Session ID Format
`user{user_id}_ch{chapter}_session{count:03d}_{timestamp}`

### Table Relationships
```
users (1:1) user_progress, user_statistics
users (1:N) user_auth_tokens, learning_sessions
learning_sessions (1:N) session_conversations
learning_sessions (1:1) session_quizzes
```

### Basic Indexes
- `users`: login_id, email (UNIQUE)
- `user_auth_tokens`: user_id, refresh_token
- `learning_sessions`: user_id, chapter_number

## Error Handling

### Basic Error Types
- `DatabaseConnectionError`: 연결 실패
- `DatabaseQueryError`: 쿼리 실행 실패
- `DatabaseIntegrityError`: 제약조건 위반

## Testing Strategy

### Test Categories
- 연결 테스트
- 테이블 생성 테스트
- 기본 CRUD 테스트
- 외래키 관계 테스트

## Security

### Data Protection
- 비밀번호: bcrypt 해시 저장
- 환경변수: .env 파일에서 관리
- 토큰: 데이터베이스에 안전하게 저장