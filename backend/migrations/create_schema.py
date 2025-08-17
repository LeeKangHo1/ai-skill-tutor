# backend/migrations/create_schema.py
# 데이터베이스 스키마 생성 스크립트 v2.0
# 기존 DB 삭제 및 새 스키마 생성 기능 구현

import os
import sys
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.db_config import get_db_connection, DatabaseConnectionError, DatabaseQueryError

# 로깅 설정
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / 'schema_creation.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class SchemaCreationError(Exception):
    """스키마 생성 관련 오류"""
    def __init__(self, message: str, sql_statement: str = None, original_error: Exception = None):
        super().__init__(message)
        self.sql_statement = sql_statement
        self.original_error = original_error

class DatabaseSchemaManager:
    """데이터베이스 스키마 관리 클래스 v2.0"""
    
    def __init__(self):
        """스키마 관리자 초기화"""
        self.schema_file_path = Path(__file__).parent / 'schema.sql'
        self.expected_tables = [
            'users', 'user_auth_tokens', 'user_progress', 'user_statistics',
            'learning_sessions', 'session_conversations', 'session_quizzes'
        ]
        self.expected_views = [
            'v_table_status', 'v_quiz_json_validation', 'v_statistics_validation'
        ]
    
    def drop_all_existing_tables(self) -> bool:
        """기존 모든 테이블 삭제 (외래키 제약조건 고려)"""
        logger.info("=== 기존 테이블 삭제 시작 ===")
        
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    # 1. 현재 테이블 목록 조회
                    cursor.execute("SHOW TABLES")
                    existing_tables = [table[list(table.keys())[0]] for table in cursor.fetchall()]
                    
                    if not existing_tables:
                        logger.info("삭제할 테이블이 없습니다.")
                        return True
                    
                    logger.info(f"기존 테이블 발견: {existing_tables}")
                    
                    # 2. 외래키 제약조건 비활성화
                    logger.info("외래키 제약조건 비활성화...")
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                    
                    # 3. 뷰 먼저 삭제
                    logger.info("기존 뷰 삭제...")
                    for view_name in self.expected_views:
                        try:
                            cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
                            logger.info(f"뷰 삭제 완료: {view_name}")
                        except Exception as e:
                            logger.warning(f"뷰 삭제 실패 (무시): {view_name} - {e}")
                    
                    # 4. 모든 테이블 삭제 (역순으로)
                    tables_to_drop = [
                        'session_quizzes', 'session_conversations', 'learning_sessions',
                        'user_statistics', 'user_progress', 'user_auth_tokens', 'users'
                    ]
                    
                    # 기존 테이블 중에서 삭제 대상 확인
                    for table_name in tables_to_drop:
                        if table_name in existing_tables:
                            try:
                                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                                logger.info(f"테이블 삭제 완료: {table_name}")
                            except Exception as e:
                                logger.error(f"테이블 삭제 실패: {table_name} - {e}")
                                raise SchemaCreationError(f"테이블 삭제 실패: {table_name}", original_error=e)
                    
                    # 5. 남은 테이블들도 삭제 (예상치 못한 테이블들)
                    cursor.execute("SHOW TABLES")
                    remaining_tables = [table[list(table.keys())[0]] for table in cursor.fetchall()]
                    
                    for table_name in remaining_tables:
                        try:
                            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                            logger.info(f"추가 테이블 삭제 완료: {table_name}")
                        except Exception as e:
                            logger.warning(f"추가 테이블 삭제 실패 (무시): {table_name} - {e}")
                    
                    # 6. 외래키 제약조건 재활성화
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                    logger.info("외래키 제약조건 재활성화 완료")
                    
                    # 7. 삭제 확인
                    cursor.execute("SHOW TABLES")
                    final_tables = cursor.fetchall()
                    
                    if final_tables:
                        logger.warning(f"삭제되지 않은 테이블: {[table[list(table.keys())[0]] for table in final_tables]}")
                    else:
                        logger.info("✅ 모든 테이블 삭제 완료")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"❌ 테이블 삭제 실패: {e}")
            raise SchemaCreationError("기존 테이블 삭제 실패", original_error=e)
    
    def parse_schema_file(self) -> List[str]:
        """schema.sql 파일 파싱 및 SQL 문 분리"""
        logger.info(f"스키마 파일 파싱: {self.schema_file_path}")
        
        try:
            if not self.schema_file_path.exists():
                raise FileNotFoundError(f"스키마 파일을 찾을 수 없습니다: {self.schema_file_path}")
            
            with open(self.schema_file_path, 'r', encoding='utf-8') as f:
                schema_content = f.read()
            
            # 주석 및 빈 줄 제거
            lines = []
            for line in schema_content.split('\n'):
                line = line.strip()
                # 주석 라인 제거 (# 또는 -- 로 시작)
                if line and not line.startswith('#') and not line.startswith('--'):
                    lines.append(line)
            
            # 다시 합치고 세미콜론으로 분리
            clean_sql = ' '.join(lines)
            sql_statements = []
            
            # 세미콜론으로 분리하되, 빈 문장 제거
            for stmt in clean_sql.split(';'):
                stmt = stmt.strip()
                if stmt and len(stmt) > 10:  # 너무 짧은 문장 제외
                    sql_statements.append(stmt)
            
            logger.info(f"파싱 완료: {len(sql_statements)}개의 SQL 문")
            return sql_statements
            
        except Exception as e:
            logger.error(f"스키마 파일 파싱 실패: {e}")
            raise SchemaCreationError("스키마 파일 파싱 실패", original_error=e)
    
    def execute_sql_statements(self, sql_statements: List[str]) -> bool:
        """SQL 문들을 순차적으로 실행"""
        logger.info("=== SQL 문 실행 시작 ===")
        
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    success_count = 0
                    failure_count = 0
                    
                    for i, sql in enumerate(sql_statements, 1):
                        try:
                            # SQL 문 타입 확인
                            sql_type = self._get_sql_type(sql)
                            logger.info(f"[{i}/{len(sql_statements)}] {sql_type} 실행 중...")
                            logger.debug(f"SQL: {sql[:100]}...")
                            
                            # SQL 실행
                            cursor.execute(sql)
                            success_count += 1
                            logger.info(f"✅ 성공: {sql_type}")
                            
                            # 테이블 생성의 경우 추가 정보 출력
                            if sql_type.startswith('CREATE TABLE'):
                                table_name = self._extract_table_name(sql)
                                if table_name:
                                    logger.info(f"   테이블 생성됨: {table_name}")
                            
                        except Exception as e:
                            failure_count += 1
                            sql_type = self._get_sql_type(sql)
                            logger.error(f"❌ 실패: {sql_type} - {e}")
                            logger.debug(f"실패한 SQL: {sql[:200]}...")
                            
                            # 중요한 테이블 생성 실패는 예외 발생
                            if 'CREATE TABLE' in sql.upper():
                                table_name = self._extract_table_name(sql)
                                if table_name in self.expected_tables:
                                    raise SchemaCreationError(
                                        f"필수 테이블 생성 실패: {table_name}",
                                        sql_statement=sql,
                                        original_error=e
                                    )
                    
                    logger.info(f"SQL 실행 완료: 성공 {success_count}개, 실패 {failure_count}개")
                    return failure_count == 0
                    
        except Exception as e:
            if isinstance(e, SchemaCreationError):
                raise
            logger.error(f"SQL 실행 중 오류: {e}")
            raise SchemaCreationError("SQL 실행 실패", original_error=e)
    
    def _get_sql_type(self, sql: str) -> str:
        """SQL 문의 타입 확인"""
        sql_upper = sql.upper().strip()
        
        if sql_upper.startswith('CREATE TABLE'):
            table_name = self._extract_table_name(sql)
            return f"CREATE TABLE ({table_name})"
        elif sql_upper.startswith('CREATE VIEW'):
            return "CREATE VIEW"
        elif sql_upper.startswith('ALTER TABLE'):
            return "ALTER TABLE"
        elif sql_upper.startswith('DROP TABLE'):
            return "DROP TABLE"
        elif sql_upper.startswith('INSERT'):
            return "INSERT"
        elif sql_upper.startswith('SELECT'):
            return "SELECT"
        else:
            return "기타 SQL"
    
    def _extract_table_name(self, sql: str) -> Optional[str]:
        """SQL 문에서 테이블 이름 추출"""
        try:
            sql_upper = sql.upper().strip()
            if 'CREATE TABLE' in sql_upper:
                # CREATE TABLE table_name 패턴에서 테이블 이름 추출
                parts = sql.split()
                for i, part in enumerate(parts):
                    if part.upper() == 'TABLE' and i + 1 < len(parts):
                        table_name = parts[i + 1].strip('(').strip()
                        return table_name
            return None
        except:
            return None
    
    def verify_schema_creation(self) -> Dict[str, Any]:
        """스키마 생성 결과 검증"""
        logger.info("=== 스키마 생성 검증 시작 ===")
        
        verification_result = {
            'success': False,
            'created_tables': [],
            'missing_tables': [],
            'created_views': [],
            'missing_views': [],
            'table_details': {},
            'error': None
        }
        
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    # 1. 테이블 확인
                    cursor.execute("SHOW TABLES")
                    existing_tables = [table[list(table.keys())[0]] for table in cursor.fetchall()]
                    
                    verification_result['created_tables'] = existing_tables
                    verification_result['missing_tables'] = [
                        table for table in self.expected_tables 
                        if table not in existing_tables
                    ]
                    
                    logger.info(f"생성된 테이블: {existing_tables}")
                    if verification_result['missing_tables']:
                        logger.warning(f"누락된 테이블: {verification_result['missing_tables']}")
                    
                    # 2. 뷰 확인
                    cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
                    existing_views = [view[list(view.keys())[0]] for view in cursor.fetchall()]
                    
                    verification_result['created_views'] = existing_views
                    verification_result['missing_views'] = [
                        view for view in self.expected_views 
                        if view not in existing_views
                    ]
                    
                    logger.info(f"생성된 뷰: {existing_views}")
                    if verification_result['missing_views']:
                        logger.warning(f"누락된 뷰: {verification_result['missing_views']}")
                    
                    # 3. 각 테이블의 상세 정보 확인
                    for table_name in existing_tables:
                        try:
                            # 테이블 구조 확인
                            cursor.execute(f"DESCRIBE {table_name}")
                            columns = cursor.fetchall()
                            
                            # 인덱스 확인
                            cursor.execute(f"SHOW INDEX FROM {table_name}")
                            indexes = cursor.fetchall()
                            
                            verification_result['table_details'][table_name] = {
                                'columns': len(columns),
                                'indexes': len(indexes),
                                'column_names': [col['Field'] for col in columns]
                            }
                            
                            logger.info(f"테이블 {table_name}: {len(columns)}개 컬럼, {len(indexes)}개 인덱스")
                            
                        except Exception as e:
                            logger.warning(f"테이블 {table_name} 상세 정보 확인 실패: {e}")
                    
                    # 4. 성공 여부 판단
                    verification_result['success'] = (
                        len(verification_result['missing_tables']) == 0 and
                        len(existing_tables) >= len(self.expected_tables)
                    )
                    
                    if verification_result['success']:
                        logger.info("✅ 스키마 생성 검증 성공")
                    else:
                        logger.error("❌ 스키마 생성 검증 실패")
                    
                    return verification_result
                    
        except Exception as e:
            logger.error(f"스키마 검증 중 오류: {e}")
            verification_result['error'] = str(e)
            return verification_result
    
    def create_fresh_schema(self) -> bool:
        """기존 DB 삭제 후 새 스키마 생성 (전체 프로세스)"""
        logger.info("=== 데이터베이스 스키마 v2.0 생성 시작 ===")
        start_time = time.time()
        
        try:
            # 1. 기존 테이블 삭제
            logger.info("1단계: 기존 테이블 삭제")
            if not self.drop_all_existing_tables():
                raise SchemaCreationError("기존 테이블 삭제 실패")
            
            # 2. 스키마 파일 파싱
            logger.info("2단계: 스키마 파일 파싱")
            sql_statements = self.parse_schema_file()
            
            # 3. SQL 문 실행
            logger.info("3단계: 새 스키마 생성")
            if not self.execute_sql_statements(sql_statements):
                logger.warning("일부 SQL 문 실행에 실패했지만 계속 진행합니다.")
            
            # 4. 생성 결과 검증
            logger.info("4단계: 스키마 생성 검증")
            verification_result = self.verify_schema_creation()
            
            # 5. 결과 출력
            elapsed_time = time.time() - start_time
            logger.info(f"스키마 생성 완료 (소요시간: {elapsed_time:.2f}초)")
            
            if verification_result['success']:
                logger.info("✅ 데이터베이스 스키마 v2.0 생성 성공!")
                logger.info(f"생성된 테이블: {len(verification_result['created_tables'])}개")
                logger.info(f"생성된 뷰: {len(verification_result['created_views'])}개")
                return True
            else:
                logger.error("❌ 스키마 생성 완료되었으나 검증에서 문제 발견")
                logger.error(f"누락된 테이블: {verification_result['missing_tables']}")
                return False
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"❌ 스키마 생성 실패 (소요시간: {elapsed_time:.2f}초): {e}")
            if isinstance(e, SchemaCreationError) and e.original_error:
                logger.error(f"원본 오류: {e.original_error}")
            return False

def create_database_schema() -> bool:
    """데이터베이스 스키마 생성 메인 함수 v2.0"""
    try:
        # 로그 디렉토리 생성
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # 스키마 관리자 생성 및 실행
        schema_manager = DatabaseSchemaManager()
        return schema_manager.create_fresh_schema()
        
    except Exception as e:
        logger.error(f"스키마 생성 프로세스 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("AI 활용법 학습 튜터 - 데이터베이스 스키마 v2.0 생성")
    print("=" * 60)
    
    try:
        success = create_database_schema()
        
        if success:
            print("\n🎉 데이터베이스 스키마 생성이 완료되었습니다!")
            print("다음 단계: 기본 CRUD 테스트를 실행해보세요.")
        else:
            print("\n❌ 데이터베이스 스키마 생성에 실패했습니다.")
            print("로그를 확인하여 문제를 해결해주세요.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()