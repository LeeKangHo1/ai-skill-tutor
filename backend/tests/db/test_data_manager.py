# backend/tests/test_data_manager.py
# TestDataManager 클래스 기본 동작 테스트

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fixtures.test_data import TestDataManager

def test_test_data_manager_creation():
    """TestDataManager 클래스 생성 테스트"""
    try:
        # TestDataManager 인스턴스 생성
        manager = TestDataManager()
        
        # 초기 상태 확인
        summary = manager.get_created_data_summary()
        print("✅ TestDataManager 생성 성공")
        print(f"초기 데이터 상태: {summary}")
        
        # 테스트 데이터 생성 확인
        user_data = manager.create_test_user_data()
        print(f"✅ 테스트 사용자 데이터 생성: {user_data['login_id']}")
        
        session_data = manager.create_test_session_data()
        print(f"✅ 테스트 세션 데이터 생성: {session_data['session_id']}")
        
        conversation_data = manager.create_test_conversation_data(session_data['session_id'])
        print(f"✅ 테스트 대화 데이터 생성: 메시지 {conversation_data['message_sequence']}")
        
        quiz_data = manager.create_test_quiz_data(session_data['session_id'])
        print(f"✅ 테스트 퀴즈 데이터 생성: 문제 {quiz_data['quiz_sequence']}")
        
        print("\n🎉 TestDataManager 클래스 기본 동작 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ TestDataManager 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("=== TestDataManager 클래스 테스트 시작 ===\n")
    success = test_test_data_manager_creation()
    
    if success:
        print("\n✅ 모든 테스트 통과!")
    else:
        print("\n❌ 테스트 실패!")
        sys.exit(1)