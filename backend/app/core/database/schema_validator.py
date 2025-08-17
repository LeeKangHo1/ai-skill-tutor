# backend/app/core/database/schema_validator.py
"""
데이터베이스 스키마 검증 도구
테이블 구조, 인덱스, 제약조건을 검증하는 기능을 제공합니다.
"""

from typing import Dict, List, Any, Optional, Tuple
import json
from dataclasses import dataclass
from enum import Enum
from .mysql_client import MySQLClient


class ValidationStatus(Enum):
    """검증 상태 열거형"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    MISSING = "MISSING"


@dataclass
class ValidationResult:
    """검증 결과 데이터 클래스"""
    status: ValidationStatus
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class TableInfo:
    """테이블 정보 데이터 클래스"""
    name: str
    engine: str
    charset: str
    collation: str
    row_count: int
    data_length: int
    index_length: int


@dataclass
class ColumnInfo:
    """컬럼 정보 데이터 클래스"""
    name: str
    data_type: str
    is_nullable: bool
    default_value: Optional[str]
    is_primary_key: bool
    is_unique: bool
    is_auto_increment: bool
    character_set: Optional[str]
    collation: Optional[str]


@dataclass
class IndexInfo:
    """인덱스 정보 데이터 클래스"""
    name: str
    table_name: str
    columns: List[str]
    is_unique: bool
    index_type: str


@dataclass
class ConstraintInfo:
    """제약조건 정보 데이터 클래스"""
    name: str
    table_name: str
    constraint_type: str
    column_names: List[str]
    referenced_table: Optional[str] = None
    referenced_columns: Optional[List[str]] = None
    check_clause: Optional[str] = None


class SchemaValidator:
    """데이터베이스 스키마 검증 클래스"""
    
    def __init__(self, mysql_client: MySQLClient):
        """
        스키마 검증기 초기화
        
        Args:
            mysql_client: MySQL 클라이언트 인스턴스
        """
        self.client = mysql_client
        self.database_name = mysql_client.connection_config['database']
        
        # v2.0 예상 테이블 목록
        self.expected_tables = {
            'users', 'user_auth_tokens', 'user_progress', 'user_statistics',
            'learning_sessions', 'session_conversations', 'session_quizzes'
        }
        
        # v2.0 예상 뷰 목록
        self.expected_views = {
            'v_table_status', 'v_quiz_json_validation', 'v_statistics_validation'
        }
    
    def validate_all(self) -> Dict[str, List[ValidationResult]]:
        """
        전체 스키마를 검증합니다.
        
        Returns:
            Dict[str, List[ValidationResult]]: 카테고리별 검증 결과
        """
        results = {
            'database': [],
            'tables': [],
            'columns': [],
            'indexes': [],
            'constraints': [],
            'views': [],
            'json_columns': []
        }
        
        # 데이터베이스 연결 검증
        results['database'].extend(self._validate_database_connection())
        
        # 테이블 존재 검증
        results['tables'].extend(self._validate_tables_exist())
        
        # 컬럼 구조 검증
        results['columns'].extend(self._validate_table_columns())
        
        # 인덱스 검증
        results['indexes'].extend(self._validate_indexes())
        
        # 제약조건 검증
        results['constraints'].extend(self._validate_constraints())
        
        # 뷰 검증
        results['views'].extend(self._validate_views())
        
        # JSON 컬럼 검증
        results['json_columns'].extend(self._validate_json_columns())
        
        return results
    
    def _validate_database_connection(self) -> List[ValidationResult]:
        """데이터베이스 연결을 검증합니다."""
        results = []
        
        try:
            if self.client.check_connection():
                results.append(ValidationResult(
                    status=ValidationStatus.PASS,
                    message=f"데이터베이스 '{self.database_name}' 연결 성공"
                ))
            else:
                results.append(ValidationResult(
                    status=ValidationStatus.FAIL,
                    message=f"데이터베이스 '{self.database_name}' 연결 실패"
                ))
        except Exception as e:
            results.append(ValidationResult(
                status=ValidationStatus.FAIL,
                message=f"데이터베이스 연결 검증 중 오류: {str(e)}"
            ))
        
        return results
    
    def _validate_tables_exist(self) -> List[ValidationResult]:
        """테이블 존재 여부를 검증합니다."""
        results = []
        
        try:
            # 실제 테이블 목록 조회
            actual_tables = self.get_table_list()
            actual_table_names = {table.name for table in actual_tables}
            
            # 예상 테이블 검증
            for expected_table in self.expected_tables:
                if expected_table in actual_table_names:
                    results.append(ValidationResult(
                        status=ValidationStatus.PASS,
                        message=f"테이블 '{expected_table}' 존재 확인"
                    ))
                else:
                    results.append(ValidationResult(
                        status=ValidationStatus.MISSING,
                        message=f"테이블 '{expected_table}' 누락"
                    ))
            
            # 예상하지 않은 테이블 확인
            unexpected_tables = actual_table_names - self.expected_tables
            for unexpected_table in unexpected_tables:
                results.append(ValidationResult(
                    status=ValidationStatus.WARNING,
                    message=f"예상하지 않은 테이블 '{unexpected_table}' 발견"
                ))
                
        except Exception as e:
            results.append(ValidationResult(
                status=ValidationStatus.FAIL,
                message=f"테이블 목록 조회 중 오류: {str(e)}"
            ))
        
        return results
    
    def _validate_table_columns(self) -> List[ValidationResult]:
        """테이블 컬럼 구조를 검증합니다."""
        results = []
        
        # 각 테이블별 예상 컬럼 정의
        expected_columns = self._get_expected_columns()
        
        for table_name, expected_cols in expected_columns.items():
            try:
                actual_columns = self.get_table_columns(table_name)
                actual_col_names = {col.name for col in actual_columns}
                expected_col_names = set(expected_cols.keys())
                
                # 필수 컬럼 검증
                missing_columns = expected_col_names - actual_col_names
                for missing_col in missing_columns:
                    results.append(ValidationResult(
                        status=ValidationStatus.MISSING,
                        message=f"테이블 '{table_name}'에서 컬럼 '{missing_col}' 누락"
                    ))
                
                # 존재하는 컬럼의 타입 검증
                for col in actual_columns:
                    if col.name in expected_cols:
                        expected_type = expected_cols[col.name]['type']
                        if self._normalize_column_type(col.data_type) == self._normalize_column_type(expected_type):
                            results.append(ValidationResult(
                                status=ValidationStatus.PASS,
                                message=f"테이블 '{table_name}' 컬럼 '{col.name}' 타입 검증 통과"
                            ))
                        else:
                            results.append(ValidationResult(
                                status=ValidationStatus.FAIL,
                                message=f"테이블 '{table_name}' 컬럼 '{col.name}' 타입 불일치: 예상={expected_type}, 실제={col.data_type}"
                            ))
                
            except Exception as e:
                results.append(ValidationResult(
                    status=ValidationStatus.FAIL,
                    message=f"테이블 '{table_name}' 컬럼 검증 중 오류: {str(e)}"
                ))
        
        return results
    
    def _validate_indexes(self) -> List[ValidationResult]:
        """인덱스를 검증합니다."""
        results = []
        
        # 각 테이블별 예상 인덱스 정의
        expected_indexes = self._get_expected_indexes()
        
        for table_name, expected_idx_list in expected_indexes.items():
            try:
                actual_indexes = self.get_table_indexes(table_name)
                
                for expected_idx in expected_idx_list:
                    # 인덱스 이름 또는 컬럼 조합으로 검증
                    found = False
                    for actual_idx in actual_indexes:
                        if (expected_idx['name'] == actual_idx.name or 
                            set(expected_idx['columns']) == set(actual_idx.columns)):
                            found = True
                            results.append(ValidationResult(
                                status=ValidationStatus.PASS,
                                message=f"테이블 '{table_name}' 인덱스 '{expected_idx['name']}' 존재 확인"
                            ))
                            break
                    
                    if not found:
                        results.append(ValidationResult(
                            status=ValidationStatus.MISSING,
                            message=f"테이블 '{table_name}' 인덱스 '{expected_idx['name']}' 누락"
                        ))
                        
            except Exception as e:
                results.append(ValidationResult(
                    status=ValidationStatus.FAIL,
                    message=f"테이블 '{table_name}' 인덱스 검증 중 오류: {str(e)}"
                ))
        
        return results
    
    def _validate_constraints(self) -> List[ValidationResult]:
        """제약조건을 검증합니다."""
        results = []
        
        # 각 테이블별 예상 제약조건 정의
        expected_constraints = self._get_expected_constraints()
        
        for table_name, expected_const_list in expected_constraints.items():
            try:
                actual_constraints = self.get_table_constraints(table_name)
                
                for expected_const in expected_const_list:
                    # 제약조건 이름 또는 타입으로 검증
                    found = False
                    for actual_const in actual_constraints:
                        if (expected_const['type'] == actual_const.constraint_type and
                            set(expected_const.get('columns', [])) == set(actual_const.column_names)):
                            found = True
                            results.append(ValidationResult(
                                status=ValidationStatus.PASS,
                                message=f"테이블 '{table_name}' 제약조건 '{expected_const['name']}' 존재 확인"
                            ))
                            break
                    
                    if not found:
                        results.append(ValidationResult(
                            status=ValidationStatus.MISSING,
                            message=f"테이블 '{table_name}' 제약조건 '{expected_const['name']}' 누락"
                        ))
                        
            except Exception as e:
                results.append(ValidationResult(
                    status=ValidationStatus.FAIL,
                    message=f"테이블 '{table_name}' 제약조건 검증 중 오류: {str(e)}"
                ))
        
        return results
    
    def _validate_views(self) -> List[ValidationResult]:
        """뷰를 검증합니다."""
        results = []
        
        try:
            actual_views = self.get_view_list()
            actual_view_names = {view['name'] for view in actual_views}
            
            # 예상 뷰 검증
            for expected_view in self.expected_views:
                if expected_view in actual_view_names:
                    results.append(ValidationResult(
                        status=ValidationStatus.PASS,
                        message=f"뷰 '{expected_view}' 존재 확인"
                    ))
                else:
                    results.append(ValidationResult(
                        status=ValidationStatus.MISSING,
                        message=f"뷰 '{expected_view}' 누락"
                    ))
                    
        except Exception as e:
            results.append(ValidationResult(
                status=ValidationStatus.FAIL,
                message=f"뷰 검증 중 오류: {str(e)}"
            ))
        
        return results
    
    def _validate_json_columns(self) -> List[ValidationResult]:
        """JSON 컬럼을 검증합니다."""
        results = []
        
        # JSON 컬럼이 있는 테이블들
        json_tables = {
            'session_quizzes': ['quiz_options', 'quiz_evaluation_criteria']
        }
        
        for table_name, json_columns in json_tables.items():
            try:
                # 테이블이 존재하는지 확인
                table_columns = self.get_table_columns(table_name)
                actual_col_names = {col.name for col in table_columns}
                
                for json_col in json_columns:
                    if json_col in actual_col_names:
                        # JSON 컬럼 타입 확인
                        col_info = next((col for col in table_columns if col.name == json_col), None)
                        if col_info and 'json' in col_info.data_type.lower():
                            results.append(ValidationResult(
                                status=ValidationStatus.PASS,
                                message=f"테이블 '{table_name}' JSON 컬럼 '{json_col}' 타입 검증 통과"
                            ))
                        else:
                            results.append(ValidationResult(
                                status=ValidationStatus.FAIL,
                                message=f"테이블 '{table_name}' 컬럼 '{json_col}'이 JSON 타입이 아님"
                            ))
                    else:
                        results.append(ValidationResult(
                            status=ValidationStatus.MISSING,
                            message=f"테이블 '{table_name}' JSON 컬럼 '{json_col}' 누락"
                        ))
                        
            except Exception as e:
                results.append(ValidationResult(
                    status=ValidationStatus.FAIL,
                    message=f"테이블 '{table_name}' JSON 컬럼 검증 중 오류: {str(e)}"
                ))
        
        return results
    
    def get_table_list(self) -> List[TableInfo]:
        """데이터베이스의 테이블 목록을 조회합니다."""
        query = """
        SELECT 
            TABLE_NAME as name,
            ENGINE as engine,
            TABLE_COLLATION as collation,
            TABLE_ROWS as row_count,
            DATA_LENGTH as data_length,
            INDEX_LENGTH as index_length
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        
        results = self.client.execute_query(query, (self.database_name,))
        
        tables = []
        for row in results:
            # CHARACTER_SET 추출 (COLLATION에서)
            charset = row['collation'].split('_')[0] if row['collation'] else 'utf8mb4'
            
            tables.append(TableInfo(
                name=row['name'],
                engine=row['engine'] or 'InnoDB',
                charset=charset,
                collation=row['collation'] or 'utf8mb4_unicode_ci',
                row_count=row['row_count'] or 0,
                data_length=row['data_length'] or 0,
                index_length=row['index_length'] or 0
            ))
        
        return tables
    
    def get_table_columns(self, table_name: str) -> List[ColumnInfo]:
        """특정 테이블의 컬럼 정보를 조회합니다."""
        query = """
        SELECT 
            COLUMN_NAME as name,
            DATA_TYPE as data_type,
            IS_NULLABLE as is_nullable,
            COLUMN_DEFAULT as default_value,
            COLUMN_KEY as column_key,
            EXTRA as extra,
            CHARACTER_SET_NAME as character_set,
            COLLATION_NAME as collation
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        
        results = self.client.execute_query(query, (self.database_name, table_name))
        
        columns = []
        for row in results:
            columns.append(ColumnInfo(
                name=row['name'],
                data_type=row['data_type'],
                is_nullable=row['is_nullable'] == 'YES',
                default_value=row['default_value'],
                is_primary_key=row['column_key'] == 'PRI',
                is_unique=row['column_key'] in ('PRI', 'UNI'),
                is_auto_increment='auto_increment' in (row['extra'] or '').lower(),
                character_set=row['character_set'],
                collation=row['collation']
            ))
        
        return columns
    
    def get_table_indexes(self, table_name: str) -> List[IndexInfo]:
        """특정 테이블의 인덱스 정보를 조회합니다."""
        query = """
        SELECT 
            INDEX_NAME as name,
            COLUMN_NAME as column_name,
            NON_UNIQUE as non_unique,
            INDEX_TYPE as index_type
        FROM information_schema.STATISTICS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
        """
        
        results = self.client.execute_query(query, (self.database_name, table_name))
        
        # 인덱스별로 컬럼들을 그룹화
        index_dict = {}
        for row in results:
            index_name = row['name']
            if index_name not in index_dict:
                index_dict[index_name] = {
                    'columns': [],
                    'is_unique': row['non_unique'] == 0,
                    'index_type': row['index_type']
                }
            index_dict[index_name]['columns'].append(row['column_name'])
        
        indexes = []
        for index_name, index_data in index_dict.items():
            indexes.append(IndexInfo(
                name=index_name,
                table_name=table_name,
                columns=index_data['columns'],
                is_unique=index_data['is_unique'],
                index_type=index_data['index_type']
            ))
        
        return indexes
    
    def get_table_constraints(self, table_name: str) -> List[ConstraintInfo]:
        """특정 테이블의 제약조건 정보를 조회합니다."""
        constraints = []
        
        # 외래키 제약조건 조회
        fk_query = """
        SELECT 
            CONSTRAINT_NAME as name,
            COLUMN_NAME as column_name,
            REFERENCED_TABLE_NAME as referenced_table,
            REFERENCED_COLUMN_NAME as referenced_column
        FROM information_schema.KEY_COLUMN_USAGE 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s 
            AND REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY CONSTRAINT_NAME, ORDINAL_POSITION
        """
        
        fk_results = self.client.execute_query(fk_query, (self.database_name, table_name))
        
        # 외래키별로 그룹화
        fk_dict = {}
        for row in fk_results:
            constraint_name = row['name']
            if constraint_name not in fk_dict:
                fk_dict[constraint_name] = {
                    'columns': [],
                    'referenced_table': row['referenced_table'],
                    'referenced_columns': []
                }
            fk_dict[constraint_name]['columns'].append(row['column_name'])
            fk_dict[constraint_name]['referenced_columns'].append(row['referenced_column'])
        
        for constraint_name, fk_data in fk_dict.items():
            constraints.append(ConstraintInfo(
                name=constraint_name,
                table_name=table_name,
                constraint_type='FOREIGN KEY',
                column_names=fk_data['columns'],
                referenced_table=fk_data['referenced_table'],
                referenced_columns=fk_data['referenced_columns']
            ))
        
        # CHECK 제약조건 조회 (MySQL 8.0+)
        try:
            check_query = """
            SELECT 
                CONSTRAINT_NAME as name,
                CHECK_CLAUSE as check_clause
            FROM information_schema.CHECK_CONSTRAINTS 
            WHERE CONSTRAINT_SCHEMA = %s 
                AND CONSTRAINT_NAME LIKE CONCAT(%s, '%')
            """
            
            check_results = self.client.execute_query(check_query, (self.database_name, table_name))
            
            for row in check_results:
                constraints.append(ConstraintInfo(
                    name=row['name'],
                    table_name=table_name,
                    constraint_type='CHECK',
                    column_names=[],  # CHECK 제약조건은 컬럼 정보를 별도로 파싱해야 함
                    check_clause=row['check_clause']
                ))
        except Exception:
            # MySQL 버전이 낮거나 CHECK 제약조건이 지원되지 않는 경우
            pass
        
        return constraints
    
    def get_view_list(self) -> List[Dict[str, Any]]:
        """데이터베이스의 뷰 목록을 조회합니다."""
        query = """
        SELECT 
            TABLE_NAME as name,
            VIEW_DEFINITION as definition
        FROM information_schema.VIEWS 
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_NAME
        """
        
        results = self.client.execute_query(query, (self.database_name,))
        return [{'name': row['name'], 'definition': row['definition']} for row in results]
    
    def _get_expected_columns(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """예상 컬럼 정의를 반환합니다."""
        return {
            'users': {
                'user_id': {'type': 'int', 'nullable': False, 'auto_increment': True},
                'login_id': {'type': 'varchar', 'nullable': False},
                'username': {'type': 'varchar', 'nullable': False},
                'email': {'type': 'varchar', 'nullable': False},
                'password_hash': {'type': 'varchar', 'nullable': False},
                'user_type': {'type': 'varchar', 'nullable': False},
                'diagnosis_completed': {'type': 'tinyint', 'nullable': True},
                'created_at': {'type': 'timestamp', 'nullable': True},
                'updated_at': {'type': 'timestamp', 'nullable': True}
            },
            'user_progress': {
                'progress_id': {'type': 'int', 'nullable': False, 'auto_increment': True},
                'user_id': {'type': 'int', 'nullable': False},
                'current_chapter': {'type': 'int', 'nullable': False},
                'current_section': {'type': 'int', 'nullable': False},
                'last_study_date': {'type': 'date', 'nullable': True},
                'created_at': {'type': 'timestamp', 'nullable': True},
                'updated_at': {'type': 'timestamp', 'nullable': True}
            },
            'learning_sessions': {
                'session_id': {'type': 'int', 'nullable': False, 'auto_increment': True},
                'user_id': {'type': 'int', 'nullable': False},
                'chapter_number': {'type': 'int', 'nullable': False},
                'section_number': {'type': 'int', 'nullable': False},
                'session_start_time': {'type': 'timestamp', 'nullable': False},
                'session_end_time': {'type': 'timestamp', 'nullable': False},
                'study_duration_minutes': {'type': 'int', 'nullable': True},
                'retry_decision_result': {'type': 'varchar', 'nullable': True},
                'created_at': {'type': 'timestamp', 'nullable': True}
            },
            'session_quizzes': {
                'quiz_id': {'type': 'int', 'nullable': False, 'auto_increment': True},
                'session_id': {'type': 'int', 'nullable': False},
                'quiz_type': {'type': 'varchar', 'nullable': False},
                'quiz_content': {'type': 'text', 'nullable': False},
                'quiz_options': {'type': 'json', 'nullable': True},
                'quiz_evaluation_criteria': {'type': 'json', 'nullable': True},
                'user_answer': {'type': 'text', 'nullable': True},
                'multiple_answer_correct': {'type': 'tinyint', 'nullable': True},
                'subjective_answer_score': {'type': 'int', 'nullable': True},
                'created_at': {'type': 'timestamp', 'nullable': True}
            }
        }
    
    def _get_expected_indexes(self) -> Dict[str, List[Dict[str, Any]]]:
        """예상 인덱스 정의를 반환합니다."""
        return {
            'users': [
                {'name': 'idx_login_id', 'columns': ['login_id']},
                {'name': 'idx_email', 'columns': ['email']},
                {'name': 'idx_user_type', 'columns': ['user_type']}
            ],
            'user_progress': [
                {'name': 'idx_current_chapter', 'columns': ['current_chapter']},
                {'name': 'idx_current_section', 'columns': ['current_section']}
            ],
            'learning_sessions': [
                {'name': 'idx_user_id', 'columns': ['user_id']},
                {'name': 'idx_chapter_section', 'columns': ['chapter_number', 'section_number']},
                {'name': 'idx_user_chapter_section', 'columns': ['user_id', 'chapter_number', 'section_number']}
            ],
            'session_quizzes': [
                {'name': 'idx_session_id', 'columns': ['session_id']},
                {'name': 'idx_quiz_type', 'columns': ['quiz_type']}
            ]
        }
    
    def _get_expected_constraints(self) -> Dict[str, List[Dict[str, Any]]]:
        """예상 제약조건 정의를 반환합니다."""
        return {
            'user_auth_tokens': [
                {'name': 'user_auth_tokens_ibfk_1', 'type': 'FOREIGN KEY', 'columns': ['user_id']}
            ],
            'user_progress': [
                {'name': 'user_progress_ibfk_1', 'type': 'FOREIGN KEY', 'columns': ['user_id']}
            ],
            'user_statistics': [
                {'name': 'user_statistics_ibfk_1', 'type': 'FOREIGN KEY', 'columns': ['user_id']}
            ],
            'learning_sessions': [
                {'name': 'learning_sessions_ibfk_1', 'type': 'FOREIGN KEY', 'columns': ['user_id']}
            ],
            'session_conversations': [
                {'name': 'session_conversations_ibfk_1', 'type': 'FOREIGN KEY', 'columns': ['session_id']}
            ],
            'session_quizzes': [
                {'name': 'session_quizzes_ibfk_1', 'type': 'FOREIGN KEY', 'columns': ['session_id']}
            ]
        }
    
    def _normalize_column_type(self, column_type: str) -> str:
        """컬럼 타입을 정규화합니다."""
        # 괄호와 크기 정보 제거
        normalized = column_type.lower().split('(')[0]
        
        # 타입 매핑
        type_mapping = {
            'tinyint': 'tinyint',
            'boolean': 'tinyint',
            'bool': 'tinyint',
            'int': 'int',
            'integer': 'int',
            'varchar': 'varchar',
            'text': 'text',
            'timestamp': 'timestamp',
            'date': 'date',
            'json': 'json',
            'decimal': 'decimal'
        }
        
        return type_mapping.get(normalized, normalized)
    
    def generate_validation_report(self, results: Dict[str, List[ValidationResult]]) -> str:
        """검증 결과를 보고서 형태로 생성합니다."""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("데이터베이스 스키마 검증 보고서")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # 전체 요약
        total_pass = sum(len([r for r in category_results if r.status == ValidationStatus.PASS]) 
                        for category_results in results.values())
        total_fail = sum(len([r for r in category_results if r.status == ValidationStatus.FAIL]) 
                        for category_results in results.values())
        total_warning = sum(len([r for r in category_results if r.status == ValidationStatus.WARNING]) 
                           for category_results in results.values())
        total_missing = sum(len([r for r in category_results if r.status == ValidationStatus.MISSING]) 
                           for category_results in results.values())
        
        report_lines.append(f"전체 요약:")
        report_lines.append(f"  ✅ 통과: {total_pass}")
        report_lines.append(f"  ❌ 실패: {total_fail}")
        report_lines.append(f"  ⚠️  경고: {total_warning}")
        report_lines.append(f"  ❓ 누락: {total_missing}")
        report_lines.append("")
        
        # 카테고리별 상세 결과
        for category, category_results in results.items():
            if not category_results:
                continue
                
            report_lines.append(f"[{category.upper()}]")
            report_lines.append("-" * 40)
            
            for result in category_results:
                status_icon = {
                    ValidationStatus.PASS: "✅",
                    ValidationStatus.FAIL: "❌",
                    ValidationStatus.WARNING: "⚠️",
                    ValidationStatus.MISSING: "❓"
                }[result.status]
                
                report_lines.append(f"{status_icon} {result.message}")
                
                if result.details:
                    for key, value in result.details.items():
                        report_lines.append(f"    {key}: {value}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def generate_json_report(self, results: Dict[str, List[ValidationResult]]) -> Dict[str, Any]:
        """검증 결과를 JSON 형태로 생성합니다."""
        # 전체 요약 계산
        total_pass = sum(len([r for r in category_results if r.status == ValidationStatus.PASS]) 
                        for category_results in results.values())
        total_fail = sum(len([r for r in category_results if r.status == ValidationStatus.FAIL]) 
                        for category_results in results.values())
        total_warning = sum(len([r for r in category_results if r.status == ValidationStatus.WARNING]) 
                           for category_results in results.values())
        total_missing = sum(len([r for r in category_results if r.status == ValidationStatus.MISSING]) 
                           for category_results in results.values())
        
        # JSON 보고서 구조
        json_report = {
            "summary": {
                "total_pass": total_pass,
                "total_fail": total_fail,
                "total_warning": total_warning,
                "total_missing": total_missing,
                "total_checks": total_pass + total_fail + total_warning + total_missing,
                "overall_status": "PASS" if total_fail == 0 and total_missing == 0 else "FAIL"
            },
            "categories": {}
        }
        
        # 카테고리별 결과
        for category, category_results in results.items():
            category_data = {
                "results": [],
                "summary": {
                    "pass": len([r for r in category_results if r.status == ValidationStatus.PASS]),
                    "fail": len([r for r in category_results if r.status == ValidationStatus.FAIL]),
                    "warning": len([r for r in category_results if r.status == ValidationStatus.WARNING]),
                    "missing": len([r for r in category_results if r.status == ValidationStatus.MISSING])
                }
            }
            
            for result in category_results:
                result_data = {
                    "status": result.status.value,
                    "message": result.message,
                    "details": result.details
                }
                category_data["results"].append(result_data)
            
            json_report["categories"][category] = category_data
        
        return json_report
    
    def get_schema_summary(self) -> Dict[str, Any]:
        """현재 스키마의 요약 정보를 반환합니다."""
        try:
            summary = {
                "database_name": self.database_name,
                "tables": [],
                "views": [],
                "total_tables": 0,
                "total_views": 0,
                "total_indexes": 0,
                "total_constraints": 0
            }
            
            # 테이블 정보
            tables = self.get_table_list()
            summary["total_tables"] = len(tables)
            
            for table in tables:
                table_info = {
                    "name": table.name,
                    "engine": table.engine,
                    "charset": table.charset,
                    "row_count": table.row_count,
                    "data_size_mb": round(table.data_length / 1024 / 1024, 2),
                    "index_size_mb": round(table.index_length / 1024 / 1024, 2)
                }
                
                # 컬럼 수 추가
                columns = self.get_table_columns(table.name)
                table_info["column_count"] = len(columns)
                
                # 인덱스 수 추가
                indexes = self.get_table_indexes(table.name)
                table_info["index_count"] = len(indexes)
                summary["total_indexes"] += len(indexes)
                
                # 제약조건 수 추가
                constraints = self.get_table_constraints(table.name)
                table_info["constraint_count"] = len(constraints)
                summary["total_constraints"] += len(constraints)
                
                summary["tables"].append(table_info)
            
            # 뷰 정보
            views = self.get_view_list()
            summary["total_views"] = len(views)
            summary["views"] = [{"name": view["name"]} for view in views]
            
            return summary
            
        except Exception as e:
            return {"error": f"스키마 요약 생성 중 오류: {str(e)}"}
    
    def check_schema_health(self) -> Dict[str, Any]:
        """스키마 상태를 간단히 확인합니다."""
        try:
            health_check = {
                "status": "healthy",
                "issues": [],
                "recommendations": []
            }
            
            # 기본 연결 확인
            if not self.client.check_connection():
                health_check["status"] = "unhealthy"
                health_check["issues"].append("데이터베이스 연결 실패")
                return health_check
            
            # 필수 테이블 확인
            tables = self.get_table_list()
            table_names = {table.name for table in tables}
            
            missing_tables = self.expected_tables - table_names
            if missing_tables:
                health_check["status"] = "degraded"
                health_check["issues"].append(f"누락된 테이블: {', '.join(missing_tables)}")
                health_check["recommendations"].append("누락된 테이블을 생성하세요")
            
            # 큰 테이블 확인 (100MB 이상)
            large_tables = [table for table in tables if table.data_length > 100 * 1024 * 1024]
            if large_tables:
                health_check["recommendations"].append(
                    f"큰 테이블 발견: {', '.join([t.name for t in large_tables])} - 성능 모니터링 권장"
                )
            
            # 인덱스가 없는 테이블 확인
            for table in tables:
                try:
                    indexes = self.get_table_indexes(table.name)
                    if len(indexes) <= 1:  # PRIMARY KEY만 있는 경우
                        health_check["recommendations"].append(
                            f"테이블 '{table.name}'에 추가 인덱스 고려"
                        )
                except Exception:
                    # 인덱스 조회 실패 시 무시
                    pass
            
            return health_check
            
        except Exception as e:
            return {
                "status": "error",
                "issues": [f"상태 확인 중 오류: {str(e)}"],
                "recommendations": ["데이터베이스 연결 및 권한을 확인하세요"]
            }