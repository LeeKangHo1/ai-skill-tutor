# backend/tests/0813/test_integrated_tools.py

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


def load_section_data(chapter_num, section_num):
    """챕터와 섹션 번호로 섹션 데이터 로드"""
    try:
        # backend/data 기준 경로
        chapter_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'chapters', f'chapter_{chapter_num:02d}.json')
        with open(chapter_file, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        for section in chapter_data.get('sections', []):
            if section.get('section_number') == section_num:
                return section, chapter_data
        
        print(f"❌ 챕터 {chapter_num} 섹션 {section_num}을 찾을 수 없습니다.")
        return None, None
        
    except FileNotFoundError:
        print(f"❌ 챕터 파일을 찾을 수 없습니다: {chapter_file}")
        return None, None
    except Exception as e:
        print(f"❌ 데이터 로드 오류: {str(e)}")
        return None, None


def test_theory_generation():
    """이론 생성 테스트"""
    print("=" * 60)
    print("🎓 이론 생성 테스트")
    print("=" * 60)
    
    # 챕터 1 섹션 1 데이터 로드 (AI 기초 개념)
    section_data, chapter_data = load_section_data(1, 1)
    
    if not section_data:
        return
    
    print(f"📖 챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"📝 섹션: {section_data['section_number']} - {section_data['title']}")
    print(f"👤 사용자 유형: beginner")
    print(f"🔄 재학습 여부: False")
    print()
    
    try:
        # 이론 생성 도구 실행
        result = theory_generation_tool(
            section_data=section_data,
            user_type="beginner",
            vector_materials=[],
            is_retry_session=False
        )
        
        print("✅ 생성된 이론 설명:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        print()
        
    except Exception as e:
        print(f"❌ 이론 생성 오류: {str(e)}")
        import traceback
        traceback.print_exc()


def test_multiple_choice_quiz():
    """객관식 퀴즈 생성 테스트"""
    print("=" * 60)
    print("📝 객관식 퀴즈 생성 테스트")
    print("=" * 60)
    
    # 챕터 1 섹션 2 데이터 로드 (객관식 퀴즈가 있는 섹션)
    section_data, chapter_data = load_section_data(1, 2)
    
    if not section_data:
        return
    
    theory_content = section_data.get('theory', {}).get('content', '')
    quiz_type = section_data.get('quiz', {}).get('type', 'multiple_choice')
    
    print(f"📖 챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"📝 섹션: {section_data['section_number']} - {section_data['title']}")
    print(f"❓ 퀴즈 타입: {quiz_type}")
    print(f"👤 사용자 유형: beginner")
    print(f"🔄 재학습 여부: False")
    print(f"📄 이론 내용 길이: {len(theory_content)}자")
    print()
    
    try:
        # 객관식 퀴즈 생성 도구 실행
        result = quiz_generation_tool(
            section_data=section_data,
            user_type="beginner",
            is_retry_session=False,
            theory_content=theory_content
        )
        
        print("✅ 생성된 객관식 퀴즈:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        print()
        
    except Exception as e:
        print(f"❌ 객관식 퀴즈 생성 오류: {str(e)}")
        import traceback
        traceback.print_exc()


def test_subjective_quiz():
    """주관식 퀴즈 생성 테스트"""
    print("=" * 60)
    print("✍️ 주관식 퀴즈 생성 테스트")
    print("=" * 60)
    
    # 챕터 5 섹션 1 데이터 로드 (주관식 퀴즈가 있는 섹션)
    section_data, chapter_data = load_section_data(5, 1)
    
    if not section_data:
        return
    
    theory_content = section_data.get('theory', {}).get('content', '')
    quiz_type = section_data.get('quiz', {}).get('type', 'subjective')
    
    print(f"📖 챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"📝 섹션: {section_data['section_number']} - {section_data['title']}")
    print(f"❓ 퀴즈 타입: {quiz_type}")
    print(f"👤 사용자 유형: beginner")
    print(f"🔄 재학습 여부: False")
    print(f"📄 이론 내용 길이: {len(theory_content)}자")
    print()
    
    try:
        # 주관식 퀴즈 생성 도구 실행
        result = quiz_generation_tool(
            section_data=section_data,
            user_type="beginner",
            is_retry_session=False,
            theory_content=theory_content
        )
        
        print("✅ 생성된 주관식 퀴즈:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        print()
        
    except Exception as e:
        print(f"❌ 주관식 퀴즈 생성 오류: {str(e)}")
        import traceback
        traceback.print_exc()


def test_connection():
    """OpenAI API 연결 테스트"""
    print("=" * 60)
    print("🔗 OpenAI API 연결 테스트")
    print("=" * 60)
    
    try:
        import os
        from langchain_openai import ChatOpenAI
        
        # 환경변수 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            return
        
        # ChatOpenAI 모델 초기화
        model = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            openai_api_key=api_key,
            temperature=0.7,
            max_tokens=100
        )
        
        # 간단한 테스트 메시지
        test_message = "안녕하세요. 연결 테스트입니다."
        response = model.invoke(test_message)
        
        print("✅ OpenAI API 연결 성공")
        print(f"📝 테스트 응답: {response.content[:50]}...")
            
    except Exception as e:
        print(f"❌ OpenAI API 연결 테스트 오류: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()


def show_menu():
    """메뉴 표시"""
    print("=" * 60)
    print("🤖 AI 학습 도구 통합 테스트")
    print("=" * 60)
    print("1. 이론 생성 테스트")
    print("2. 객관식 퀴즈 생성 테스트")
    print("3. 주관식 퀴즈 생성 테스트")
    print("4. 전체 테스트 실행")
    print("5. 연결 테스트")
    print("0. 종료")
    print("=" * 60)


def main():
    """메인 실행 함수"""
    while True:
        show_menu()
        choice = input("선택하세요 (0-5): ").strip()
        
        if choice == '1':
            test_theory_generation()
        elif choice == '2':
            test_multiple_choice_quiz()
        elif choice == '3':
            test_subjective_quiz()
        elif choice == '4':
            print("🚀 전체 테스트 실행 중...")
            print()
            test_connection()
            test_theory_generation()
            test_multiple_choice_quiz()
            test_subjective_quiz()
            print("✅ 전체 테스트 완료!")
        elif choice == '5':
            test_connection()
        elif choice == '0':
            print("👋 테스트를 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
        
        input("\n계속하려면 Enter를 누르세요...")
        print("\n" * 2)


if __name__ == "__main__":
    main()