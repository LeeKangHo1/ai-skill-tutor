# ⚠️ DEPRECATED - 사용 중단된 모듈

## 개요

이 `backend/app/core/database` 폴더의 모든 모듈들은 **더 이상 사용되지 않습니다**.

## 사용 중단 일자

**2025년 8월 20일**

## 대체 모듈

현재 프로젝트에서는 다음 모듈을 사용합니다:

### 주요 데이터베이스 연결
- **기존**: `app.core.database.mysql_client.MySQLClient`
- **현재**: `app.config.db_config.get_db_connection()` (컨텍스트 매니저)

### 쿼리 빌더
- **기존**: `app.core.database.query_builder.QueryBuilder`
- **현재**: `app.utils.database.query_builder.QueryBuilder`

### 트랜잭션 관리
- **기존**: `app.core.database.transaction.TransactionManager`
- **현재**: `app.utils.database.transaction.TransactionManager`

### 기본 쿼리 실행
- **기존**: `MySQLClient` 메서드들
- **현재**: `app.utils.database.connection` 모듈의 함수들
  - `execute_query()`
  - `fetch_one()`
  - `fetch_all()`

## 마이그레이션 가이드

### 기존 코드
```python
from app.core.database import MySQLClient

client = MySQLClient()
connection = client.connect()
cursor = connection.cursor()
# ... 쿼리 실행
cursor.close()
connection.close()
```

### 새로운 코드
```python
from app.config.db_config import get_db_connection

with get_db_connection() as connection:
    cursor = connection.cursor()
    # ... 쿼리 실행
    # 자동으로 커밋/롤백 및 연결 해제됨
```

### 유틸리티 함수 사용
```python
from app.utils.database import execute_query, fetch_one, fetch_all

# 단일 레코드 조회
user = fetch_one("SELECT * FROM users WHERE user_id = %s", (user_id,))

# 다중 레코드 조회
users = fetch_all("SELECT * FROM users WHERE user_type = %s", ("beginner",))

# 데이터 수정
execute_query("UPDATE users SET last_login = NOW() WHERE user_id = %s", (user_id,))
```

## 사용 중단 이유

1. **연결 풀링**: 새로운 시스템은 연결 풀링을 지원하여 성능이 향상됨
2. **자동 재연결**: 연결 끊김 시 자동으로 재연결 시도
3. **컨텍스트 매니저**: 자동 트랜잭션 관리 및 리소스 해제
4. **환경별 최적화**: 개발/테스트/운영 환경별 최적화된 설정
5. **헬스체크**: 주기적인 연결 상태 확인 및 관리

## 주의사항

- 이 폴더의 모듈들을 import하면 DeprecationWarning이 발생합니다
- 새로운 코드에서는 절대 이 모듈들을 사용하지 마세요
- 기존 코드는 점진적으로 새로운 모듈로 마이그레이션하세요

## 삭제 예정

이 폴더는 모든 코드가 새로운 모듈로 마이그레이션된 후 삭제될 예정입니다.

---

**문의사항이 있으시면 개발팀에 연락하세요.**