# backend/test_theory_tools.py

import sys
import os
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.content.theory_tools import theory_generation_tool

def test_theory_tools():
    # chapter_01.json에서 실제 데이터 로드
    with open('data/chapters/chapter_01.json', 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    
    learning_context = {
        "user_type": "beginner",
        "current_section": 1,
        "session_count": 0,
        "is_retry_session": False
    }
    
    print("=== Theory Tools 테스트 시작 ===")
    print(f"챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"사용자 유형: {learning_context['user_type']}")
    print(f"현재 섹션: {learning_context['current_section']}")
    print()
    
    try:
        # theory_generation_tool 실행
        result = theory_generation_tool(chapter_data, "beginner", learning_context)
        
        # 결과 출력
        result_json = json.loads(result)
        print("=== 생성된 이론 설명 ===")
        print(json.dumps(result_json, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    test_theory_tools()