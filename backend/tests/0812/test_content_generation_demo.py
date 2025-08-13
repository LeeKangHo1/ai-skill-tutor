# backend/tests/test_content_generation_demo.py

import pytest
import sys
import os
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.tools.content.theory_tools_gemini import theory_generation_tool
from app.tools.content.quiz_tools import quiz_generation_tool

class TestContentGenerationDemo:
    """컨텐츠 생성 데모 테스트 (API 키 필요)"""
    
    def setup_method(self):
        """테스트 전 설정"""
        # API 키 확인
        self.has_gemini_key = bool(os.getenv('GEMINI_API_KEY'))
        self.has_openai_key = bool(os.getenv('OPENAI_API_KEY'))
        
        print(f"\n🔑 API 키 상태:")
        print(f"   Gemini API Key: {'✅ 설정됨' if self.has_gemini_key else '❌ 없음'}")
        print(f"   OpenAI API Key: {'✅ 설정됨' if self.has_openai_key else '❌ 없음'}")
        
        # 테스트용 챕터 데이터
        self.test_chapter_data = {
            "id": 1,
            "title": "AI 기초 개념",
            "description": "인공지능의 기본 개념과 머신러닝 입문",
            "sections": [
                {
                    "section_number": 1,
                    "title": "인공지능이란 무엇인가?",
                    "content": "인공지능(AI)은 인간의 지능을 모방하여 학습, 추론, 문제해결 등을 수행하는 컴퓨터 시스템입니다. AI는 데이터를 분석하고 패턴을 찾아 예측하거나 결정을 내릴 수 있습니다.",
                    "quiz_type": "multiple_choice",
                    "learning_objectives": [
                        "AI의 정의를 이해한다",
                        "AI의 주요 특징을 설명할 수 있다",
                        "AI와 일반 프로그램의 차이점을 구분한다"
                    ]
                }
            ]
        }
        
        self.test_user_type = "beginner"
        self.test_learning_context = {
            "current_section": 1,
            "user_level": "beginner",
            "previous_topics": [],
            "session_count": 1,
            "is_retry_session": False
        }
    
    def test_api_key_status(self):
        """API 키 상태 확인"""
        print("\n" + "="*80)
        print("🔑 API KEY STATUS CHECK")
        print("="*80)
        
        if not self.has_gemini_key and not self.has_openai_key:
            print("⚠️ 경고: API 키가 설정되지 않았습니다.")
            print("실제 LLM 호출 테스트를 위해서는 다음 중 하나 이상의 API 키가 필요합니다:")
            print("  - GEMINI_API_KEY")
            print("  - OPENAI_API_KEY")
            print("\n.env 파일에 API 키를 설정하고 다시 실행해주세요.")
            return False
        
        print("✅ API 키가 설정되어 있습니다. 실제 LLM 호출 테스트를 진행합니다.")
        return True
    
    def test_theory_generation_demo(self):
        """이론 생성 데모 테스트"""
        print("\n" + "="*80)
        print("🧠 THEORY GENERATION DEMO")
        print("="*80)
        
        if not self.test_api_key_status():
            print("⏭️ API 키가 없어 데모를 건너뜁니다.")
            return
        
        try:
            print(f"📚 챕터: {self.test_chapter_data['title']}")
            print(f"📖 섹션: {self.test_chapter_data['sections'][0]['title']}")
            print(f"👤 사용자 유형: {self.test_user_type}")
            print(f"⏰ 생성 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n🔄 이론 컨텐츠 생성 중...")
            
            result = theory_generation_tool(
                chapter_data=self.test_chapter_data,
                user_type=self.test_user_type,
                learning_context=self.test_learning_context
            )
            
            print(f"\n📝 생성된 이론 컨텐츠:")
            print("=" * 80)
            print(result)
            print("=" * 80)
            
            # 컨텐츠 분석
            word_count = len(result.split())
            char_count = len(result)
            
            print(f"\n📊 컨텐츠 분석:")
            print(f"   총 문자 수: {char_count:,}")
            print(f"   총 단어 수: {word_count:,}")
            print(f"   평균 문장 길이: {char_count // max(result.count('.'), 1)} 문자")
            
            # 키워드 분석
            keywords = ['AI', '인공지능', '머신러닝', '학습', '데이터', '알고리즘']
            found_keywords = [kw for kw in keywords if kw in result]
            print(f"   포함된 키워드: {', '.join(found_keywords) if found_keywords else '없음'}")
            
            print("✅ 이론 생성 데모 완료!")
            
        except Exception as e:
            print(f"❌ 이론 생성 실패: {str(e)}")
            print(f"오류 타입: {type(e).__name__}")
            if hasattr(e, '__dict__'):
                print(f"오류 상세: {e.__dict__}")
    
    def test_quiz_generation_demo(self):
        """퀴즈 생성 데모 테스트"""
        print("\n" + "="*80)
        print("🧩 QUIZ GENERATION DEMO")
        print("="*80)
        
        if not self.test_api_key_status():
            print("⏭️ API 키가 없어 데모를 건너뜁니다.")
            return
        
        try:
            # 객관식 퀴즈 생성
            quiz_context = self.test_learning_context.copy()
            quiz_context["quiz_type"] = "multiple_choice"
            
            print(f"🧩 퀴즈 유형: 객관식")
            print(f"📚 기반 챕터: {self.test_chapter_data['title']}")
            print(f"⏰ 생성 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n🔄 객관식 퀴즈 생성 중...")
            
            result = quiz_generation_tool(
                chapter_data=self.test_chapter_data,
                user_type=self.test_user_type,
                learning_context=quiz_context
            )
            
            print(f"\n🧩 생성된 퀴즈 컨텐츠:")
            print("=" * 80)
            print(result)
            print("=" * 80)
            
            # JSON 파싱 시도
            try:
                quiz_data = json.loads(result)
                self._display_quiz_analysis(quiz_data, "객관식")
            except json.JSONDecodeError as json_error:
                print(f"⚠️ JSON 파싱 실패: {json_error}")
                print("생성된 컨텐츠가 올바른 JSON 형식이 아닙니다.")
                self._analyze_raw_content(result)
            
            print("✅ 객관식 퀴즈 생성 데모 완료!")
            
        except Exception as e:
            print(f"❌ 퀴즈 생성 실패: {str(e)}")
            print(f"오류 타입: {type(e).__name__}")
    
    def test_subjective_quiz_demo(self):
        """주관식 퀴즈 생성 데모 테스트"""
        print("\n" + "="*80)
        print("📝 SUBJECTIVE QUIZ GENERATION DEMO")
        print("="*80)
        
        if not self.test_api_key_status():
            print("⏭️ API 키가 없어 데모를 건너뜁니다.")
            return
        
        try:
            # 주관식 퀴즈 생성
            subjective_context = self.test_learning_context.copy()
            subjective_context["quiz_type"] = "subjective"
            
            print(f"📝 퀴즈 유형: 주관식")
            print(f"📚 기반 챕터: {self.test_chapter_data['title']}")
            print(f"⏰ 생성 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n🔄 주관식 퀴즈 생성 중...")
            
            result = quiz_generation_tool(
                chapter_data=self.test_chapter_data,
                user_type=self.test_user_type,
                learning_context=subjective_context
            )
            
            print(f"\n📝 생성된 주관식 퀴즈:")
            print("=" * 80)
            print(result)
            print("=" * 80)
            
            # JSON 파싱 시도
            try:
                quiz_data = json.loads(result)
                self._display_quiz_analysis(quiz_data, "주관식")
            except json.JSONDecodeError:
                print("⚠️ JSON 파싱 실패 - 원시 컨텐츠 분석")
                self._analyze_raw_content(result)
            
            print("✅ 주관식 퀴즈 생성 데모 완료!")
            
        except Exception as e:
            print(f"❌ 주관식 퀴즈 생성 실패: {str(e)}")
    
    def _display_quiz_analysis(self, quiz_data: dict, quiz_type: str):
        """퀴즈 데이터 분석 표시"""
        print(f"\n📊 {quiz_type} 퀴즈 분석:")
        print(f"   문제 유형: {quiz_data.get('type', 'N/A')}")
        print(f"   문제 길이: {len(quiz_data.get('question', ''))} 문자")
        
        if quiz_type == "객관식":
            options = quiz_data.get('options', [])
            print(f"   선택지 개수: {len(options)}")
            if options:
                avg_option_length = sum(len(opt) for opt in options) / len(options)
                print(f"   평균 선택지 길이: {avg_option_length:.1f} 문자")
            print(f"   정답: {quiz_data.get('correct_answer', 'N/A')}")
        else:
            print(f"   예시 답안 길이: {len(quiz_data.get('sample_answer', ''))} 문자")
        
        print(f"   설명 길이: {len(quiz_data.get('explanation', ''))} 문자")
        print(f"   힌트 길이: {len(quiz_data.get('hint', ''))} 문자")
    
    def _analyze_raw_content(self, content: str):
        """원시 컨텐츠 분석"""
        print(f"\n📊 원시 컨텐츠 분석:")
        print(f"   총 길이: {len(content)} 문자")
        print(f"   줄 수: {content.count(chr(10)) + 1}")
        print(f"   단어 수: {len(content.split())}")

if __name__ == "__main__":
    test = TestContentGenerationDemo()
    test.setup_method()
    
    print("🚀 컨텐츠 생성 데모 테스트 시작")
    print("=" * 80)
    
    # API 키 상태 확인
    if test.test_api_key_status():
        # 실제 LLM 호출 테스트들
        test.test_theory_generation_demo()
        test.test_quiz_generation_demo()
        test.test_subjective_quiz_demo()
    else:
        print("\n💡 API 키 설정 방법:")
        print("1. backend/.env 파일을 생성하거나 편집")
        print("2. 다음 중 하나 이상의 API 키 추가:")
        print("   GEMINI_API_KEY=your_gemini_api_key_here")
        print("   OPENAI_API_KEY=your_openai_api_key_here")
        print("3. 테스트 다시 실행")
    
    print("\n🎉 컨텐츠 생성 데모 테스트 완료!")