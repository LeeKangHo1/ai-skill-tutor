# backend/app/services/learning/session_service.py
from typing import Dict, Any, Optional
from datetime import datetime
import copy
import json
import os

from app.core.langraph.state_manager import state_manager, TutorState
from app.core.langraph.workflow import execute_tutor_workflow_sync
from app.utils.auth.jwt_handler import decode_token
from app.utils.response.formatter import success_response, error_response
from app.utils.database.connection import fetch_one
from app.utils.database.query_builder import QueryBuilder


class SessionService:
    """
    학습 세션 서비스 - 사용자별 State 관리 및 워크플로우 실행
    
    주요 기능:
    1. 사용자별 TutorState 메모리 저장 및 관리
    2. 세션 시작/메시지 처리 통합 관리
    3. 워크플로우 실행 및 응답 처리
    4. 단일 세션 보장 (기존 JWT 정책 활용)
    5. 기존 인증/진단 시스템과 완전 호환
    """
    
    def __init__(self):
        # 사용자별 State 저장소 (메모리)
        # {user_id: {"state": TutorState, "last_activity": datetime, "session_id": str}}
        self._user_states: Dict[int, Dict[str, Any]] = {}
        
        # State 만료 시간 (1시간)
        self.STATE_EXPIRE_SECONDS = 3600
    
    def start_session(self, token: str, chapter_number: int, section_number: int, user_message: str) -> Dict[str, Any]:
        """
        학습 세션 시작
        
        Args:
            token: JWT 액세스 토큰
            chapter_number: 시작할 챕터 번호
            section_number: 시작할 섹션 번호
            user_message: 사용자 초기 메시지 ("2챕터 시작할게요")
            
        Returns:
            세션 시작 결과 및 워크플로우 응답
        """
        try:
            # JWT 토큰에서 사용자 정보 추출
            user_info = decode_token(token)
            if not user_info:
                return error_response("AUTH_TOKEN_INVALID", "유효하지 않은 토큰입니다.")
            
            user_id = user_info.get("user_id")
            user_type = user_info.get("user_type")
            
            if not user_id or not user_type:
                return error_response("AUTH_TOKEN_INVALID", "토큰에 필요한 정보가 없습니다.")
            
            # 사용자 유형이 설정되지 않은 경우
            if user_type == "unassigned":
                return error_response("DIAGNOSIS_NOT_COMPLETED", "진단을 먼저 완료해주세요.")
            
            # 사용자 학습 권한 확인 (JWT 검증 제외)
            access_validation = self._validate_learning_access(user_id, chapter_number, section_number)
            if not access_validation["valid"]:
                return error_response(access_validation["error_code"], access_validation["message"])
            
            # 기존 활성 세션이 있다면 정리
            self._clear_user_state(user_id)
            
            # 새로운 TutorState 생성
            initial_state = state_manager.initialize_state(
                user_id=user_id,
                user_type=user_type,
                current_chapter=chapter_number,
                current_section=section_number
            )
            
            # 사용자 메시지를 State에 추가
            initial_state = state_manager.add_conversation(
                initial_state,
                agent_name="user",
                message=user_message,
                message_type="user"
            )
            
            # 세션 시작 시간 설정
            initial_state["session_start_time"] = datetime.now()
            initial_state["user_intent"] = "next_step"  # 세션 시작은 자동으로 next_step
            
            # 워크플로우 실행
            final_state = execute_tutor_workflow_sync(initial_state)
            
            # 사용자 State 저장
            session_id = f"session_{user_id}_{int(datetime.now().timestamp())}"
            self._store_user_state(user_id, final_state, session_id)
            
            # 세션 정보 및 워크플로우 응답 반환
            session_info = {
                "chapter_number": chapter_number,
                "section_number": section_number,
                "chapter_title": self._get_chapter_title(chapter_number),
                "section_title": self._get_section_title(chapter_number, section_number),
                "estimated_duration": "15분"  # 기본값
            }
            
            workflow_response = final_state.get("workflow_response", {})
            
            return success_response({
                "session_info": session_info,
                "workflow_response": workflow_response
            }, "학습 세션이 시작되었습니다.")
            
        except Exception as e:
            return error_response("SESSION_START_ERROR", f"세션 시작 중 오류 발생: {str(e)}")
    
    def process_message(self, token: str, user_message: str) -> Dict[str, Any]:
        """
        사용자 메시지 처리
        
        Args:
            token: JWT 액세스 토큰
            user_message: 사용자 메시지
            
        Returns:
            워크플로우 처리 결과
        """
        try:
            # JWT 토큰에서 사용자 정보 추출
            user_info = decode_token(token)
            if not user_info:
                return error_response("AUTH_TOKEN_INVALID", "유효하지 않은 토큰입니다.")
            
            user_id = user_info.get("user_id")
            if not user_id:
                return error_response("AUTH_TOKEN_INVALID", "토큰에 사용자 정보가 없습니다.")
            
            # 저장된 State 가져오기
            current_state = self._get_user_state(user_id)
            if not current_state:
                return error_response("SESSION_NOT_FOUND", "활성 세션을 찾을 수 없습니다.")
            
            # 사용자 메시지를 State에 추가
            updated_state = state_manager.add_conversation(
                current_state,
                agent_name="user",
                message=user_message,
                message_type="user"
            )
            
            # 워크플로우 실행 (LearningSupervisor가 의도 분석 처리)
            final_state = execute_tutor_workflow_sync(updated_state)
            
            # 업데이트된 State 저장
            self._update_user_state(user_id, final_state)
            
            # 워크플로우 응답 반환
            workflow_response = final_state.get("workflow_response", {})
            
            return success_response({
                "workflow_response": workflow_response
            }, "메시지가 처리되었습니다.")
            
        except Exception as e:
            return error_response("MESSAGE_PROCESS_ERROR", f"메시지 처리 중 오류 발생: {str(e)}")
    
    def submit_quiz_answer(self, token: str, user_answer: str) -> Dict[str, Any]:
        """
        퀴즈 답변 제출 (State에 직접 설정 후 워크플로우 실행)
        
        Args:
            token: JWT 액세스 토큰
            user_answer: 사용자 답변
            
        Returns:
            퀴즈 평가 결과 및 워크플로우 응답
        """
        try:
            # JWT 토큰에서 사용자 정보 추출
            user_info = decode_token(token)
            if not user_info:
                return error_response("AUTH_TOKEN_INVALID", "유효하지 않은 토큰입니다.")
            
            user_id = user_info.get("user_id")
            if not user_id:
                return error_response("AUTH_TOKEN_INVALID", "토큰에 사용자 정보가 없습니다.")
            
            # 저장된 State 가져오기
            current_state = self._get_user_state(user_id)
            if not current_state:
                return error_response("SESSION_NOT_FOUND", "활성 세션을 찾을 수 없습니다.")
            
            # 사용자 답변을 State에 직접 설정
            updated_state = current_state.copy()
            updated_state["user_answer"] = user_answer
            updated_state["user_intent"] = "quiz_answer"  # 명확한 의도 설정
            
            # 워크플로우 실행 (바로 EvaluationFeedbackAgent로 라우팅)
            final_state = execute_tutor_workflow_sync(updated_state)
            
            # 업데이트된 State 저장
            self._update_user_state(user_id, final_state)
            
            # 워크플로우 응답 반환
            workflow_response = final_state.get("workflow_response", {})
            
            return success_response({
                "workflow_response": workflow_response
            }, "퀴즈 답변이 평가되었습니다.")
            
        except Exception as e:
            return error_response("QUIZ_SUBMIT_ERROR", f"퀴즈 답변 처리 중 오류 발생: {str(e)}")
    
    def complete_session(self, token: str, proceed_decision: str) -> Dict[str, Any]:
        """
        세션 완료 처리
        
        Args:
            token: JWT 액세스 토큰
            proceed_decision: 진행 결정 ("proceed" 또는 "retry")
            
        Returns:
            세션 완료 결과
        """
        try:
            # JWT 토큰에서 사용자 정보 추출
            user_info = decode_token(token)
            if not user_info:
                return error_response("AUTH_TOKEN_INVALID", "유효하지 않은 토큰입니다.")
            
            user_id = user_info.get("user_id")
            if not user_id:
                return error_response("AUTH_TOKEN_INVALID", "토큰에 사용자 정보가 없습니다.")
            
            # 저장된 State 가져오기
            current_state = self._get_user_state(user_id)
            if not current_state:
                return error_response("SESSION_NOT_FOUND", "활성 세션을 찾을 수 없습니다.")
            
            # 진행 결정 검증
            if proceed_decision not in ["proceed", "retry"]:
                return error_response("INVALID_DECISION", "올바르지 않은 진행 결정입니다.")
            
            # 진행 결정 업데이트
            updated_state = state_manager.update_session_decision(current_state, proceed_decision)
            updated_state["user_intent"] = "next_step"  # 세션 완료 처리
            
            # 워크플로우 실행 (SessionManager가 호출되어 DB 저장)
            final_state = execute_tutor_workflow_sync(updated_state)
            
            # SessionManager에서 DB 저장이 완료되면 State 초기화
            self._clear_user_state(user_id)
            
            # 워크플로우 응답 반환
            workflow_response = final_state.get("workflow_response", {})
            
            return success_response({
                "workflow_response": workflow_response
            }, "세션이 완료되었습니다.")
            
        except Exception as e:
            return error_response("SESSION_COMPLETE_ERROR", f"세션 완료 중 오류 발생: {str(e)}")
    
    def get_session_status(self, token: str) -> Dict[str, Any]:
        """
        현재 세션 상태 조회
        
        Args:
            token: JWT 액세스 토큰
            
        Returns:
            세션 상태 정보
        """
        try:
            # JWT 토큰에서 사용자 정보 추출
            user_info = decode_token(token)
            if not user_info:
                return error_response("AUTH_TOKEN_INVALID", "유효하지 않은 토큰입니다.")
            
            user_id = user_info.get("user_id")
            if not user_id:
                return error_response("AUTH_TOKEN_INVALID", "토큰에 사용자 정보가 없습니다.")
            
            # 저장된 State 확인
            current_state = self._get_user_state(user_id)
            
            if not current_state:
                return success_response({
                    "has_active_session": False,
                    "session_info": None
                }, "활성 세션이 없습니다.")
            
            # 세션 정보 구성
            session_info = {
                "has_active_session": True,
                "current_chapter": current_state.get("current_chapter"),
                "current_section": current_state.get("current_section"),
                "chapter_title": self._get_chapter_title(current_state.get("current_chapter")),
                "section_title": self._get_section_title(current_state.get("current_chapter"), current_state.get("current_section")),
                "session_progress_stage": current_state.get("session_progress_stage"),
                "last_activity": self._user_states[user_id]["last_activity"].isoformat()
            }
            
            return success_response({
                "session_info": session_info
            }, "세션 상태를 조회했습니다.")
            
        except Exception as e:
            return error_response("SESSION_STATUS_ERROR", f"세션 상태 조회 중 오류 발생: {str(e)}")
    
    # ==========================================
    # 내부 State 관리 메서드
    # ==========================================
    
    def _store_user_state(self, user_id: int, state: TutorState, session_id: str) -> None:
        """사용자 State 저장"""
        self._user_states[user_id] = {
            "state": copy.deepcopy(state),
            "last_activity": datetime.now(),
            "session_id": session_id
        }
    
    def _get_user_state(self, user_id: int) -> Optional[TutorState]:
        """사용자 State 조회 (만료 체크 포함)"""
        if user_id not in self._user_states:
            return None
        
        user_state_data = self._user_states[user_id]
        last_activity = user_state_data["last_activity"]
        
        # 만료 체크
        if (datetime.now() - last_activity).total_seconds() > self.STATE_EXPIRE_SECONDS:
            self._clear_user_state(user_id)
            return None
        
        return user_state_data["state"]
    
    def _update_user_state(self, user_id: int, state: TutorState) -> None:
        """사용자 State 업데이트"""
        if user_id in self._user_states:
            self._user_states[user_id]["state"] = copy.deepcopy(state)
            self._user_states[user_id]["last_activity"] = datetime.now()
    
    def _clear_user_state(self, user_id: int) -> None:
        """사용자 State 삭제"""
        if user_id in self._user_states:
            del self._user_states[user_id]
    
    # ==========================================
    # 워크플로우 응답 처리 메서드
    # ==========================================
    
    def _extract_workflow_response(self, state: TutorState) -> Dict[str, Any]:
        """워크플로우 실행 결과에서 응답 추출"""
        # response_generator에서 생성한 workflow_response 형태 추출
        current_agent = state.get("current_agent", "")
        session_progress_stage = state.get("session_progress_stage", "")
        
        # 기본 응답 구조
        workflow_response = {
            "current_agent": current_agent,
            "session_progress_stage": session_progress_stage,
            "ui_mode": "chat"  # 기본값
        }
        
        # 에이전트별 응답 내용 추출
        if current_agent == "theory_educator":
            return {
                **workflow_response,
                "ui_mode": "chat",
                "content": {
                    "type": "theory",
                    "content": state.get("theory_draft", "이론 설명을 준비 중입니다...")
                }
            }
        elif current_agent == "quiz_generator":
            return {
                **workflow_response,
                "ui_mode": "quiz",
                "content": {
                    "type": "quiz",
                    "quiz_type": state.get("quiz_type", "multiple_choice"),
                    "quiz_content": state.get("quiz_content", ""),
                    "quiz_options": state.get("quiz_options", []),
                    "quiz_hint": state.get("quiz_hint", "")
                }
            }
        elif current_agent == "evaluation_feedback_agent":
            return {
                **workflow_response,
                "ui_mode": "chat",
                "evaluation_result": {
                    "quiz_type": state.get("quiz_type", "multiple_choice"),
                    "is_answer_correct": state.get("multiple_answer_correct", False),
                    "score": state.get("subjective_answer_score", 0),
                    "feedback": {
                        "type": "feedback",
                        "content": state.get("evaluation_feedback_draft", "평가 결과를 준비 중입니다..."),
                        "next_step_decision": state.get("session_decision_result", "proceed")
                    }
                }
            }
        elif current_agent == "qna_resolver":
            return {
                **workflow_response,
                "ui_mode": "chat",
                "content": {
                    "type": "qna",
                    "content": state.get("qna_draft", "질문에 대한 답변을 준비 중입니다...")
                }
            }
        elif current_agent == "session_manager":
            return {
                **workflow_response,
                "ui_mode": "chat",
                "session_completion": {
                    "completed_chapter": state.get("current_chapter"),
                    "completed_section": state.get("current_section"),
                    "next_chapter": state.get("current_chapter"),
                    "next_section": state.get("current_section") + 1,
                    "session_summary": f"{state.get('current_chapter')}챕터 {state.get('current_section')}섹션을 완료했습니다.",
                    "study_time_minutes": self._calculate_study_time(state)
                }
            }
        else:
            return {
                **workflow_response,
                "content": {
                    "type": "general",
                    "content": "처리 중입니다..."
                }
            }
    
    def _validate_learning_access(self, user_id: int, chapter_number: int, section_number: int) -> Dict[str, Any]:
        """
        사용자 학습 권한 검증 (진행 상태만 확인)
        
        Args:
            user_id: 사용자 ID
            chapter_number: 접근하려는 챕터
            section_number: 접근하려는 섹션
            
        Returns:
            검증 결과 딕셔너리
        """
        try:
            # 사용자 진행 상태 확인
            progress_query = (QueryBuilder()
                            .select(["current_chapter", "current_section"])
                            .from_table("user_progress")
                            .where("user_id = %s", [user_id])
                            .build())
            
            progress_result = fetch_one(progress_query['query'], progress_query['params'])
            
            if not progress_result:
                # 진행 상태가 없으면 1챕터 1섹션만 허용
                if chapter_number == 1 and section_number == 1:
                    return {"valid": True}
                else:
                    return {
                        "valid": False,
                        "error_code": "CHAPTER_ACCESS_DENIED",
                        "message": "1챕터 1섹션부터 시작해주세요."
                    }
            
            current_chapter = progress_result["current_chapter"]
            current_section = progress_result["current_section"]
            
            # 챕터 접근 권한 확인
            if chapter_number < current_chapter:
                # 이전 챕터는 언제든 접근 가능
                return {"valid": True}
            elif chapter_number == current_chapter:
                # 현재 챕터는 현재 섹션까지만 접근 가능
                if section_number <= current_section:
                    return {"valid": True}
                else:
                    return {
                        "valid": False,
                        "error_code": "SECTION_ACCESS_DENIED",
                        "message": f"아직 {chapter_number}챕터 {section_number}섹션에 접근할 수 없습니다."
                    }
            elif chapter_number == current_chapter + 1 and current_section >= self._get_max_sections(current_chapter):
                # 다음 챕터 첫 섹션 (현재 챕터 완료 시)
                if section_number == 1:
                    return {"valid": True}
                else:
                    return {
                        "valid": False,
                        "error_code": "SECTION_ACCESS_DENIED",
                        "message": f"{chapter_number}챕터 1섹션부터 시작해주세요."
                    }
            else:
                return {
                    "valid": False,
                    "error_code": "CHAPTER_ACCESS_DENIED",
                    "message": f"아직 {chapter_number}챕터에 접근할 수 없습니다."
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error_code": "ACCESS_VALIDATION_ERROR",
                "message": f"접근 권한 확인 중 오류 발생: {str(e)}"
            }
    
    def _load_chapters_metadata(self) -> Optional[Dict[str, Any]]:
        """
        챕터 메타데이터 로드 (요청 시마다 파일 읽기)
        """
        try:
            # backend/data/chapters/ 경로에서 메타데이터 파일 읽기
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            metadata_file = os.path.join(base_dir, "data", "chapters", "chapters_metadata.json")
            
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"챕터 메타데이터 로드 오류: {str(e)}")
            return None
    
    def _get_chapter_title(self, chapter_number: int) -> str:
        """챕터 제목 가져오기 (메타데이터 활용)"""
        metadata = self._load_chapters_metadata()
        if metadata and "chapters" in metadata:
            for chapter in metadata["chapters"]:
                if chapter["chapter_number"] == chapter_number:
                    return chapter["chapter_title"]
        
        # 메타데이터를 찾을 수 없으면 기본값 반환
        return f"{chapter_number}챕터"
    
    def _get_section_title(self, chapter_number: int, section_number: int) -> str:
        """섹션 제목 가져오기 (메타데이터 활용)"""
        metadata = self._load_chapters_metadata()
        if metadata and "chapters" in metadata:
            for chapter in metadata["chapters"]:
                if chapter["chapter_number"] == chapter_number:
                    sections = chapter.get("sections", [])
                    for section in sections:
                        if section["section_number"] == section_number:
                            return section["section_title"]
        
        # 메타데이터를 찾을 수 없으면 기본값 반환
        return f"{chapter_number}챕터 {section_number}섹션"
    
    def _get_max_sections(self, chapter_number: int) -> int:
        """챕터별 최대 섹션 수 반환 (메타데이터 활용)"""
        metadata = self._load_chapters_metadata()
        if metadata and "chapters" in metadata:
            for chapter in metadata["chapters"]:
                if chapter["chapter_number"] == chapter_number:
                    return chapter["total_sections"]
        
        # 메타데이터를 찾을 수 없으면 기본값 반환
        return 4
    
    def _calculate_study_time(self, state: TutorState) -> int:
        """학습 시간 계산 (분 단위)"""
        start_time = state.get("session_start_time")
        if not start_time:
            return 0
        
        duration = datetime.now() - start_time
        return int(duration.total_seconds() / 60)
    
    def _load_chapter_data(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """챕터 데이터 로드 (요청 시마다 파일 읽기) - 기존 메서드 유지"""
        try:
            # backend/data/chapters/ 경로에서 JSON 파일 읽기
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            chapter_file = os.path.join(base_dir, "data", "chapters", f"chapter_{chapter_number:02d}.json")
            
            if os.path.exists(chapter_file):
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"챕터 데이터 로드 오류: {str(e)}")
            return None
    
    # ==========================================
    # 관리용 메서드 (개발/디버깅용)
    # ==========================================
    
    def get_active_sessions_count(self) -> int:
        """현재 활성 세션 수 반환"""
        return len(self._user_states)
    
    def clear_expired_sessions(self) -> int:
        """만료된 세션 정리"""
        expired_users = []
        current_time = datetime.now()
        
        for user_id, state_data in self._user_states.items():
            last_activity = state_data["last_activity"]
            if (current_time - last_activity).total_seconds() > self.STATE_EXPIRE_SECONDS:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            self._clear_user_state(user_id)
        
        return len(expired_users)
    
    def clear_all_sessions(self) -> int:
        """모든 활성 세션 정리 (테스트용)"""
        session_count = len(self._user_states)
        self._user_states.clear()
        return session_count
    

# state 공유를 위한 세션 서비스 단일 인스턴스
session_service = SessionService()