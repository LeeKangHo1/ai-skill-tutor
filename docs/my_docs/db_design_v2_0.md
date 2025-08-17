# 부록: DB 설계 v2.0

## 1. 🏗️ 전체 테이블 구조 개요

### 1.1 테이블 관계도

```
users (사용자 기본 정보)
├── user_auth_tokens (인증 토큰 관리)
├── user_progress (학습 진행 상태)
├── user_statistics (학습 통계)
├── learning_sessions (학습 세션 기록)
│   ├── session_conversations (세션 내 대화 상세)
│   └── session_quizzes (세션별 퀴즈 정보)

chapters (챕터 기본 정보) - 독립적 관리
```

### 1.2 테이블 생성 순서

1. **사용자 관련**: `users` → `user_auth_tokens` → `user_progress` → `user_statistics`
2. **세션 관련**: `learning_sessions` → `session_conversations` + `session_quizzes`
3. **챕터 관련**: `chapters` (나중에 추가)

---

## 2. 📋 테이블 상세 설계

### 2.1 users (사용자 기본 정보)

```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    login_id VARCHAR(20) NOT NULL UNIQUE COMMENT '로그인용 ID (4-20자)',
    username VARCHAR(50) NOT NULL COMMENT '표시용 닉네임',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '이메일 (회원가입 시에만 입력)',
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL DEFAULT 'unassigned' COMMENT 'unassigned: 미설정, beginner: AI 입문자, advanced: 실무 응용형',
    diagnosis_completed BOOLEAN DEFAULT FALSE COMMENT '진단 퀴즈 완료 여부',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_login_id (login_id),
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_user_type (user_type)
);
```

### 2.2 user_auth_tokens (인증 토큰 관리)

```sql
CREATE TABLE user_auth_tokens (
    token_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    refresh_token VARCHAR(512) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    device_info VARCHAR(255) COMMENT '디바이스 정보 (선택사항)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_refresh_token (refresh_token),
    INDEX idx_expires_at (expires_at)
);
```

