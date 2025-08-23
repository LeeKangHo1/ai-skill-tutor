# backend/check_db_schema.py
"""
현재 데이터베이스 스키마 확인 스크립트
user_statistics 테이블의 실제 컬럼 구조를 확인합니다.
"""

import os
import sys
from dotenv import load_dotenv
import pymysql

# 환경변수 로드
load_dotenv()

def check_user_statistics_schema():
    """user_statistics 테이블의 스키마를 확인합니다."""
    try:
        # 데이터베이스 연결
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'ai_skill_tutor'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # user_statistics 테이블 스키마 조회
            cursor.execute("DESCRIBE user_statistics")
            columns = cursor.fetchall()
            
            print("=== user_statistics 테이블 스키마 ===")
            for column in columns:
                print(f"컬럼명: {column['Field']}")
                print(f"  타입: {column['Type']}")
                print(f"  NULL 허용: {column['Null']}")
                print(f"  키: {column['Key']}")
                print(f"  기본값: {column['Default']}")
                print(f"  추가정보: {column['Extra']}")
                print("-" * 40)
            
            # learning_sessions 테이블 스키마도 확인
            print("\n=== learning_sessions 테이블 스키마 ===")
            cursor.execute("DESCRIBE learning_sessions")
            columns = cursor.fetchall()
            
            for column in columns:
                if 'duration' in column['Field'].lower():
                    print(f"컬럼명: {column['Field']}")
                    print(f"  타입: {column['Type']}")
                    print(f"  NULL 허용: {column['Null']}")
                    print(f"  키: {column['Key']}")
                    print(f"  기본값: {column['Default']}")
                    print(f"  추가정보: {column['Extra']}")
                    print("-" * 40)
            
            # 샘플 데이터 확인
            print("\n=== user_statistics 샘플 데이터 ===")
            cursor.execute("SELECT * FROM user_statistics LIMIT 3")
            sample_data = cursor.fetchall()
            
            for row in sample_data:
                print(f"사용자 ID: {row.get('user_id')}")
                print(f"총 세션 수: {row.get('total_study_sessions')}")
                
                # 시간 관련 컬럼들 확인
                time_columns = [col for col in row.keys() if 'time' in col.lower() or 'duration' in col.lower()]
                for col in time_columns:
                    print(f"{col}: {row.get(col)}")
                print("-" * 40)
                
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()
    
    return True

if __name__ == "__main__":
    check_user_statistics_schema()