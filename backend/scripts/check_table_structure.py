# backend/scripts/check_table_structure.py
# 테이블 구조 확인 스크립트

import os
import sys

# 프로젝트 루트 경로를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

from app.config.db_config import get_db_connection

def check_table_structure(table_name: str):
    """테이블 구조 확인"""
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{table_name}`")
                columns = cursor.fetchall()
                
                print(f"\n=== {table_name} 테이블 구조 ===")
                for column in columns:
                    field = column['Field']
                    type_info = column['Type']
                    null = column['Null']
                    key = column['Key']
                    default = column['Default']
                    extra = column['Extra']
                    
                    print(f"  {field}: {type_info} (NULL: {null}, KEY: {key}, DEFAULT: {default}, EXTRA: {extra})")
                    
    except Exception as e:
        print(f"❌ {table_name} 테이블 구조 확인 실패: {e}")

def main():
    """메인 함수"""
    tables_to_check = ['learning_sessions', 'user_statistics']
    
    print("=== 테이블 구조 확인 ===")
    
    for table_name in tables_to_check:
        check_table_structure(table_name)

if __name__ == "__main__":
    main()