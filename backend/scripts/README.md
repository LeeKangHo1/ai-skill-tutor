# backend/scripts/README.md
# 백엔드 스크립트 사용 가이드

이 폴더에는 AI 활용법 학습 튜터 프로젝트의 백엔드 관리용 스크립트들이 포함되어 있습니다.

## 📋 스크립트 목록

### 1. clear_all_tables.py
모든 데이터베이스 테이블의 데이터를 삭제하는 스크립트입니다.

**⚠️ 주의사항:**
- 이 스크립트는 **모든 데이터를 영구적으로 삭제**합니다.
- 실행 전 반드시 데이터 백업을 권장합니다.
- 개발 환경에서만 사용하세요.

## 🚀 사용법

### 사전 준비

1. **가상환경 활성화**
   ```bash
   # 프로젝트 루트에서 실행
   venv\Scripts\activate
   ```

2. **환경변수 설정 확인**
   - `backend/.env` 파일이 존재하고 올바른 DB 연결 정보가 설정되어 있는지 확인
   - 필수 환경변수: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

3. **의존성 패키지 설치**
   ```bash
   pip install -r backend/requirements.txt
   ```

### clear_all_tables.py 사용법

#### 기본 사용법 (대화형 모드)
```bash
# 프로젝트 루트에서 실행
python backend/scripts/clear_all_tables.py
```

실행하면 다음과 같은 과정을 거칩니다:
1. 현재 테이블 상태 조회 및 표시
2. 삭제될 데이터 행 수 표시
3. 사용자 확인 요청 (`yes`/`no` 입력)
4. 확인 후 테이블 데이터 삭제 실행
5. 삭제 결과 및 후 상태 표시

#### 강제 실행 모드 (확인 없이 실행)
```bash
# 확인 없이 바로 실행 (자동화 스크립트용)
python backend/scripts/clear_all_tables.py --force
```

**⚠️ --force 옵션 주의사항:**
- 사용자 확인 없이 즉시 모든 데이터를 삭제합니다.
- CI/CD 파이프라인이나 자동화된 테스트 환경에서만 사용하세요.

## 📊 실행 결과 예시

### 성공적인 실행 예시
```
=== 테이블 상태 조회 ===
테이블 'session_conversations': 150행
테이블 'session_quizzes': 75행
테이블 'learning_sessions': 75행
테이블 'user_auth_tokens': 10행
테이블 'user_statistics': 5행
테이블 'user_progress': 5행
테이블 'users': 5행
테이블 'chapters': 존재하지 않음
총 데이터 행 수: 325

⚠️  경고: 모든 테이블의 데이터가 삭제됩니다!
이 작업은 되돌릴 수 없습니다.
삭제될 총 행 수: 325

계속하시겠습니까? (yes/no): yes

=== 삭제 결과 ===
성공 여부: True
메시지: 성공: 7개, 실패: 0개
삭제된 테이블: ['session_conversations', 'session_quizzes', 'learning_sessions', 'user_auth_tokens', 'user_statistics', 'user_progress', 'users']
실패한 테이블: []
삭제된 총 행 수: 325
```

### 이미 비어있는 경우
```
=== 테이블 상태 조회 ===
테이블 'session_conversations': 0행
테이블 'session_quizzes': 0행
테이블 'learning_sessions': 0행
테이블 'user_auth_tokens': 0행
테이블 'user_statistics': 0행
테이블 'user_progress': 0행
테이블 'users': 0행
테이블 'chapters': 존재하지 않음
총 데이터 행 수: 0

모든 테이블이 이미 비어있습니다.
```

## 🔧 기술적 세부사항

### 삭제 순서
스크립트는 외래키 제약조건을 고려하여 다음 순서로 테이블을 삭제합니다:

1. **종속 테이블 (외래키 참조하는 테이블)**
   - `session_conversations` (learning_sessions 참조)
   - `session_quizzes` (learning_sessions 참조)
   - `learning_sessions` (users 참조)
   - `user_auth_tokens` (users 참조)
   - `user_statistics` (users 참조)
   - `user_progress` (users 참조)

2. **기본 테이블**
   - `users` (기본 사용자 테이블)
   - `chapters` (독립적 테이블, 추후 구현)

### 사용되는 SQL 명령어
- `TRUNCATE TABLE`: 빠른 삭제 및 AUTO_INCREMENT 값 리셋
- `SET FOREIGN_KEY_CHECKS = 0/1`: 외래키 제약조건 임시 비활성화/활성화
- `SHOW TABLES`: 존재하는 테이블 목록 조회
- `SELECT COUNT(*)`: 테이블별 행 수 조회

### 로깅
- 모든 실행 과정이 콘솔과 로그 파일에 기록됩니다.
- 로그 파일 위치: `logs/clear_tables.log`
- 로그 레벨: INFO (일반 정보), ERROR (오류), WARNING (경고)

## 🛠️ 문제 해결

### 일반적인 오류와 해결방법

#### 1. 데이터베이스 연결 오류
```
❌ 데이터베이스 연결 실패: (2003, "Can't connect to MySQL server")
```
**해결방법:**
- MySQL 서버가 실행 중인지 확인
- `.env` 파일의 DB 연결 정보 확인 (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`)
- 방화벽 설정 확인

#### 2. 권한 오류
```
❌ 오류 발생: (1142, "DROP command denied to user")
```
**해결방법:**
- DB 사용자에게 `DELETE`, `TRUNCATE` 권한이 있는지 확인
- 필요시 관리자 권한으로 실행

#### 3. 환경변수 누락
```
❌ 필수 데이터베이스 설정이 누락되었습니다: database, user, password
```
**해결방법:**
- `backend/.env` 파일 존재 여부 확인
- 필수 환경변수 설정 확인

#### 4. 가상환경 미활성화
```
ModuleNotFoundError: No module named 'app'
```
**해결방법:**
- 가상환경 활성화: `venv\Scripts\activate`
- 프로젝트 루트에서 스크립트 실행

## 📝 개발자 노트

### 스크립트 확장 방법

새로운 테이블이 추가되면 `clear_all_tables.py`의 `tables_to_clear` 리스트를 업데이트하세요:

```python
self.tables_to_clear = [
    # 새로운 종속 테이블 추가
    'new_dependent_table',    # 다른 테이블 참조
    
    # 기존 테이블들...
    'session_conversations',
    'session_quizzes',
    # ...
]
```

### 안전 장치

1. **외래키 제약조건 처리**: 삭제 중 일시적으로 비활성화
2. **트랜잭션 관리**: 각 테이블 삭제는 개별 트랜잭션으로 처리
3. **존재 여부 확인**: 존재하지 않는 테이블은 자동으로 건너뜀
4. **상세 로깅**: 모든 과정이 로그로 기록됨
5. **사용자 확인**: 대화형 모드에서 명시적 확인 요구

### 성능 최적화

- `TRUNCATE` 사용으로 `DELETE`보다 빠른 삭제
- 외래키 제약조건 임시 비활성화로 삭제 속도 향상
- 연결 풀 사용으로 DB 연결 오버헤드 최소화

## 🔒 보안 고려사항

- 운영 환경에서는 절대 사용하지 마세요
- 스크립트 실행 전 반드시 데이터 백업
- `.env` 파일의 DB 접근 권한 최소화
- 로그 파일에 민감한 정보 노출 방지

---

**마지막 업데이트**: 2025-08-23  
**작성자**: AI 활용법 학습 튜터 개발팀