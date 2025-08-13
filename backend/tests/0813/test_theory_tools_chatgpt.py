# backend/tests/0812/test_theory_tools_chatgpt.py

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.tools.content.theory_tools_chatgpt import theory_generation_tool


class TestTheoryToolsChatGPT(unittest.TestCase):
    """ChatGPT 이론 생성 도구 테스트"""
    
    def test_import_success(self):
        """ChatGPT Theory Tools 임포트 테스트"""
        print("✅ ChatGPT Theory Tools 임포트 성공")
    
    @patch('app.tools.content.theory_tools_chatgpt.ChatGPTClient')
    def test_theory_generation_tool_structure(self, mock_chatgpt_client):
        """ChatGPT 이론 생성 도구 함수 구조 테스트"""
        
        # Mock ChatGPT 클라이언트 설정
        mock_client_instance = MagicMock()
        mock_client_instance.generate_content.return_value = "ChatGPT로 생성된 테스트 이론 설명입니다."
        mock_chatgpt_client.return_value = mock_client_instance
        
        # 테스트 파라미터
        section_data = {
            "title": "테스트 섹션",
            "theory": {
                "content": "테스트 이론 내용"
            }
        }
        user_type = "beginner"
        is_retry_session = False
        
        # 함수 실행
        result = theory_generation_tool(
            section_data=section_data,
            user_type=user_type,
            vector_materials=[],
            is_retry_session=is_retry_session
        )
        
        # 검증
        self.assertIsInstance(result, str)
        self.assertIn("ChatGPT로 생성된", result)
        
        # ChatGPT 클라이언트가 호출되었는지 확인
        mock_chatgpt_client.assert_called_once()
        mock_client_instance.generate_content.assert_called_once()
        
        print("✅ ChatGPT 이론 생성 도구 구조 테스트 통과")
    
    @patch('app.tools.content.theory_tools_chatgpt.ChatGPTClient')
    def test_theory_generation_beginner_user(self, mock_chatgpt_client):
        """초보자 사용자 타입 테스트"""
        
        # Mock 설정
        mock_client_instance = MagicMock()
        mock_client_instance.generate_content.return_value = "친근한 초보자용 설명 🙂"
        mock_chatgpt_client.return_value = mock_client_instance
        
        # 테스트 데이터
        section_data = {
            "title": "AI 기초",
            "theory": {
                "content": "인공지능의 기본 개념"
            }
        }
        
        # 함수 실행
        result = theory_generation_tool(
            section_data=section_data,
            user_type="beginner",
            vector_materials=[],
            is_retry_session=False
        )
        
        # 검증
        self.assertIsInstance(result, str)
        mock_client_instance.generate_content.assert_called_once()
        
        # 호출된 인자 확인
        call_args = mock_client_instance.generate_content.call_args
        system_instruction = call_args[1]['system_instruction']
        
        # 초보자용 지시사항이 포함되어 있는지 확인
        self.assertIn("친근한", system_instruction)
        self.assertIn("입문자", system_instruction)
        
        print("✅ 초보자 사용자 타입 테스트 통과")
    
    @patch('app.tools.content.theory_tools_chatgpt.ChatGPTClient')
    def test_theory_generation_advanced_user(self, mock_chatgpt_client):
        """고급 사용자 타입 테스트"""
        
        # Mock 설정
        mock_client_instance = MagicMock()
        mock_client_instance.generate_content.return_value = "효율적이고 체계적인 설명"
        mock_chatgpt_client.return_value = mock_client_instance
        
        # 테스트 데이터
        section_data = {
            "title": "머신러닝 알고리즘",
            "theory": {
                "content": "고급 머신러닝 개념"
            }
        }
        
        # 함수 실행
        result = theory_generation_tool(
            section_data=section_data,
            user_type="advanced",
            vector_materials=[],
            is_retry_session=False
        )
        
        # 검증
        self.assertIsInstance(result, str)
        mock_client_instance.generate_content.assert_called_once()
        
        # 호출된 인자 확인
        call_args = mock_client_instance.generate_content.call_args
        system_instruction = call_args[1]['system_instruction']
        
        # 고급 사용자용 지시사항이 포함되어 있는지 확인
        self.assertIn("효율적", system_instruction)
        self.assertIn("실무", system_instruction)
        
        print("✅ 고급 사용자 타입 테스트 통과")
    
    @patch('app.tools.content.theory_tools_chatgpt.ChatGPTClient')
    def test_theory_generation_retry_session(self, mock_chatgpt_client):
        """재학습 세션 테스트"""
        
        # Mock 설정
        mock_client_instance = MagicMock()
        mock_client_instance.generate_content.return_value = "더 쉽게 설명된 내용"
        mock_chatgpt_client.return_value = mock_client_instance
        
        # 테스트 데이터
        section_data = {
            "title": "딥러닝",
            "theory": {
                "content": "딥러닝 기본 개념"
            }
        }
        
        # 함수 실행 (재학습 세션)
        result = theory_generation_tool(
            section_data=section_data,
            user_type="beginner",
            vector_materials=[],
            is_retry_session=True
        )
        
        # 검증
        self.assertIsInstance(result, str)
        mock_client_instance.generate_content.assert_called_once()
        
        # 호출된 인자 확인
        call_args = mock_client_instance.generate_content.call_args
        system_instruction = call_args[1]['system_instruction']
        
        # 재학습 지시사항이 포함되어 있는지 확인
        self.assertIn("더 쉽게", system_instruction)
        
        print("✅ 재학습 세션 테스트 통과")
    
    @patch('app.tools.content.theory_tools_chatgpt.ChatGPTClient')
    def test_theory_generation_error_handling(self, mock_chatgpt_client):
        """오류 처리 테스트"""
        
        # Mock 설정 (오류 발생)
        mock_client_instance = MagicMock()
        mock_client_instance.generate_content.side_effect = Exception("ChatGPT API 오류")
        mock_chatgpt_client.return_value = mock_client_instance
        
        # 테스트 데이터
        section_data = {
            "title": "테스트 섹션",
            "theory": {
                "content": "테스트 내용"
            }
        }
        
        # 함수 실행
        result = theory_generation_tool(
            section_data=section_data,
            user_type="beginner",
            vector_materials=[],
            is_retry_session=False
        )
        
        # 검증 - fallback 응답이 반환되어야 함
        self.assertIsInstance(result, str)
        self.assertIn("문제가 발생했습니다", result)
        self.assertIn("테스트 섹션", result)
        
        print("✅ 오류 처리 테스트 통과")


if __name__ == '__main__':
    print("=" * 60)
    print("ChatGPT Theory Tools 테스트 시작")
    print("=" * 60)
    
    # 테스트 실행
    unittest.main(verbosity=2)