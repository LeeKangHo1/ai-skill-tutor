# backend/migrations/schema.sql
-- AI 활용법 학습 튜터 데이터베이스 스키마
-- MySQL 8.0 기반 테이블 생성 스크립트
-- 외래키 의존성을 고려한 테이블 생성 순서로 구성

-- 데이터베이스 생성 (필요시)
-- CREATE DATABASE IF NOT EXISTS ai_skill_tutor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE ai_skill_tutor;

-- 기존 테이블 삭제 (역순으로 삭제하여 외래키 제약조건 문제 방지)
DROP TABLE IF EXISTS session_quizzes;
DROP TABLE IF EXISTS session_conversations;
DROP TABLE IF EXISTS learning_sessions;
DROP TABLE IF EXISTS user_statistics;
DROP TABLE IF EXISTS user_progress;
DROP TABLE IF EXISTS user_auth_tokens;
DROP TABLE IF EXISTS users;

-- ============================================================================
-- 1. 기본 테이블 (외래키 의존성 없음)
-- ============================================================================

-- 사용자 기본 정보 테이블
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '사용자 고유 ID',
    login_id VARCHAR(20) NOT NULL UNIQUE COMMENT '로그인용 사용자 ID',
    username VARCHAR(50) NOT NULL COMMENT '사용자 이름',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '이메일 주소',
    password_hash VARCHAR(255) NOT NULL COMMENT 'bcrypt 해시된 비밀번호',
    user_type VARCHAR(20) NOT NULL DEFAULT 'unassigned' COMMENT '사용자 유형 (AI 입문자 등)',
    diagnosis_completed BOOLEAN DEFAULT FALSE COMMENT '진단 완료 여부',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '계정 생성 시간',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '마지막 수정 시간',
    
    -- 인덱스 설정
    INDEX idx_login_id (login_id),
    INDEX idx_email (email),
    INDEX idx_user_type (user_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 기본 정보';

-- ============================================================================
-- 2. 사용자 의존 테이블들 (users 테이블 참조)
-- ============================================================================

-- 사용자 인증 토큰 테이블
CREATE TABLE user_auth_tokens (
    token_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '토큰 고유 ID',
    user_id INT NOT NULL COMMENT '사용자 ID',
    refresh_token VARCHAR(512) NOT NULL COMMENT 'JWT 리프레시 토큰',
    expires_at TIMESTAMP NOT NULL COMMENT '토큰 만료 시간',
    is_active BOOLEAN DEFAULT TRUE COMMENT '토큰 활성 상태',
    device_info VARCHAR(255) COMMENT '디바이스 정보',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '토큰 생성 시간',
    
    -- 외래키 제약조건
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- 인덱스 설정
    INDEX idx_user_id (user_id),
    INDEX idx_refresh_token (refresh_token),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 인증 토큰';

-- 사용자 학습 진행 상태 테이블
CREATE TABLE user_progress (
    progress_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '진행 상태 고유 ID',
    user_id INT NOT NULL UNIQUE COMMENT '사용자 ID (각 사용자당 하나의 레코드)',
    current_chapter INT NOT NULL DEFAULT 1 COMMENT '현재 학습 중인 챕터',
    last_study_date DATE COMMENT '마지막 학습 날짜',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '레코드 생성 시간',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '마지막 수정 시간',
    
    -- 외래키 제약조건
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- 인덱스 설정
    INDEX idx_current_chapter (current_chapter),
    INDEX idx_last_study_date (last_study_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 학습 진행 상태';

-- 사용자 학습 통계 테이블
CREATE TABLE user_statistics (
    stats_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '통계 고유 ID',
    user_id INT NOT NULL UNIQUE COMMENT '사용자 ID (각 사용자당 하나의 레코드)',
    total_study_time_minutes INT DEFAULT 0 COMMENT '총 학습 시간 (분)',
    total_study_sessions INT DEFAULT 0 COMMENT '총 학습 세션 수',
    total_completed_sessions INT DEFAULT 0 COMMENT '완료된 세션 수',
    total_correct_answers INT DEFAULT 0 COMMENT '총 정답 수',
    average_accuracy DECIMAL(5,2) DEFAULT 0.00 COMMENT '평균 정답률 (%)',
    last_study_date DATE COMMENT '마지막 학습 날짜',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '레코드 생성 시간',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '마지막 수정 시간',
    
    -- 외래키 제약조건
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- 인덱스 설정
    INDEX idx_total_study_sessions (total_study_sessions),
    INDEX idx_average_accuracy (average_accuracy),
    INDEX idx_last_study_date (last_study_date),
    
    -- 데이터 무결성 제약조건
    CHECK (total_study_time_minutes >= 0),
    CHECK (total_study_sessions >= 0),
    CHECK (total_completed_sessions >= 0),
    CHECK (total_completed_sessions <= total_study_sessions),
    CHECK (total_correct_answers >= 0),
    CHECK (average_accuracy >= 0.00 AND average_accuracy <= 100.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 학습 통계';

-- ============================================================================
-- 3. 학습 세션 테이블 (users 테이블 참조)
-- ============================================================================

-- 학습 세션 테이블
CREATE TABLE learning_sessions (
    session_id VARCHAR(100) PRIMARY KEY COMMENT '세션 ID (user{id}_ch{chapter}_session{count}_{timestamp} 형식)',
    user_id INT NOT NULL COMMENT '사용자 ID',
    chapter_number INT NOT NULL COMMENT '챕터 번호',
    session_sequence INT NOT NULL COMMENT '해당 챕터 내 세션 순서',
    session_start_time TIMESTAMP NOT NULL COMMENT '세션 시작 시간',
    session_end_time TIMESTAMP NOT NULL COMMENT '세션 종료 시간',
    study_duration_minutes INT COMMENT '학습 소요 시간 (분)',
    session_decision_result VARCHAR(20) COMMENT '세션 결과 (완료/미완료 등)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '레코드 생성 시간',
    
    -- 외래키 제약조건
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- 인덱스 설정
    INDEX idx_user_id (user_id),
    INDEX idx_chapter_number (chapter_number),
    INDEX idx_user_chapter (user_id, chapter_number),
    INDEX idx_session_start_time (session_start_time),
    INDEX idx_session_decision_result (session_decision_result),
    
    -- 데이터 무결성 제약조건
    CHECK (chapter_number > 0),
    CHECK (session_sequence > 0),
    CHECK (session_end_time >= session_start_time),
    CHECK (study_duration_minutes >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='학습 세션 정보';

-- ============================================================================
-- 4. 세션 의존 테이블들 (learning_sessions 테이블 참조)
-- ============================================================================

-- 세션 대화 기록 테이블
CREATE TABLE session_conversations (
    conversation_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '대화 고유 ID',
    session_id VARCHAR(100) NOT NULL COMMENT '세션 ID',
    message_sequence INT NOT NULL COMMENT '메시지 순서',
    agent_name VARCHAR(50) NOT NULL COMMENT '에이전트 이름',
    message_type ENUM('user', 'system', 'tool') NOT NULL COMMENT '메시지 유형',
    message_content TEXT NOT NULL COMMENT '메시지 내용',
    message_timestamp TIMESTAMP NOT NULL COMMENT '메시지 시간',
    session_progress_stage VARCHAR(50) COMMENT '세션 진행 단계',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '레코드 생성 시간',
    
    -- 외래키 제약조건
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id) ON DELETE CASCADE,
    
    -- 인덱스 설정 (세션별 대화 순서 보장을 위한 복합 인덱스)
    INDEX idx_session_sequence (session_id, message_sequence),
    INDEX idx_agent_name (agent_name),
    INDEX idx_message_type (message_type),
    INDEX idx_message_timestamp (message_timestamp),
    INDEX idx_session_progress_stage (session_progress_stage),
    
    -- 유니크 제약조건 (같은 세션 내에서 메시지 순서 중복 방지)
    UNIQUE KEY uk_session_message_sequence (session_id, message_sequence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='세션 대화 기록';

-- 세션 퀴즈 테이블
CREATE TABLE session_quizzes (
    quiz_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '퀴즈 고유 ID',
    session_id VARCHAR(100) NOT NULL UNIQUE COMMENT '세션 ID (각 세션당 하나의 퀴즈)',
    question_number INT COMMENT '문제 번호',
    question_type VARCHAR(20) COMMENT '문제 유형 (객관식/주관식)',
    question_content TEXT COMMENT '문제 내용',
    user_answer TEXT COMMENT '사용자 답변',
    is_answer_correct INT COMMENT '정답 여부 (1: 정답, 0: 오답, NULL: 미채점)',
    evaluation_feedback TEXT COMMENT '평가 피드백',
    hint_usage_count INT DEFAULT 0 COMMENT '힌트 사용 횟수',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '레코드 생성 시간',
    
    -- 외래키 제약조건
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id) ON DELETE CASCADE,
    
    -- 인덱스 설정
    INDEX idx_question_type (question_type),
    INDEX idx_is_answer_correct (is_answer_correct),
    INDEX idx_created_at (created_at),
    
    -- 데이터 무결성 제약조건
    CHECK (question_number > 0),
    CHECK (is_answer_correct IN (0, 1) OR is_answer_correct IS NULL),
    CHECK (hint_usage_count >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='세션 퀴즈 정보';

-- ============================================================================
-- 5. 추가 인덱스 및 성능 최적화
-- ============================================================================

-- 복합 인덱스 추가 (자주 함께 조회되는 컬럼들)
ALTER TABLE user_auth_tokens ADD INDEX idx_user_active_expires (user_id, is_active, expires_at);
ALTER TABLE learning_sessions ADD INDEX idx_user_chapter_sequence (user_id, chapter_number, session_sequence);
ALTER TABLE session_conversations ADD INDEX idx_session_stage_timestamp (session_id, session_progress_stage, message_timestamp);

-- ============================================================================
-- 6. 테이블 생성 완료 확인용 뷰
-- ============================================================================

-- 테이블 생성 상태 확인용 뷰 (개발/디버깅 용도)
CREATE VIEW v_table_status AS
SELECT 
    TABLE_NAME as table_name,
    TABLE_ROWS as row_count,
    DATA_LENGTH as data_size,
    INDEX_LENGTH as index_size,
    CREATE_TIME as created_at
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- 스키마 생성 완료 로그
SELECT 'AI Skill Tutor Database Schema Created Successfully' as status, NOW() as created_at;