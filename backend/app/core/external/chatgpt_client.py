# backend/app/core/external/chatgpt_client.py

import os
import logging
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.utils.common.exceptions import ExternalAPIError


class ChatGPTClient:
    """
    ChatGPT API 클라이언트 (LangChain 기반)
    - 채팅 기능에 특화된 간소화된 인터페이스
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_client()
    
    def _initialize_client(self):
        """ChatGPT 클라이언트 초기화"""
        try:
            # 환경변수에서 API 키 로드
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            
            # 모델 설정 로드
            self.model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
            self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
            
            # LangChain ChatOpenAI 모델 생성
            self.llm = ChatOpenAI(
                model=self.model_name,
                openai_api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            self.logger.info(f"ChatGPT 클라이언트 초기화 완료 - 모델: {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"ChatGPT 클라이언트 초기화 실패: {str(e)}")
            raise ExternalAPIError(f"ChatGPT API 초기화 오류: {str(e)}")
    
    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        컨텐츠 생성
        
        Args:
            prompt: 사용자 프롬프트
            system_instruction: 시스템 지시사항
            temperature: 창의성 수준 (0.0-1.0)
            
        Returns:
            생성된 텍스트 응답
            
        Raises:
            ExternalAPIError: API 호출 실패 시
        """
        try:
            # 메시지 생성
            messages = []
            if system_instruction:
                messages.append(SystemMessage(content=system_instruction))
            messages.append(HumanMessage(content=prompt))
            
            self.logger.info(f"ChatGPT 호출 시작 - 모델: {self.model_name}")
            
            # 동적 temperature 설정
            if temperature is not None:
                original_temp = self.llm.temperature
                self.llm.temperature = temperature
                
                try:
                    response = self.llm.invoke(messages)
                finally:
                    self.llm.temperature = original_temp
            else:
                response = self.llm.invoke(messages)
            
            # 응답 검증
            if not response.content:
                raise ExternalAPIError("ChatGPT에서 빈 응답을 반환했습니다.")
            
            self.logger.info(f"ChatGPT 응답 수신 완료 - 길이: {len(response.content)}")
            return response.content
            
        except Exception as e:
            error_msg = f"ChatGPT 컨텐츠 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def test_connection(self) -> bool:
        """
        ChatGPT 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            test_response = self.generate_content(
                prompt="테스트 메시지입니다. '성공'이라고 답변해주세요.",
                temperature=0.1
            )
            
            success = "성공" in test_response or "success" in test_response.lower()
            self.logger.info(f"ChatGPT 연결 테스트 {'성공' if success else '실패'}")
            return success
            
        except Exception as e:
            self.logger.error(f"ChatGPT 연결 테스트 실패: {str(e)}")
            return False