### 2.3 user_progress (학습 진행 상태)

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
    INDEX idx_user_id (user_id),
    INDEX idx_current_chapter (current_chapter),
    INDEX idx_current_section (current_section)
);
```

### 2.4 user_statistics (학습 통계)

```sql
CREATE TABLE user_statistics (
    stats_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    total_study_time_minutes INT DEFAULT 0 COMMENT '총 학습 시간 (분)',
    total_study_sessions INT DEFAULT 0 COMMENT '총 학습 횟수',
    total_completed_sessions INT DEFAULT 0 COMMENT '완료한 학습 세션 수',
    
    -- 객관식 통계
    total_multiple_choice_count INT DEFAULT 0 COMMENT '총 객관식 문제 수',
    total_multiple_choice_correct INT DEFAULT 0 COMMENT '객관식 정답 수',
    multiple_choice_accuracy DECIMAL(5,2) DEFAULT 0.00 COMMENT '객관식 정답률 (%)',
    
    -- 주관식 통계
    total_subjective_count INT DEFAULT 0 COMMENT '총 주관식 문제 수',
    total_subjective_score INT DEFAULT 0 COMMENT '주관식 총 점수',
    subjective_average_score DECIMAL(5,2) DEFAULT 0.00 COMMENT '주관식 평균 점수',
    
    last_study_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_last_study_date (last_study_date),
    INDEX idx_multiple_choice_accuracy (multiple_choice_accuracy),
    INDEX idx_subjective_average_score (subjective_average_score)
);
```

### 2.5 learning_sessions (학습 세션 기록)

```sql
CREATE TABLE learning_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '자동 증가 세션 ID',
    user_id INT NOT NULL,
    chapter_number INT NOT NULL,
    section_number INT NOT NULL COMMENT '챕터 내 섹션 번호',
    session_start_time TIMESTAMP NOT NULL,
    session_end_time TIMESTAMP NOT NULL,
    study_duration_minutes INT COMMENT '해당 세션 학습 소요 시간 (분)',
    retry_decision_result VARCHAR(20) COMMENT 'proceed: 다음 단계 진행, retry: 재학습',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_chapter_section (chapter_number, section_number),
    INDEX idx_user_chapter_section (user_id, chapter_number, section_number),
    INDEX idx_session_start_time (session_start_time),
    
    CONSTRAINT chk_retry_decision CHECK (retry_decision_result IN ('proceed', 'retry'))
);
```

### 2.6 session_conversations (세션 내 대화 상세)

```sql
CREATE TABLE session_conversations (
    conversation_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL COMMENT '세션 ID (AUTO_INCREMENT 참조)',
    message_sequence INT NOT NULL COMMENT '해당 세션 내에서의 메시지 순서',
    agent_name VARCHAR(50) NOT NULL COMMENT '에이전트 이름 (스네이크 케이스)',
    message_type ENUM('user', 'system', 'tool') NOT NULL,
    message_content TEXT NOT NULL,
    message_timestamp TIMESTAMP NOT NULL,
    session_progress_stage VARCHAR(50) COMMENT '메시지 발생 시점의 세션 진행 단계',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_message_sequence (session_id, message_sequence),
    INDEX idx_agent_name (agent_name),
    INDEX idx_session_progress_stage (session_progress_stage),
    
    UNIQUE KEY unique_session_message_sequence (session_id, message_sequence)
);
```

### 2.7 session_quizzes (세션별 퀴즈 정보)

```sql
CREATE TABLE session_quizzes (
    quiz_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL COMMENT '세션 ID (AUTO_INCREMENT)',
    
    -- 퀴즈 기본 정보
    quiz_type VARCHAR(20) NOT NULL COMMENT 'multiple_choice: 객관식, subjective: 주관식',
    quiz_content TEXT NOT NULL COMMENT '퀴즈 문제 내용',
    
    -- 객관식 전용 필드
    quiz_options JSON COMMENT '객관식 선택지 배열 ["선택지1", "선택지2", "선택지3", "선택지4"]',
    quiz_correct_answer INT COMMENT '객관식 정답 번호 (1-4)',
    quiz_explanation TEXT COMMENT '객관식 정답 해설',
    
    -- 주관식 전용 필드
    quiz_sample_answer TEXT COMMENT '주관식 모범 답안 예시',
    quiz_evaluation_criteria JSON COMMENT '주관식 평가 기준 배열 ["기준1", "기준2", "기준3"]',
    
    -- 공통 필드
    quiz_hint TEXT COMMENT '힌트 내용',
    user_answer TEXT COMMENT '사용자 답변',
    
    -- 평가 결과 분리
    multiple_answer_correct BOOLEAN COMMENT '객관식 정답 여부 (true/false)',
    subjective_answer_score INT COMMENT '주관식 점수 (0-100)',
    
    evaluation_feedback TEXT COMMENT '평가 및 피드백 내용',
    hint_usage_count INT DEFAULT 0 COMMENT '힌트 사용 횟수',
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

### 2.8 chapters (챕터 기본 정보) - 추후 구현

```sql
CREATE TABLE chapters (
    chapter_id INT PRIMARY KEY AUTO_INCREMENT,
    chapter_number INT NOT NULL UNIQUE,
    chapter_title VARCHAR(200) NOT NULL,
    chapter_description TEXT,
    target_user_type VARCHAR(20) NOT NULL COMMENT 'beginner: AI 입문자, advanced: 실무 응용형',
    estimated_duration_minutes INT COMMENT '예상 학습 시간 (분)',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_chapter_number (chapter_number),
    INDEX idx_target_user_type (target_user_type)
);
```

---

## 3. 🔧 주요 비즈니스 로직 및 제약사항

### 3.1 사용자 가입 및 진단 프로세스

```sql
-- 1. 회원가입 시 기본 레코드 생성
INSERT INTO users (login_id, username, email, password_hash) VALUES (?, ?, ?, ?);
INSERT INTO user_progress (user_id) VALUES (LAST_INSERT_ID());
INSERT INTO user_statistics (user_id) VALUES (LAST_INSERT_ID());

-- 2. 로그인 인증
SELECT user_id, login_id, username, user_type, diagnosis_completed 
FROM users 
WHERE login_id = ? AND password_hash = ?;

-- 3. 진단 퀴즈 완료 시
UPDATE users SET user_type = ?, diagnosis_completed = TRUE WHERE user_id = ?;
```

### 3.2 단일 세션 강제 로직

```sql
-- 새 로그인 시 기존 활성 토큰 비활성화
UPDATE user_auth_tokens 
SET is_active = FALSE 
WHERE user_id = ? AND is_active = TRUE;

-- 새 리프레시 토큰 생성
INSERT INTO user_auth_tokens (user_id, refresh_token, expires_at) 
VALUES (?, ?, DATE_ADD(NOW(), INTERVAL 30 DAY));
```

### 3.3 세션 완료 시 데이터 저장

```sql
-- 1. 세션 기본 정보 저장 (AUTO_INCREMENT로 session_id 생성)
INSERT INTO learning_sessions (
    user_id, chapter_number, section_number, session_start_time, 
    session_end_time, study_duration_minutes, retry_decision_result
) VALUES (?, ?, ?, ?, ?, ?, ?);

SET @session_id = LAST_INSERT_ID();

-- 2. 퀴즈 정보 저장 (객관식 예시)
INSERT INTO session_quizzes (
    session_id, quiz_type, quiz_content, quiz_options, quiz_correct_answer,
    quiz_explanation, quiz_hint, user_answer, multiple_answer_correct,
    evaluation_feedback, hint_usage_count
) VALUES (@session_id, 'multiple_choice', ?, ?, ?, ?, ?, ?, ?, ?, ?);

-- 3. 주관식 퀴즈 저장 예시
INSERT INTO session_quizzes (
    session_id, quiz_type, quiz_content, quiz_sample_answer, 
    quiz_evaluation_criteria, quiz_hint, user_answer, subjective_answer_score,
    evaluation_feedback, hint_usage_count
) VALUES (@session_id, 'subjective', ?, ?, ?, ?, ?, ?, ?, ?);

-- 4. 대화 기록 저장
INSERT INTO session_conversations (
    session_id, message_sequence, agent_name, message_type, 
    message_content, message_timestamp, session_progress_stage
) VALUES (@session_id, ?, ?, ?, ?, ?, ?);
```

### 3.4 사용자 진행 상태 업데이트

```sql
-- 세션 완료 후 진행 상태 업데이트
UPDATE user_progress 
SET 
    current_chapter = ?,
    current_section = ?,
    last_study_date = CURDATE()
WHERE user_id = ?;
```

### 3.5 통계 업데이트 로직 (객관식/주관식 분리)

```sql
-- 객관식 퀴즈 완료 시 통계 업데이트
UPDATE user_statistics 
SET 
    total_study_sessions = total_study_sessions + 1,
    total_completed_sessions = total_completed_sessions + 1,
    total_multiple_choice_count = total_multiple_choice_count + 1,
    total_multiple_choice_correct = total_multiple_choice_correct + CASE WHEN ? = TRUE THEN 1 ELSE 0 END,
    multiple_choice_accuracy = (total_multiple_choice_correct * 100.0) / total_multiple_choice_count,
    total_study_time_minutes = total_study_time_minutes + ?,
    last_study_date = CURDATE()
WHERE user_id = ?;

-- 주관식 퀴즈 완료 시 통계 업데이트
UPDATE user_statistics 
SET 
    total_study_sessions = total_study_sessions + 1,
    total_completed_sessions = total_completed_sessions + 1,
    total_subjective_count = total_subjective_count + 1,
    total_subjective_score = total_subjective_score + ?,
    subjective_average_score = total_subjective_score / total_subjective_count,
    total_study_time_minutes = total_study_time_minutes + ?,
    last_study_date = CURDATE()
WHERE user_id = ?;
```

---

## 4. 📊 인덱스 전략

### 4.1 성능 최적화 인덱스

**자주 사용되는 조회 패턴:**
- 로그인 인증: `users(login_id)`
- 사용자별 학습 진행 상태 조회: `user_progress(user_id)`
- 사용자별 세션 기록 조회: `learning_sessions(user_id, chapter_number, section_number)`
- 세션별 대화 조회: `session_conversations(session_id, message_sequence)`
- 세션별 퀴즈 조회: `session_quizzes(session_id)`
- 퀴즈 타입별 분석: `session_quizzes(quiz_type)`

### 4.2 복합 인덱스

```sql
-- 사용자별 챕터/섹션별 세션 조회 최적화
ALTER TABLE learning_sessions ADD INDEX idx_user_chapter_section 
(user_id, chapter_number, section_number);

-- 세션 내 대화 순서 조회 최적화
ALTER TABLE session_conversations ADD INDEX idx_session_message_sequence 
(session_id, message_sequence);

-- 퀴즈 타입별 분석 최적화
ALTER TABLE session_quizzes ADD INDEX idx_quiz_type (quiz_type);

-- 사용자별 챕터/섹션 진행 조회 최적화
ALTER TABLE user_progress ADD INDEX idx_user_chapter_section 
(user_id, current_chapter, current_section);
```

---

## 5. 🔒 데이터 무결성 및 보안

### 5.1 제약 조건

**비즈니스 규칙 제약:**
- `login_id`: 4-20자 길이 제한 (애플리케이션 레벨에서 검증)
- `user_type`: 'unassigned'(미설정), 'beginner'(AI 입문자), 'advanced'(실무 응용형)만 허용
- `quiz_type`: 'multiple_choice'(객관식) 또는 'subjective'(주관식)만 허용
- `subjective_answer_score`: 0~100 범위만 허용
- `retry_decision_result`: 'proceed'(다음 단계) 또는 'retry'(재학습)만 허용
- `current_chapter`, `current_section`: 1 이상의 값만 허용

### 5.2 데이터 정합성 체크

```sql
-- 퀴즈 타입별 필수 필드 검증
CONSTRAINT chk_multiple_choice_fields CHECK (
    (quiz_type = 'multiple_choice' AND quiz_options IS NOT NULL AND quiz_correct_answer IS NOT NULL)
    OR quiz_type = 'subjective'
);

CONSTRAINT chk_subjective_fields CHECK (
    (quiz_type = 'subjective' AND quiz_sample_answer IS NOT NULL)
    OR quiz_type = 'multiple_choice'
);

-- 점수 및 정확도 범위 제한
CONSTRAINT chk_score_range CHECK (
    subjective_answer_score IS NULL OR (subjective_answer_score >= 0 AND subjective_answer_score <= 100)
);

CONSTRAINT chk_accuracy_range CHECK (
    multiple_choice_accuracy >= 0 AND multiple_choice_accuracy <= 100 AND
    subjective_average_score >= 0 AND subjective_average_score <= 100
);

-- 진행 상태 검증
CONSTRAINT chk_progress_range CHECK (
    current_chapter >= 1 AND current_section >= 1
);
```

---

*DB 설계 버전: v2.0*  
*최종 수정일: 2025.08.17*  
*주요 변경사항: State 설계 v2.0 반영, AUTO_INCREMENT 도입, 퀴즈 구조 확장*