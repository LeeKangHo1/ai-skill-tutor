# backend/app/core/langsmith/langsmith_client.py

import os
import logging
from typing import Optional, Dict, Any
from langsmith import Client

logger = logging.getLogger(__name__)

class LangSmithManager:
    """LangSmith 클라이언트 관리 클래스 (간소화 버전)"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_enabled = False
        self._initialize()
    
    def _initialize(self):
        """LangSmith 클라이언트 초기화"""
        try:
            # 환경변수 확인
            tracing_env = os.getenv('LANGCHAIN_TRACING_V2', '').lower()
            
            if tracing_env == 'true':
                api_key = os.getenv('LANGSMITH_API_KEY')
                
                if not api_key:
                    logger.warning("LANGSMITH_API_KEY가 설정되지 않았습니다.")
                    return
                
                # LangSmith 클라이언트 생성
                self.client = Client(
                    api_key=api_key,
                    api_url=os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
                )
                
                # LangChain 자동 추적을 위한 환경변수 설정 확인
                project_name = self.get_project_name()
                
                # 환경변수가 제대로 설정되었는지 확인
                logger.info(f"LangChain 환경변수 상태:")
                logger.info(f"  LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
                logger.info(f"  LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
                logger.info(f"  LANGCHAIN_ENDPOINT: {os.getenv('LANGCHAIN_ENDPOINT')}")
                logger.info(f"  LANGSMITH_API_KEY: {'설정됨' if api_key else '없음'}")
                
                # 간단한 연결 테스트
                try:
                    list(self.client.list_projects(limit=1))
                    self.is_enabled = True
                    logger.info(f"LangSmith 추적 활성화됨 - 프로젝트: {project_name}")
                    logger.info("LangChain 자동 추적이 활성화되었습니다.")
                except Exception as conn_e:
                    logger.error(f"LangSmith 연결 실패: {str(conn_e)}")
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
    
    def get_project_name(self) -> str:
        """현재 프로젝트명 반환"""
        return os.getenv('LANGCHAIN_PROJECT', 'ai-skill-tutor')
    
    def create_run(self, name: str, run_type: str = "tool", inputs: Dict[str, Any] = None, **kwargs) -> Optional[str]:
        """새로운 실행 추적 시작 (간소화 버전)"""
        if not self.is_enabled or not self.client:
            return None
        
        try:
            from datetime import datetime
            import uuid
            
            # 고유 run_id 생성 (409 Conflict 방지)
            run_id = kwargs.get('run_id', str(uuid.uuid4()))
            
            run_data = {
                "name": name,
                "run_type": run_type,
                "inputs": inputs or {},
                "project_name": self.get_project_name(),
                "start_time": datetime.utcnow(),
                "id": run_id,
                **{k: v for k, v in kwargs.items() if k != 'run_id'}
            }
            
            run = self.client.create_run(**run_data)
            
            # run 객체에서 ID 추출
            if hasattr(run, 'id'):
                actual_run_id = str(run.id)
                logger.info(f"LangSmith run 생성 성공: {actual_run_id}")
                return actual_run_id
            elif isinstance(run, dict) and 'id' in run:
                actual_run_id = str(run['id'])
                logger.info(f"LangSmith run 생성 성공: {actual_run_id}")
                return actual_run_id
            else:
                logger.info(f"LangSmith run 생성 (fallback ID): {run_id}")
                return run_id  # fallback
                
        except Exception as e:
            logger.error(f"LangSmith run 생성 실패: {str(e)}")
            return None
    
    def update_run(self, run_id: str, outputs: Dict[str, Any] = None, error: str = None, **kwargs):
        """실행 추적 업데이트 (LangSmith 0.4.13 호환 버전)"""
        if not self.is_enabled or not self.client or not run_id:
            return
        
        try:
            update_data = {}
            
            # outputs 설정
            if outputs:
                update_data['outputs'] = outputs
            
            # error 설정
            if error:
                update_data['error'] = error
            
            # status 처리 - LangSmith 0.4.13에서는 end_run을 별도로 호출해야 함
            status = kwargs.get('status')
            if status == 'completed':
                # 성공적으로 완료된 경우
                if outputs:
                    update_data['outputs'] = outputs
                # end_run을 별도로 호출
                self.client.update_run(run_id, **update_data)
                self._end_run(run_id)
                return
            elif status == 'error':
                # 오류로 완료된 경우
                if error:
                    update_data['error'] = error
                # end_run을 별도로 호출
                self.client.update_run(run_id, **update_data)
                self._end_run(run_id, error=error)
                return
            
            # 일반적인 업데이트 (status가 없는 경우)
            other_kwargs = {k: v for k, v in kwargs.items() if k != 'status'}
            update_data.update(other_kwargs)
            
            self.client.update_run(run_id, **update_data)
            
        except Exception as e:
            logger.error(f"LangSmith run 업데이트 실패: {str(e)}")
    
    def _end_run(self, run_id: str, error: str = None):
        """run을 명시적으로 종료 (LangSmith 0.4.13 호환)"""
        try:
            from datetime import datetime
            
            end_data = {
                'end_time': datetime.utcnow()
            }
            
            if error:
                end_data['error'] = error
            
            # LangSmith 0.4.13에서는 end_time을 설정하여 run을 종료
            self.client.update_run(run_id, **end_data)
            logger.info(f"LangSmith run 종료됨: {run_id}")
            
        except Exception as e:
            logger.error(f"LangSmith run 종료 실패: {str(e)}")

# 전역 인스턴스
langsmith_manager = LangSmithManager()

def get_langsmith_client() -> Optional[Client]:
    """LangSmith 클라이언트 가져오기"""
    return langsmith_manager.get_client()

def is_langsmith_enabled() -> bool:
    """LangSmith 활성화 여부 확인"""
    return langsmith_manager.is_tracing_enabled()

def get_langsmith_project() -> str:
    """LangSmith 프로젝트명 가져오기"""
    return langsmith_manager.get_project_name()