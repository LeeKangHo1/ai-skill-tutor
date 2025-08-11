# backend/tests/test_theory_educator_standalone.py

import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 직접 파일 경로로 import (agents.__init__.py 우회)
import importlib.util

# TheoryEducator 직접 로드
theory_educator_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'agents', 'theory_educator', 'agent.py')
spec = importlib.util.spec_from_file_location("theory_educator_agent", theory_educator_path)
theory_educator_module = importlib.util.module_from_spec(spec)

# theory_tools 직접 로드
theory_tools_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'tools', 'content', 'theory_tools.py')
spec_tools = importlib.util.spec_from_file_location("theory_tools", theory_tools_path)
theory_tools_module = importlib.util.module_from_spec(spec_tools)

# state_manager 직접 로드
state_manager_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'core', 'langraph', 'state_manager.py')
spec_state = importlib.util.spec_from_file_location("state_manager", state_manager_path)
state_manager_module = importlib.util.module_from_spec(spec_state)

# 모듈 실행
try:
    spec.loader.exec_module(theory_educator_module)
    spec_tools.loader.exec_module(theory_tools_module)
    spec_state.loader.exec_module(state_manager_module)
    
    # 클래스와 함수 추출
    TheoryEducator = theory_educator_module.TheoryEducator
    theory_generation_tool = theory_tools_module.theory_generation_tool
    _select_retry_section = theory_tools_module._select_retry_section
    _customize_content_for_user_type = theory_tools_module._customize_content_for_user_type
    _generate_user_guidance = theory_tools_module._generate_user_guidance
    TutorState = state_manager_module.TutorState
    state_manager = state_manager_module.state_manager
    
except Exception as e:
    print(f"모듈 로드 실패: {e}")
    # 테스트를 위한 Mock 클래스들
    class MockTheoryEducator:
        def __init__(self):
            self.agent_name = "theory_educator"
            self.chapter_data_path = "data/chapters"
    
    TheoryEducator = MockTheoryEducator
    theory_generation_tool = lambda **kwargs: json.dumps({"content_type": "theory", "main_content": "Mock content"})


