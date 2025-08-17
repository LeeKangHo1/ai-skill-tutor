# Requirements Document

## Introduction

AI 활용법 학습 튜터 프로젝트의 데이터베이스 시스템 v2.0을 구축합니다. 이 시스템은 MySQL 8.0을 기반으로 하며, 통합 워크플로우와 하이브리드 UX를 지원하는 새로운 데이터 구조를 제공합니다. 주요 개선사항으로는 AUTO_INCREMENT 세션 ID 도입, 객관식/주관식 퀴즈 분리, 통계 시스템 개선, JSON 컬럼 활용 등이 있습니다. State 설계 v2.0과 완벽하게 연동되어 LangGraph 워크플로우를 효율적으로 지원합니다.

## Requirements

### Requirement 1

**User Story:** 시스템 관리자로서, MySQL 데이터베이스 연결을 설정하고 기본 환경을 구성하여 애플리케이션이 데이터를 저장할 수 있기를 원합니다.

#### Acceptance Criteria

1. WHEN 애플리케이션이 시작되면 THEN 시스템은 MySQL 8.0 데이터베이스에 성공적으로 연결되어야 합니다
2. WHEN 데이터베이스 연결 설정이 환경변수로 제공되면 THEN 시스템은 해당 설정을 사용하여 연결해야 합니다
3. WHEN 데이터베이스 연결이 실패하면 THEN 시스템은 명확한 오류 메시지를 로그에 기록해야 합니다
4. WHEN 애플리케이션이 종료되면 THEN 시스템은 데이터베이스 연결을 안전하게 종료해야 합니다
5. WHEN 연결 풀이 설정되면 THEN 시스템은 동시 접속을 효율적으로 관리해야 합니다

### Requirement 2

**User Story:** 데이터베이스 관리자로서, 사용자 관련 테이블들이 v2.0 구조와 제약조건으로 생성되어 섹션별 진행 상태와 분리된 통계를 안전하게 저장하고 싶습니다.

#### Acceptance Criteria

1. WHEN 데이터베이스 초기화가 실행되면 THEN 시스템은 users 테이블을 생성하고 적절한 인덱스를 설정해야 합니다
2. WHEN users 테이블이 생성되면 THEN login_id와 email 필드에 UNIQUE 제약조건이 적용되어야 합니다
3. WHEN user_progress 테이블이 생성되면 THEN current_chapter와 current_section 필드로 섹션별 진행 상태를 추적해야 합니다
4. WHEN user_statistics 테이블이 생성되면 THEN 객관식 통계(total_multiple_choice_count, multiple_choice_accuracy)와 주관식 통계(total_subjective_count, subjective_average_score)가 분리되어야 합니다
5. WHEN 통계 테이블이 생성되면 THEN 정확도와 점수 범위(0-100) 제약조건이 적용되어야 합니다

### Requirement 3

**User Story:** 개발자로서, AUTO_INCREMENT 기반의 효율적인 세션 관리와 객관식/주관식 분리된 퀴즈 구조를 통해 학습 과정을 정확하게 추적하고 싶습니다.

#### Acceptance Criteria

1. WHEN learning_sessions 테이블이 생성되면 THEN AUTO_INCREMENT 세션 ID와 section_number 필드를 지원해야 합니다
2. WHEN session_conversations 테이블이 생성되면 THEN INT 타입 session_id 외래키와 메시지 순서 복합 인덱스가 설정되어야 합니다
3. WHEN session_quizzes 테이블이 생성되면 THEN quiz_type 기반으로 객관식/주관식 필드가 분리되어 저장되어야 합니다
4. WHEN 객관식 퀴즈가 저장되면 THEN quiz_options(JSON), quiz_correct_answer, quiz_explanation 필드가 필수로 채워져야 합니다
5. WHEN 주관식 퀴즈가 저장되면 THEN quiz_sample_answer, quiz_evaluation_criteria(JSON) 필드가 필수로 채워져야 합니다
6. WHEN 퀴즈 평가 결과가 저장되면 THEN multiple_answer_correct(boolean)과 subjective_answer_score(0-100) 필드가 분리되어 저장되어야 합니다

### Requirement 4

**User Story:** 백엔드 개발자로서, 데이터베이스 작업을 위한 일관된 모델과 유틸리티 함수를 사용하여 효율적으로 개발하고 싶습니다.

#### Acceptance Criteria

1. WHEN 데이터베이스 모델이 정의되면 THEN 각 테이블에 대응하는 Python 클래스가 생성되어야 합니다
2. WHEN CRUD 작업이 필요하면 THEN 재사용 가능한 데이터베이스 유틸리티 함수가 제공되어야 합니다
3. WHEN 데이터베이스 쿼리가 실행되면 THEN 적절한 오류 처리와 로깅이 수행되어야 합니다

### Requirement 5

**User Story:** 개발자로서, v2.0 데이터베이스 구조의 기본 CRUD 작업이 정상적으로 작동하는지 간단하게 테스트할 수 있기를 원합니다.

#### Acceptance Criteria

1. WHEN 데이터베이스 연결 테스트가 실행되면 THEN 연결 상태를 확인할 수 있어야 합니다
2. WHEN 사용자 CRUD 테스트가 실행되면 THEN 생성/조회/수정/삭제가 정상 작동해야 합니다
3. WHEN AUTO_INCREMENT 세션 생성 테스트가 실행되면 THEN 세션 ID가 자동으로 생성되고 조회 가능해야 합니다
4. WHEN JSON 컬럼 기본 테스트가 실행되면 THEN quiz_options와 quiz_evaluation_criteria 저장/조회가 정상 작동해야 합니다
5. WHEN 분리된 통계 기본 테스트가 실행되면 THEN 객관식/주관식 통계 저장/조회가 정상 작동해야 합니다

### Requirement 6

**User Story:** 시스템 관리자로서, 기존 데이터베이스를 완전히 삭제하고 v2.0 구조로 새로 생성할 수 있는 도구를 원합니다.

#### Acceptance Criteria

1. WHEN 데이터베이스 초기화 스크립트가 실행되면 THEN 기존 모든 테이블이 삭제되어야 합니다
2. WHEN 스키마 생성 스크립트가 실행되면 THEN v2.0 구조의 모든 테이블이 생성되어야 합니다
3. WHEN 테이블 생성이 완료되면 THEN 모든 인덱스와 제약조건이 적용되어야 합니다
4. WHEN 초기화 중 오류가 발생하면 THEN 명확한 오류 메시지가 출력되어야 합니다
5. WHEN 초기화가 완료되면 THEN 테이블 구조 검증이 자동으로 수행되어야 합니다