# backend/app/core/external/gemini_client.py

import os
import json
import logging
from typing import Dict, Any, Optional, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.utils.common.exceptions import ExternalAPIError


class GeminiClient:
    """
    LangChain Google Gemini 클라이언트
    - LangChain ChatGoogleGenerativeAI 사용
    - 자동 LangSmith 추적 지원
    - JSON 출력 파서 통합
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_client()
    
    def _initialize_client(self):
        """LangChain Gemini 클라이언트 초기화"""
        try:
            # 환경변수에서 API 키 로드
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
            
            # 모델 설정 로드
            self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
            self.max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '8192'))
            self.temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
            
            # LangChain ChatGoogleGenerativeAI 모델 생성
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=api_key,
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                convert_system_message_to_human=True  # 시스템 메시지를 휴먼 메시지로 변환
            )
            
            # JSON 출력 파서
            self.json_parser = JsonOutputParser()
            
            self.logger.info(f"LangChain Gemini 클라이언트 초기화 완료 - 모델: {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"LangChain Gemini 클라이언트 초기화 실패: {str(e)}")
            raise ExternalAPIError(f"LangChain Gemini API 초기화 오류: {str(e)}")
    
    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        LangChain을 통해 컨텐츠 생성 (자동 LangSmith 추적)
        
        Args:
            prompt: 사용자 프롬프트
            system_instruction: 시스템 지시사항 (선택)
            temperature: 창의성 수준 (0.0-1.0)
            max_tokens: 최대 토큰 수
            
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
            
            self.logger.info(f"LangChain Gemini 호출 시작 - 모델: {self.model_name}")
            
            # LangChain을 통한 호출 (자동 LangSmith 추적)
            response = self.llm.invoke(messages)
            
            # 응답 검증
            if not response.content:
                raise ExternalAPIError("LangChain Gemini에서 빈 응답을 반환했습니다.")
            
            self.logger.info(f"LangChain Gemini 응답 수신 완료 - 길이: {len(response.content)}")
            return response.content
            
        except Exception as e:
            error_msg = f"LangChain Gemini 컨텐츠 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def generate_content_with_messages(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        LangChain Messages를 직접 사용한 컨텐츠 생성 (자동 LangSmith 추적)
        
        Args:
            messages: LangChain 메시지 리스트 (SystemMessage, HumanMessage 등)
            temperature: 창의성 수준 (0.0-1.0)
            max_tokens: 최대 토큰 수
            **kwargs: 추가 파라미터
            
        Returns:
            생성된 텍스트 응답
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            self.logger.info(f"LangChain Gemini Messages 호출 시작 - 메시지 수: {len(messages)}")
            
            # 동적으로 temperature 설정
            if temperature is not None:
                # 임시로 temperature 변경
                original_temp = self.llm.temperature
                self.llm.temperature = temperature
                
                try:
                    # LangChain을 통한 직접 호출 (자동 LangSmith 추적)
                    response = self.llm.invoke(messages)
                finally:
                    # temperature 복원
                    self.llm.temperature = original_temp
            else:
                # LangChain을 통한 직접 호출 (자동 LangSmith 추적)
                response = self.llm.invoke(messages)
            
            # 응답 검증
            if not response.content:
                raise ExternalAPIError("LangChain Gemini에서 빈 응답을 반환했습니다.")
            
            self.logger.info(f"LangChain Gemini Messages 응답 수신 완료 - 길이: {len(response.content)}")
            return response.content
                
        except Exception as e:
            error_msg = f"LangChain Messages 기반 컨텐츠 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def generate_json_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        JSON 형태 응답을 위한 컨텐츠 생성
        
        Args:
            prompt: 사용자 프롬프트
            system_instruction: 시스템 지시사항 (선택)
            temperature: 창의성 수준 (0.0-1.0)
            max_tokens: 최대 토큰 수
            
        Returns:
            JSON 형태로 파싱된 응답
            
        Raises:
            ExternalAPIError: 생성 또는 파싱 실패 시
        """
        try:
            # JSON 전용 시스템 지시사항 준비
            json_system_instruction = (
                "반드시 유효한 JSON 형식으로만 응답해주세요. "
                "추가적인 설명이나 마크다운 포맷팅은 사용하지 마세요.\n"
                f"{system_instruction or ''}"
            )
            
            # 프롬프트에 JSON 형태 요청 추가
            json_prompt = f"{prompt}\n\n응답은 반드시 유효한 JSON 형태로만 제공해주세요."
            
            # 컨텐츠 생성
            response_text = self.generate_content(
                prompt=json_prompt,
                system_instruction=json_system_instruction,
                temperature=temperature
            )
            
            # JSON 파싱 시도
            try:
                # 응답에서 JSON 부분만 추출 (```json 등의 마크다운 제거)
                cleaned_response = self._extract_json_from_response(response_text)
                parsed_response = json.loads(cleaned_response)
                
                self.logger.info("JSON 응답 파싱 성공")
                return parsed_response
                
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON 파싱 실패: {str(e)}")
                self.logger.error(f"원본 응답: {response_text}")
                raise ExternalAPIError(f"Gemini API 응답을 JSON으로 파싱할 수 없습니다: {str(e)}")
            
        except ExternalAPIError:
            raise
        except Exception as e:
            error_msg = f"JSON 컨텐츠 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def generate_json_content_with_messages(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        LangChain Messages를 사용한 JSON 컨텐츠 생성 (자동 LangSmith 추적)
        
        Args:
            messages: LangChain 메시지 리스트 (SystemMessage, HumanMessage 등)
            temperature: 창의성 수준 (0.0-1.0)
            max_tokens: 최대 토큰 수
            **kwargs: 추가 파라미터
            
        Returns:
            JSON 형태로 파싱된 응답
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            # JSON 출력을 위한 시스템 메시지 추가/수정
            enhanced_messages = []
            system_found = False
            
            for message in messages:
                if isinstance(message, SystemMessage):
                    # 기존 시스템 메시지에 JSON 지시사항 추가
                    json_instruction = (
                        f"{message.content}\n\n"
                        "**중요**: 반드시 유효한 JSON 형식으로만 응답해주세요. "
                        "추가적인 설명이나 마크다운 포맷팅은 사용하지 마세요."
                    )
                    enhanced_messages.append(SystemMessage(content=json_instruction))
                    system_found = True
                else:
                    enhanced_messages.append(message)
            
            # 시스템 메시지가 없으면 JSON 전용 시스템 메시지 추가
            if not system_found:
                json_system_msg = SystemMessage(
                    content="반드시 유효한 JSON 형식으로만 응답해주세요. "
                           "추가적인 설명이나 마크다운 포맷팅은 사용하지 마세요."
                )
                enhanced_messages.insert(0, json_system_msg)
            
            self.logger.info(f"LangChain Gemini JSON 생성 시작 - 메시지 수: {len(enhanced_messages)}")
            
            # 동적으로 temperature 설정
            if temperature is not None:
                original_temp = self.llm.temperature
                self.llm.temperature = temperature
                
                try:
                    # LangChain + JSON Parser 체인 생성 및 실행 (자동 LangSmith 추적)
                    chain = self.llm | self.json_parser
                    response = chain.invoke(enhanced_messages)
                finally:
                    self.llm.temperature = original_temp
            else:
                # LangChain + JSON Parser 체인 생성 및 실행 (자동 LangSmith 추적)
                chain = self.llm | self.json_parser
                response = chain.invoke(enhanced_messages)
            
            self.logger.info("LangChain Gemini JSON 생성 완료")
            return response
                
        except Exception as e:
            error_msg = f"LangChain JSON 컨텐츠 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            
            # Fallback: 일반 텍스트로 생성 후 JSON 파싱 시도
            try:
                self.logger.info("JSON 파싱 실패, 일반 텍스트로 재시도")
                text_response = self.generate_content_with_messages(messages, temperature, max_tokens)
                
                # JSON 추출 시도
                cleaned_response = self._extract_json_from_response(text_response)
                parsed_response = json.loads(cleaned_response)
                
                self.logger.info("Fallback JSON 파싱 성공")
                return parsed_response
                
            except Exception as fallback_error:
                self.logger.error(f"Fallback JSON 파싱도 실패: {str(fallback_error)}")
                raise ExternalAPIError(f"JSON 컨텐츠 생성 완전 실패: {error_msg}")
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """
        응답 텍스트에서 JSON 부분만 추출
        
        Args:
            response_text: 원본 응답 텍스트
            
        Returns:
            정제된 JSON 문자열
        """
        # 마크다운 코드 블록 제거
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end != -1:
                return response_text[start:end].strip()
        
        # 첫 번째 { 부터 마지막 } 까지 추출
        start = response_text.find('{')
        end = response_text.rfind('}')
        
        if start != -1 and end != -1 and start < end:
            return response_text[start:end+1]
        
        # JSON 형태를 찾을 수 없으면 원본 반환
        return response_text.strip()
    
    def test_connection(self) -> bool:
        """
        LangChain Gemini 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            test_response = self.generate_content(
                prompt="테스트 메시지입니다. '성공'이라고 답변해주세요.",
                temperature=0.1
            )
            
            success = "성공" in test_response or "success" in test_response.lower()
            self.logger.info(f"LangChain Gemini 연결 테스트 {'성공' if success else '실패'}")
            return success
            
        except Exception as e:
            self.logger.error(f"LangChain Gemini 연결 테스트 실패: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        현재 설정된 모델 정보 반환
        
        Returns:
            모델 설정 정보
        """
        return {
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "provider": "LangChain Google Gemini",
            "langsmith_tracing": "자동 추적 활성화"
        }