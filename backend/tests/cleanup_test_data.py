# backend/cleanup_test_data.py
# 테스트 데이터 정리 스크립트

import sys
import os

# 백엔드 앱 경로를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.utils.database.connection import execute_query, fetch_all

def cleanup_test_data():
    """테스트 관련 데이터를 모두 정리합니다"""
    try:
        print("🧹 테스트 데이터 정리 시작...")
        
        # 1. 테스트 사용자 목록 확인
        test_users = fetch_all(
            "SELECT user_id, login_id, username, email FROM users WHERE login_id LIKE 'test%'"
        )
        
        if not test_users:
            print("✅ 정리할 테스트 데이터가 없습니다.")
            return
        
        print(f"📋 발견된 테스트 사용자: {len(test_users)}명")
        for user in test_users:
            print(f"  - {user['login_id']} ({user['username']}, {user['email']})")
        
        # 사용자 확인
        confirm = input("\n위 테스트 데이터를 모두 삭제하시겠습니까? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 작업이 취소되었습니다.")
            return
        
        # 2. 외래키 제약 조건 임시 비활성화
        execute_query("SET FOREIGN_KEY_CHECKS = 0")
        print("🔓 외래키 제약 조건 비활성화")
        
        # 3. 테스트 사용자 관련 데이터 삭제
        deleted_counts = {}
        
        # user_auth_tokens 테이블
        result = execute_query(
            "DELETE FROM user_auth_tokens WHERE user_id IN (SELECT user_id FROM users WHERE login_id LIKE 'test%')"
        )
        deleted_counts['user_auth_tokens'] = result
        
        # user_statistics 테이블
        result = execute_query(
            "DELETE FROM user_statistics WHERE user_id IN (SELECT user_id FROM users WHERE login_id LIKE 'test%')"
        )
        deleted_counts['user_statistics'] = result
        
        # user_progress 테이블
        result = execute_query(
            "DELETE FROM user_progress WHERE user_id IN (SELECT user_id FROM users WHERE login_id LIKE 'test%')"
        )
        deleted_counts['user_progress'] = result
        
        # learning_sessions 테이블 (있다면)
        try:
            result = execute_query(
                "DELETE FROM learning_sessions WHERE user_id IN (SELECT user_id FROM users WHERE login_id LIKE 'test%')"
            )
            deleted_counts['learning_sessions'] = result
        except:
            pass
        
        # session_conversations 테이블 (있다면)
        try:
            result = execute_query(
                "DELETE FROM session_conversations WHERE session_id IN (SELECT session_id FROM learning_sessions WHERE user_id IN (SELECT user_id FROM users WHERE login_id LIKE 'test%'))"
            )
            deleted_counts['session_conversations'] = result
        except:
            pass
        
        # session_quizzes 테이블 (있다면)
        try:
            result = execute_query(
                "DELETE FROM session_quizzes WHERE session_id IN (SELECT session_id FROM learning_sessions WHERE user_id IN (SELECT user_id FROM users WHERE login_id LIKE 'test%'))"
            )
            deleted_counts['session_quizzes'] = result
        except:
            pass
        
        # users 테이블 (마지막에 삭제)
        result = execute_query(
            "DELETE FROM users WHERE login_id LIKE 'test%'"
        )
        deleted_counts['users'] = result
        
        # 4. 외래키 제약 조건 재활성화
        execute_query("SET FOREIGN_KEY_CHECKS = 1")
        print("🔒 외래키 제약 조건 재활성화")
        
        # 5. 결과 출력
        print("\n📊 삭제된 데이터:")
        total_deleted = 0
        for table, count in deleted_counts.items():
            if count > 0:
                print(f"  - {table}: {count}개 행")
                total_deleted += count
        
        print(f"\n✅ 총 {total_deleted}개 행이 삭제되었습니다.")
        
        # 6. 정리 후 확인
        remaining_test_users = fetch_all(
            "SELECT COUNT(*) as count FROM users WHERE login_id LIKE 'test%'"
        )
        remaining_count = remaining_test_users[0]['count'] if remaining_test_users else 0
        
        if remaining_count == 0:
            print("🎉 모든 테스트 데이터가 성공적으로 정리되었습니다!")
        else:
            print(f"⚠️ {remaining_count}개의 테스트 사용자가 남아있습니다.")
        
    except Exception as e:
        print(f"❌ 테스트 데이터 정리 중 오류 발생: {e}")
        
        # 오류 발생 시 외래키 제약 조건 복구
        try:
            execute_query("SET FOREIGN_KEY_CHECKS = 1")
            print("🔒 외래키 제약 조건 복구 완료")
        except:
            pass

def show_test_data():
    """현재 테스트 데이터 현황을 보여줍니다"""
    try:
        print("📊 현재 테스트 데이터 현황:")
        
        # 테스트 사용자 수
        test_users = fetch_all(
            "SELECT COUNT(*) as count FROM users WHERE login_id LIKE 'test%'"
        )
        user_count = test_users[0]['count'] if test_users else 0
        print(f"  - 테스트 사용자: {user_count}명")
        
        if user_count > 0:
            # 테스트 사용자 목록
            users = fetch_all(
                "SELECT user_id, login_id, username, email, created_at FROM users WHERE login_id LIKE 'test%' ORDER BY created_at DESC"
            )
            print("\n📋 테스트 사용자 목록:")
            for user in users:
                print(f"  - ID: {user['user_id']}, 로그인ID: {user['login_id']}, 이름: {user['username']}")
                print(f"    이메일: {user['email']}, 생성일: {user['created_at']}")
            
            # 관련 테이블 데이터 수
            tables_to_check = [
                'user_auth_tokens',
                'user_statistics', 
                'user_progress'
            ]
            
            print("\n📈 관련 테이블 데이터:")
            for table in tables_to_check:
                try:
                    result = fetch_all(
                        f"SELECT COUNT(*) as count FROM {table} WHERE user_id IN (SELECT user_id FROM users WHERE login_id LIKE 'test%')"
                    )
                    count = result[0]['count'] if result else 0
                    print(f"  - {table}: {count}개 행")
                except Exception as e:
                    print(f"  - {table}: 확인 불가 ({e})")
        
    except Exception as e:
        print(f"❌ 테스트 데이터 현황 조회 중 오류: {e}")

if __name__ == "__main__":
    print("🔍 MySQL 테스트 데이터 정리 도구")
    print("=" * 50)
    
    # 현재 상황 확인
    show_test_data()
    
    print("\n" + "=" * 50)
    
    # 정리 실행
    cleanup_test_data()