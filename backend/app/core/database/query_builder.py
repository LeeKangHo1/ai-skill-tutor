# backend/app/core/database/query_builder.py
"""
SQL 쿼리 빌더 모듈
기본 SQL 생성, 파라미터 바인딩, JSON 컬럼 지원을 제공합니다.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import json


class QueryBuilder:
    """SQL 쿼리 빌더 클래스"""
    
    def __init__(self):
        """쿼리 빌더 초기화"""
        self.reset()
    
    def reset(self) -> 'QueryBuilder':
        """쿼리 빌더 상태를 초기화합니다."""
        self._select_fields = []
        self._from_table = ""
        self._joins = []
        self._where_conditions = []
        self._order_by = []
        self._limit_value = None
        self._offset_value = None
        self._params = []
        return self
    
    def select(self, fields: Union[str, List[str]]) -> 'QueryBuilder':
        """
        SELECT 필드를 설정합니다.
        
        Args:
            fields: 선택할 필드명 또는 필드명 리스트
        """
        if isinstance(fields, str):
            self._select_fields = [fields]
        else:
            self._select_fields = fields
        return self
    
    def from_table(self, table: str) -> 'QueryBuilder':
        """
        FROM 테이블을 설정합니다.
        
        Args:
            table: 테이블명
        """
        self._from_table = table
        return self
    
    def join(self, table: str, on_condition: str, join_type: str = "INNER") -> 'QueryBuilder':
        """
        JOIN 절을 추가합니다.
        
        Args:
            table: 조인할 테이블명
            on_condition: 조인 조건
            join_type: 조인 타입 (INNER, LEFT, RIGHT, FULL)
        """
        self._joins.append(f"{join_type} JOIN {table} ON {on_condition}")
        return self
    
    def where(self, condition: str, value: Any = None) -> 'QueryBuilder':
        """
        WHERE 조건을 추가합니다.
        
        Args:
            condition: WHERE 조건 (파라미터 바인딩 시 %s 사용)
            value: 바인딩할 값
        """
        self._where_conditions.append(condition)
        if value is not None:
            self._params.append(value)
        return self
    
    def where_json(self, column: str, json_path: str, value: Any) -> 'QueryBuilder':
        """
        JSON 컬럼에 대한 WHERE 조건을 추가합니다.
        
        Args:
            column: JSON 컬럼명
            json_path: JSON 경로 (예: '$.key')
            value: 비교할 값
        """
        condition = f"JSON_EXTRACT({column}, %s) = %s"
        self._where_conditions.append(condition)
        self._params.extend([json_path, value])
        return self
    
    def where_json_contains(self, column: str, value: Any) -> 'QueryBuilder':
        """
        JSON 컬럼이 특정 값을 포함하는지 확인하는 WHERE 조건을 추가합니다.
        
        Args:
            column: JSON 컬럼명
            value: 포함되어야 할 값
        """
        condition = f"JSON_CONTAINS({column}, %s)"
        self._where_conditions.append(condition)
        self._params.append(json.dumps(value))
        return self
    
    def order_by(self, field: str, direction: str = "ASC") -> 'QueryBuilder':
        """
        ORDER BY 절을 추가합니다.
        
        Args:
            field: 정렬할 필드명
            direction: 정렬 방향 (ASC, DESC)
        """
        self._order_by.append(f"{field} {direction}")
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """
        LIMIT 절을 설정합니다.
        
        Args:
            count: 제한할 행 수
        """
        self._limit_value = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """
        OFFSET 절을 설정합니다.
        
        Args:
            count: 건너뛸 행 수
        """
        self._offset_value = count
        return self
    
    def build_select(self) -> Tuple[str, List[Any]]:
        """
        SELECT 쿼리를 빌드합니다.
        
        Returns:
            Tuple[str, List[Any]]: (쿼리 문자열, 파라미터 리스트)
        """
        if not self._select_fields or not self._from_table:
            raise ValueError("SELECT 필드와 FROM 테이블이 필요합니다.")
        
        # SELECT 절
        select_clause = "SELECT " + ", ".join(self._select_fields)
        
        # FROM 절
        from_clause = f"FROM {self._from_table}"
        
        # JOIN 절
        join_clause = " ".join(self._joins) if self._joins else ""
        
        # WHERE 절
        where_clause = ""
        if self._where_conditions:
            where_clause = "WHERE " + " AND ".join(self._where_conditions)
        
        # ORDER BY 절
        order_clause = ""
        if self._order_by:
            order_clause = "ORDER BY " + ", ".join(self._order_by)
        
        # LIMIT 절
        limit_clause = ""
        if self._limit_value is not None:
            limit_clause = f"LIMIT {self._limit_value}"
            if self._offset_value is not None:
                limit_clause += f" OFFSET {self._offset_value}"
        
        # 쿼리 조합
        query_parts = [select_clause, from_clause]
        if join_clause:
            query_parts.append(join_clause)
        if where_clause:
            query_parts.append(where_clause)
        if order_clause:
            query_parts.append(order_clause)
        if limit_clause:
            query_parts.append(limit_clause)
        
        query = " ".join(query_parts)
        return query, self._params.copy()
    
    def build_insert(self, table: str, data: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        INSERT 쿼리를 빌드합니다.
        
        Args:
            table: 테이블명
            data: 삽입할 데이터 딕셔너리
            
        Returns:
            Tuple[str, List[Any]]: (쿼리 문자열, 파라미터 리스트)
        """
        if not data:
            raise ValueError("삽입할 데이터가 필요합니다.")
        
        columns = list(data.keys())
        values = list(data.values())
        
        # JSON 데이터 처리
        processed_values = []
        for value in values:
            if isinstance(value, (dict, list)):
                processed_values.append(json.dumps(value, ensure_ascii=False))
            else:
                processed_values.append(value)
        
        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join(columns)
        
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        return query, processed_values
    
    def build_update(self, table: str, data: Dict[str, Any], where_conditions: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        UPDATE 쿼리를 빌드합니다.
        
        Args:
            table: 테이블명
            data: 업데이트할 데이터 딕셔너리
            where_conditions: WHERE 조건 딕셔너리
            
        Returns:
            Tuple[str, List[Any]]: (쿼리 문자열, 파라미터 리스트)
        """
        if not data:
            raise ValueError("업데이트할 데이터가 필요합니다.")
        if not where_conditions:
            raise ValueError("WHERE 조건이 필요합니다.")
        
        # SET 절 생성
        set_clauses = []
        params = []
        
        for column, value in data.items():
            set_clauses.append(f"{column} = %s")
            if isinstance(value, (dict, list)):
                params.append(json.dumps(value, ensure_ascii=False))
            else:
                params.append(value)
        
        # WHERE 절 생성
        where_clauses = []
        for column, value in where_conditions.items():
            where_clauses.append(f"{column} = %s")
            params.append(value)
        
        set_clause = ", ".join(set_clauses)
        where_clause = " AND ".join(where_clauses)
        
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        return query, params
    
    def build_delete(self, table: str, where_conditions: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        DELETE 쿼리를 빌드합니다.
        
        Args:
            table: 테이블명
            where_conditions: WHERE 조건 딕셔너리
            
        Returns:
            Tuple[str, List[Any]]: (쿼리 문자열, 파라미터 리스트)
        """
        if not where_conditions:
            raise ValueError("WHERE 조건이 필요합니다.")
        
        where_clauses = []
        params = []
        
        for column, value in where_conditions.items():
            where_clauses.append(f"{column} = %s")
            params.append(value)
        
        where_clause = " AND ".join(where_clauses)
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return query, params


class JSONQueryHelper:
    """JSON 컬럼 쿼리를 위한 헬퍼 클래스"""
    
    @staticmethod
    def extract_json_value(column: str, json_path: str) -> str:
        """
        JSON 값을 추출하는 SQL 표현식을 생성합니다.
        
        Args:
            column: JSON 컬럼명
            json_path: JSON 경로 (예: '$.key')
            
        Returns:
            str: JSON_EXTRACT SQL 표현식
        """
        return f"JSON_EXTRACT({column}, '{json_path}')"
    
    @staticmethod
    def json_contains_condition(column: str, value: Any) -> Tuple[str, str]:
        """
        JSON_CONTAINS 조건을 생성합니다.
        
        Args:
            column: JSON 컬럼명
            value: 포함되어야 할 값
            
        Returns:
            Tuple[str, str]: (조건 문자열, JSON 문자열 값)
        """
        condition = f"JSON_CONTAINS({column}, %s)"
        json_value = json.dumps(value, ensure_ascii=False)
        return condition, json_value
    
    @staticmethod
    def json_array_contains_condition(column: str, value: Any) -> Tuple[str, str]:
        """
        JSON 배열에 특정 값이 포함되어 있는지 확인하는 조건을 생성합니다.
        
        Args:
            column: JSON 컬럼명
            value: 포함되어야 할 값
            
        Returns:
            Tuple[str, str]: (조건 문자열, JSON 문자열 값)
        """
        condition = f"JSON_CONTAINS({column}, %s, '$')"
        json_value = json.dumps([value], ensure_ascii=False)
        return condition, json_value