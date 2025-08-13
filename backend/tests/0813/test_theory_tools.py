# backend/test_theory_tools.py

import sys
import os
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.content.theory_tools_gemini import theory_generation_tool

def test_theory_tools():
    # chapter_01.json에서 실제 데이터 로드
    with open('data/chapters/chapter_01.json', 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    
    # 섹션 3번 데이터만 추출
    section_number = 1
    section_data = None
    for section in chapter_data.get('sections', []):
        if section.get('section_number') == section_number:
            section_data = section
            break
    
    if not section_data:
        print(f"섹션 {section_number}를 찾을 수 없습니다.")
        return
    
    print("=== Theory Tools 테스트 시작 ===")
    print(f"챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"섹션: {section_data['section_number']} - {section_data['title']}")
    print(f"사용자 유형: beginner")
    print(f"재학습 여부: False")
    print()
    
    try:
        # theory_generation_tool 실행 (새로운 파라미터)
        result = theory_generation_tool(
            section_data=section_data,
            user_type="beginner",
            vector_materials=[],
            is_retry_session=False
        )
        
        # 결과 출력 (이제 일반 텍스트)
        print("=== 생성된 이론 설명 ===")
        print(result)
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    test_theory_tools()