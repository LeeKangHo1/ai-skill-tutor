# backend/debug_ai_client.py

import sys
import os
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment_variables():
    """환경변수 확인"""
    print("=== 환경변수 확인 ===")
    
    # .env 파일 로드
    from dotenv import load_dotenv
    load_dotenv()
    
    # AI API 키 확인
    gemini_key = os.getenv('GOOGLE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"GOOGLE_API_KEY: {'설정됨' if gemini_key else '❌ 없음'}")
    print(f"OPENAI_API_KEY: {'설정됨' if openai_key else '❌ 없음'}")
    
    if gemini_key:
        print(f"Gemini 키 앞 4자리: {gemini_key[:4]}...")
    
    return gemini_key, openai_key

def test_ai_client_initialization():
    """AI 클라이언트 초기화 테스트"""
    print("\n=== AI 클라이언트 초기화 테스트 ===")
    
    try:
        from app.core.external.ai_client_manager import get_ai_client_manager
        
        client_manager = get_ai_client_manager()
        print("✅ AI Client Manager 초기화 성공")
        
        # 사용 가능한 클라이언트 확인
        available_providers = client_manager.get_available_providers()
        print(f"사용 가능한 제공자: {available_providers}")
        
        # 연결 테스트
        connection_status = client_manager.test_all_connections()
        print(f"연결 상태: {connection_status}")
        
        return client_manager
        
    except Exception as e:
        print(f"❌ AI Client Manager 초기화 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_simple_generation(client_manager):
    """간단한 텍스트 생성 테스트"""
    print("\n=== 간단한 텍스트 생성 테스트 ===")
    
    if not client_manager:
        print("❌ 클라이언트 매니저가 없어서 테스트 불가")
        return
    
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # 간단한 메시지 테스트
        messages = [
            SystemMessage(content="간단하게 답변해주세요."),
            HumanMessage(content="안녕하세요! 테스트입니다.")
        ]
        
        # 텍스트 생성 시도
        response = client_manager.generate_content_with_messages(messages)
        print(f"✅ 텍스트 생성 성공:")
        print(f"응답: {response}")
        
    except Exception as e:
        print(f"❌ 텍스트 생성 실패: {str(e)}")
        import traceback
        traceback.print_exc()

def test_json_generation(client_manager):
    """JSON 생성 테스트"""
    print("\n=== JSON 생성 테스트 ===")
    
    if not client_manager:
        print("❌ 클라이언트 매니저가 없어서 테스트 불가")
        return
    
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # JSON 형식 요청
        messages = [
            SystemMessage(content="""다음 JSON 형식으로만 응답해주세요:
{
  "test": "성공",
  "message": "간단한 테스트 메시지"
}"""),
            HumanMessage(content="JSON 테스트를 위한 간단한 응답을 생성해주세요.")
        ]
        
        # JSON 생성 시도
        response = client_manager.generate_json_content_with_messages(messages)
        print(f"✅ JSON 생성 성공:")
        print(f"응답 타입: {type(response)}")
        if isinstance(response, dict):
            print(f"JSON 내용: {json.dumps(response, ensure_ascii=False, indent=2)}")
        else:
            print(f"원본 응답: {response}")
        
    except Exception as e:
        print(f"❌ JSON 생성 실패: {str(e)}")
        import traceback
        traceback.print_exc()

def test_theory_generation():
    """Theory Tools 테스트"""
    print("\n=== Theory Tools 테스트 ===")
    
    try:
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
        
        # Theory generation tool 실행
        from backend.app.tools.content.theory_tools_gemini import theory_generation_tool
        
        result = theory_generation_tool(
            chapter_data=test_chapter_data,
            user_type="beginner",
            learning_context=test_learning_context
        )
        
        print("✅ Theory Tools 실행 성공")
        
        # 결과 파싱 시도
        try:
            result_json = json.loads(result)
            print("✅ JSON 파싱 성공")
            print(json.dumps(result_json, ensure_ascii=False, indent=2))
        except json.JSONDecodeError as parse_error:
            print(f"❌ JSON 파싱 실패: {parse_error}")
            print(f"원본 응답 (첫 200자): {result[:200]}...")
        
    except Exception as e:
        print(f"❌ Theory Tools 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """메인 디버깅 함수"""
    print("🔍 AI 클라이언트 디버깅 시작")
    print("=" * 60)
    
    # 1. 환경변수 확인
    gemini_key, openai_key = test_environment_variables()
    
    # 2. AI 클라이언트 초기화
    client_manager = test_ai_client_initialization()
    
    # 3. 간단한 텍스트 생성
    test_simple_generation(client_manager)
    
    # 4. JSON 생성 테스트
    test_json_generation(client_manager)
    
    # 5. Theory Tools 테스트
    test_theory_generation()
    
    print("\n🎯 디버깅 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()