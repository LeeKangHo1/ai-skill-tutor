# DB 설계 v2.0 수정내용 정리

## 📝 주요 테이블 구조 변경사항

### 1. **learning_sessions 테이블**

#### 변경사항:
- **세션 ID**: `VARCHAR(100)` → `INT AUTO_INCREMENT`
- **필드명 변경**: `session_decision_result` → `retry_decision_result`
- **구조 개선**: `session_sequence` → `section_number` (의미 명확화)

#### 기존 (v1.3):
```sql
session_id VARCHAR(100) PRIMARY KEY COMMENT '고유 세션 ID',
session_sequence INT NOT NULL COMMENT '해당 챕터 내에서의 세션 순서',
session_decision_result VARCHAR(20) COMMENT 'proceed: 다음 단계 진행, retry: 재학습',
```

#### 신규 (v2.0):
```sql
session_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '자동 증가 세션 ID',
section_number INT NOT NULL COMMENT '챕터 내 섹션 번호',
retry_decision_result VARCHAR(20) COMMENT 'proceed: 다음 단계 진행, retry: 재학습',
```

### 2. **session_conversations 테이블**

#### 변경사항:
- **외래키 타입**: `session_id VARCHAR(100)` → `session_id INT`

#### 기존 (v1.3):
```sql
session_id VARCHAR(100) NOT NULL,
```

#### 신규 (v2.0):
```sql
session_id INT NOT NULL COMMENT '세션 ID (AUTO_INCREMENT 참조)',
```

### 3. **session_quizzes 테이블 완전 재설계**

#### 기존 (v1.3):
```sql
session_id VARCHAR(100) NOT NULL UNIQUE COMMENT '세션과 1:1 연결',
question_number INT COMMENT '문제 번호',
question_type VARCHAR(20) COMMENT '문제 유형',
question_content TEXT COMMENT '문제 내용',
user_answer TEXT COMMENT '사용자 답변',
is_answer_correct INT COMMENT '객관식: 1(정답)/0(오답), 주관식: 0~100점',
```

#### 신규 (v2.0):
```sql
session_id INT NOT NULL COMMENT '세션 ID (AUTO_INCREMENT)',

-- 퀴즈 기본 정보
quiz_type VARCHAR(20) NOT NULL COMMENT 'multiple_choice: 객관식, subjective: 주관식',
quiz_content TEXT NOT NULL COMMENT '퀴즈 문제 내용',

-- 객관식 전용 필드
quiz_options JSON COMMENT '객관식 선택지 배열',
quiz_correct_answer INT COMMENT '객관식 정답 번호 (1-4)',
quiz_explanation TEXT COMMENT '객관식 정답 해설',

-- 주관식 전용 필드
quiz_sample_answer TEXT COMMENT '주관식 모범 답안 예시',
quiz_evaluation_criteria JSON COMMENT '주관식 평가 기준 배열',

-- 공통 필드
quiz_hint TEXT COMMENT '힌트 내용',
user_answer TEXT COMMENT '사용자 답변',

-- 평가 결과 분리
multiple_answer_correct BOOLEAN COMMENT '객관식 정답 여부',
subjective_answer_score INT COMMENT '주관식 점수 (0-100)',
```

### 4. **user_progress 테이블**

#### 변경사항:
- **새 필드 추가**: `current_section INT NOT NULL DEFAULT 1`

#### 기존 (v1.3):
```sql
current_chapter INT NOT NULL DEFAULT 1,
```

#### 신규 (v2.0):
```sql
current_chapter INT NOT NULL DEFAULT 1,
current_section INT NOT NULL DEFAULT 1,
```

### 5. **user_statistics 테이블 완전 재설계**

#### 기존 (v1.3):
```sql
total_correct_answers INT DEFAULT 0 COMMENT '총 정답 수',
average_accuracy DECIMAL(5,2) DEFAULT 0.00 COMMENT '평균 정답률 (%)',
```

#### 신규 (v2.0):
```sql
-- 객관식 통계
total_multiple_choice_count INT DEFAULT 0 COMMENT '총 객관식 문제 수',
total_multiple_choice_correct INT DEFAULT 0 COMMENT '객관식 정답 수',
multiple_choice_accuracy DECIMAL(5,2) DEFAULT 0.00 COMMENT '객관식 정답률 (%)',

-- 주관식 통계
total_subjective_count INT DEFAULT 0 COMMENT '총 주관식 문제 수',
total_subjective_score INT DEFAULT 0 COMMENT '주관식 총 점수',
subjective_average_score DECIMAL(5,2) DEFAULT 0.00 COMMENT '주관식 평균 점수',
```

