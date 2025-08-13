# backend/tests/0813/quick_test.py

import sys
import os
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

from app.tools.content.theory_tools_chatgpt import theory_generation_tool
from app.tools.content.quiz_tools_chatgpt import quiz_generation_tool


def quick_test():
    """빠른 통합 테스트 - 이론생성, 객관식, 주관식 순서로 실행"""
    
    print("🚀 AI 학습 도구 빠른 테스트 시작")
    print("=" * 60)
    
    # 환경변수 확인
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY를 설정해주세요.")
        return
    
    # 1. 이론 생성 테스트
    print("1️⃣ 이론 생성 테스트")
    print("-" * 30)
    
    try:
        # 챕터 1 섹션 1 데이터 로드 (backend/data 기준 경로)
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'chapters', 'chapter_01.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        section_data = chapter_data['sections'][0]  # 첫 번째 섹션
        
        print(f"📖 {chapter_data['title']} - {section_data['title']}")
        
        theory_result = theory_generation_tool(
            section_data=section_data,
            user_type="beginner",
            vector_materials=[],
            is_retry_session=False
        )
        
        print("✅ 이론 생성 성공!")
        print(f"📝 생성된 내용 (처음 100자): {theory_result[:100]}...")
        
    except Exception as e:
        print(f"❌ 이론 생성 실패: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60 + "\n")
    
    # 2. 객관식 퀴즈 생성 테스트
    print("2️⃣ 객관식 퀴즈 생성 테스트")
    print("-" * 30)
    
    try:
        # 챕터 1 섹션 2 데이터 로드 (객관식)
        section_data = None
        for section in chapter_data['sections']:
            if section.get('quiz', {}).get('type') == 'multiple_choice':
                section_data = section
                break
        
        if section_data:
            print(f"📖 {chapter_data['title']} - {section_data['title']}")
            
            theory_content = section_data.get('theory', {}).get('content', '')
            
            quiz_result = quiz_generation_tool(
                section_data=section_data,
                user_type="beginner",
                is_retry_session=False,
                theory_content=theory_content
            )
            
            print("✅ 객관식 퀴즈 생성 성공!")
            print(f"📝 생성된 내용 (처음 200자): {quiz_result[:200]}...")
        else:
            print("❌ 객관식 퀴즈 섹션을 찾을 수 없습니다.")
        
    except Exception as e:
        print(f"❌ 객관식 퀴즈 생성 실패: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60 + "\n")
    
    # 3. 주관식 퀴즈 생성 테스트
    print("3️⃣ 주관식 퀴즈 생성 테스트")
    print("-" * 30)
    
    try:
        # 챕터 5 데이터 로드 (주관식) (backend/data 기준 경로)
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'chapters', 'chapter_05.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            chapter5_data = json.load(f)
        
        section_data = None
        for section in chapter5_data['sections']:
            if section.get('quiz', {}).get('type') == 'subjective':
                section_data = section
                break
        
        if section_data:
            print(f"📖 {chapter5_data['title']} - {section_data['title']}")
            
            theory_content = section_data.get('theory', {}).get('content', '')
            
            quiz_result = quiz_generation_tool(
                section_data=section_data,
                user_type="beginner",
                is_retry_session=False,
                theory_content=theory_content
            )
            
            print("✅ 주관식 퀴즈 생성 성공!")
            print(f"📝 생성된 내용 (처음 200자): {quiz_result[:200]}...")
        else:
            print("❌ 주관식 퀴즈 섹션을 찾을 수 없습니다.")
        
    except Exception as e:
        print(f"❌ 주관식 퀴즈 생성 실패: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 빠른 테스트 완료!")


if __name__ == "__main__":
    quick_test()