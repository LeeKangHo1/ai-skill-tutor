# backend/app/agents/quiz_generator/agent.py

from typing import Dict, Any, List
import json
import os
from datetime import datetime

from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.content.quiz_tools import quiz_generation_tool, hint_generation_tool


class QuizGenerator:
    """
    퀴즈 생성 에이전트
    - 객관식/주관식 문제 생성
    - JSON 파일 기반 챕터 데이터 참조
    - 힌트 시스템 지원
    - 사용자와 직접 소통하지 않고 대본만 생성
    """
    
    def __init__(self):
        self.agent_name = "quiz_generator"
        self.chapter_data_path = "data/chapters"
    
    def process(self, state: TutorState) -> TutorState:
        """
        퀴즈 생성 대본 생성 메인 프로세스
        
        Args:
            state: 현재 TutorState
            
        Returns:
            업데이트된 TutorState (quiz_draft 포함, UI 모드 quiz로 전환)
        """
        try:
            print(f"[{self.agent_name}] 퀴즈 생성 시작 - 챕터 {state['current_chapter']}")
            
            # 1. 챕터 데이터 로드
            chapter_data = self._load_chapter_data(state["current_chapter"])
            if not chapter_data:
                raise ValueError(f"챕터 {state['current_chapter']} 데이터를 찾을 수 없습니다.")
            
            # 2. 퀴즈 맥락 분석
            quiz_context = self._analyze_quiz_context(state)
            
            # 3. 퀴즈 생성
            quiz_content = quiz_generation_tool(
                chapter_data=chapter_data,
                user_type=state["user_type"],
                quiz_context=quiz_context,
                session_progress=state["session_progress_stage"]
            )
            
            # 4. State 업데이트 - 대본 저장
            updated_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                quiz_content
            )
            
            # 5. UI 모드를 퀴즈 모드로 전환
            updated_state = state_manager.update_ui_mode(
                updated_state, 
                "quiz"
            )
            
            # 6. 퀴즈 정보 State에 업데이트
            quiz_data = json.loads(quiz_content)
            updated_state = self._update_quiz_state(updated_state, quiz_data)
            
            # 7. 대화 기록 추가
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=f"챕터 {state['current_chapter']} 퀴즈 생성 완료",
                message_type="system"
            )
            
            print(f"[{self.agent_name}] 퀴즈 생성 완료")
            return updated_state
            
        except Exception as e:
            print(f"[{self.agent_name}] 오류 발생: {str(e)}")
            # 오류 시에도 State는 반환 (기본 퀴즈로)
            error_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                self._create_error_quiz(str(e))
            )
            return error_state
    
    def generate_hint(self, state: TutorState) -> TutorState:
        """
        힌트 생성 기능
        
        Args:
            state: 현재 TutorState
            
        Returns:
            힌트가 포함된 업데이트된 State
        """
        try:
            print(f"[{self.agent_name}] 힌트 생성 - 문제 {state['current_question_number']}")
            
            # 현재 퀴즈 정보 추출
            current_quiz = self._extract_current_quiz_info(state)
            
            # 힌트 생성
            hint_content = hint_generation_tool(
                question_content=state["current_question_content"],
                question_type=state["current_question_type"],
                user_type=state["user_type"],
                hint_level=state["hint_usage_count"] + 1,
                quiz_context=current_quiz
            )
            
            # 힌트 사용 횟수 증가
            updated_state = state_manager.update_quiz_info(
                state,
                hint_count=state["hint_usage_count"] + 1
            )
            
            # 힌트를 QnA 대본에 저장 (임시)
            updated_state = state_manager.update_agent_draft(
                updated_state,
                "qna_resolver",
                hint_content
            )
            
            print(f"[{self.agent_name}] 힌트 생성 완료")
            return updated_state
            
        except Exception as e:
            print(f"[{self.agent_name}] 힌트 생성 오류: {str(e)}")
            return state
    
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
    
    def _analyze_quiz_context(self, state: TutorState) -> Dict[str, Any]:
        """
        퀴즈 생성을 위한 맥락 분석
        
        Args:
            state: 현재 TutorState
            
        Returns:
            퀴즈 맥락 정보
        """
        context = {
            "user_type": state["user_type"],
            "current_chapter": state["current_chapter"],
            "session_count": state["current_session_count"],
            "is_retry_session": state["current_session_count"] > 0,
            "previous_quiz_score": state.get("is_answer_correct", 0),
            "session_progress_stage": state["session_progress_stage"]
        }
        
        # 재학습 세션인 경우
        if context["is_retry_session"]:
            context["difficulty_adjustment"] = "easier"
            context["focus_areas"] = "기본 개념 중심"
        else:
            context["difficulty_adjustment"] = "normal"
            context["focus_areas"] = "전체 이해도 확인"
        
        # 사용자 유형별 설정
        if state["user_type"] == "beginner":
            context["question_style"] = "friendly"
            context["prefer_multiple_choice"] = True
            context["provide_detailed_explanation"] = True
        else:  # advanced
            context["question_style"] = "professional" 
            context["prefer_multiple_choice"] = False
            context["provide_detailed_explanation"] = False
        
        return context
    
    def _update_quiz_state(self, state: TutorState, quiz_data: Dict[str, Any]) -> TutorState:
        """
        퀴즈 데이터를 State에 업데이트
        
        Args:
            state: 현재 State
            quiz_data: 생성된 퀴즈 데이터
            
        Returns:
            업데이트된 State
        """
        quiz_info = quiz_data.get("quiz_info", {})
        
        updated_state = state_manager.update_quiz_info(
            state,
            question_type=quiz_info.get("question_type", "multiple_choice"),
            question_number=quiz_info.get("question_number", 1),
            question_content=quiz_info.get("question", ""),
            hint_count=0  # 새 문제이므로 힌트 카운트 초기화
        )
        
        return updated_state
    
    def _extract_current_quiz_info(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 State에서 퀴즈 정보 추출
        
        Args:
            state: 현재 State
            
        Returns:
            퀴즈 정보 딕셔너리
        """
        return {
            "question_number": state["current_question_number"],
            "question_type": state["current_question_type"],
            "question_content": state["current_question_content"],
            "hint_usage_count": state["hint_usage_count"]
        }
    
    def _create_error_quiz(self, error_message: str) -> str:
        """
        오류 발생 시 기본 퀴즈 생성
        
        Args:
            error_message: 오류 메시지
            
        Returns:
            기본 퀴즈 JSON 문자열
        """
        error_quiz = {
            "content_type": "quiz",
            "quiz_info": {
                "question_type": "multiple_choice",
                "question_number": 1,
                "question": f"퀴즈 생성 중 오류가 발생했습니다: {error_message}",
                "options": [
                    "다시 시도",
                    "다음으로 넘어가기",
                    "이전으로 돌아가기",
                    "도움말"
                ],
                "correct_answer": 1
            },
            "explanation": "시스템 오류로 인한 기본 문제입니다.",
            "user_guidance": "다시 시도해 주세요."
        }
        return json.dumps(error_quiz, ensure_ascii=False, indent=2)