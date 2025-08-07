# backend/app/core/external/chatgpt_client.py
"""
ChatGPT API 클라이언트 모듈
OpenAI API를 통한 ChatGPT 및 임베딩 서비스 연동을 관리합니다.
"""

import openai
from typing import List, Dict, Any, Optional
import os
import asyncio

class ChatGPTClient:
    """ChatGPT API 클라이언트 클래스"""
    
    def __init__(self):
        """ChatGPT 클라이언트 초기화"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # 기본 모델 설정
        self.chat_model = os.getenv('OPENAI_CHAT_MODEL', 'gpt-4o-mini')
        self.embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
    
    def generate_chat_completion(self, messages: List[Dict[str, str]], 
                               model: Optional[str] = None,
                               temperature: float = 0.7,
                               max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        ChatGPT를 사용하여 채팅 완성을 생성합니다.
        
        Args:
            messages (List[Dict[str, str]]): 대화 메시지 목록
            model (Optional[str]): 사용할 모델 (기본값: self.chat_model)
            temperature (float): 창의성 수준 (0.0-2.0)
            max_tokens (Optional[int]): 최대 토큰 수
            
        Returns:
            Dict[str, Any]: ChatGPT 응답
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.chat_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'usage': response.usage.model_dump() if response.usage else None,
                'model': response.model
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': None
            }
    
    def generate_embeddings(self, texts: List[str], 
                          model: Optional[str] = None) -> Dict[str, Any]:
        """
        텍스트 목록에 대한 임베딩을 생성합니다.
        
        Args:
            texts (List[str]): 임베딩할 텍스트 목록
            model (Optional[str]): 사용할 임베딩 모델
            
        Returns:
            Dict[str, Any]: 임베딩 결과
        """
        try:
            response = self.client.embeddings.create(
                model=model or self.embedding_model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            
            return {
                'success': True,
                'embeddings': embeddings,
                'usage': response.usage.model_dump() if response.usage else None,
                'model': response.model
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'embeddings': None
            }
    
    def generate_single_embedding(self, text: str, 
                                model: Optional[str] = None) -> Dict[str, Any]:
        """
        단일 텍스트에 대한 임베딩을 생성합니다.
        
        Args:
            text (str): 임베딩할 텍스트
            model (Optional[str]): 사용할 임베딩 모델
            
        Returns:
            Dict[str, Any]: 임베딩 결과
        """
        result = self.generate_embeddings([text], model)
        
        if result['success'] and result['embeddings']:
            result['embedding'] = result['embeddings'][0]
        
        return result
    
    async def generate_chat_completion_async(self, messages: List[Dict[str, str]], 
                                           model: Optional[str] = None,
                                           temperature: float = 0.7,
                                           max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        비동기적으로 ChatGPT 채팅 완성을 생성합니다.
        
        Args:
            messages (List[Dict[str, str]]): 대화 메시지 목록
            model (Optional[str]): 사용할 모델
            temperature (float): 창의성 수준
            max_tokens (Optional[int]): 최대 토큰 수
            
        Returns:
            Dict[str, Any]: ChatGPT 응답
        """
        # 동기 함수를 비동기로 실행
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.generate_chat_completion,
            messages, model, temperature, max_tokens
        )
    
    def validate_api_key(self) -> bool:
        """
        API 키의 유효성을 검증합니다.
        
        Returns:
            bool: API 키 유효성 여부
        """
        try:
            # 간단한 API 호출로 키 유효성 확인
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False