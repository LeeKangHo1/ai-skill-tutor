# backend/app/agents/theory_educator/theory_educator_agent.py

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
    - LangChain + LangSmith 통합
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
            print(f"[{self.agent_name}] 이론 설명 생성 시작 - 챕터 {state['current_chapter']} 섹션 {state['current_section']}")
            
            # 1. 챕터 데이터 로드
            chapter_data = self._load_chapter_data(state["current_chapter"])
            if not chapter_data:
                raise ValueError(f"챕터 {state['current_chapter']} 데이터를 찾을 수 없습니다.")
            
            # 2. 사용자 학습 맥락 분석
            learning_context = self._analyze_learning_context(state)
            
            # 3. 벡터 DB에서 관련 자료 검색 (추후 활용)
            vector_materials = self._get_vector_search_materials(chapter_data, state["user_type"])
            
            # 4. 이론 설명 대본 생성 (수정된 파라미터)
            theory_content = theory_generation_tool(
                chapter_data=chapter_data,
                user_type=state["user_type"],
                learning_context=learning_context,
                vector_materials=vector_materials
            )
            
            # 5. State 업데이트 - 대본 저장
            updated_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                theory_content
            )
            
            # 6. 세션 진행 단계 업데이트
            updated_state = state_manager.update_session_progress(
                updated_state, 
                self.agent_name
            )
            
            # 7. 대화 기록 추가
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=f"챕터 {state['current_chapter']} 섹션 {state['current_section']} 이론 설명 대본 생성 완료",
                message_type="system"
            )
            
            print(f"[{self.agent_name}] 이론 설명 생성 완료")
            return updated_state
            
        except Exception as e:
            print(f"[{self.agent_name}] 오류 발생: {str(e)}")
            # 오류 시에도 State는 반환 (오류 메시지 대본으로)
            error_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                self._create_error_response(str(e))
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
    
    def _get_vector_search_materials(self, chapter_data: Dict[str, Any], user_type: str) -> List[Dict[str, Any]]:
        """
        벡터 DB에서 관련 학습 자료 검색 (추후 구현)
        
        Args:
            chapter_data: 챕터 데이터
            user_type: 사용자 유형
            
        Returns:
            검색된 관련 자료 목록
        """
        # TODO: ChromaDB 벡터 검색 구현
        # search_query = f"챕터 {chapter_data['chapter_number']} {chapter_data['title']}"
        # vector_results = vector_search_tool(
        #     query=search_query,
        #     top_k=3,
        #     user_type=user_type
        # )
        # return vector_results
        
        # 현재는 빈 리스트 반환 (JSON 파일 기반 학습)
        print(f"[{self.agent_name}] 벡터 검색 기능은 추후 구현 예정")
        return []
    
    def _analyze_learning_context(self, state: TutorState) -> Dict[str, Any]:
        """
        사용자의 학습 맥락 분석 (learning_context 생성)
        
        Args:
            state: 현재 TutorState
            
        Returns:
            학습 맥락 정보
        """
        context = {
            "user_type": state["user_type"],
            "current_chapter": state["current_chapter"],
            "current_section": state["current_section"],  # 섹션 정보 추가
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
    
    def _create_error_response(self, error_message: str) -> str:
        """
        오류 발생 시 기본 응답 생성
        
        Args:
            error_message: 오류 메시지
            
        Returns:
            오류 응답 JSON 문자열
        """
        error_response = {
            "content_type": "theory",
            "chapter_info": {
                "chapter_number": 1,
                "title": "오류 발생",
                "user_type": "beginner"
            },
            "section_info": {
                "section_number": 1,
                "title": "시스템 오류"
            },
            "main_content": f"이론 설명을 생성하는 중 문제가 발생했습니다: {error_message}",
            "key_points": ["시스템 일시 오류", "질문으로 학습 계속 가능", "잠시 후 재시도"],
            "analogy": "",
            "examples": [],
            "user_guidance": "시스템 문제로 설명이 생성되지 않았습니다. 궁금한 점을 질문해주세요.",
            "next_step_preview": "질문이 있으시면 언제든 말씀해주세요."
        }
        
        return json.dumps(error_response, ensure_ascii=False, indent=2)