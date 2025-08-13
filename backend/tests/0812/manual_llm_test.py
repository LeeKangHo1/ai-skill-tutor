# backend/tests/manual_llm_test.py

"""
수동 LLM 테스트 스크립트
실제 API 키가 설정되었을 때 LLM 호출을 테스트하는 스크립트입니다.

사용법:
1. .env 파일에 API 키 설정
2. python tests/manual_llm_test.py 실행
"""

import sys
import os
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def check_environment():
    """환경 설정 확인"""
    print("🔍 환경 설정 확인")
    print("=" * 50)
    
    # API 키 확인
    gemini_key = os.getenv('GOOGLE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"Gemini API Key: {'✅ 설정됨' if gemini_key else '❌ 없음'}")
    print(f"OpenAI API Key: {'✅ 설정됨' if openai_key else '❌ 없음'}")
    
    if not gemini_key and not openai_key:
        print("\n❌ API 키가 설정되지 않았습니다.")
        print("backend/.env 파일에 다음 중 하나 이상을 추가하세요:")
        print("GEMINI_API_KEY=your_gemini_api_key")
        print("OPENAI_API_KEY=your_openai_api_key")
        return False
    
    return True

def test_theory_generation():
    """이론 생성 테스트"""
    print("\n🧠 이론 생성 테스트")
    print("=" * 50)
    
    try:
        from backend.app.tools.content.theory_tools_gemini import theory_generation_tool
        
        # 테스트 데이터
        chapter_data = {
            "id": 1,
            "title": "머신러닝 기초",
            "sections": [{
                "section_number": 1,
                "title": "머신러닝이란?",
                "content": "머신러닝은 데이터로부터 패턴을 학습하는 AI 기술입니다."
            }]
        }
        
        learning_context = {
            "current_section": 1,
            "user_level": "beginner",
            "session_count": 1,
            "is_retry_session": False
        }
        
        print("📝 이론 생성 중...")
        result = theory_generation_tool(
            chapter_data=chapter_data,
            user_type="beginner",
            learning_context=learning_context
        )
        
        print("\n📚 생성된 이론:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 이론 생성 실패: {e}")
        return False

def test_quiz_generation():
    """퀴즈 생성 테스트"""
    print("\n🧩 퀴즈 생성 테스트")
    print("=" * 50)
    
    try:
        from app.tools.content.quiz_tools import quiz_generation_tool
        
        # 테스트 데이터
        chapter_data = {
            "id": 1,
            "title": "머신러닝 기초",
            "sections": [{
                "section_number": 1,
                "title": "머신러닝이란?",
                "content": "머신러닝은 데이터로부터 패턴을 학습하는 AI 기술입니다.",
                "quiz_type": "multiple_choice"
            }]
        }
        
        learning_context = {
            "current_section": 1,
            "quiz_type": "multiple_choice",
            "user_level": "beginner"
        }
        
        print("🧩 객관식 퀴즈 생성 중...")
        result = quiz_generation_tool(
            chapter_data=chapter_data,
            user_type="beginner",
            learning_context=learning_context
        )
        
        print("\n🎯 생성된 퀴즈:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # JSON 파싱 시도
        try:
            quiz_data = json.loads(result)
            print("\n📊 퀴즈 구조 분석:")
            print(f"문제: {quiz_data.get('question', 'N/A')}")
            print(f"선택지 수: {len(quiz_data.get('options', []))}")
            print(f"정답: {quiz_data.get('correct_answer', 'N/A')}")
        except json.JSONDecodeError:
            print("⚠️ JSON 형식이 아닙니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ 퀴즈 생성 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 수동 LLM 테스트 시작")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 환경 확인
    if not check_environment():
        return
    
    # 테스트 실행
    theory_success = test_theory_generation()
    quiz_success = test_quiz_generation()
    
    # 결과 요약
    print("\n📋 테스트 결과 요약")
    print("=" * 50)
    print(f"이론 생성: {'✅ 성공' if theory_success else '❌ 실패'}")
    print(f"퀴즈 생성: {'✅ 성공' if quiz_success else '❌ 실패'}")
    
    if theory_success and quiz_success:
        print("\n🎉 모든 테스트가 성공했습니다!")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")
        print("API 키 설정과 네트워크 연결을 확인해주세요.")

if __name__ == "__main__":
    main()