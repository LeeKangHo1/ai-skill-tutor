# backend/create_schema.py
# 데이터베이스 스키마 생성 스크립트

import os
from app.config.db_config import get_db_connection

def create_database_schema():
    """데이터베이스 스키마 생성"""
    try:
        # schema.sql 파일 읽기
        with open('migrations/schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # 주석과 빈 줄 제거
        lines = []
        for line in schema_sql.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('--'):
                lines.append(line)
        
        # 다시 합치고 세미콜론으로 분리
        clean_sql = ' '.join(lines)
        sql_statements = [stmt.strip() for stmt in clean_sql.split(';') if stmt.strip()]
        
        print(f"총 {len(sql_statements)}개의 SQL 문을 실행합니다.")
        
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                for i, sql in enumerate(sql_statements, 1):
                    try:
                        print(f"\n[{i}] 실행 중: {sql[:100]}...")
                        cursor.execute(sql)
                        print(f"✅ 성공")
                    except Exception as e:
                        print(f"⚠️ 실패: {e}")
                        # CREATE TABLE 실패는 중요하므로 상세 출력
                        if 'CREATE TABLE' in sql.upper():
                            print(f"실패한 SQL: {sql[:500]}...")
        
        # 테이블 생성 확인
        print("\n=== 테이블 생성 확인 ===")
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"생성된 테이블: {[table['Tables_in_mas_ai_tutor'] for table in tables]}")
        
        print("✅ 데이터베이스 스키마 생성 완료!")
        
    except Exception as e:
        print(f"❌ 스키마 생성 실패: {e}")

if __name__ == '__main__':
    create_database_schema()