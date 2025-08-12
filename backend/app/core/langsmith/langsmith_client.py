# backend/app/core/langsmith/client.py
import os
import logging
from typing import Optional
from langsmith import Client

logger = logging.getLogger(__name__)

class LangSmithManager:
    """LangSmith 클라이언트 관리 클래스"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_enabled = False
        self._initialize()
    
    def _initialize(self):
        """LangSmith 클라이언트 초기화"""
        try:
            if os.getenv('LANGCHAIN_TRACING_V2', '').lower() == 'true':
                api_key = os.getenv('LANGCHAIN_API_KEY')
                if not api_key:
                    logger.warning("LANGCHAIN_API_KEY가 설정되지 않았습니다.")
                    return
                
                self.client = Client(
                    api_key=api_key,
                    api_url=os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
                )
                self.is_enabled = True
                logger.info("LangSmith 추적이 활성화되었습니다.")
            else:
                logger.info("LangSmith 추적이 비활성화되어 있습니다.")
        except Exception as e:
            logger.error(f"LangSmith 초기화 실패: {str(e)}")
            self.is_enabled = False
    
    def get_client(self) -> Optional[Client]:
        """LangSmith 클라이언트 반환"""
        return self.client if self.is_enabled else None
    
    def is_tracing_enabled(self) -> bool:
        """추적 활성화 여부 확인"""
        return self.is_enabled

# 전역 인스턴스
langsmith_manager = LangSmithManager()

def get_langsmith_client() -> Optional[Client]:
    """LangSmith 클라이언트 가져오기"""
    return langsmith_manager.get_client()

def is_langsmith_enabled() -> bool:
    """LangSmith 활성화 여부 확인"""
    return langsmith_manager.is_tracing_enabled()