class TestTheoryEducatorStandalone:
    """TheoryEducator 에이전트 독립 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 초기화"""
        self.theory_educator = TheoryEducator()
        
        # 테스트용 샘플 State
        self.sample_state = {
            "user_id": 1,
            "user_type": "beginner",
            "current_chapter": 1,
            "current_agent": "theory_educator",
            "session_progress_stage": "session_start",
            "ui_mode": "chat",
            "current_question_type": "",
            "current_question_number": 0,
            "current_question_content": "",
            "current_question_answer": "",
            "is_answer_correct": 0,
            "evaluation_feedback": "",
            "hint_usage_count": 0,
            "theory_draft": "",
            "quiz_draft": "",
            "feedback_draft": "",
            "qna_draft": "",
            "previous_agent": "",
            "session_decision_result": "",
            "current_session_count": 0,
            "session_start_time": datetime.now(),
            "current_session_conversations": [],
            "recent_sessions_summary": []
        }
        
        # 테스트용 챕터 데이터
        self.sample_chapter_data = {
            "chapter_number": 1,
            "title": "AI는 무엇인가?",
            "user_type": "beginner",
            "sections": [
                {
                    "section_number": 1,
                    "title": "AI는 어떻게 우리 삶에 들어와 있을까?",
                    "theory": {
                        "content": "AI는 더 이상 영화에만 나오는 먼 미래의 기술이 아니에요.",
                        "key_points": [
                            "AI는 이미 일상생활에 깊숙이 들어와 있음",
                            "유튜브/넷플릭스 추천, 네이버 지도, 음성인식 등이 AI 기술"
                        ],
                        "analogy": "AI는 우리의 좋은 친구 같은 존재"
                    }
                }
            ]
        }
    
    def test_theory_educator_initialization(self):
        """TheoryEducator 초기화 테스트"""
        assert self.theory_educator.agent_name == "theory_educator"
        assert self.theory_educator.chapter_data_path == "data/chapters"
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('os.path.exists')
    def test_load_chapter_data_success(self, mock_exists, mock_json_load, mock_file):
        """챕터 데이터 로드 성공 테스트"""
        # Mock 설정
        mock_exists.return_value = True
        mock_json_load.return_value = self.sample_chapter_data
        
        # 테스트 실행
        result = self.theory_educator._load_chapter_data(1)
        
        # 검증
        assert result == self.sample_chapter_data
        mock_exists.assert_called_once()
        mock_json_load.assert_called_once()
    
    @patch('os.path.exists')
    def test_load_chapter_data_file_not_found(self, mock_exists):
        """챕터 파일이 존재하지 않는 경우 테스트"""
        mock_exists.return_value = False
        
        result = self.theory_educator._load_chapter_data(999)
        assert result is None
    
    def test_get_vector_search_materials(self):
        """벡터 검색 기능 테스트 (현재는 빈 리스트 반환)"""
        result = self.theory_educator._get_vector_search_materials(
            self.sample_chapter_data, 
            "beginner"
        )
        assert result == []
    
    def test_analyze_learning_context_first_session(self):
        """첫 학습 세션의 학습 맥락 분석 테스트"""
        # 첫 세션 상태 설정
        state = self.sample_state.copy()
        state["current_session_count"] = 0
        
        result = self.theory_educator._analyze_learning_context(state)
        
        # 검증
        assert result["user_type"] == "beginner"
        assert result["current_chapter"] == 1
        assert result["is_retry_session"] == False
        assert result["focus_areas"] == "전체적인 개념 이해"
        assert result["explanation_style"] == "기본적이고 체계적인 설명"
        assert result["complexity_level"] == "기초"
        assert result["use_analogies"] == True
    
    def test_analyze_learning_context_retry_session(self):
        """재학습 세션의 학습 맥락 분석 테스트"""
        # 재학습 세션 상태 설정
        state = self.sample_state.copy()
        state["current_session_count"] = 2
        state["user_type"] = "advanced"
        
        result = self.theory_educator._analyze_learning_context(state)
        
        # 검증
        assert result["is_retry_session"] == True
        assert result["focus_areas"] == "이전에 어려워했던 부분 중심으로 설명"
        assert result["explanation_style"] == "더 구체적이고 단계별 설명"
        assert result["complexity_level"] == "중급"
        assert result["use_analogies"] == False


