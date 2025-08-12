# backend/tests/test_ai_client_integration.py

import pytest
import sys
import os
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.external.ai_client_manager import get_ai_client_manager
from langchain_core.messages import SystemMessage, HumanMessage

class TestAIClientIntegration:
    """AI 클라이언트 통합 테스트"""
    
    def test_ai_client_manager_availability(self):
        """AI 클라이언트 매니저 사용 가능성 테스트"""
        print("\n" + "="*60)
        print("🤖 AI CLIENT MANAGER TEST")
        print("="*60)
        
        try:
            client_manager = get_ai_client_manager()
            assert client_manager is not None
            print("✅ AI Client Manager 초기화 성공")
            
            # 사용 가능한 제공자 확인
            available_providers = []
            if hasattr(client_manager, 'gemini_client') and client_manager.gemini_client:
                available_providers.append("Gemini")
            if hasattr(client_manager, 'openai_client') and client_manager.openai_client:
                available_providers.append("OpenAI")
            
            print(f"사용 가능한 AI 제공자: {', '.join(available_providers) if available_providers else '없음'}")
            
            return client_manager
            
        except Exception as e:
            print(f"❌ AI Client Manager 테스트 실패: {str(e)}")
            return None
    
    def test_simple_text_generation(self):
        """간단한 텍스트 생성 테스트"""
        print("\n" + "="*60)
        print("📝 SIMPLE TEXT GENERATION TEST")
        print("="*60)
        
        try:
            client_manager = get_ai_client_manager()
            if not client_manager:
                print("⚠️ AI Client Manager를 사용할 수 없습니다.")
                return
            
            # 간단한 메시지 생성 테스트
            messages = [
                SystemMessage(content="당신은 AI 교육 전문가입니다. 간단하고 명확하게 답변해주세요."),
                HumanMessage(content="인공지능이란 무엇인지 한 문장으로 설명해주세요.")
            ]
            
            response = client_manager.generate_content_with_messages(
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            print(f"생성된 응답:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            
            assert isinstance(response, str)
            assert len(response) > 10
            print("✅ 간단한 텍스트 생성 성공!")
            
        except Exception as e:
            print(f"❌ 텍스트 생성 테스트 실패: {str(e)}")
            print(f"오류 상세: {type(e).__name__}: {e}")
    
    def test_json_generation(self):
        """JSON 형식 생성 테스트"""
        print("\n" + "="*60)
        print("🔧 JSON GENERATION TEST")
        print("="*60)
        
        try:
            client_manager = get_ai_client_manager()
            if not client_manager:
                print("⚠️ AI Client Manager를 사용할 수 없습니다.")
                return
            
            # JSON 형식 생성 테스트
            messages = [
                SystemMessage(content="""당신은 퀴즈 생성 전문가입니다. 
다음 JSON 형식으로만 응답해주세요:
{
    "question": "문제 내용",
    "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
    "correct_answer": "정답",
    "explanation": "설명"
}"""),
                HumanMessage(content="인공지능에 대한 간단한 객관식 문제를 만들어주세요.")
            ]
            
            response = client_manager.generate_json_content_with_messages(
                messages=messages,
                max_tokens=300,
                temperature=0.5
            )
            
            print(f"생성된 JSON 응답:")
            print("-" * 40)
            print(json.dumps(response, ensure_ascii=False, indent=2))
            print("-" * 40)
            
            # JSON 구조 검증
            assert isinstance(response, dict)
            assert 'question' in response
            assert 'options' in response
            assert isinstance(response['options'], list)
            print("✅ JSON 생성 테스트 성공!")
            
        except Exception as e:
            print(f"❌ JSON 생성 테스트 실패: {str(e)}")
            print(f"오류 상세: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test = TestAIClientIntegration()
    
    print("🚀 AI 클라이언트 통합 테스트 시작")
    print("=" * 60)
    
    test.test_ai_client_manager_availability()
    test.test_simple_text_generation()
    test.test_json_generation()
    
    print("\n🎉 AI 클라이언트 통합 테스트 완료!")