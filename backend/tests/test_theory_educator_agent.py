# backend/tests/test_theory_educator_agent.py

import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# agents.__init__.py를 거치지 않고 직접 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
from agents.theory_educator.agent import TheoryEducator
from tools.content.theory_tools import theory_generation_tool, _select_retry_section, _customize_content_for_user_type, _generate_user_guidance
from core.langraph.state_manager import TutorState, state_manager


class TestTheoryEducatorAgent:
    """TheoryEducator 에이전트 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 초기화"""
        self.theory_educator = TheoryEducator()
        self.sample_state = state_manager.initialize_state(
            user_id=1,
            user_type="beginner",
            current_chapter=1
        )
        
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
    
    @patch('app.agents.theory_educator.agent.theory_generation_tool')
    @patch.object(TheoryEducator, '_load_chapter_data')
    def test_process_success(self, mock_load_chapter, mock_theory_tool):
        """정상적인 이론 설명 생성 프로세스 테스트"""
        # Mock 설정
        mock_load_chapter.return_value = self.sample_chapter_data
        mock_theory_tool.return_value = json.dumps({
            "content_type": "theory",
            "main_content": "테스트 이론 설명 내용"
        })
        
        # 테스트 실행
        result_state = self.theory_educator.process(self.sample_state)
        
        # 검증
        assert result_state["theory_draft"] != ""
        assert "테스트 이론 설명 내용" in result_state["theory_draft"]
        assert result_state["session_progress_stage"] == "theory_completed"
        assert len(result_state["current_session_conversations"]) > 0
        
        # Mock 호출 검증
        mock_load_chapter.assert_called_once_with(1)
        mock_theory_tool.assert_called_once()
    
    @patch.object(TheoryEducator, '_load_chapter_data')
    def test_process_chapter_not_found(self, mock_load_chapter):
        """챕터 데이터를 찾을 수 없는 경우 테스트"""
        # Mock 설정 - 챕터 데이터 없음
        mock_load_chapter.return_value = None
        
        # 테스트 실행
        result_state = self.theory_educator.process(self.sample_state)
        
        # 검증 - 오류 상황에서도 State는 반환되어야 함
        assert result_state is not None
        assert "오류가 발생했습니다" in result_state["theory_draft"]
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_chapter_data_file_not_found(self, mock_open):
        """챕터 파일이 존재하지 않는 경우 테스트"""
        result = self.theory_educator._load_chapter_data(999)
        assert result is None
    
    @patch('builtins.open')
    @patch('json.load')
    def test_load_chapter_data_success(self, mock_json_load, mock_open):
        """챕터 데이터 로드 성공 테스트"""
        # Mock 설정
        mock_json_load.return_value = self.sample_chapter_data
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # 테스트 실행
        result = self.theory_educator._load_chapter_data(1)
        
        # 검증
        assert result == self.sample_chapter_data
        mock_open.assert_called_once()
        mock_json_load.assert_called_once_with(mock_file)
    
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


class TestTheoryTools:
    """theory_tools.py의 함수들 테스트 클래스"""
    
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


class TestStateManagerIntegration:
    """StateManager와의 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 초기화"""
        self.sample_state = state_manager.initialize_state(
            user_id=1,
            user_type="beginner",
            current_chapter=1
        )
    
    def test_update_agent_draft(self):
        """에이전트 대본 업데이트 테스트"""
        draft_content = "테스트 대본 내용"
        
        updated_state = state_manager.update_agent_draft(
            self.sample_state,
            "theory_educator",
            draft_content
        )
        
        assert updated_state["theory_draft"] == draft_content
        # 원본 state는 변경되지 않아야 함
        assert self.sample_state["theory_draft"] == ""
    
    def test_update_session_progress(self):
        """세션 진행 단계 업데이트 테스트"""
        updated_state = state_manager.update_session_progress(
            self.sample_state,
            "theory_educator"
        )
        
        assert updated_state["session_progress_stage"] == "theory_completed"
    
    def test_add_conversation(self):
        """대화 내용 추가 테스트"""
        updated_state = state_manager.add_conversation(
            self.sample_state,
            agent_name="theory_educator",
            message="테스트 메시지",
            message_type="system"
        )
        
        assert len(updated_state["current_session_conversations"]) == 1
        conversation = updated_state["current_session_conversations"][0]
        assert conversation["agent_name"] == "theory_educator"
        assert conversation["message"] == "테스트 메시지"
        assert conversation["message_type"] == "system"


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v"])