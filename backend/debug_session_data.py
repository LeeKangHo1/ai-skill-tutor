# backend/debug_session_data.py
"""
세션 데이터 저장 과정 디버깅 스크립트
learning_sessions에서 user_statistics로 데이터가 제대로 전달되는지 확인합니다.
"""

import os
import sys
from dotenv import load_dotenv
import pymysql

# 환경변수 로드
load_dotenv()

def debug_session_data():
    """세션 데이터와 통계 데이터의 연관성을 확인합니다."""
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
            # learning_sessions에서 최근 세션들의 study_duration_seconds 확인
            print("=== learning_sessions 최근 데이터 ===")
            cursor.execute("""
                SELECT user_id, session_id, chapter_number, section_number, 
                       study_duration_seconds, session_start_time, session_end_time,
                       retry_decision_result
                FROM learning_sessions 
                ORDER BY session_id DESC 
                LIMIT 10
            """)
            
            sessions = cursor.fetchall()
            for session in sessions:
                print(f"세션 ID: {session['session_id']}")
                print(f"사용자 ID: {session['user_id']}")
                print(f"챕터.섹션: {session['chapter_number']}.{session['section_number']}")
                print(f"학습 시간(초): {session['study_duration_seconds']}")
                print(f"결정 결과: {session['retry_decision_result']}")
                print(f"시작 시간: {session['session_start_time']}")
                print(f"종료 시간: {session['session_end_time']}")
                
                # 시간 계산 검증
                if session['session_start_time'] and session['session_end_time']:
                    calculated_seconds = (session['session_end_time'] - session['session_start_time']).total_seconds()
                    print(f"계산된 시간(초): {calculated_seconds}")
                    print(f"저장된 시간과 일치: {abs(calculated_seconds - (session['study_duration_seconds'] or 0)) < 5}")
                
                print("-" * 50)
            
            # 각 사용자별 총 학습 시간 계산 (learning_sessions 기준)
            print("\n=== 사용자별 실제 학습 시간 (learning_sessions 기준) ===")
            cursor.execute("""
                SELECT user_id, 
                       COUNT(*) as session_count,
                       SUM(study_duration_seconds) as total_seconds_from_sessions,
                       AVG(study_duration_seconds) as avg_seconds_per_session
                FROM learning_sessions 
                WHERE study_duration_seconds IS NOT NULL
                GROUP BY user_id
                ORDER BY user_id
            """)
            
            session_stats = cursor.fetchall()
            for stat in session_stats:
                print(f"사용자 ID: {stat['user_id']}")
                print(f"세션 수: {stat['session_count']}")
                print(f"총 학습 시간(초): {stat['total_seconds_from_sessions']}")
                print(f"평균 세션 시간(초): {stat['avg_seconds_per_session']:.1f}")
                print("-" * 30)
            
            # user_statistics와 비교
            print("\n=== user_statistics vs learning_sessions 비교 ===")
            cursor.execute("""
                SELECT 
                    us.user_id,
                    us.total_study_sessions as stats_sessions,
                    us.total_study_time_seconds as stats_seconds,
                    ls_agg.actual_sessions,
                    ls_agg.actual_seconds
                FROM user_statistics us
                LEFT JOIN (
                    SELECT user_id, 
                           COUNT(*) as actual_sessions,
                           SUM(study_duration_seconds) as actual_seconds
                    FROM learning_sessions 
                    WHERE study_duration_seconds IS NOT NULL
                    GROUP BY user_id
                ) ls_agg ON us.user_id = ls_agg.user_id
                WHERE us.total_study_sessions > 0
                ORDER BY us.user_id
            """)
            
            comparisons = cursor.fetchall()
            for comp in comparisons:
                print(f"사용자 ID: {comp['user_id']}")
                print(f"통계 테이블 - 세션 수: {comp['stats_sessions']}, 학습 시간(초): {comp['stats_seconds']}")
                print(f"실제 데이터 - 세션 수: {comp['actual_sessions']}, 학습 시간(초): {comp['actual_seconds']}")
                
                # 불일치 확인
                session_match = comp['stats_sessions'] == comp['actual_sessions']
                time_match = comp['stats_seconds'] == comp['actual_seconds']
                
                print(f"세션 수 일치: {session_match}")
                print(f"학습 시간 일치: {time_match}")
                
                if not session_match or not time_match:
                    print("⚠️  데이터 불일치 발견!")
                
                print("-" * 50)
                
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()
    
    return True

if __name__ == "__main__":
    debug_session_data()