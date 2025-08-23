# backend/app/agents/session_manager/session_manager_agent.py

"""
SessionManager v2.3 - 세션 관리 에이전트 (다음 진행 상태 계산 로직 추가)

주요 v2.3 변경사항:
- 다음 챕터/섹션 계산 로직 추가
- chapters_metadata.json 파일 기반 최대 섹션 수 조회
- session_data에 next_chapter, next_section 필드 추가
- SessionHandlers로 계산된 진행 상태 전달
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any

from app.core.langraph.state_manager import TutorState, state_manager
from app.agents.session_manager.session_handlers import SessionHandlers


class SessionManager:
    """
    세션 관리 에이전트 (DB 저장 + 다음 진행 상태 계산)
    
    주요 역할:
    1. 현재 세션 데이터를 DB에 저장 (learning_sessions, session_conversations, session_quizzes)
    2. 다음 진행 상태 계산 (next_chapter, next_section)
    3. 사용자 진행 상태 업데이트 (user_progress, user_statistics)
    4. 저장 완료 메시지를 State에 기록
    """
    
    def __init__(self):
        self.agent_name = "session_manager"
        self.logger = logging.getLogger(__name__)
        self.session_handlers = SessionHandlers()
        
        # chapters_metadata.json 캐시
        self._chapters_metadata = None
    
    def process(self, state: TutorState) -> TutorState:
        """
        세션 DB 저장 및 다음 진행 상태 계산 처리
        
        Args:
            state: 현재 TutorState (retry_decision_result가 설정된 상태)
            
        Returns:
            저장 완료 메시지가 기록된 TutorState
        """
        try:
            self.logger.info(f"[{self.agent_name}] 세션 DB 저장 시작")
            
            # 1. 현재 세션 결정 결과 확인
            decision_result = state.get("retry_decision_result", "proceed")
            self.logger.info(f"세션 결정 결과: {decision_result}")
            
            # 2. 다음 진행 상태 계산 (proceed인 경우에만)
            session_data = self._prepare_session_data_with_next_progress(state, decision_result)
            
            # 3. 현재 세션 데이터를 DB에 저장
            session_id = self._save_current_session_to_db_with_progress(state, session_data)
            
            # 4. 대화 요약 생성 및 추가 (SessionService에서 활용할 수 있도록)
            updated_state = self._add_session_summary_to_state(state, decision_result, session_id)
            
            # 5. 저장 완료 메시지를 State에 기록
            completion_message = self._create_completion_message(state, decision_result, session_id)
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=completion_message,
                message_type="system"
            )
            
            # 6. 현재 에이전트 정보 업데이트
            updated_state = state_manager.update_agent_transition(updated_state, self.agent_name)
            
            self.logger.info(f"[{self.agent_name}] 세션 DB 저장 완료 - 세션ID: {session_id}")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"[{self.agent_name}] 세션 저장 중 오류: {str(e)}")
            return self._handle_save_error(state, str(e))
    
    def _prepare_session_data_with_next_progress(self, state: TutorState, decision_result: str) -> Dict[str, Any]:
        """
        세션 데이터 준비 + 다음 진행 상태 계산 (v2.3 신규)
        
        Args:
            state: 현재 TutorState
            decision_result: 세션 결정 결과
            
        Returns:
            next_chapter, next_section이 포함된 세션 데이터
        """
        # 기본 세션 데이터 준비
        session_data = self._prepare_session_data(state)
        
        # 다음 진행 상태 계산
        current_chapter = state["current_chapter"]
        current_section = state["current_section"]
        
        if decision_result == "proceed":
            # 다음 섹션/챕터 계산
            next_chapter, next_section = self._calculate_next_progress(current_chapter, current_section)
            
            self.logger.info(f"진행 상태 계산: {current_chapter}챕터 {current_section}섹션 → {next_chapter}챕터 {next_section}섹션")
        else:
            # retry인 경우 현재 상태 유지
            next_chapter, next_section = current_chapter, current_section
            
            self.logger.info(f"재학습으로 진행 상태 유지: {current_chapter}챕터 {current_section}섹션")
        
        # 계산된 다음 진행 상태 추가
        session_data["next_chapter"] = next_chapter
        session_data["next_section"] = next_section
        
        return session_data
    
    def _calculate_next_progress(self, current_chapter: int, current_section: int) -> tuple:
        """
        다음 챕터/섹션 계산 (v2.3 신규)
        
        Args:
            current_chapter: 현재 챕터
            current_section: 현재 섹션
            
        Returns:
            (next_chapter, next_section) 튜플
        """
        try:
            # 현재 챕터의 최대 섹션 수 조회
            max_sections = self._get_max_sections_for_chapter(current_chapter)
            
            if current_section < max_sections:
                # 같은 챕터 내 다음 섹션으로 진행
                next_chapter = current_chapter
                next_section = current_section + 1
            else:
                # 다음 챕터의 첫 번째 섹션으로 진행
                next_chapter = current_chapter + 1
                next_section = 1
            
            # 최대 챕터 수 확인 (총 8챕터)
            total_chapters = self._get_total_chapters()
            if next_chapter > total_chapters:
                # 모든 학습 완료
                self.logger.info(f"모든 학습 완료: {current_chapter}챕터 {current_section}섹션이 마지막")
                return current_chapter, current_section
            
            return next_chapter, next_section
            
        except Exception as e:
            self.logger.error(f"다음 진행 상태 계산 중 오류: {str(e)}")
            # 오류 시 현재 상태 유지
            return current_chapter, current_section
    
    def _get_max_sections_for_chapter(self, chapter_number: int) -> int:
        """
        chapters_metadata.json 파일에서 챕터의 최대 섹션 수 조회 (v2.3 신규)
        
        Args:
            chapter_number: 챕터 번호
            
        Returns:
            해당 챕터의 최대 섹션 수
        """
        try:
            metadata = self._load_chapters_metadata()
            
            if metadata and "chapters" in metadata:
                for chapter in metadata["chapters"]:
                    if chapter["chapter_number"] == chapter_number:
                        return chapter["total_sections"]
            
            # 메타데이터를 찾을 수 없으면 기본값 반환
            self.logger.warning(f"챕터 {chapter_number} 메타데이터 없음, 기본값 4 반환")
            return 4
            
        except Exception as e:
            self.logger.error(f"최대 섹션 수 조회 중 오류: {str(e)}")
            return 4
    
    def _get_total_chapters(self) -> int:
        """
        총 챕터 수 조회 (v2.3 신규)
        
        Returns:
            총 챕터 수
        """
        try:
            metadata = self._load_chapters_metadata()
            
            if metadata and "metadata" in metadata:
                return metadata["metadata"]["total_chapters"]
            
            # 메타데이터를 찾을 수 없으면 기본값 반환
            self.logger.warning("총 챕터 수 메타데이터 없음, 기본값 8 반환")
            return 8
            
        except Exception as e:
            self.logger.error(f"총 챕터 수 조회 중 오류: {str(e)}")
            return 8
    
    def _load_chapters_metadata(self) -> Dict[str, Any]:
        """
        chapters_metadata.json 파일 로드 (캐싱 적용) (v2.3 신규)
        
        Returns:
            챕터 메타데이터 딕셔너리
        """
        # 캐시된 데이터가 있으면 반환
        if self._chapters_metadata is not None:
            return self._chapters_metadata
        
        try:
            # backend/data/chapters/chapters_metadata.json 경로
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            metadata_file = os.path.join(project_root, "data", "chapters", "chapters_metadata.json")
            
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self._chapters_metadata = json.load(f)
                    self.logger.info(f"챕터 메타데이터 로드 완료: {metadata_file}")
                    return self._chapters_metadata
            else:
                self.logger.error(f"챕터 메타데이터 파일 없음: {metadata_file}")
                return {}
                
        except Exception as e:
            self.logger.error(f"챕터 메타데이터 로드 중 오류: {str(e)}")
            return {}
    
    def _save_current_session_to_db_with_progress(self, state: TutorState, session_data: Dict[str, Any]) -> int:
        """
        세션 데이터와 진행 상태를 분리하여 DB에 저장 (v2.3 수정)
        
        Args:
            state: 현재 TutorState (퀴즈 정보 및 대화 기록용)
            session_data: 세션 기본 정보 + 진행 상태 정보
            
        Returns:
            저장된 세션 ID
        """
        try:
            # 1. session_data와 progress_data 분리
            learning_sessions_data = {
                "user_id": session_data["user_id"],
                "chapter_number": session_data["chapter_number"],
                "section_number": session_data["section_number"],
                "session_start_time": session_data["session_start_time"],
                "session_end_time": session_data["session_end_time"],
                "study_duration_seconds": session_data["study_duration_seconds"],
                "retry_decision_result": session_data["retry_decision_result"]
            }
            
            progress_data = {
                "next_chapter": session_data.get("next_chapter"),
                "next_section": session_data.get("next_section")
            }
            
            # 2. SessionHandlers에 분리된 데이터 전달
            session_id = self.session_handlers.save_session_info(learning_sessions_data, progress_data)
            
            if not session_id:
                raise Exception("세션 ID 생성 실패")
            
            # 3. 대화 기록 저장
            conversations = state.get("current_session_conversations", [])
            if conversations:
                success = self.session_handlers.save_session_conversations(session_id, conversations)
                if not success:
                    self.logger.warning(f"대화 기록 저장 실패: session_id={session_id}")
            
            # 4. 퀴즈 정보 저장
            quiz_data = self._prepare_quiz_data(state, session_id)
            if quiz_data:
                success = self.session_handlers.save_session_quiz(quiz_data)
                if not success:
                    self.logger.warning(f"퀴즈 정보 저장 실패: session_id={session_id}")

            # 5. 모든 저장 완료 후 퀴즈 통계 재계산 (v2.4 추가)
            self.session_handlers.finalize_session_statistics(session_data["user_id"])
            
            self.logger.info(f"세션 데이터 DB 저장 완료: session_id={session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"DB 저장 중 오류: {str(e)}")
            return -1
    
    def _save_current_session_to_db(self, state: TutorState) -> int:
        """
        현재 세션 데이터를 DB에 저장 (기존 메서드 유지)
        
        Args:
            state: 현재 TutorState
            
        Returns:
            저장된 세션 ID (AUTO_INCREMENT로 생성된 정수)
        """
        # 진행 상태 계산이 포함된 새 메서드 사용
        decision_result = state.get("retry_decision_result", "proceed")
        session_data = self._prepare_session_data_with_next_progress(state, decision_result)
        return self._save_current_session_to_db_with_progress(state, session_data)
    
    def _prepare_session_data(self, state: TutorState) -> Dict[str, Any]:
        """learning_sessions 테이블용 데이터 준비"""
        session_start = state.get("session_start_time", datetime.now())
        session_end = datetime.now()
        
        # 학습 시간 계산 (초 단위)
        if isinstance(session_start, datetime):
            duration = (session_end - session_start).total_seconds()
        else:
            duration = 0
        
        return {
            # session_id는 AUTO_INCREMENT로 자동 생성되므로 제외
            "user_id": state["user_id"],
            "chapter_number": state["current_chapter"],
            "section_number": state["current_section"],
            "session_start_time": session_start,
            "session_end_time": session_end,
            "study_duration_seconds": int(duration),
            "retry_decision_result": state.get("retry_decision_result", "proceed"),
            "current_session_conversations": state.get("current_session_conversations", [])
        }
    
    def _prepare_quiz_data(self, state: TutorState, session_id: int) -> Dict[str, Any]:
        """session_quizzes 테이블용 데이터 준비"""
        # 퀴즈 정보가 있는 경우에만 데이터 준비
        if not state.get("quiz_content"):
            return None
        
        quiz_type = state.get("quiz_type", "multiple_choice")
        
        # 기본 퀴즈 데이터
        quiz_data = {
            "session_id": session_id,
            "quiz_type": quiz_type,
            "quiz_content": state.get("quiz_content", ""),
            "quiz_hint": state.get("quiz_hint", ""),
            "user_answer": state.get("user_answer", ""),
            "evaluation_feedback": state.get("evaluation_feedback", ""),
            "hint_usage_count": state.get("hint_usage_count", 0)
        }
        
        # 객관식 전용 필드
        if quiz_type == "multiple_choice":
            quiz_options = state.get("quiz_options", [])
            quiz_options_json = json.dumps(quiz_options, ensure_ascii=False) if quiz_options else "[]"
            
            quiz_data.update({
                "quiz_options": quiz_options_json,
                "quiz_correct_answer": state.get("quiz_correct_answer"),
                "quiz_explanation": state.get("quiz_explanation", ""),
                "multiple_answer_correct": state.get("multiple_answer_correct", False),
                # 주관식 필드는 NULL
                "quiz_sample_answer": None,
                "quiz_evaluation_criteria": None,
                "subjective_answer_score": None
            })
        
        # 주관식 전용 필드
        else:  # subjective
            evaluation_criteria = state.get("quiz_evaluation_criteria", [])
            evaluation_criteria_json = json.dumps(evaluation_criteria, ensure_ascii=False) if evaluation_criteria else "[]"
            
            quiz_data.update({
                "quiz_sample_answer": state.get("quiz_sample_answer", ""),
                "quiz_evaluation_criteria": evaluation_criteria_json,
                "subjective_answer_score": state.get("subjective_answer_score", 0),
                # 객관식 필드는 NULL
                "quiz_options": None,
                "quiz_correct_answer": None,
                "quiz_explanation": None,
                "multiple_answer_correct": None
            })
        
        return quiz_data
    
    def _add_session_summary_to_state(self, state: TutorState, decision_result: str, session_id: int) -> TutorState:
        """
        세션 요약을 State에 추가 (SessionService에서 활용 가능)
        
        Args:
            state: 현재 TutorState
            decision_result: 세션 결정 결과
            session_id: 저장된 세션 ID
            
        Returns:
            요약이 추가된 TutorState
        """
        try:
            # 현재 세션 요약 생성
            session_summary = self._create_session_summary(state, decision_result, session_id)
            
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
            
            return updated_state
            
        except Exception as e:
            self.logger.error(f"세션 요약 추가 중 오류: {str(e)}")
            return state
    
    def _create_session_summary(self, state: TutorState, decision_result: str, session_id: int) -> Dict[str, Any]:
        """현재 세션 요약 생성"""
        chapter = state["current_chapter"]
        section = state["current_section"]
        quiz_type = state.get("quiz_type", "unknown")
        
        # 객관식/주관식 분리된 점수 처리
        if quiz_type == "multiple_choice":
            is_correct = state.get("multiple_answer_correct", False)
            score_display = "정답" if is_correct else "오답"
        else:  # subjective
            score = state.get("subjective_answer_score", 0)
            score_display = f"{score}점"
        
        return {
            "session_id": session_id,
            "chapter_section": f"{chapter}챕터 {section}섹션",
            "quiz_result": f"{quiz_type} 퀴즈 {score_display}",
            "decision": "재학습 필요" if decision_result == "retry" else "진행 완료",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "study_duration_seconds": self._calculate_study_time(state)
        }
    
    def _create_completion_message(self, state: TutorState, decision_result: str, session_id: int) -> str:
        """세션 완료 메시지 생성"""
        chapter = state["current_chapter"]
        section = state["current_section"]
        
        if session_id > 0:
            if decision_result == "proceed":
                return f"{chapter}챕터 {section}섹션이 성공적으로 완료되었습니다. (세션 ID: {session_id})"
            else:
                return f"{chapter}챕터 {section}섹션 재학습이 필요합니다. (세션 ID: {session_id})"
        else:
            return f"{chapter}챕터 {section}섹션 처리가 완료되었습니다. (저장 중 오류 발생)"
    
    def _calculate_study_time(self, state: TutorState) -> int:
        """학습 시간 계산 (초 단위)"""
        start_time = state.get("session_start_time")
        if not start_time or not isinstance(start_time, datetime):
            return 0
        
        duration = datetime.now() - start_time
        return int(duration.total_seconds())
    
    def _handle_save_error(self, state: TutorState, error_message: str) -> TutorState:
        """
        저장 오류 처리
        
        Args:
            state: 현재 TutorState
            error_message: 오류 메시지
            
        Returns:
            오류 메시지가 추가된 TutorState
        """
        self.logger.error(f"세션 저장 오류 처리: {error_message}")
        
        # 오류 메시지 생성
        chapter = state["current_chapter"]
        section = state["current_section"]
        error_msg = f"{chapter}챕터 {section}섹션 처리 중 저장 오류가 발생했습니다. 학습은 계속 진행됩니다. (오류: {error_message})"
        
        # State에 오류 메시지 추가
        updated_state = state_manager.add_conversation(
            state,
            agent_name=self.agent_name,
            message=error_msg,
            message_type="system"
        )
        
        # 현재 에이전트 정보 업데이트
        updated_state = state_manager.update_agent_transition(updated_state, self.agent_name)
        
        return updated_state
    
    # ==========================================
    # 유틸리티 및 조회 메서드
    # ==========================================
    
    def get_session_save_status(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 세션 저장 가능 상태 확인
        
        Args:
            state: 현재 TutorState
            
        Returns:
            저장 상태 요약
        """
        return {
            "ready_for_save": bool(state.get("retry_decision_result")),
            "current_chapter": state["current_chapter"],
            "current_section": state["current_section"],
            "session_stage": state.get("session_progress_stage", "session_start"),
            "has_quiz_data": bool(state.get("quiz_content")),
            "conversations_count": len(state.get("current_session_conversations", [])),
            "decision_result": state.get("retry_decision_result", ""),
            "estimated_study_time": self._calculate_study_time(state)
        }
    
    def get_user_session_history_count(self, user_id: int, chapter_number: int, section_number: int) -> int:
        """
        특정 사용자의 특정 챕터/섹션에서의 세션 횟수 조회 (외부 호출용)
        
        Args:
            user_id: 사용자 ID
            chapter_number: 챕터 번호
            section_number: 섹션 번호
            
        Returns:
            해당 섹션에서의 세션 횟수
        """
        return self.session_handlers.get_user_session_count(user_id, chapter_number, section_number)
    
    def cleanup_old_session_data(self, days_to_keep: int = 90) -> bool:
        """
        오래된 세션 데이터 정리 (관리용)
        
        Args:
            days_to_keep: 보관할 일 수
            
        Returns:
            정리 성공 여부
        """
        return self.session_handlers.cleanup_old_sessions(days_to_keep)