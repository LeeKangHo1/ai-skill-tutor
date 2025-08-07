# 부록: DB 설계 v1.3

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
    last_study_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_current_chapter (current_chapter)
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
    total_correct_answers INT DEFAULT 0 COMMENT '총 정답 수',
    average_accuracy DECIMAL(5,2) DEFAULT 0.00 COMMENT '평균 정답률 (%)',
    last_study_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_last_study_date (last_study_date)
);
```

### 2.5 learning_sessions (학습 세션 기록)

```sql
CREATE TABLE learning_sessions (
    session_id VARCHAR(100) PRIMARY KEY COMMENT '고유 세션 ID (형식: user{user_id}_ch{chapter}_session{count:03d}_{timestamp})',
    user_id INT NOT NULL,
    chapter_number INT NOT NULL,
    session_sequence INT NOT NULL COMMENT '해당 챕터 내에서의 세션 순서',
    session_start_time TIMESTAMP NOT NULL,
    session_end_time TIMESTAMP NOT NULL,
    study_duration_minutes INT COMMENT '해당 세션 학습 소요 시간 (분)',
    session_decision_result VARCHAR(20) COMMENT 'proceed: 다음 단계 진행, retry: 재학습',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_chapter_number (chapter_number),
    INDEX idx_user_chapter (user_id, chapter_number),
    INDEX idx_session_start_time (session_start_time),
    
    UNIQUE KEY unique_user_chapter_sequence (user_id, chapter_number, session_sequence)
);
```

### 2.6 session_conversations (세션 내 대화 상세)

```sql
CREATE TABLE session_conversations (
    conversation_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(100) NOT NULL,
    message_sequence INT NOT NULL COMMENT '해당 세션 내에서의 메시지 순서',
    agent_name VARCHAR(50) NOT NULL COMMENT '에이전트 이름 (스네이크 케이스)',
    message_type ENUM('user', 'system', 'tool') NOT NULL,
    message_content TEXT NOT NULL,
    message_timestamp TIMESTAMP NOT NULL,
    session_progress_stage VARCHAR(50) COMMENT '메시지 발생 시점의 세션 진행 단계 (session_start, theory_completed, quiz_and_feedback_completed)',
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
    session_id VARCHAR(100) NOT NULL UNIQUE COMMENT '세션과 1:1 연결',
    question_number INT COMMENT '문제 번호',
    question_type VARCHAR(20) COMMENT '문제 유형 (multiple_choice: 객관식, subjective: 주관식)',
    question_content TEXT COMMENT '문제 내용',
    user_answer TEXT COMMENT '사용자 답변',
    is_answer_correct INT COMMENT '객관식: 1(정답)/0(오답), 주관식: 0~100점',
    evaluation_feedback TEXT COMMENT '평가 및 피드백 내용',
    hint_usage_count INT DEFAULT 0 COMMENT '힌트 사용 횟수',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_question_number (question_number),
    INDEX idx_question_type (question_type)
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

### 3.3 세션 ID 생성 규칙

```python
# 새로운 세션 ID 생성 형식
def generate_session_id(user_id: int, chapter: int, session_count: int) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"user{user_id}_ch{chapter}_session{session_count:03d}_{timestamp}"

# 생성 예시: "user123_ch1_session001_20250805_143052"
```

### 3.4 학습 진행 제어

```sql
-- 챕터 접근 권한 확인
SELECT current_chapter 
FROM user_progress 
WHERE user_id = ?;

-- 세션 완료 시 진행 상태 업데이트
UPDATE user_progress 
SET current_chapter = ?, last_study_date = CURDATE()
WHERE user_id = ?;
```

### 3.5 통계 업데이트 로직

```sql
-- 세션 완료 시 통계 업데이트 (퀴즈 점수 반영)
UPDATE user_statistics 
SET 
    total_study_sessions = total_study_sessions + 1,
    total_completed_sessions = total_completed_sessions + 1,
    total_correct_answers = total_correct_answers + CASE 
        WHEN ? >= 60 THEN 1 ELSE 0 END,  -- 60점 이상을 정답으로 간주
    total_study_time_minutes = total_study_time_minutes + ?,
    average_accuracy = (total_correct_answers * 100.0) / total_completed_sessions,
    last_study_date = CURDATE()
WHERE user_id = ?;
```

---

## 4. 📊 인덱스 전략

### 4.1 성능 최적화 인덱스

**자주 사용되는 조회 패턴:**
- 로그인 인증: `users(login_id)`
- 사용자별 학습 진행 상태 조회: `user_progress(user_id)`
- 사용자별 세션 기록 조회: `learning_sessions(user_id, chapter_number)`
- 세션별 대화 조회: `session_conversations(session_id, message_sequence)`
- 세션별 퀴즈 조회: `session_quizzes(session_id)`
- 세션 진행 단계별 대화 조회: `session_conversations(session_progress_stage)`

### 4.2 복합 인덱스

```sql
-- 사용자별 챕터별 세션 조회 최적화
ALTER TABLE learning_sessions ADD INDEX idx_user_chapter_sequence 
(user_id, chapter_number, session_sequence);

-- 세션 내 대화 순서 조회 최적화
ALTER TABLE session_conversations ADD INDEX idx_session_message_sequence 
(session_id, message_sequence);

-- 세션 진행 단계별 대화 분석 최적화
ALTER TABLE session_conversations ADD INDEX idx_session_progress_stage 
(session_progress_stage);
```

---

## 5. 🔒 데이터 무결성 및 보안

### 5.1 제약 조건

**비즈니스 규칙 제약:**
- `login_id`: 4-20자 길이 제한 (애플리케이션 레벨에서 검증)
- `user_type`: 'unassigned'(미설정), 'beginner'(AI 입문자), 'advanced'(실무 응용형)만 허용
- `current_chapter`: 1 이상의 값만 허용
- `question_type`: 'multiple_choice'(객관식) 또는 'subjective'(주관식)만 허용
- `is_answer_correct`: 객관식(0/1), 주관식(0~100) 범위만 허용
- `session_decision_result`: 'proceed'(다음 단계) 또는 'retry'(재학습)만 허용
- `session_progress_stage`: 'session_start', 'theory_completed', 'quiz_and_feedback_completed'만 허용

### 5.2 데이터 정합성 체크

```sql
-- 진단 미완료 사용자의 학습 진행 방지
ALTER TABLE user_progress 
ADD CONSTRAINT check_diagnosis_completed 
CHECK (
    (SELECT diagnosis_completed FROM users WHERE users.user_id = user_progress.user_id) = TRUE
);

-- 퀴즈 점수 범위 제한
ALTER TABLE session_quizzes 
ADD CONSTRAINT check_answer_score_range 
CHECK (is_answer_correct >= 0 AND is_answer_correct <= 100);
```

### 5.3 개인정보 보호

**민감 정보 처리:**
- 비밀번호: bcrypt 해시 저장
- 이메일: 필요시 별도 암호화 테이블 분리 가능
- 학습 기록: 개인식별 불가능한 익명화 처리 옵션

---

## 6. 💾 백업 및 유지보수

### 6.1 백업 전략

**테이블별 백업 우선순위:**
1. **High**: `users`, `user_progress`, `user_statistics`
2. **Medium**: `learning_sessions`, `session_quizzes`, `user_auth_tokens`
3. **Low**: `session_conversations` (대용량, 복구 시간 고려)

### 6.2 데이터 정리

```sql
-- 만료된 토큰 정리 (배치 작업)
DELETE FROM user_auth_tokens 
WHERE expires_at < NOW() OR is_active = FALSE;

-- 오래된 대화 아카이브 (필요시)
-- session_conversations 테이블의 경우 용량 관리를 위해 아카이브 테이블로 이동 가능
```

---

## 7. 🚀 확장성 고려사항

### 7.1 수평 확장 대비

**파티셔닝 전략:**
- `learning_sessions`: `user_id` 기준 해시 파티셔닝
- `session_conversations`: `session_id` 기준 파티셔닝 (상위 테이블 따라)
- `session_quizzes`: `session_id` 기준 파티셔닝

### 7.2 캐싱 전략

**Redis 캐싱 대상:**
- 사용자 진행 상태 (`user_progress`)
- 활성 세션 정보 (`user_auth_tokens`)
- 자주 조회되는 학습 통계

### 7.3 미래 확장 대비

**추가 예정 테이블:**
- `chapter_contents`: 상세 챕터 내용
- `quiz_templates`: 퀴즈 템플릿
- `user_feedback`: 사용자 피드백
- `system_logs`: 시스템 로그
- `session_summaries`: 세션 요약 정보 (State의 recent_sessions_summary 영구 저장용)

---

## 8. 📈 모니터링 및 분석

### 8.1 비즈니스 메트릭 추출 쿼리

```sql
-- 일별 활성 사용자 수
SELECT DATE(last_study_date) as study_date, COUNT(*) as active_users
FROM user_statistics 
WHERE last_study_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY DATE(last_study_date);

-- 챕터별 완료율
SELECT chapter_number, COUNT(DISTINCT user_id) as completed_users
FROM learning_sessions 
WHERE session_decision_result = 'proceed'
GROUP BY chapter_number;

-- 평균 학습 시간
SELECT AVG(total_study_time_minutes) as avg_study_time
FROM user_statistics 
WHERE total_study_sessions > 0;

-- 세션 진행 단계별 대화 분포
SELECT session_progress_stage, COUNT(*) as message_count
FROM session_conversations
GROUP BY session_progress_stage;

-- 퀴즈 유형별 정답률 분석
SELECT 
    question_type,
    AVG(CASE WHEN question_type = 'multiple_choice' 
        THEN is_answer_correct 
        ELSE CASE WHEN is_answer_correct >= 60 THEN 1 ELSE 0 END 
    END) * 100 as accuracy_rate
FROM session_quizzes
GROUP BY question_type;
```

### 8.2 성능 모니터링

**모니터링 대상:**
- 테이블별 레코드 수 증가율
- 인덱스 사용률 및 쿼리 성능
- 디스크 사용량 (특히 `session_conversations`)
- 세션 진행 단계별 처리 시간

---

## 9. 📋 v1.3 주요 변경사항

### 9.1 테이블 구조 변경
- **session_conversations**: `session_progress_stage VARCHAR(50)` 컬럼 추가
- **session_quizzes**: `question_type VARCHAR(20)` 컬럼 추가, `is_answer_correct TINYINT` → `INT`로 변경

### 9.2 세션 ID 형식 변경
- 기존: 임의 문자열
- 신규: `user{user_id}_ch{chapter}_session{count:03d}_{timestamp}` 구조화된 형식

### 9.3 퀴즈 시스템 강화
- 객관식(0/1)과 주관식(0~100점) 구분 처리
- 문제 유형별 정답률 분석 가능

### 9.4 세션 추적 개선
- 메시지별 세션 진행 단계 기록으로 더 정밀한 학습 과정 분석 가능
- 단계별 소요 시간 및 사용자 행동 패턴 분석 지원

---

*DB 설계 버전: v1.3*  
*최종 수정일: 2025.08.05*  
*연관 문서: AI 활용법 학습 튜터 PRD v1.3, 랭그래프 State 설계 v1.3*