# backend/debug_theory_specific.py

import sys
import os
import json
import traceback

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_theory_tools_detailed():
    """Theory Tools 상세 디버깅"""
    print("=== Theory Tools 상세 디버깅 ===")
    
    # .env 파일 로드
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # 1. AI 클라이언트 매니저 직접 테스트
        from app.core.external.ai_client_manager import get_ai_client_manager
        from langchain_core.messages import SystemMessage, HumanMessage
        
        ai_manager = get_ai_client_manager()
        print("✅ AI Manager 초기화 성공")
        
        # 2. Theory 스타일 JSON 생성 직접 테스트
        print("\n--- 직접 JSON 생성 테스트 ---")
        
        system_msg = SystemMessage(content="""당신은 AI 학습을 처음 시작하는 사용자를 위한 친근한 튜터입니다.
다음 JSON 형식으로만 응답해주세요:
{
  "content_type": "theory",
  "chapter_info": {
    "chapter_number": 1,
    "title": "AI 테스트",
    "user_type": "beginner"
  },
  "section_info": {
    "section_number": 1,
    "title": "기본 개념"
  },
  "main_content": "AI는 인공지능을 의미합니다. 간단히 설명하면 컴퓨터가 사람처럼 학습하고 판단할 수 있는 기술입니다.",
  "key_points": ["AI 정의", "기본 개념", "학습 능력"],
  "analogy": "AI는 마치 디지털 두뇌와 같습니다.",
  "examples": ["음성 인식", "이미지 분석"],
  "user_guidance": "천천히 읽어보시고 질문해주세요!",
  "next_step_preview": "이제 퀴즈를 풀어보겠습니다."
}""")
        
        user_msg = HumanMessage(content="AI의 기본 개념에 대해 초보자를 위한 설명을 JSON 형식으로 생성해주세요.")
        
        # AI 생성 테스트
        direct_result = ai_manager.generate_json_content_with_messages([system_msg, user_msg])
        
        print("✅ 직접 JSON 생성 성공:")
        print(f"응답 타입: {type(direct_result)}")
        print(json.dumps(direct_result, ensure_ascii=False, indent=2))
        
        # 3. Theory Tools 내부 단계별 테스트
        print("\n--- Theory Tools 내부 단계별 테스트 ---")
        
        # 테스트 데이터 준비
        test_chapter_data = {
            "chapter_number": 1,
            "title": "AI 테스트",
            "sections": [{
                "section_number": 1,
                "title": "기본 개념",
                "theory": {
                    "content": "AI는 인공지능을 의미합니다.",
                    "key_points": ["AI 정의", "기본 개념"],
                    "analogy": "AI는 마치 디지털 두뇌와 같습니다."
                }
            }]
        }
        
        test_learning_context = {
            "user_type": "beginner",
            "current_section": 1,
            "session_count": 0,
            "is_retry_session": False
        }
        
        # Theory Tools 내부 함수들 단계별 테스트
        from app.tools.content.theory_tools import (
            _get_current_section_data,
            _create_prompt_templates,
            _prepare_prompt_data
        )
        
        # 4a. 섹션 데이터 추출 테스트
        current_section = _get_current_section_data(test_chapter_data, test_learning_context)
        print(f"✅ 현재 섹션 데이터: {current_section}")
        
        # 4b. 프롬프트 템플릿 생성 테스트
        system_template, user_template = _create_prompt_templates("beginner", test_learning_context)
        print("✅ 프롬프트 템플릿 생성 성공")
        
        # 4c. 프롬프트 데이터 준비 테스트
        prompt_data = _prepare_prompt_data(test_chapter_data, current_section, test_learning_context)
        print(f"✅ 프롬프트 데이터 준비: {prompt_data}")
        
        # 4d. 실제 메시지 생성 테스트
        system_message = SystemMessage(content=system_template.format(**prompt_data))
        user_message = HumanMessage(content=user_template.format(**prompt_data))
        
        print(f"\n--- 생성된 프롬프트 확인 ---")
        print(f"System Message 길이: {len(system_message.content)}")
        print(f"User Message 길이: {len(user_message.content)}")
        print(f"System Message 앞 200자: {system_message.content[:200]}...")
        print(f"User Message 앞 200자: {user_message.content[:200]}...")
        
        # 4e. AI 생성 테스트 (Theory Tools와 동일한 방식)
        print(f"\n--- AI 생성 테스트 (Theory Tools 방식) ---")
        
        try:
            generated_response = ai_manager.generate_json_content_with_messages(
                messages=[system_message, user_message],
                langsmith_run_id=None  # LangSmith 비활성화
            )
            
            print("✅ AI 생성 성공!")
            print(f"응답 타입: {type(generated_response)}")
            
            if isinstance(generated_response, dict):
                print("✅ 딕셔너리 형태로 반환됨")
                print(json.dumps(generated_response, ensure_ascii=False, indent=2))
            else:
                print(f"⚠️ 예상치 못한 타입: {type(generated_response)}")
                print(f"응답 내용: {generated_response}")
                
        except Exception as ai_error:
            print(f"❌ AI 생성 실패: {ai_error}")
            traceback.print_exc()
        
        # 5. 실제 Theory Tools 호출 테스트
        print(f"\n--- 실제 Theory Tools 호출 테스트 ---")
        
        from app.tools.content.theory_tools import theory_generation_tool
        
        try:
            final_result = theory_generation_tool(
                chapter_data=test_chapter_data,
                user_type="beginner",
                learning_context=test_learning_context
            )
            
            print("✅ Theory Tools 호출 성공!")
            print(f"결과 타입: {type(final_result)}")
            
            # JSON 파싱 시도
            try:
                parsed_result = json.loads(final_result)
                print("✅ JSON 파싱 성공!")
                print(json.dumps(parsed_result, ensure_ascii=False, indent=2))
            except json.JSONDecodeError as parse_error:
                print(f"❌ JSON 파싱 실패: {parse_error}")
                print(f"원본 응답 (첫 500자): {final_result[:500]}...")
                print(f"원본 응답 (마지막 100자): ...{final_result[-100:]}")
                
        except Exception as theory_error:
            print(f"❌ Theory Tools 호출 실패: {theory_error}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ 전체 테스트 실패: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    test_theory_tools_detailed()