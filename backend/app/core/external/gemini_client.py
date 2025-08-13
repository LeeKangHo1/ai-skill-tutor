# backend/app/core/external/gemini_client.py

import os
import logging
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from app.utils.common.exceptions import ExternalAPIError


class GeminiClient:
    """
    Google Gemini API 클라이언트 (LangChain 기반)
    - 시스템 메시지를 휴먼 메시지로 자동 변환
    - 간소화된 인터페이스 제공
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_client()
    
    def _initialize_client(self):
        """Gemini 클라이언트 초기화"""
        try:
            # 환경변수에서 API 키 로드
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
            
            # 모델 설정 로드
            self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            self.max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '8192'))
            self.temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
            
            # LangChain ChatGoogleGenerativeAI 모델 생성 (경고 제거)
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=api_key,
                temperature=self.temperature,
                max_output_tokens=self.max_tokens
            )
            
            self.logger.info(f"Gemini 클라이언트 초기화 완료 - 모델: {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"Gemini 클라이언트 초기화 실패: {str(e)}")
            raise ExternalAPIError(f"Gemini API 초기화 오류: {str(e)}")
    
    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        컨텐츠 생성 (시스템 메시지를 휴먼 메시지로 통합)
        
        Args:
            prompt: 사용자 프롬프트
            system_instruction: 시스템 지시사항 (휴먼 메시지로 변환됨)
            temperature: 창의성 수준 (0.0-1.0)
            
        Returns:
            생성된 텍스트 응답
            
        Raises:
            ExternalAPIError: API 호출 실패 시
        """
        try:
            # 시스템 지시사항과 사용자 프롬프트를 하나의 휴먼 메시지로 통합
            if system_instruction:
                combined_prompt = f"{system_instruction}\n\n{prompt}"
            else:
                combined_prompt = prompt
            
            # 휴먼 메시지 생성
            message = HumanMessage(content=combined_prompt)
            
            self.logger.info(f"Gemini 호출 시작 - 모델: {self.model_name}")
            
            # 동적 temperature 설정
            if temperature is not None:
                original_temp = self.llm.temperature
                self.llm.temperature = temperature
                
                try:
                    response = self.llm.invoke([message])
                finally:
                    self.llm.temperature = original_temp
            else:
                response = self.llm.invoke([message])
            
            # 응답 검증
            if not response.content:
                raise ExternalAPIError("Gemini에서 빈 응답을 반환했습니다.")
            
            self.logger.info(f"Gemini 응답 수신 완료 - 길이: {len(response.content)}")
            return response.content
            
        except Exception as e:
            error_msg = f"Gemini 컨텐츠 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def test_connection(self) -> bool:
        """
        Gemini 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            test_response = self.generate_content(
                prompt="테스트 메시지입니다. '성공'이라고 답변해주세요.",
                temperature=0.1
            )
            
            success = "성공" in test_response or "success" in test_response.lower()
            self.logger.info(f"Gemini 연결 테스트 {'성공' if success else '실패'}")
            return success
            
        except Exception as e:
            self.logger.error(f"Gemini 연결 테스트 실패: {str(e)}")
            return False