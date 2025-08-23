# backend/fix_user_statistics.py
"""
user_statistics 테이블의 total_study_time_seconds를 
learning_sessions 테이블의 실제 데이터를 기반으로 수정하는 스크립트
"""

import os
import sys
from dotenv import load_dotenv
import pymysql

# 환경변수 로드
load_dotenv()

def fix_user_statistics():
    """user_statistics의 total_study_time_seconds를 실제 데이터로 수정합니다."""
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
            # 각 사용자별 실제 학습 시간 계산
            cursor.execute("""
                SELECT user_id, 
                       SUM(study_duration_seconds) as total_seconds
                FROM learning_sessions 
                WHERE study_duration_seconds IS NOT NULL
                GROUP BY user_id
            """)
            
            user_totals = cursor.fetchall()
            
            print("=== user_statistics 수정 작업 시작 ===")
            
            for user_total in user_totals:
                user_id = user_total['user_id']
                total_seconds = user_total['total_seconds'] or 0
                
                print(f"사용자 ID {user_id}: {total_seconds}초로 업데이트")
                
                # user_statistics 업데이트
                cursor.execute("""
                    UPDATE user_statistics 
                    SET total_study_time_seconds = %s,
                        updated_at = NOW()
                    WHERE user_id = %s
                """, (total_seconds, user_id))
            
            # 변경사항 커밋
            connection.commit()
            
            print(f"총 {len(user_totals)}명의 사용자 통계를 업데이트했습니다.")
            
            # 수정 결과 확인
            print("\n=== 수정 결과 확인 ===")
            cursor.execute("""
                SELECT 
                    us.user_id,
                    us.total_study_time_seconds as stats_seconds,
                    COALESCE(ls_agg.actual_seconds, 0) as actual_seconds
                FROM user_statistics us
                LEFT JOIN (
                    SELECT user_id, 
                           SUM(study_duration_seconds) as actual_seconds
                    FROM learning_sessions 
                    WHERE study_duration_seconds IS NOT NULL
                    GROUP BY user_id
                ) ls_agg ON us.user_id = ls_agg.user_id
                WHERE us.total_study_sessions > 0
                ORDER BY us.user_id
            """)
            
            results = cursor.fetchall()
            for result in results:
                user_id = result['user_id']
                stats_seconds = result['stats_seconds']
                actual_seconds = result['actual_seconds']
                
                match = stats_seconds == actual_seconds
                status = "✅ 일치" if match else "❌ 불일치"
                
                print(f"사용자 ID {user_id}: 통계={stats_seconds}초, 실제={actual_seconds}초 {status}")
                
    except Exception as e:
        print(f"오류 발생: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()
    
    return True

if __name__ == "__main__":
    print("user_statistics 테이블의 total_study_time_seconds를 수정합니다.")
    print("이 작업은 learning_sessions 테이블의 실제 데이터를 기반으로 합니다.")
    
    confirm = input("계속하시겠습니까? (y/N): ")
    if confirm.lower() == 'y':
        fix_user_statistics()
    else:
        print("작업이 취소되었습니다.")