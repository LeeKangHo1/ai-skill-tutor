# backend/migrations/schema.sql
-- AI 활용법 학습 튜터 데이터베이스 스키마 v2.0
-- MySQL 8.0 기반 테이블 생성 스크립트
-- AUTO_INCREMENT 세션 ID, JSON 컬럼, 객관식/주관식 분리 구조
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

-- 사용자 기본 정보 테이블 v2.0
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 기본 정보 v2.0';

-- ============================================================================
-- 2. 사용자 의존 테이블들 (users 테이블 참조)
-- ============================================================================

-- 사용자 인증 토큰 테이블 v2.0
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 인증 토큰 v2.0';

-- 사용자 학습 진행 상태 테이블 v2.0 (current_section 필드 추가)
CREATE TABLE user_progress (
    progress_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '진행 상태 고유 ID',
    user_id INT NOT NULL UNIQUE COMMENT '사용자 ID (각 사용자당 하나의 레코드)',
    current_chapter INT NOT NULL DEFAULT 1 COMMENT '현재 학습 중인 챕터',
    current_section INT NOT NULL DEFAULT 1 COMMENT '현재 학습 중인 섹션',
    last_study_date DATE COMMENT '마지막 학습 날짜',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '레코드 생성 시간',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '마지막 수정 시간',
    
    -- 외래키 제약조건
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- 인덱스 설정
    INDEX idx_current_chapter (current_chapter),
    INDEX idx_current_section (current_section),
    INDEX idx_last_study_date (last_study_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 학습 진행 상태 v2.0';

-- 사용자 학습 통계 테이블 v2.0 (객관식/주관식 분리 구조)
CREATE TABLE user_statistics (
    stats_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '통계 고유 ID',
    user_id INT NOT NULL UNIQUE COMMENT '사용자 ID (각 사용자당 하나의 레코드)',
    total_study_time_minutes INT DEFAULT 0 COMMENT '총 학습 시간 (분)',
    total_study_sessions INT DEFAULT 0 COMMENT '총 학습 세션 수',
    total_completed_sessions INT DEFAULT 0 COMMENT '완료된 세션 수',
    
    -- 객관식 통계
    total_multiple_choice_count INT DEFAULT 0 COMMENT '총 객관식 문제 수',
    total_multiple_choice_correct INT DEFAULT 0 COMMENT '객관식 정답 수',
    multiple_choice_accuracy DECIMAL(5,2) DEFAULT 0.00 COMMENT '객관식 정답률 (%)',
    
    -- 주관식 통계
    total_subjective_count INT DEFAULT 0 COMMENT '총 주관식 문제 수',
    total_subjective_score INT DEFAULT 0 COMMENT '주관식 총 점수',
    subjective_average_score DECIMAL(5,2) DEFAULT 0.00 COMMENT '주관식 평균 점수',
    
    last_study_date DATE COMMENT '마지막 학습 날짜',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '레코드 생성 시간',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '마지막 수정 시간',
    
    -- 외래키 제약조건
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- 인덱스 설정
    INDEX idx_total_study_sessions (total_study_sessions),
    INDEX idx_multiple_choice_accuracy (multiple_choice_accuracy),
    INDEX idx_subjective_average_score (subjective_average_score),
    INDEX idx_last_study_date (last_study_date),
    
    -- 데이터 무결성 제약조건
    CHECK (total_study_time_minutes >= 0),
    CHECK (total_study_sessions >= 0),
    CHECK (total_completed_sessions >= 0),
    CHECK (total_completed_sessions <= total_study_sessions),
    CHECK (total_multiple_choice_count >= 0),
    CHECK (total_multiple_choice_correct >= 0),
    CHECK (total_multiple_choice_correct <= total_multiple_choice_count),
    CHECK (multiple_choice_accuracy >= 0.00 AND multiple_choice_accuracy <= 100.00),
    CHECK (total_subjective_count >= 0),
    CHECK (total_subjective_score >= 0),
    CHECK (subjective_average_score >= 0.00 AND subjective_average_score <= 100.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 학습 통계 v2.0';

-- ============================================================================
-- 3. 학습 세션 테이블 v2.0 (AUTO_INCREMENT 세션 ID)
-- ============================================================================

-- 학습 세션 테이블 v2.0 (AUTO_INCREMENT 기반)
CREATE TABLE learning_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '세션 ID (AUTO_INCREMENT)',
    user_id INT NOT NULL COMMENT '사용자 ID',
    chapter_number INT NOT NULL COMMENT '챕터 번호',
    section_number INT NOT NULL COMMENT '섹션 번호',
    session_start_time TIMESTAMP NOT NULL COMMENT '세션 시작 시간',
    session_end_time TIMESTAMP NOT NULL COMMENT '세션 종료 시간',
    study_duration_minutes INT COMMENT '학습 소요 시간 (분)',
    retry_decision_result VARCHAR(20) COMMENT '재학습 결정 결과 (proceed/retry)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '레코드 생성 시간',
    
    -- 외래키 제약조건
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- 인덱스 설정
    INDEX idx_user_id (user_id),
    INDEX idx_chapter_section (chapter_number, section_number),
    INDEX idx_user_chapter_section (user_id, chapter_number, section_number),
    INDEX idx_session_start_time (session_start_time),
    INDEX idx_retry_decision_result (retry_decision_result),
    
    -- 데이터 무결성 제약조건
    CHECK (chapter_number > 0),
    CHECK (section_number > 0),
    CHECK (session_end_time >= session_start_time),
    CHECK (study_duration_minutes >= 0),
    CHECK (retry_decision_result IN ('proceed', 'retry') OR retry_decision_result IS NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='학습 세션 정보 v2.0';

-- ============================================================================
-- 4. 세션 의존 테이블들 v2.0 (learning_sessions 테이블 참조)
-- ============================================================================

-- 세션 대화 기록 테이블 v2.0 (INT 타입 session_id)
CREATE TABLE session_conversations (
    conversation_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '대화 고유 ID',
    session_id INT NOT NULL COMMENT '세션 ID (INT 타입)',
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
    INDEX idx_session_id (session_id),
    INDEX idx_message_sequence (session_id, message_sequence),
    INDEX idx_agent_name (agent_name),
    INDEX idx_message_type (message_type),
    INDEX idx_message_timestamp (message_timestamp),
    INDEX idx_session_progress_stage (session_progress_stage),
    
    -- 유니크 제약조건 (같은 세션 내에서 메시지 순서 중복 방지)
    UNIQUE KEY unique_session_message_sequence (session_id, message_sequence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='세션 대화 기록 v2.0';

-- 세션 퀴즈 테이블 v2.0 (객관식/주관식 분리 구조, JSON 컬럼 활용)
CREATE TABLE session_quizzes (
    quiz_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '퀴즈 고유 ID',
    session_id INT NOT NULL COMMENT '세션 ID (INT 타입)',
    
    -- 퀴즈 기본 정보
    quiz_type VARCHAR(20) NOT NULL COMMENT '퀴즈 유형 (multiple_choice/subjective)',
    quiz_content TEXT NOT NULL COMMENT '퀴즈 내용',
    
    -- 객관식 전용 필드
    quiz_options JSON COMMENT '객관식 선택지 (JSON 배열)',
    quiz_correct_answer INT COMMENT '객관식 정답 번호',
    quiz_explanation TEXT COMMENT '객관식 해설',
    
    -- 주관식 전용 필드
    quiz_sample_answer TEXT COMMENT '주관식 모범 답안',
    quiz_evaluation_criteria JSON COMMENT '주관식 평가 기준 (JSON 배열)',
    
    -- 공통 필드
    quiz_hint TEXT COMMENT '퀴즈 힌트',
    user_answer TEXT COMMENT '사용자 답변',
    
    -- 평가 결과 분리
    multiple_answer_correct BOOLEAN COMMENT '객관식 정답 여부',
    subjective_answer_score INT COMMENT '주관식 점수 (0-100)',
    
    evaluation_feedback TEXT COMMENT '평가 피드백',
    hint_usage_count INT DEFAULT 0 COMMENT '힌트 사용 횟수',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '레코드 생성 시간',
    
    -- 외래키 제약조건
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id) ON DELETE CASCADE,
    
    -- 인덱스 설정
    INDEX idx_session_id (session_id),
    INDEX idx_quiz_type (quiz_type),
    INDEX idx_multiple_answer_correct (multiple_answer_correct),
    INDEX idx_subjective_answer_score (subjective_answer_score),
    INDEX idx_created_at (created_at),
    
    -- 퀴즈 타입별 제약조건
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
    ),
    CONSTRAINT chk_hint_usage CHECK (hint_usage_count >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='세션 퀴즈 정보 v2.0';

-- ============================================================================
-- 5. 추가 인덱스 및 성능 최적화 v2.0
-- ============================================================================

-- 복합 인덱스 추가 (자주 함께 조회되는 컬럼들)
ALTER TABLE user_auth_tokens ADD INDEX idx_user_active_expires (user_id, is_active, expires_at);
ALTER TABLE session_conversations ADD INDEX idx_session_stage_timestamp (session_id, session_progress_stage, message_timestamp);

-- v2.0 추가 성능 최적화 인덱스
ALTER TABLE user_statistics ADD INDEX idx_user_multiple_choice_stats (user_id, total_multiple_choice_count, multiple_choice_accuracy);
ALTER TABLE user_statistics ADD INDEX idx_user_subjective_stats (user_id, total_subjective_count, subjective_average_score);
ALTER TABLE session_quizzes ADD INDEX idx_quiz_type_score (quiz_type, subjective_answer_score);
ALTER TABLE session_quizzes ADD INDEX idx_quiz_type_correct (quiz_type, multiple_answer_correct);

-- ============================================================================
-- 6. 테이블 생성 완료 확인용 뷰 v2.0
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

-- JSON 컬럼 검증용 뷰 (퀴즈 데이터 구조 확인)
CREATE VIEW v_quiz_json_validation AS
SELECT 
    quiz_id,
    session_id,
    quiz_type,
    CASE 
        WHEN quiz_type = 'multiple_choice' AND JSON_VALID(quiz_options) THEN 'Valid'
        WHEN quiz_type = 'subjective' AND JSON_VALID(quiz_evaluation_criteria) THEN 'Valid'
        ELSE 'Invalid'
    END as json_status,
    quiz_options,
    quiz_evaluation_criteria
FROM session_quizzes
WHERE quiz_options IS NOT NULL OR quiz_evaluation_criteria IS NOT NULL;

-- 통계 데이터 검증용 뷰 (객관식/주관식 분리 통계 확인)
CREATE VIEW v_statistics_validation AS
SELECT 
    user_id,
    total_multiple_choice_count,
    total_multiple_choice_correct,
    multiple_choice_accuracy,
    total_subjective_count,
    subjective_average_score,
    CASE 
        WHEN total_multiple_choice_count > 0 AND total_multiple_choice_correct <= total_multiple_choice_count THEN 'Valid'
        WHEN total_multiple_choice_count = 0 AND total_multiple_choice_correct = 0 THEN 'Valid'
        ELSE 'Invalid'
    END as multiple_choice_validation,
    CASE 
        WHEN subjective_average_score >= 0 AND subjective_average_score <= 100 THEN 'Valid'
        ELSE 'Invalid'
    END as subjective_score_validation
FROM user_statistics;

-- 스키마 생성 완료 로그 v2.0
SELECT 'AI Skill Tutor Database Schema v2.0 Created Successfully' as status, 
       'AUTO_INCREMENT sessions, JSON columns, separated quiz types' as features,
       NOW() as created_at;