# backend/app/core/external/gemini_client.py

import os
import json
import logging
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.utils.common.exceptions import ExternalAPIError


class GeminiClient:
    """
    Google Gemini API 클라이언트
    - 프롬프트 전송 및 응답 처리
    - 에러 처리 및 재시도 로직
    - 설정 관리 및 안전 필터링
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_client()
    
    def _initialize_client(self):
        """Gemini API 클라이언트 초기화"""
        try:
            # 환경변수에서 API 키 로드 (.env.example 형식에 맞춤)
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
            
            # Gemini API 설정
            genai.configure(api_key=api_key)
            
            # 모델 설정 로드 (.env.example 형식에 맞춤)
            self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            self.max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '8192'))
            self.temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
            
            # 모델 인스턴스 생성
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
            
            self.logger.info(f"Gemini 클라이언트 초기화 완료 - 모델: {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"Gemini 클라이언트 초기화 실패: {str(e)}")
            raise ExternalAPIError(f"Gemini API 초기화 오류: {str(e)}")
    
    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Gemini API를 통해 컨텐츠 생성
        
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
            # 파라미터 설정
            gen_temperature = temperature if temperature is not None else self.temperature
            gen_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
            
            # 시스템 지시사항이 있는 경우 프롬프트에 포함
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            self.logger.info(f"Gemini API 호출 시작 - 모델: {self.model_name}")
            self.logger.debug(f"프롬프트 길이: {len(full_prompt)}")
            
            # Gemini API 호출
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=gen_temperature,
                    max_output_tokens=gen_max_tokens,
                    candidate_count=1
                )
            )
            
            # 응답 검증
            if not response.text:
                raise ExternalAPIError("Gemini API에서 빈 응답을 반환했습니다.")
            
            self.logger.info("Gemini API 호출 성공")
            return response.text.strip()
            
        except Exception as e:
            error_msg = f"Gemini API 호출 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def generate_json_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        JSON 형태의 구조화된 응답 생성
        
        Args:
            prompt: 사용자 프롬프트
            system_instruction: 시스템 지시사항
            temperature: 창의성 수준
            
        Returns:
            JSON 형태로 파싱된 응답
            
        Raises:
            ExternalAPIError: API 호출 또는 JSON 파싱 실패 시
        """
        try:
            # JSON 응답 요청을 위한 시스템 지시사항 추가
            json_system_instruction = (
                "응답은 반드시 유효한 JSON 형태로만 제공해주세요. "
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
        Gemini API 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            test_response = self.generate_content(
                prompt="테스트 메시지입니다. '성공'이라고 답변해주세요.",
                temperature=0.1
            )
            
            success = "성공" in test_response or "success" in test_response.lower()
            self.logger.info(f"Gemini API 연결 테스트 {'성공' if success else '실패'}")
            return success
            
        except Exception as e:
            self.logger.error(f"Gemini API 연결 테스트 실패: {str(e)}")
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
            "provider": "Google Gemini"
        }