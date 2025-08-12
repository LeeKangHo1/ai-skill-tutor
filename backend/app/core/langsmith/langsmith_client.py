# backend/app/core/langsmith/langsmith_client.py

import os
import logging
from typing import Optional, Dict, Any
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
            # .env.example 형식에 맞는 환경변수 사용
            tracing_env = os.getenv('LANGCHAIN_TRACING_V2', '')
            logger.info(f"LANGCHAIN_TRACING_V2: '{tracing_env}'")
            
            if tracing_env.lower() == 'true':
                api_key = os.getenv('LANGSMITH_API_KEY')
                logger.info(f"API Key exists: {bool(api_key)}")
                logger.info(f"API Key prefix: {api_key[:15]}..." if api_key else "None")
                
                if not api_key:
                    logger.warning("LANGSMITH_API_KEY가 설정되지 않았습니다.")
                    return
                
                # 프로젝트명과 엔드포인트 설정
                project_name = os.getenv('LANGCHAIN_PROJECT', 'ai-skill-tutor')
                endpoint = os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
                
                logger.info(f"Project Name: {project_name}")
                logger.info(f"Endpoint: {endpoint}")
                
                # LangSmith 클라이언트 생성
                self.client = Client(
                    api_key=api_key,
                    api_url=endpoint
                )
                logger.info(f"LangSmith Client created: {self.client}")
                
                # LangChain 환경변수는 이미 .env에 설정되어 있음
                logger.info("LangChain 환경변수 확인:")
                logger.info(f"LANGCHAIN_PROJECT: {os.environ.get('LANGCHAIN_PROJECT')}")
                logger.info(f"LANGCHAIN_TRACING_V2: {os.environ.get('LANGCHAIN_TRACING_V2')}")
                logger.info(f"LANGCHAIN_ENDPOINT: {os.environ.get('LANGCHAIN_ENDPOINT')}")
                
                # 클라이언트 연결 테스트
                try:
                    # 프로젝트 목록을 가져와서 연결 확인
                    projects = list(self.client.list_projects(limit=1))
                    logger.info(f"LangSmith 연결 성공. 프로젝트 수: {len(projects)}")
                except Exception as conn_e:
                    logger.error(f"LangSmith 연결 테스트 실패: {str(conn_e)}")
                
                self.is_enabled = True
                logger.info(f"LangSmith 추적이 활성화되었습니다. 프로젝트: {project_name}")
            else:
                logger.info("LangSmith 추적이 비활성화되어 있습니다.")
        except Exception as e:
            logger.error(f"LangSmith 초기화 실패: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
        """새로운 실행 추적 시작"""
        if not self.is_enabled or not self.client:
            logger.warning(f"LangSmith가 비활성화되어 있어 run 생성을 건너뜁니다. enabled: {self.is_enabled}, client: {bool(self.client)}")
            return None
        
        try:
            logger.info(f"LangSmith run 생성 시작: {name} (type: {run_type})")
            logger.info(f"Inputs: {inputs}")
            logger.info(f"Project name: {self.get_project_name()}")
            
            # LangSmith 0.4.13 버전에 맞는 방식으로 수정
            from datetime import datetime
            import uuid
            
            run_data = {
                "name": name,
                "run_type": run_type,
                "inputs": inputs or {},
                "project_name": self.get_project_name(),
                "start_time": datetime.utcnow(),
                **kwargs
            }
            
            logger.info(f"Run data: {run_data}")
            
            # create_run 대신 다른 방식 시도
            run = self.client.create_run(**run_data)
            
            # run이 None인 경우 처리
            if run is None:
                logger.error("create_run이 None을 반환했습니다.")
                # 직접 추적 시도 (fallback)
                run_id = str(uuid.uuid4())
                logger.info(f"수동으로 생성한 run_id: {run_id}")
                return run_id
            
            run_id = getattr(run, 'id', None)
            if run_id is None:
                logger.error(f"Run 객체에 id 속성이 없습니다. Run type: {type(run)}")
                logger.error(f"Run 객체 내용: {run}")
                # 수동 ID 생성
                run_id = str(uuid.uuid4())
                logger.info(f"수동으로 생성한 run_id: {run_id}")
                return run_id
            
            logger.info(f"LangSmith run 생성 성공: {run_id}")
            return run_id
            
        except Exception as e:
            logger.error(f"LangSmith 실행 생성 실패: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def update_run(self, run_id: str, outputs: Dict[str, Any] = None, error: str = None, **kwargs):
        """실행 추적 업데이트"""
        if not self.is_enabled or not self.client or not run_id:
            logger.warning(f"LangSmith run 업데이트 건너뜀. enabled: {self.is_enabled}, client: {bool(self.client)}, run_id: {run_id}")
            return
        
        try:
            logger.info(f"LangSmith run 업데이트: {run_id}")
            logger.info(f"Outputs: {outputs}")
            logger.info(f"Error: {error}")
            
            update_data = {}
            if outputs:
                update_data['outputs'] = outputs
            if error:
                update_data['error'] = error
            update_data.update(kwargs)
            
            self.client.update_run(run_id, **update_data)
            logger.info(f"LangSmith run 업데이트 성공: {run_id}")
        except Exception as e:
            logger.error(f"LangSmith 실행 업데이트 실패: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def end_run(self, run_id: str, outputs: Dict[str, Any] = None, error: str = None):
        """실행 추적 종료"""
        if not self.is_enabled or not self.client or not run_id:
            logger.warning(f"LangSmith run 종료 건너뜀. enabled: {self.is_enabled}, client: {bool(self.client)}, run_id: {run_id}")
            return
        
        try:
            logger.info(f"LangSmith run 종료: {run_id}")
            logger.info(f"Final outputs: {outputs}")
            logger.info(f"Final error: {error}")
            
            end_data = {}
            if outputs:
                end_data['outputs'] = outputs
            if error:
                end_data['error'] = error
            
            self.client.update_run(run_id, end_time=None, **end_data)
            logger.info(f"LangSmith run 종료 성공: {run_id}")
        except Exception as e:
            logger.error(f"LangSmith 실행 종료 실패: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

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

def create_langsmith_run(name: str, run_type: str = "tool", inputs: Dict[str, Any] = None, **kwargs) -> Optional[str]:
    """새로운 LangSmith 실행 추적 시작"""
    logger.info(f"create_langsmith_run 호출: {name}")
    return langsmith_manager.create_run(name, run_type, inputs, **kwargs)

def update_langsmith_run(run_id: str, outputs: Dict[str, Any] = None, error: str = None, **kwargs):
    """LangSmith 실행 추적 업데이트"""
    logger.info(f"update_langsmith_run 호출: {run_id}")
    langsmith_manager.update_run(run_id, outputs, error, **kwargs)

def end_langsmith_run(run_id: str, outputs: Dict[str, Any] = None, error: str = None):
    """LangSmith 실행 추적 종료"""
    logger.info(f"end_langsmith_run 호출: {run_id}")
    langsmith_manager.end_run(run_id, outputs, error)