# backend/tests/0813/test_three_agents/run_test.py
"""
세 에이전트 통합 테스트 실행 스크립트
"""

import sys
import os
import asyncio
from pathlib import Path

# 백엔드 루트를 Python 경로에 추가
backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root))

# 환경변수 설정
os.environ.setdefault('FLASK_ENV', 'testing')

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("세 에이전트 통합 테스트 실행")
    print("=" * 60)
    
    try:
        # 테스트 클래스 import 및 실행
        from test_agents_integration import TestThreeAgentsIntegration
        
        test_instance = TestThreeAgentsIntegration()
        test_instance.setup_method()
        
        # 테스트 실행
        print("\n1. 객관식 퀴즈 플로우 테스트 (챕터 2 섹션 2)")
        test_instance.test_objective_quiz_flow_chapter2_section2()
        
        print("\n" + "="*60)
        print("\n2. 주관식 퀴즈 플로우 테스트 (챕터 5 섹션 3)")
        test_instance.test_subjective_quiz_flow_chapter5_section3()
        
        print("\n" + "="*60)
        print("\n3. State 데이터 지속성 테스트")
        test_instance.test_state_persistence_through_agents()
        
        print("\n" + "="*60)
        print("✅ 모든 테스트가 성공적으로 완료되었습니다!")
        print("="*60)
        
    except ImportError as e:
        print(f"❌ 모듈 import 오류: {e}")
        print("필요한 패키지가 설치되어 있는지 확인해주세요.")
        return 1
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)