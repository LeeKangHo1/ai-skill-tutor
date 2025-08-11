# backend/app/agents/theory_educator/agent.py

from typing import Dict, Any, List
import json
import os
from datetime import datetime

from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.content.theory_tools import theory_generation_tool


class TheoryEducator:
    """
    이론 설명 에이전트
    - 사용자 레벨별 맞춤 개념 설명 생성
    - JSON 파일 기반 챕터 데이터 참조
    - 사용자와 직접 소통하지 않고 대본만 생성
    """
    
    def __init__(self):
        self.agent_name = "theory_educator"
        self.chapter_data_path = "data/chapters"
    
    def process(self, state: TutorState) -> TutorState:
        """
        이론 설명 대본 생성 메인 프로세스
        
        Args:
            state: 현재 TutorState
            
        Returns:
            업데이트된 TutorState (theory_draft 포함)
        """
        try:
            print(f"[{self.agent_name}] 이론 설명 생성 시작 - 챕터 {state['current_chapter']}")
            
            # 1. 챕터 데이터 로드
            chapter_data = self._load_chapter_data(state["current_chapter"])
            if not chapter_data:
                raise ValueError(f"챕터 {state['current_chapter']} 데이터를 찾을 수 없습니다.")
            
            # 2. 사용자 학습 맥락 분석
            learning_context = self._analyze_learning_context(state)
            
            # 3. 이론 설명 대본 생성
            theory_content = theory_generation_tool(
                chapter_data=chapter_data,
                user_type=state["user_type"],
                learning_context=learning_context,
                recent_sessions=state["recent_sessions_summary"]
            )
            
            # 4. State 업데이트 - 대본 저장
            updated_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                theory_content
            )
            
            # 5. 세션 진행 단계 업데이트
            updated_state = state_manager.update_session_progress(
                updated_state, 
                self.agent_name
            )
            
            # 6. 대화 기록 추가
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=f"챕터 {state['current_chapter']} 이론 설명 대본 생성 완료",
                message_type="system"
            )
            
            print(f"[{self.agent_name}] 이론 설명 생성 완료")
            return updated_state
            
        except Exception as e:
            print(f"[{self.agent_name}] 오류 발생: {str(e)}")
            # 오류 시에도 State는 반환 (빈 대본으로)
            error_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                f"이론 설명 생성 중 오류가 발생했습니다: {str(e)}"
            )
            return error_state
    
    def _load_chapter_data(self, chapter_number: int) -> Dict[str, Any]:
        """
        JSON 파일에서 챕터 데이터 로드
        
        Args:
            chapter_number: 챕터 번호
            
        Returns:
            챕터 데이터 딕셔너리
        """
        try:
            chapter_file = os.path.join(
                self.chapter_data_path, 
                f"chapter_{chapter_number:02d}.json"
            )
            
            if not os.path.exists(chapter_file):
                print(f"[{self.agent_name}] 챕터 파일이 존재하지 않음: {chapter_file}")
                return None
            
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            print(f"[{self.agent_name}] 챕터 {chapter_number} 데이터 로드 완료")
            return chapter_data
            
        except Exception as e:
            print(f"[{self.agent_name}] 챕터 데이터 로드 실패: {str(e)}")
            return None
    
    def _analyze_learning_context(self, state: TutorState) -> Dict[str, Any]:
        """
        사용자의 학습 맥락 분석
        
        Args:
            state: 현재 TutorState
            
        Returns:
            학습 맥락 정보
        """
        context = {
            "user_type": state["user_type"],
            "current_chapter": state["current_chapter"],
            "session_count": state["current_session_count"],
            "is_retry_session": state["current_session_count"] > 0,
            "has_recent_sessions": len(state["recent_sessions_summary"]) > 0,
            "session_progress_stage": state["session_progress_stage"]
        }
        
        # 재학습 세션인 경우 특별 처리
        if context["is_retry_session"]:
            context["focus_areas"] = "이전에 어려워했던 부분 중심으로 설명"
            context["explanation_style"] = "더 구체적이고 단계별 설명"
        else:
            context["focus_areas"] = "전체적인 개념 이해"
            context["explanation_style"] = "기본적이고 체계적인 설명"
        
        # 사용자 유형별 설정
        if state["user_type"] == "beginner":
            context["complexity_level"] = "기초"
            context["use_analogies"] = True
            context["detailed_examples"] = True
        else:  # advanced
            context["complexity_level"] = "중급"
            context["use_analogies"] = False
            context["detailed_examples"] = False
        
        return context