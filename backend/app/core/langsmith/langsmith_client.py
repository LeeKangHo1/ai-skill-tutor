# backend/app/core/langsmith/langsmith_client.py

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LangSmithManager:
    """
    LangSmith 환경변수 관리 클래스 (LangChain 자동 추적 전용)
    - 수동 추적 제거, 환경변수 확인만 담당
    - LangChain이 자동으로 모든 추적 관리
    """
    
    def __init__(self):
        self.is_enabled = False
        self._check_environment()
    
    def _check_environment(self):
        """LangChain 자동 추적을 위한 환경변수 확인"""
        try:
            # 환경변수 확인
            tracing_env = os.getenv('LANGCHAIN_TRACING_V2', '').lower()
            
            if tracing_env == 'true':
                api_key = os.getenv('LANGSMITH_API_KEY')
                
                if not api_key:
                    logger.warning("LANGSMITH_API_KEY가 설정되지 않았습니다.")
                    return
                
                project_name = self.get_project_name()
                
                # 환경변수 상태 로깅
                logger.info(f"LangChain 자동 추적 환경변수 확인:")
                logger.info(f"  LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
                logger.info(f"  LANGCHAIN_PROJECT: {project_name}")
                logger.info(f"  LANGCHAIN_ENDPOINT: {os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')}")
                logger.info(f"  LANGSMITH_API_KEY: {'설정됨' if api_key else '없음'}")
                
                self.is_enabled = True
                logger.info(f"LangChain 자동 추적 활성화됨 - 프로젝트: {project_name}")
            else:
                logger.info("LangSmith 추적이 비활성화되어 있습니다.")
                
        except Exception as e:
            logger.error(f"LangSmith 환경변수 확인 실패: {str(e)}")
            self.is_enabled = False
    
    def is_tracing_enabled(self) -> bool:
        """LangChain 자동 추적 활성화 여부 확인"""
        return self.is_enabled
    
    def get_project_name(self) -> str:
        """현재 프로젝트명 반환"""
        return os.getenv('LANGCHAIN_PROJECT', 'ai-skill-tutor')
    
# 전역 인스턴스
langsmith_manager = LangSmithManager()

def is_langsmith_enabled() -> bool:
    """LangChain 자동 추적 활성화 여부 확인"""
    return langsmith_manager.is_tracing_enabled()

def get_langsmith_project() -> str:
    """LangSmith 프로젝트명 가져오기"""
    return langsmith_manager.get_project_name()