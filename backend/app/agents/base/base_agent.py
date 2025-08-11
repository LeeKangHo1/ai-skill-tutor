# app/agents/base/base_agent.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
import time
from datetime import datetime

from app.agents.base.agent_config import AgentConfig
from app.utils.common.exceptions import AgentException, StateValidationException


class BaseAgent(ABC):
    """
    모든 에이전트의 기본 클래스
    공통 기능을 제공하고 하위 에이전트에서 구현해야 할 추상 메서드를 정의
    """
    
    def __init__(self, config: AgentConfig):
        """
        BaseAgent 초기화
        
        Args:
            config: 에이전트 설정 객체
        """
        self.config = config
        self.logger = self._setup_logger()
        self.tools = self._register_tools()
        self.start_time = None
        self.execution_history = []
        
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger(f"agent.{self.get_agent_name()}")
        logger.setLevel(self.config.log_level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[%(asctime)s] %(levelname)s [Agent:{self.get_agent_name()}] %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _register_tools(self) -> Dict[str, Any]:
        """도구 등록 및 초기화"""
        tools = {}
        tool_list = self.get_tools()
        
        for tool_name in tool_list:
            try:
                # 도구 동적 로딩 (추후 구현)
                tools[tool_name] = self._load_tool(tool_name)
            except Exception as e:
                self.logger.warning(f"도구 로딩 실패: {tool_name}, 오류: {e}")
                
        return tools
    
    def _load_tool(self, tool_name: str):
        """도구 동적 로딩 (추후 구현 예정)"""
        # TODO: tools 패키지에서 도구 함수 로딩
        return None
    
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        에이전트의 메인 처리 로직
        
        Args:
            state: 현재 TutorState
            
        Returns:
            업데이트된 TutorState
        """
        pass
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """에이전트 이름 반환"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[str]:
        """사용할 도구 목록 반환"""
        pass
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        에이전트 실행 메인 함수
        검증 -> 처리 -> 로깅 -> 에러 처리를 통합 관리
        """
        self.start_time = time.time()
        
        try:
            # State 검증
            self.validate_state(state)
            
            # 실행 전 로깅
            self.log_activity("STARTED", f"에이전트 실행 시작")
            
            # 메인 처리 로직 실행
            updated_state = self.process(state)
            
            # State 업데이트 검증
            self.validate_state(updated_state)
            
            # 실행 완료 로깅
            execution_time = time.time() - self.start_time
            self.log_activity("COMPLETED", f"에이전트 실행 완료 (소요시간: {execution_time:.2f}초)")
            
            return updated_state
            
        except Exception as e:
            return self.handle_error(e, state)
    
    def validate_state(self, state: Dict[str, Any]) -> None:
        """
        State 검증
        필수 필드 존재 여부 및 데이터 타입 검증
        """
        required_fields = [
            'user_id', 'current_chapter', 'current_agent', 
            'session_progress_stage', 'ui_mode'
        ]
        
        for field in required_fields:
            if field not in state:
                raise StateValidationException(f"필수 필드 누락: {field}")
                
        # 기본 타입 검증
        if not isinstance(state.get('user_id'), int):
            raise StateValidationException("user_id는 정수여야 합니다")
            
        if not isinstance(state.get('current_chapter'), int):
            raise StateValidationException("current_chapter는 정수여야 합니다")
    
    def update_state(self, state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        State 업데이트
        
        Args:
            state: 현재 State
            updates: 업데이트할 필드들
            
        Returns:
            업데이트된 State
        """
        updated_state = state.copy()
        
        for key, value in updates.items():
            updated_state[key] = value
            self.logger.debug(f"State 업데이트: {key} = {value}")
            
        # previous_agent 업데이트
        if 'current_agent' in updates:
            updated_state['previous_agent'] = state.get('current_agent', '')
            
        return updated_state
    
    def log_activity(self, level: str, message: str, details: Optional[Dict] = None) -> None:
        """
        활동 로깅
        
        Args:
            level: 로그 레벨 (STARTED, COMPLETED, ERROR 등)
            message: 로그 메시지
            details: 추가 상세 정보
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent_name': self.get_agent_name(),
            'level': level,
            'message': message,
            'details': details or {}
        }
        
        self.execution_history.append(log_entry)
        
        # 로그 레벨에 따른 출력
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def handle_error(self, error: Exception, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        에러 처리
        
        Args:
            error: 발생한 예외
            state: 현재 State
            
        Returns:
            에러 정보가 포함된 State
        """
        error_message = f"에이전트 실행 중 오류 발생: {str(error)}"
        self.log_activity("ERROR", error_message, {
            'error_type': type(error).__name__,
            'error_details': str(error)
        })
        
        # 에러 상태를 State에 기록
        error_state = state.copy()
        error_state.update({
            'error_occurred': True,
            'error_message': error_message,
            'error_agent': self.get_agent_name(),
            'error_timestamp': datetime.now().isoformat()
        })
        
        return error_state
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """실행 통계 반환"""
        return {
            'agent_name': self.get_agent_name(),
            'execution_count': len(self.execution_history),
            'last_execution': self.execution_history[-1] if self.execution_history else None,
            'average_execution_time': self._calculate_average_execution_time()
        }
    
    def _calculate_average_execution_time(self) -> float:
        """평균 실행 시간 계산"""
        if not self.execution_history:
            return 0.0
            
        completed_executions = [
            entry for entry in self.execution_history 
            if entry['level'] == 'COMPLETED'
        ]
        
        if not completed_executions:
            return 0.0
            
        # 실제 실행 시간 계산은 추후 개선
        return 0.0