# Implementation Plan

- [x] 1. 데이터베이스 연결 시스템 v2.0 업그레이드





  - db_config.py를 v2.0 요구사항에 맞게 업데이트 (최적화된 연결 풀 설정)
  - connection.py에 자동 재연결 및 헬스체크 기능 추가
  - 개발/테스트/운영 환경별 설정 분리 구현
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. v2.0 데이터베이스 스키마 생성





  - schema.sql을 v2.0 구조로 완전 재작성 (AUTO_INCREMENT, JSON 컬럼, 분리된 통계)
  - 퀴즈 타입별 제약조건 및 JSON 스키마 검증 추가
  - 복합 인덱스 및 성능 최적화 인덱스 설정
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. v2.0 데이터베이스 모델 클래스 업데이트




- [x] 3.1 사용자 관련 모델 v2.0 업데이트


  - UserProgress 모델에 current_section 필드 추가
  - UserStatistics 모델을 객관식/주관식 분리 구조로 업데이트
  - 분리된 통계 계산 메서드 구현 (calculate_multiple_choice_accuracy, calculate_subjective_average)
  - _Requirements: 4.1, 2.3, 2.4_



- [x] 3.2 학습 세션 관련 모델 v2.0 재구현





  - LearningSession 모델을 AUTO_INCREMENT 기반으로 변경
  - SessionQuiz 모델을 객관식/주관식 분리 구조로 완전 재설계
  - JSON 필드 처리 메서드 구현 (quiz_options, quiz_evaluation_criteria)
  - 퀴즈 타입별 검증 로직 구현
  - _Requirements: 4.1, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 4. 기본 데이터베이스 유틸리티 시스템 구현





- [x] 4.1 쿼리 빌더 기본 기능 구현


  - query_builder.py에 기본 SQL 생성 기능 구현
  - 파라미터 바인딩 및 SQL 인젝션 방지
  - JSON 컬럼 기본 쿼리 지원
  - _Requirements: 4.2, 4.3_

- [x] 4.2 트랜잭션 관리자 기본 구현


  - transaction.py에 기본 트랜잭션 기능 구현
  - 자동 롤백 및 커밋 컨텍스트 관리자
  - _Requirements: 4.2, 4.3_

- [x] 5. 데이터베이스 초기화 시스템 구현




- [x] 5.1 기존 DB 삭제 및 새 스키마 생성


  - create_schema.py를 v2.0 구조로 완전 재작성
  - 기존 모든 테이블 삭제 기능 구현
  - v2.0 구조 테이블 생성 기능 구현
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 5.2 스키마 검증 도구 구현






  - 테이블 구조 검증 기능
  - 인덱스 및 제약조건 확인 기능
  - _Requirements: 6.5_

- [x] 5.3 실제 데이터베이스 초기화 및 v2.0 스키마 적용










  - 5-1번에서 생성한 create_schema.py를 실행하여 실제 DB 초기화
  - 기존 데이터베이스의 모든 테이블과 데이터 완전 삭제
  - v2.0 스키마 구조로 새로운 테이블 생성 및 적용
  - 스키마 생성 결과 검증 및 로그 확인
  - 데이터베이스 연결 테스트 및 기본 동작 확인
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 6. 기본 CRUD 테스트 시스템 구현





- [x] 6.1 연결 및 기본 CRUD 테스트


  - 데이터베이스 연결 테스트
  - 각 테이블별 기본 CRUD 작업 테스트
  - AUTO_INCREMENT 세션 ID 생성 테스트
  - _Requirements: 5.1, 5.2, 5.3_


- [x] 6.2 JSON 컬럼 및 통계 기본 테스트





  - JSON 컬럼 기본 저장/조회 테스트
  - 객관식/주관식 분리 통계 기본 테스트
  - _Requirements: 5.4, 5.5_