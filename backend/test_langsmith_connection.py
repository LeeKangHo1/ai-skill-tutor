# backend/test_langsmith_connection.py

import sys
import os
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.langsmith.langsmith_client import (
    get_langsmith_client, 
    is_langsmith_enabled,
    get_langsmith_project,
    create_langsmith_run,
    update_langsmith_run,
    end_langsmith_run
)

def test_langsmith_connection():
    """LangSmith 연결 및 추적 테스트"""
    print("=== LangSmith 연결 테스트 시작 ===")
    
    # 1. 환경변수 확인
    print("\n1. 환경변수 확인:")
    langchain_tracing = os.getenv('LANGCHAIN_TRACING_V2')
    langsmith_api_key = os.getenv('LANGSMITH_API_KEY')
    langchain_project = os.getenv('LANGCHAIN_PROJECT')
    langchain_endpoint = os.getenv('LANGCHAIN_ENDPOINT')
    
    print(f"LANGCHAIN_TRACING_V2: {langchain_tracing}")
    print(f"LANGSMITH_API_KEY: {'설정됨' if langsmith_api_key else '없음'} ({langsmith_api_key[:15]}... if langsmith_api_key else None)")
    print(f"LANGCHAIN_PROJECT: {langchain_project}")
    print(f"LANGCHAIN_ENDPOINT: {langchain_endpoint}")
    
    # 2. LangSmith 활성화 상태 확인
    print(f"\n2. LangSmith 활성화 상태: {is_langsmith_enabled()}")
    print(f"프로젝트명: {get_langsmith_project()}")
    
    # 3. 클라이언트 가져오기 테스트
    print(f"\n3. 클라이언트 테스트:")
    client = get_langsmith_client()
    print(f"클라이언트 객체: {client}")
    print(f"클라이언트 타입: {type(client)}")
    
    if not client:
        print("❌ LangSmith 클라이언트가 없습니다.")
        return
    
    # 4. 클라이언트 직접 테스트
    print(f"\n4. 클라이언트 직접 테스트:")
    try:
        # 프로젝트 목록 조회 (연결 테스트)
        projects = list(client.list_projects(limit=3))
        print(f"✅ 프로젝트 목록 조회 성공: {len(projects)}개")
        for project in projects:
            print(f"  - {project.name} (id: {project.id})")
    except Exception as e:
        print(f"❌ 프로젝트 목록 조회 실패: {str(e)}")
        return
    
    # 5. Run 생성 테스트
    print(f"\n5. Run 생성 테스트:")
    try:
        run_id = create_langsmith_run(
            name="test_theory_tools",
            run_type="tool",
            inputs={
                "chapter_number": 1,
                "user_type": "beginner",
                "test_time": datetime.now().isoformat()
            }
        )
        print(f"✅ Run 생성 성공: {run_id}")
        
        if run_id:
            # 6. Run 업데이트 테스트
            print(f"\n6. Run 업데이트 테스트:")
            update_langsmith_run(
                run_id,
                outputs={
                    "status": "processing",
                    "progress": 50
                }
            )
            print(f"✅ Run 업데이트 성공")
            
            # 7. Run 종료 테스트
            print(f"\n7. Run 종료 테스트:")
            end_langsmith_run(
                run_id,
                outputs={
                    "status": "completed",
                    "result": "test successful"
                }
            )
            print(f"✅ Run 종료 성공")
            
    except Exception as e:
        print(f"❌ Run 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== LangSmith 연결 테스트 완료 ===")

def test_with_actual_tool():
    """실제 theory_generation_tool과 함께 테스트"""
    print("\n\n=== 실제 Tool과 함께 LangSmith 테스트 ===")
    
    from app.tools.content.theory_tools import theory_generation_tool
    
    # chapter_01.json에서 데이터 로드
    with open('data/chapters/chapter_01.json', 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    
    learning_context = {
        "user_type": "beginner",
        "current_section": 1,
        "session_count": 0,
        "is_retry_session": False
    }
    
    print(f"챕터: {chapter_data['chapter_number']} - {chapter_data['title']}")
    print(f"사용자 유형: {learning_context['user_type']}")
    
    try:
        # LangSmith가 활성화된 상태에서 tool 실행
        result = theory_generation_tool(chapter_data, "beginner", learning_context)
        print("✅ Theory tool 실행 성공")
        print("LangSmith 대시보드에서 추적 기록을 확인해보세요.")
        
    except Exception as e:
        print(f"❌ Theory tool 실행 실패: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_langsmith_connection()
    test_with_actual_tool()