# backend/app/agents/session_manager/session_manager_agent.py

"""
SessionManager v2.0 - 세션 관리 에이전트

주요 v2.0 변경사항:
- AUTO_INCREMENT 세션 ID 사용 (기존 문자열 → 정수)
- 객관식/주관식 분리된 퀴즈 데이터 구조
- retry_decision_result 필드명 변경 (기존 session_decision_result)
- section_number 필드 추가로 섹션별 진행 관리
- 통합 워크플로우 지원
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any

from app.core.langraph.state_manager import TutorState, state_manager
from app.agents.session_manager.session_handlers import SessionHandlers
from app.utils.common.chat_logger import chat_logger


class SessionManager:
    """
    세션 관리 에이전트
    
    주요 역할:
    1. 현재 세션 데이터를 DB에 저장 (learning_sessions, session_conversations, session_quizzes)
    2. 세션 State 초기화 (대화 기록, 퀴즈 정보, 에이전트 대본 클리어)
    3. 대화 요약 생성 및 recent_sessions_summary 업데이트
    4. 다음 세션을 위한 챕터/섹션 진행 상태 업데이트
    """
    
    def __init__(self):
        self.agent_name = "session_manager"
        self.logger = logging.getLogger(__name__)
        self.session_handlers = SessionHandlers()
    
    def process(self, state: TutorState) -> TutorState:
        """
        세션 완료 처리 메인 프로세스
        
        Args:
            state: 현재 TutorState (retry_decision_result가 설정된 상태)
            
        Returns:
            다음 세션을 위해 정리된 TutorState
        """
        try:
            self.logger.info(f"[{self.agent_name}] 세션 완료 처리 시작")
            
            # 1. 현재 세션 결정 결과 확인
            decision_result = state.get("retry_decision_result", "proceed")
            self.logger.info(f"세션 결정 결과: {decision_result}")
            
            # 2. 현재 세션 데이터를 DB에 저장 (AUTO_INCREMENT 세션 ID 사용)
            session_id = self._save_current_session_to_db(state)
            
            # 3. 대화 요약 생성 및 recent_sessions_summary 업데이트
            updated_state = self._update_session_summary(state, decision_result)
            
            # 4. 다음 세션을 위한 진행 상태 업데이트
            updated_state = self._update_progress_for_next_session(updated_state, decision_result)
            
            # 5. 세션 State 초기화
            updated_state = self._reset_session_state(updated_state)
            
            # 6. 다음 세션 준비
            updated_state = self._prepare_next_session(updated_state)
            
            self.logger.info(f"[{self.agent_name}] 세션 완료 처리 완료 - 세션ID: {session_id}")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"[{self.agent_name}] 세션 처리 중 오류: {str(e)}")
            # 오류 시에도 기본적인 State 정리는 수행
            return self._handle_error_and_cleanup(state, str(e))
    
    def _save_current_session_to_db(self, state: TutorState) -> int:
        """
        현재 세션 데이터를 DB에 저장 (v2.0: AUTO_INCREMENT 세션 ID 사용)
        
        Args:
            state: 현재 TutorState
            
        Returns:
            저장된 세션 ID (AUTO_INCREMENT로 생성된 정수)
        """
        try:
            # 1. learning_sessions 테이블에 세션 기본 정보 저장 (AUTO_INCREMENT 사용)
            session_data = self._prepare_session_data(state)
            session_id = self.session_handlers.save_session_info(session_data)
            
            if not session_id:
                raise Exception("세션 ID 생성 실패")
            
            # 2. session_conversations 테이블에 대화 기록 저장
            conversations = state.get("current_session_conversations", [])
            if conversations:
                self.session_handlers.save_session_conversations(session_id, conversations)
            
            # 3. session_quizzes 테이블에 퀴즈 정보 저장 (v2.0: 객관식/주관식 분리)
            quiz_data = self._prepare_quiz_data(state, session_id)
            if quiz_data:
                self.session_handlers.save_session_quiz(quiz_data)
            
            self.logger.info(f"세션 데이터 DB 저장 완료: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"DB 저장 중 오류: {str(e)}")
            # 오류가 있어도 임시 세션 ID 반환 (음수로 구분)
            return -1
    
    # v2.0: AUTO_INCREMENT 사용으로 세션 ID 생성 함수 제거
    
    def _prepare_session_data(self, state: TutorState) -> Dict[str, Any]:
        """learning_sessions 테이블용 데이터 준비 (v2.0: AUTO_INCREMENT 세션 ID 사용)"""
        session_start = state.get("session_start_time", datetime.now())
        session_end = datetime.now()
        
        # 학습 시간 계산 (분 단위)
        if isinstance(session_start, datetime):
            duration = (session_end - session_start).total_seconds() / 60
        else:
            duration = 0
        
        return {
            # session_id는 AUTO_INCREMENT로 자동 생성되므로 제외
            "user_id": state["user_id"],
            "chapter_number": state["current_chapter"],
            "section_number": state["current_section"],  # v2.0: session_sequence → section_number
            "session_start_time": session_start,
            "session_end_time": session_end,
            "study_duration_minutes": int(duration),
            "retry_decision_result": state.get("retry_decision_result", "proceed")  # v2.0: 필드명 변경
        }
    
    def _prepare_quiz_data(self, state: TutorState, session_id: int) -> Dict[str, Any]:
        """session_quizzes 테이블용 데이터 준비 (v2.0: 객관식/주관식 분리)"""
        # 퀴즈 정보가 있는 경우에만 데이터 준비
        if not state.get("quiz_content"):
            return None
        
        quiz_type = state.get("quiz_type", "multiple_choice")
        
        # v2.0: 객관식/주관식 분리된 데이터 구조
        quiz_data = {
            "session_id": session_id,
            "quiz_type": quiz_type,
            "quiz_content": state.get("quiz_content", ""),
            "quiz_hint": state.get("quiz_hint", ""),
            "user_answer": state.get("user_answer", "")
        }
        
        # 객관식 전용 필드
        if quiz_type == "multiple_choice":
            quiz_data.update({
                "quiz_options": state.get("quiz_options", []),  # JSON 배열
                "quiz_correct_answer": state.get("quiz_correct_answer"),  # 정답 번호 (1-4)
                "quiz_explanation": state.get("quiz_explanation", ""),
                "multiple_answer_correct": state.get("multiple_answer_correct", False),
                # 주관식 필드는 NULL
                "quiz_sample_answer": None,
                "quiz_evaluation_criteria": None,
                "subjective_answer_score": None
            })
        
        # 주관식 전용 필드
        else:  # subjective
            quiz_data.update({
                "quiz_sample_answer": state.get("quiz_sample_answer", ""),
                "quiz_evaluation_criteria": state.get("quiz_evaluation_criteria", []),  # JSON 배열
                "subjective_answer_score": state.get("subjective_answer_score", 0),
                # 객관식 필드는 NULL
                "quiz_options": None,
                "quiz_correct_answer": None,
                "quiz_explanation": None,
                "multiple_answer_correct": None
            })
        
        return quiz_data
    
    def _update_session_summary(self, state: TutorState, decision_result: str) -> TutorState:
        """
        대화 요약 생성 및 recent_sessions_summary 업데이트
        
        Args:
            state: 현재 TutorState
            decision_result: 세션 결정 결과
            
        Returns:
            요약이 업데이트된 TutorState
        """
        try:
            # 현재 세션 요약 생성
            session_summary = self._create_session_summary(state, decision_result)
            
            # 기존 요약 목록 가져오기
            recent_summaries = state.get("recent_sessions_summary", [])
            
            # 새 요약 추가
            recent_summaries.append(session_summary)
            
            # 최근 5개만 유지
            if len(recent_summaries) > 5:
                recent_summaries = recent_summaries[-5:]
            
            # State 업데이트
            updated_state = state.copy()
            updated_state["recent_sessions_summary"] = recent_summaries
            
            self.logger.info("세션 요약 업데이트 완료")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"세션 요약 업데이트 중 오류: {str(e)}")
            return state
    
    def _create_session_summary(self, state: TutorState, decision_result: str) -> Dict[str, str]:
        """현재 세션 요약 생성"""
        chapter = state["current_chapter"]
        section = state["current_section"]
        quiz_type = state.get("quiz_type", "unknown")
        
        # v2.0: 객관식/주관식 분리된 점수 처리
        if quiz_type == "multiple_choice":
            is_correct = state.get("multiple_answer_correct", False)
            percentage = 100 if is_correct else 0
        else:  # subjective
            percentage = state.get("subjective_answer_score", 0)
        
        summary = {
            "chapter_section": f"{chapter}챕터 {section}섹션",
            "quiz_result": f"{quiz_type} 퀴즈 {percentage}점",
            "decision": "재학습 필요" if decision_result == "retry" else "진행 완료",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        return summary
    
    def _update_progress_for_next_session(self, state: TutorState, decision_result: str) -> TutorState:
        """
        다음 세션을 위한 진행 상태 업데이트
        
        Args:
            state: 현재 TutorState
            decision_result: 세션 결정 결과 ("proceed" or "retry")
            
        Returns:
            진행 상태가 업데이트된 TutorState
        """
        updated_state = state.copy()
        current_chapter = state["current_chapter"]
        current_section = state["current_section"]
        current_session_count = state.get("current_session_count", 0)
        user_type = state["user_type"]
        
        if decision_result == "proceed":
            # 현재 챕터의 최대 섹션 수 확인
            max_sections = self._get_max_sections_for_chapter(current_chapter, user_type)
            
            if current_section < max_sections:
                # 같은 챕터 내 다음 섹션으로 진행
                next_chapter = current_chapter
                next_section = current_section + 1
                next_session_count = 0  # 새 섹션이므로 세션 카운트 초기화
            else:
                # 다음 챕터로 진행
                next_chapter = current_chapter + 1
                next_section = 1  # 새 챕터의 첫 번째 섹션
                next_session_count = 0  # 새 챕터이므로 세션 카운트 초기화
            
            # State 업데이트
            updated_state["current_chapter"] = next_chapter
            updated_state["current_section"] = next_section
            updated_state["current_session_count"] = next_session_count
            
            self.logger.info(f"진행: {current_chapter}챕터 {current_section}섹션 → {next_chapter}챕터 {next_section}섹션")
            
        else:  # retry
            # 현재 섹션 유지, 세션 카운트 증가
            updated_state["current_session_count"] = current_session_count + 1
            
            self.logger.info(f"재학습: {current_chapter}챕터 {current_section}섹션 (세션 {updated_state['current_session_count']}회차)")
        
        return updated_state
    
    def _get_max_sections_for_chapter(self, chapter_number: int, user_type: str) -> int:
        """
        챕터별 최대 섹션 수 조회
        
        Args:
            chapter_number: 챕터 번호
            user_type: 사용자 유형 ("beginner" or "advanced")
            
        Returns:
            해당 챕터의 최대 섹션 수
        """
        try:
            # 챕터 데이터 파일 경로
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            data_dir = os.path.join(project_root, "data", "chapters")
            file_path = os.path.join(data_dir, f"chapter_{chapter_number:02d}.json")
            
            # JSON 파일 읽기
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    chapter_data = json.load(f)
                
                # user_type 확인 후 섹션 수 반환
                if chapter_data.get('user_type') == user_type:
                    sections = chapter_data.get('sections', [])
                    max_sections = len(sections)
                    
                    self.logger.info(f"챕터 {chapter_number} ({user_type}) 최대 섹션 수: {max_sections}")
                    return max_sections
                else:
                    self.logger.warning(f"사용자 유형 불일치: 파일={chapter_data.get('user_type')}, 요청={user_type}")
                    return 4  # 기본값
            else:
                self.logger.warning(f"챕터 데이터 파일 없음: {file_path}")
                return 4  # 기본값
                
        except Exception as e:
            self.logger.error(f"챕터 데이터 로드 중 오류: {str(e)}")
            return 4  # 기본값으로 4개 섹션 가정
    
    def _reset_session_state(self, state: TutorState) -> TutorState:
        """
        세션 State 초기화 (다음 세션을 위한 정리)
        
        Args:
            state: 현재 TutorState
            
        Returns:
            초기화된 TutorState
        """
        # state_manager의 reset_session_state 활용
        updated_state = state_manager.reset_session_state(state, new_chapter=False)
        
        self.logger.info("세션 State 초기화 완료")
        return updated_state
    
    def _prepare_next_session(self, state: TutorState) -> TutorState:
        """
        다음 세션 준비
        
        Args:
            state: 초기화된 TutorState
            
        Returns:
            다음 세션 준비가 완료된 TutorState
        """
        updated_state = state.copy()
        
        # 1. 현재 에이전트를 session_manager로 설정
        updated_state = state_manager.update_agent_transition(updated_state, "session_manager")
        
        # 2. 세션 시작 시간 갱신
        updated_state["session_start_time"] = datetime.now()
        
        # 3. 세션 완료 준비 메시지 생성
        next_section_info = f"{updated_state['current_chapter']}챕터 {updated_state['current_section']}섹션"
        completion_message = f"세션이 완료되었습니다. 다음은 {next_section_info}을 진행하겠습니다."
        
        # 4. 완료 메시지를 대화 기록에 추가
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name=self.agent_name,
            message=completion_message,
            message_type="system"
        )
        
        self.logger.info(f"다음 세션 준비 완료: {next_section_info}")
        return updated_state
    
    def prepare_next_session(self, state: TutorState) -> TutorState:
        """
        다음 세션 준비 (외부에서 호출 가능한 공개 메서드)
        
        Args:
            state: 현재 TutorState
            
        Returns:
            다음 세션 준비가 완료된 TutorState
        """
        return self._prepare_next_session(state)
    
    def _handle_error_and_cleanup(self, state: TutorState, error_message: str) -> TutorState:
        """
        오류 발생 시 기본적인 정리 작업 수행
        
        Args:
            state: 현재 TutorState
            error_message: 오류 메시지
            
        Returns:
            최소한의 정리가 완료된 TutorState
        """
        self.logger.error(f"오류 처리 및 정리: {error_message}")
        
        # 기본적인 State 초기화만 수행
        updated_state = state_manager.reset_session_state(state, new_chapter=False)
        
        # 오류 메시지 추가
        error_msg = f"세션 처리 중 오류가 발생했습니다. 다음 학습을 계속 진행합니다. (오류: {error_message})"
        updated_state = state_manager.add_conversation(
            updated_state,
            agent_name=self.agent_name,
            message=error_msg,
            message_type="system"
        )
        
        # 강제로 다음 섹션으로 진행
        next_section = state["current_section"] + 1
        updated_state = state_manager.update_section_progress(updated_state, next_section=next_section)
        updated_state["current_session_count"] = 0
        
        return updated_state
    
    def get_session_status(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 세션 상태 정보 반환 (외부에서 호출 가능)
        
        Args:
            state: 현재 TutorState
            
        Returns:
            세션 상태 요약
        """
        return {
            "current_chapter": state["current_chapter"],
            "current_section": state["current_section"],
            "session_count": state.get("current_session_count", 0),
            "session_stage": state.get("session_progress_stage", "session_start"),
            "decision_result": state.get("retry_decision_result", ""),
            "conversations_count": len(state.get("current_session_conversations", [])),
            "recent_summaries_count": len(state.get("recent_sessions_summary", []))
        }