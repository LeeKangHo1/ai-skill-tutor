# backend/test_db_connection.py
# 데이터베이스 연결 테스트

import sys
import os

# 백엔드 앱 경로를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.utils.database.connection import fetch_one, execute_query

def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        print("🔍 데이터베이스 연결 테스트 시작...")
        
        # 기본 연결 테스트
        result = fetch_one("SELECT 1 as test")
        print(f"✅ 기본 연결 성공: {result}")
        
        # 데이터베이스 목록 확인
        from app.utils.database.connection import fetch_all
        databases = fetch_all("SHOW DATABASES")
        print(f"📋 사용 가능한 데이터베이스: {[db['Database'] for db in databases]}")
        
        # 현재 데이터베이스 확인
        current_db = fetch_one("SELECT DATABASE() as current_db")
        print(f"🎯 현재 데이터베이스: {current_db}")
        
        # 테이블 목록 확인
        tables = fetch_all("SHOW TABLES")
        if tables:
            print(f"📊 테이블 목록: {[list(table.values())[0] for table in tables]}")
        else:
            print("⚠️ 테이블이 없습니다.")
        
        # users 테이블 구조 확인
        try:
            users_structure = fetch_all("DESCRIBE users")
            print("👥 users 테이블 구조:")
            for column in users_structure:
                print(f"  - {column['Field']}: {column['Type']}")
        except Exception as e:
            print(f"❌ users 테이블 없음: {e}")
        
        print("✅ 데이터베이스 연결 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print("💡 확인사항:")
        print("  1. MySQL 서버가 실행 중인지 확인")
        print("  2. .env 파일의 데이터베이스 설정 확인")
        print("  3. 데이터베이스와 사용자 권한 확인")

if __name__ == "__main__":
    test_database_connection()