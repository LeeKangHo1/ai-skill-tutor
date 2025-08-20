# backend/app/core/database/migration_runner.py
"""
⚠️ DEPRECATED - 이 모듈은 더 이상 사용되지 않습니다.
현재 프로젝트에서는 별도의 마이그레이션 도구를 사용하거나 수동으로 관리합니다.

데이터베이스 마이그레이션 실행기 모듈
SQL 마이그레이션 파일을 실행하고 관리합니다.

⚠️ 사용 중단됨: 2025-08-20
대체 방법: 수동 SQL 실행 또는 별도 마이그레이션 도구 사용
"""

import os
import glob
from typing import List, Dict, Any
from .mysql_client import MySQLClient

class MigrationRunner:
    """데이터베이스 마이그레이션을 실행하는 클래스"""
    
    def __init__(self, mysql_client: MySQLClient):
        """
        마이그레이션 실행기 초기화
        
        Args:
            mysql_client (MySQLClient): MySQL 클라이언트 인스턴스
        """
        self.mysql_client = mysql_client
        self.migrations_dir = os.path.join(os.path.dirname(__file__), '../../../migrations')
    
    def get_migration_files(self) -> List[str]:
        """
        마이그레이션 파일 목록을 가져옵니다.
        
        Returns:
            List[str]: 정렬된 마이그레이션 파일 경로 목록
        """
        pattern = os.path.join(self.migrations_dir, '*.sql')
        files = glob.glob(pattern)
        return sorted(files)
    
    def create_migration_table(self) -> None:
        """마이그레이션 기록을 위한 테이블을 생성합니다."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS migrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL UNIQUE,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        self.mysql_client.execute_update(create_table_query)
    
    def get_executed_migrations(self) -> List[str]:
        """
        이미 실행된 마이그레이션 목록을 가져옵니다.
        
        Returns:
            List[str]: 실행된 마이그레이션 파일명 목록
        """
        query = "SELECT filename FROM migrations ORDER BY executed_at"
        try:
            results = self.mysql_client.execute_query(query)
            return [row['filename'] for row in results]
        except Exception:
            # migrations 테이블이 없는 경우
            return []
    
    def execute_migration(self, file_path: str) -> bool:
        """
        단일 마이그레이션 파일을 실행합니다.
        
        Args:
            file_path (str): 마이그레이션 파일 경로
            
        Returns:
            bool: 실행 성공 여부
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # 세미콜론으로 구분된 여러 쿼리 실행
            queries = [q.strip() for q in sql_content.split(';') if q.strip()]
            
            for query in queries:
                if query:
                    self.mysql_client.execute_update(query)
            
            # 마이그레이션 실행 기록
            filename = os.path.basename(file_path)
            record_query = "INSERT INTO migrations (filename) VALUES (%s)"
            self.mysql_client.execute_update(record_query, (filename,))
            
            return True
        except Exception as e:
            print(f"마이그레이션 실행 실패 {file_path}: {e}")
            return False
    
    def run_migrations(self) -> Dict[str, Any]:
        """
        모든 미실행 마이그레이션을 실행합니다.
        
        Returns:
            Dict[str, Any]: 실행 결과 정보
        """
        self.create_migration_table()
        
        migration_files = self.get_migration_files()
        executed_migrations = self.get_executed_migrations()
        
        pending_migrations = []
        for file_path in migration_files:
            filename = os.path.basename(file_path)
            if filename not in executed_migrations:
                pending_migrations.append(file_path)
        
        executed_count = 0
        failed_migrations = []
        
        for file_path in pending_migrations:
            if self.execute_migration(file_path):
                executed_count += 1
                print(f"마이그레이션 실행 완료: {os.path.basename(file_path)}")
            else:
                failed_migrations.append(os.path.basename(file_path))
        
        return {
            'total_migrations': len(migration_files),
            'executed_count': executed_count,
            'failed_migrations': failed_migrations,
            'pending_count': len(pending_migrations)
        }