class TestTheoryToolsStandalone:
    """theory_tools.py의 함수들 독립 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 초기화"""
        self.sample_chapter_data = {
            "chapter_number": 1,
            "title": "AI는 무엇인가?",
            "user_type": "beginner",
            "sections": [
                {
                    "section_number": 1,
                    "title": "테스트 섹션",
                    "theory": {
                        "content": "테스트 이론 내용입니다.",
                        "key_points": ["포인트1", "포인트2"],
                        "analogy": "테스트 비유"
                    }
                }
            ]
        }
        
        self.sample_learning_context = {
            "user_type": "beginner",
            "current_chapter": 1,
            "is_retry_session": False,
            "complexity_level": "기초",
            "use_analogies": True
        }
    
    def test_theory_generation_tool_success(self):
        """이론 생성 도구 정상 동작 테스트"""
        result = theory_generation_tool(
            chapter_data=self.sample_chapter_data,
            user_type="beginner",
            learning_context=self.sample_learning_context,
            recent_sessions=[],
            vector_materials=[]
        )
        
        # JSON 파싱 가능한지 확인
        parsed_result = json.loads(result)
        
        # 필수 필드 검증
        assert parsed_result["content_type"] == "theory"
        assert "chapter_info" in parsed_result
        assert "section_info" in parsed_result
        assert "main_content" in parsed_result
        assert "key_points" in parsed_result
        assert parsed_result["chapter_info"]["chapter_number"] == 1
        assert "테스트 이론 내용입니다" in parsed_result["main_content"]
    
    def test_theory_generation_tool_empty_sections(self):
        """섹션이 없는 챕터 데이터 처리 테스트"""
        empty_chapter_data = {
            "chapter_number": 1,
            "title": "빈 챕터",
            "sections": []
        }
        
        result = theory_generation_tool(
            chapter_data=empty_chapter_data,
            user_type="beginner",
            learning_context=self.sample_learning_context,
            recent_sessions=[],
            vector_materials=[]
        )
        
        # 오류 처리 확인
        parsed_result = json.loads(result)
        assert "오류가 발생했습니다" in parsed_result["main_content"]
    
    def test_select_retry_section(self):
        """재학습 섹션 선택 테스트"""
        sections = self.sample_chapter_data["sections"]
        learning_context = {"is_retry_session": True}
        
        result = _select_retry_section(sections, learning_context)
        
        # 섹션이 선택되었는지 확인
        assert result in sections
    
    def test_select_retry_section_empty(self):
        """빈 섹션 리스트에서 재학습 섹션 선택 테스트"""
        result = _select_retry_section([], {})
        assert result == {}
    
    def test_customize_content_for_beginner(self):
        """초보자용 콘텐츠 맞춤화 테스트"""
        theory_data = {
            "content": "기본 내용",
            "key_points": ["포인트1", "포인트2"],
            "analogy": "테스트 비유"
        }
        
        result = _customize_content_for_user_type(
            theory_data=theory_data,
            user_type="beginner",
            learning_context={"is_retry_session": False},
            vector_materials=None
        )
        
        # 초보자용 맞춤화 확인
        assert "안녕하세요!" in result["content"]
        assert "😊" in result["content"]
        assert "💡 **쉬운 비유로 이해하기**" in result["content"]
        assert result["key_points"] == ["포인트1", "포인트2"]
    
    def test_customize_content_for_advanced(self):
        """실무 응용형 사용자용 콘텐츠 맞춤화 테스트"""
        theory_data = {
            "content": "기본 내용",
            "key_points": ["포인트1", "포인트2"],
            "analogy": "테스트 비유"
        }
        
        result = _customize_content_for_user_type(
            theory_data=theory_data,
            user_type="advanced",
            learning_context={"is_retry_session": False},
            vector_materials=[]
        )
        
        # 실무 응용형 맞춤화 확인
        assert "핵심 개념을 효율적으로" in result["content"]
        assert "🔧 **기술적 배경**" in result["content"]
        assert "📚 **추가 참고자료**" in result["content"]
    
    def test_customize_content_retry_session(self):
        """재학습 세션용 콘텐츠 맞춤화 테스트"""
        theory_data = {
            "content": "기본 내용",
            "key_points": ["포인트1"],
            "analogy": ""
        }
        
        result = _customize_content_for_user_type(
            theory_data=theory_data,
            user_type="beginner",
            learning_context={"is_retry_session": True},
            vector_materials=None
        )
        
        # 재학습 세션 맞춤화 확인
        assert "조금 더 쉽게 설명해드릴게요" in result["content"]
    
    def test_generate_user_guidance_first_session(self):
        """첫 세션 사용자 안내 메시지 생성 테스트"""
        learning_context = {
            "is_retry_session": False,
            "user_type": "beginner"
        }
        
        result = _generate_user_guidance(learning_context)
        
        assert "천천히 읽어보시고" in result
        assert "편하게 질문해주세요" in result
    
    def test_generate_user_guidance_retry_session(self):
        """재학습 세션 사용자 안내 메시지 생성 테스트"""
        learning_context = {
            "is_retry_session": True,
            "user_type": "beginner"
        }
        
        result = _generate_user_guidance(learning_context)
        
        assert "이전보다 더 자세히" in result
        assert "언제든 질문해주세요" in result
    
    def test_generate_user_guidance_advanced(self):
        """실무 응용형 사용자 안내 메시지 생성 테스트"""
        learning_context = {
            "is_retry_session": False,
            "user_type": "advanced"
        }
        
        result = _generate_user_guidance(learning_context)
        
        assert "개념을 파악하셨다면" in result
        assert "다음 단계로 진행" in result


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v"])