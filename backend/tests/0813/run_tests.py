# backend/tests/0813/run_tests.py

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

def run_quick_test():
    """빠른 테스트 실행"""
    print("🚀 빠른 테스트 실행 중...")
    print()
    
    try:
        from quick_test import quick_test
        quick_test()
    except Exception as e:
        print(f"❌ 빠른 테스트 실행 오류: {str(e)}")
        import traceback
        traceback.print_exc()

def run_interactive_test():
    """대화형 테스트 실행"""
    print("🎮 대화형 테스트 실행 중...")
    print()
    
    try:
        from test_integrated_tools import main
        main()
    except Exception as e:
        print(f"❌ 대화형 테스트 실행 오류: {str(e)}")
        import traceback
        traceback.print_exc()

def check_environment():
    """환경 설정 확인"""
    print("🔍 환경 설정 확인 중...")
    print("-" * 40)
    
    # Python 버전 확인
    print(f"Python 버전: {sys.version}")
    
    # 필요한 모듈 확인
    required_modules = [
        'langchain',
        'langchain_core', 
        'langchain_openai',
        'openai',
        'python-dotenv',
        'pydantic'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: 설치됨")
        except ImportError:
            print(f"❌ {module}: 설치되지 않음")
            missing_modules.append(module)
    
    # 환경변수 확인
    print("\n환경변수 확인:")
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = ['OPENAI_API_KEY']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: 설정됨 (길이: {len(value)})")
        else:
            print(f"❌ {var}: 설정되지 않음")
    
    # 데이터 파일 확인
    print("\n데이터 파일 확인:")
    data_files = [
        os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'chapters', 'chapter_01.json'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'chapters', 'chapter_05.json')
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)}: 존재함")
        else:
            print(f"❌ {os.path.basename(file_path)}: 존재하지 않음")
    
    # OpenAI API 연결 테스트
    print("\nOpenAI API 연결 테스트:")
    try:
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            model = ChatOpenAI(
                model='gpt-4o-mini',
                openai_api_key=api_key,
                temperature=0.7,
                max_tokens=50
            )
            response = model.invoke("Hello")
            print("✅ OpenAI API 연결 성공")
        else:
            print("❌ OPENAI_API_KEY가 설정되지 않아 연결 테스트를 건너뜁니다.")
    except Exception as e:
        print(f"❌ OpenAI API 연결 실패: {str(e)}")
    
    if missing_modules:
        print(f"\n⚠️ 누락된 모듈: {', '.join(missing_modules)}")
        print("다음 명령어로 설치하세요:")
        print(f"pip install {' '.join(missing_modules)}")
    
    print("-" * 40)

def show_main_menu():
    """메인 메뉴 표시"""
    print("=" * 60)
    print("🤖 AI 학습 도구 테스트 런처")
    print("=" * 60)
    print("1. 환경 설정 확인")
    print("2. 빠른 테스트 실행 (이론+객관식+주관식)")
    print("3. 대화형 테스트 실행 (메뉴 선택)")
    print("0. 종료")
    print("=" * 60)

def main():
    """메인 실행 함수"""
    while True:
        show_main_menu()
        choice = input("선택하세요 (0-3): ").strip()
        
        if choice == '1':
            check_environment()
        elif choice == '2':
            run_quick_test()
        elif choice == '3':
            run_interactive_test()
        elif choice == '0':
            print("👋 테스트 런처를 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
        
        input("\n계속하려면 Enter를 누르세요...")
        print("\n" * 2)

if __name__ == "__main__":
    main()