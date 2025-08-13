# backend/test_theory_tools_chatgpt.py

import sys
import os
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.content.theory_tools_chatgpt import theory_generation_tool

def test_theory_tools_chatgpt():
    """ChatGPT를 사용한 이론 생성 도구 테스트"""
    
    # chapter_01.json에서 실제 데이터 로드
    with open('data/chapters/chapter_01.json', 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    
    # 섹션 1번 데이터 추출
    section_number = 1
    section_data = None
    for section in chapter_data.get('sections', []):
        if section.get('section_number') == section_number:
            section_data = section
            break
    
    if not section_data:
        print(f"섹션 {section_number}를 찾을 수 없습니다.")
        return
    
    print("=== ChatGPT Theory Tools 테스트 시작 ===")
    print(f"챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"섹션: {section_data['section_number']} - {section_data['title']}")
    print(f"사용자 유형: beginner")
    print(f"재학습 여부: False")
    print()
    
    try:
        # ChatGPT theory_generation_tool 실행
        result = theory_generation_tool(
            section_data=section_data,
            user_type="beginner",
            vector_materials=[],
            is_retry_session=False
        )
        
        # 결과 출력
        print("=== ChatGPT로 생성된 이론 설명 ===")
        print(result)
        print()
        print("=== 테스트 완료 ===")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def test_theory_tools_chatgpt_advanced():
    """ChatGPT를 사용한 이론 생성 도구 테스트 (고급 사용자)"""
    
    # chapter_01.json에서 실제 데이터 로드
    with open('data/chapters/chapter_01.json', 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    
    # 섹션 2번 데이터 추출
    section_number = 2
    section_data = None
    for section in chapter_data.get('sections', []):
        if section.get('section_number') == section_number:
            section_data = section
            break
    
    if not section_data:
        print(f"섹션 {section_number}를 찾을 수 없습니다.")
        return
    
    print("=== ChatGPT Theory Tools 테스트 (고급 사용자) ===")
    print(f"챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"섹션: {section_data['section_number']} - {section_data['title']}")
    print(f"사용자 유형: advanced")
    print(f"재학습 여부: True")
    print()
    
    try:
        # ChatGPT theory_generation_tool 실행 (고급 사용자, 재학습)
        result = theory_generation_tool(
            section_data=section_data,
            user_type="advanced",
            vector_materials=[],
            is_retry_session=True
        )
        
        # 결과 출력
        print("=== ChatGPT로 생성된 이론 설명 (고급/재학습) ===")
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

if __name__ == "__main__":
    # 연결 테스트 먼저 실행
    test_chatgpt_client_connection()
    print("\n" + "="*60 + "\n")
    
    # 기본 테스트 실행
    test_theory_tools_chatgpt()
    print("\n" + "="*60 + "\n")
    
    # 고급 사용자 테스트 실행
    test_theory_tools_chatgpt_advanced()