## 🔧 비즈니스 로직 변경사항

### 1. **세션 저장 프로세스 변경**

#### 기존 (v1.3):
```sql
-- 1. 복잡한 세션 ID 생성
session_id = generate_session_id(user_id, chapter, section)

-- 2. 세션 저장
INSERT INTO learning_sessions (session_id, ...) VALUES (?, ...);
```

#### 신규 (v2.0):
```sql
-- 1. AUTO_INCREMENT로 세션 저장
INSERT INTO learning_sessions (...) VALUES (...);
SET @session_id = LAST_INSERT_ID();

-- 2. 생성된 session_id 사용
INSERT INTO session_quizzes (session_id, ...) VALUES (@session_id, ...);
```

### 2. **통계 업데이트 로직 분리**

#### 기존 (v1.3):
```sql
-- 통합 정답률 계산
total_correct_answers = total_correct_answers + CASE WHEN ... THEN 1 ELSE 0 END,
average_accuracy = (total_correct_answers * 100.0) / total_completed_sessions,
```

#### 신규 (v2.0):
```sql
-- 객관식 통계 업데이트
total_multiple_choice_count = total_multiple_choice_count + 1,
total_multiple_choice_correct = total_multiple_choice_correct + CASE WHEN ? = TRUE THEN 1 ELSE 0 END,
multiple_choice_accuracy = (total_multiple_choice_correct * 100.0) / total_multiple_choice_count,

-- 주관식 통계 업데이트 (별도 쿼리)
total_subjective_count = total_subjective_count + 1,
total_subjective_score = total_subjective_score + ?,
subjective_average_score = total_subjective_score / total_subjective_count,
```

### 3. **진행 상태 관리 개선**

#### 신규 (v2.0):
```sql
-- 챕터와 섹션 모두 업데이트
UPDATE user_progress 
SET 
    current_chapter = ?,
    current_section = ?,
    last_study_date = CURDATE()
WHERE user_id = ?;
```

## 🎯 제약 조건 강화

### 1. **퀴즈 타입별 필수 필드 검증**
```sql
-- 객관식: quiz_options, quiz_correct_answer 필수
CONSTRAINT chk_multiple_choice_fields CHECK (
    (quiz_type = 'multiple_choice' AND quiz_options IS NOT NULL AND quiz_correct_answer IS NOT NULL)
    OR quiz_type = 'subjective'
);

-- 주관식: quiz_sample_answer 필수
CONSTRAINT chk_subjective_fields CHECK (
    (quiz_type = 'subjective' AND quiz_sample_answer IS NOT NULL)
    OR quiz_type = 'multiple_choice'
);
```

### 2. **점수 범위 제한**
```sql
-- 점수 및 정확도 범위 제한
CONSTRAINT chk_accuracy_range CHECK (
    multiple_choice_accuracy >= 0 AND multiple_choice_accuracy <= 100 AND
    subjective_average_score >= 0 AND subjective_average_score <= 100
);
```

## 📊 성능 개선 효과

### 1. **AUTO_INCREMENT 도입**
- 세션 ID 생성 오버헤드 제거
- 외래키 참조 성능 향상 (INT vs VARCHAR)
- 인덱스 효율성 증대

### 2. **JSON 컬럼 활용**
- 배열 데이터 효율적 저장 (`quiz_options`, `quiz_evaluation_criteria`)
- 정규화 오버헤드 없이 구조화된 데이터 관리

### 3. **통계 분리**
- 객관식/주관식 성과 독립 추적
- 더 정확한 학습 분석 가능

## 🔄 마이그레이션 고려사항

### 1. **세션 ID 변경**
- 기존 VARCHAR 세션 ID → INT AUTO_INCREMENT
- 외래키 참조하는 모든 테이블 동시 변경 필요

### 2. **퀴즈 데이터 구조 변경**
- 기존 단일 필드 → 타입별 분리 필드
- JSON 컬럼 도입으로 데이터 재구성 필요

### 3. **통계 데이터 재계산**
- 기존 통합 통계 → 객관식/주관식 분리 통계
- 기존 데이터 기반 새로운 통계 재생성 필요

---

**주요 변경 효과:**
- State 설계 v2.0과 완벽한 연동
- 데이터 무결성 및 성능 향상
- 객관식/주관식 독립적 분석 가능
- 확장성 및 유지보수성 개선