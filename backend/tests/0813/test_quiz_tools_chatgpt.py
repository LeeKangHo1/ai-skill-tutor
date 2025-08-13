# backend/test_quiz_tools_chatgpt.py

import sys
import os
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.content.quiz_tools_chatgpt import quiz_generation_tool

def test_quiz_tools_multiple_choice():
    """ChatGPT를 사용한 객관식 퀴즈 생성 도구 테스트"""
    
    # chapter_01.json에서 실제 데이터 로드
    with open('data/chapters/chapter_01.json', 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    
    # 챕터 1 섹션 2 데이터 추출
    section_data = None
    for section in chapter_data.get('sections', []):
        if section.get('section_number') == 2:
            section_data = section
            break
    
    if not section_data:
        print("챕터 1 섹션 2를 찾을 수 없습니다.")
        return
    
    # 이론 내용 추출
    theory_content = section_data.get('theory', {}).get('content', '')
    
    print("=== ChatGPT 객관식 퀴즈 생성 테스트 ===")
    print(f"챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"섹션: {section_data['section_number']} - {section_data['title']}")
    print(f"퀴즈 타입: {section_data.get('quiz', {}).get('type', 'multiple_choice')}")
    print(f"사용자 유형: beginner")
    print(f"재학습 여부: False")
    print(f"이론 내용 길이: {len(theory_content)}자")
    print()
    
    try:
        # ChatGPT quiz_generation_tool 실행
        result = quiz_generation_tool(
            section_data=section_data,
            user_type="beginner",
            is_retry_session=False,
            theory_content=theory_content
        )
        
        # 결과 출력
        print("=== ChatGPT로 생성된 객관식 퀴즈 ===")
        print(result)
        print()
        print("=== 테스트 완료 ===")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def test_quiz_tools_subjective():
    """ChatGPT를 사용한 주관식 퀴즈 생성 도구 테스트"""
    
    # chapter_05.json에서 실제 데이터 로드
    with open('data/chapters/chapter_05.json', 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    
    # 챕터 5 섹션 1 데이터 추출
    section_data = None
    for section in chapter_data.get('sections', []):
        if section.get('section_number') == 1:
            section_data = section
            break
    
    if not section_data:
        print("챕터 5 섹션 1을 찾을 수 없습니다.")
        return
    
    # 이론 내용 추출
    theory_content = section_data.get('theory', {}).get('content', '')
    
    print("=== ChatGPT 주관식 퀴즈 생성 테스트 ===")
    print(f"챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"섹션: {section_data['section_number']} - {section_data['title']}")
    print(f"퀴즈 타입: {section_data.get('quiz', {}).get('type', 'subjective')}")
    print(f"사용자 유형: beginner")
    print(f"재학습 여부: False")
    print(f"이론 내용 길이: {len(theory_content)}자")
    print()
    
    try:
        # ChatGPT quiz_generation_tool 실행
        result = quiz_generation_tool(
            section_data=section_data,
            user_type="beginner",
            is_retry_session=False,
            theory_content=theory_content
        )
        
        # 결과 출력
        print("=== ChatGPT로 생성된 주관식 퀴즈 ===")
        print(result)
        print()
        print("=== 테스트 완료 ===")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def test_quiz_tools_advanced_retry():
    """ChatGPT를 사용한 퀴즈 생성 도구 테스트 (고급 사용자, 재학습)"""
    
    # chapter_01.json에서 실제 데이터 로드
    with open('data/chapters/chapter_01.json', 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    
    # 챕터 1 섹션 2 데이터 추출 (고급 사용자 테스트)
    section_data = None
    for section in chapter_data.get('sections', []):
        if section.get('section_number') == 2:
            section_data = section
            break
    
    if not section_data:
        print("챕터 1 섹션 2를 찾을 수 없습니다.")
        return
    
    # 이론 내용 추출
    theory_content = section_data.get('theory', {}).get('content', '')
    
    print("=== ChatGPT 퀴즈 생성 테스트 (고급 사용자, 재학습) ===")
    print(f"챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"섹션: {section_data.get('section_number', 2)} - {section_data.get('title', '')}")
    print(f"퀴즈 타입: {section_data.get('quiz', {}).get('type', 'multiple_choice')}")
    print(f"사용자 유형: advanced")
    print(f"재학습 여부: True")
    print(f"이론 내용 길이: {len(theory_content)}자")
    print()
    
    try:
        # ChatGPT quiz_generation_tool 실행 (고급 사용자, 재학습)
        result = quiz_generation_tool(
            section_data=section_data,
            user_type="advanced",
            is_retry_session=True,
            theory_content=theory_content
        )
        
        # 결과 출력
        print("=== ChatGPT로 생성된 퀴즈 (고급/재학습) ===")
        print(result)
        print()
        print("=== 테스트 완료 ===")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def test_chatgpt_client_connection():
    """ChatGPT 클라이언트 연결 테스트"""
    
    print("=== ChatGPT 클라이언트 연결 테스트 ===")
    
    try:
        from app.core.external.chatgpt_client import ChatGPTClient
        
        client = ChatGPTClient()
        connection_result = client.test_connection()
        
        if connection_result:
            print("✅ ChatGPT 클라이언트 연결 성공")
        else:
            print("❌ ChatGPT 클라이언트 연결 실패")
            
    except Exception as e:
        print(f"❌ ChatGPT 클라이언트 테스트 오류: {str(e)}")
        import traceback
        traceback.print_exc()

def test_section_data_loading():
    """섹션 데이터 로딩 확인 테스트"""
    
    print("=== 섹션 데이터 로딩 확인 ===")
    
    try:
        # 챕터 1 확인
        print("📖 챕터 1 섹션 데이터:")
        with open('data/chapters/chapter_01.json', 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        sections = chapter_data.get('sections', [])
        print(f"총 섹션 수: {len(sections)}")
        
        for section in sections:
            section_num = section.get('section_number', '?')
            section_title = section.get('title', '제목 없음')
            quiz_type = section.get('quiz', {}).get('type', '퀴즈 없음')
            theory_length = len(section.get('theory', {}).get('content', ''))
            print(f"  섹션 {section_num}: {section_title} - 퀴즈: {quiz_type}, 이론: {theory_length}자")
        
        print()
        
        # 챕터 5 확인
        print("📖 챕터 5 섹션 데이터:")
        with open('data/chapters/chapter_05.json', 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        sections = chapter_data.get('sections', [])
        print(f"총 섹션 수: {len(sections)}")
        
        for section in sections:
            section_num = section.get('section_number', '?')
            section_title = section.get('title', '제목 없음')
            quiz_type = section.get('quiz', {}).get('type', '퀴즈 없음')
            theory_length = len(section.get('theory', {}).get('content', ''))
            print(f"  섹션 {section_num}: {section_title} - 퀴즈: {quiz_type}, 이론: {theory_length}자")
        
    except Exception as e:
        print(f"섹션 데이터 로딩 오류: {str(e)}")

if __name__ == "__main__":
    # 섹션 데이터 확인
    test_section_data_loading()
    print("\n" + "="*60 + "\n")
    
    # 연결 테스트 먼저 실행
    test_chatgpt_client_connection()
    print("\n" + "="*60 + "\n")
    
    # 객관식 퀴즈 테스트 실행
    test_quiz_tools_multiple_choice()
    print("\n" + "="*60 + "\n")
    
    # 주관식 퀴즈 테스트 실행
    test_quiz_tools_subjective()
    print("\n" + "="*60 + "\n")
    
    # 고급 사용자 재학습 테스트 실행
    test_quiz_tools_advanced_retry()