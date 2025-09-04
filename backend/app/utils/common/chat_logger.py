# backend/app/utils/common/chat_logger.py

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from app.core.langraph.state_manager import TutorState


class ChatLogger:
    """
    대화 기록을 JSON 파일로 저장하는 유틸리티
    
    저장 구조:
    backend/logs/user_chat_log/user{user_id}/
    ├── 20250813_143052_ch1_session001.json
    ├── 20250813_150245_ch1_session002.json
    └── 20250813_163018_ch2_session001.json
    """
    
    def __init__(self, base_path: str = None):
        """
        ChatLogger 초기화
        
        Args:
            base_path: 기본 저장 경로 (기본값: backend/logs/user_chat_log)
        """
        if base_path is None:
            # 프로젝트 루트에서 backend/logs/user_chat_log 경로 설정
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            self.base_path = os.path.join(project_root, "logs", "user_chat_log")
        else:
            self.base_path = base_path
        
        # 기본 디렉토리 생성
        self._ensure_directory_exists(self.base_path)
    
    def save_session_log(self, state: TutorState, session_complete: bool = False) -> str:
        """
        세션 대화 로그를 JSON 파일로 저장
        
        Args:
            state: 현재 TutorState
            session_complete: 세션 완료 여부 (완료 시 최종 저장)
        
        Returns:
            저장된 파일 경로
        """
        try:
            # 사용자별 디렉토리 생성
            user_dir = self._get_user_directory(state["user_id"])
            self._ensure_directory_exists(user_dir)
            
            # 파일명 생성
            filename = self._generate_filename(state)
            file_path = os.path.join(user_dir, filename)
            
            # 저장할 데이터 구성
            log_data = self._prepare_log_data(state, session_complete)
            
            # JSON 파일로 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=4, ensure_ascii=False, default=str)
            
            print(f"대화 로그 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"대화 로그 저장 중 오류: {e}")
            return ""
    
    def load_session_log(self, user_id: int, session_id: str) -> Dict[str, Any]:
        """
        저장된 세션 로그 불러오기
        
        Args:
            user_id: 사용자 ID
            session_id: 세션 ID
        
        Returns:
            로드된 세션 데이터
        """
        try:
            user_dir = self._get_user_directory(user_id)
            
            # session_id에서 파일명 추출
            filename = self._extract_filename_from_session_id(session_id)
            file_path = os.path.join(user_dir, filename)
            
            if not os.path.exists(file_path):
                print(f"세션 로그 파일을 찾을 수 없음: {file_path}")
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"세션 로그 로드 중 오류: {e}")
            return {}
    
    def get_user_session_list(self, user_id: int) -> List[str]:
        """
        사용자의 모든 세션 로그 파일 목록 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            세션 파일명 목록
        """
        try:
            user_dir = self._get_user_directory(user_id)
            
            if not os.path.exists(user_dir):
                return []
            
            # .json 파일만 필터링하여 반환
            session_files = [
                f for f in os.listdir(user_dir) 
                if f.endswith('.json')
            ]
            
            # 파일명으로 정렬 (시간순)
            session_files.sort()
            
            return session_files
            
        except Exception as e:
            print(f"세션 목록 조회 중 오류: {e}")
            return []
    
    def _get_user_directory(self, user_id: int) -> str:
        """
        사용자별 디렉토리 경로 반환
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            사용자 디렉토리 경로
        """
        return os.path.join(self.base_path, f"user{user_id}")
    
    def _ensure_directory_exists(self, directory_path: str) -> None:
        """
        디렉토리가 존재하지 않으면 생성
        
        Args:
            directory_path: 디렉토리 경로
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
    
    def _generate_filename(self, state: TutorState) -> str:
        """
        세션 로그 파일명 생성
        
        Args:
            state: TutorState
        
        Returns:
            파일명 (예: 20250813_143052_ch1_session001.json)
        """
        # 세션 시작 시간에서 timestamp 추출
        session_start = state.get("session_start_time", datetime.now())
        if isinstance(session_start, str):
            session_start = datetime.fromisoformat(session_start.replace('Z', '+00:00'))
        
        timestamp = session_start.strftime("%Y%m%d_%H%M%S")
        chapter = state["current_chapter"]
        section = state["current_section"]
        session_count = state.get("current_session_count", 1)
        
        return f"{timestamp}_ch{chapter}_sec{section}_session{session_count:03d}.json"
    
    def _extract_filename_from_session_id(self, session_id: str) -> str:
        """
        session_id에서 파일명 추출
        
        Args:
            session_id: 세션 ID (예: user123_ch1_session001_20250813_143052)
        
        Returns:
            파일명 (예: 20250813_143052_ch1_session001.json)
        """
        # session_id 파싱: user{id}_ch{chapter}_session{count}_{timestamp}
        parts = session_id.split('_')
        if len(parts) >= 4:
            chapter_part = parts[1]  # ch1
            session_part = parts[2]  # session001
            date_part = parts[3]     # 20250813
            time_part = parts[4] if len(parts) > 4 else "000000"  # 143052
            
            return f"{date_part}_{time_part}_{chapter_part}_{session_part}.json"
        
        # 파싱 실패 시 기본 형식으로 생성
        return f"{session_id}.json"
    
    def _prepare_log_data(self, state: TutorState, session_complete: bool = False) -> Dict[str, Any]:
        """
        저장할 로그 데이터 구성
        
        Args:
            state: TutorState
            session_complete: 세션 완료 여부
        
        Returns:
            JSON 저장용 데이터
        """
        # 기본 세션 정보
        log_data = {
            "session_info": {
                "session_id": f"user{state['user_id']}_ch{state['current_chapter']}_session{state.get('current_session_count', 1):03d}_{state.get('session_start_time', datetime.now()).strftime('%Y%m%d_%H%M%S')}",
                "user_id": state["user_id"],
                "user_type": state["user_type"],
                "chapter": state["current_chapter"],
                "section": state["current_section"],
                "session_start_time": state.get("session_start_time", datetime.now()),
                "session_complete": session_complete,
                "saved_at": datetime.now()
            },
            "session_progress": {
                "current_stage": state["session_progress_stage"],
                "ui_mode": state["ui_mode"],
                "current_agent": state["current_agent"],
                "previous_agent": state.get("previous_agent", "")
            },
            "conversations": self._format_conversations(state.get("current_session_conversations", [])),
            "quiz_info": self._format_quiz_info(state),
            "agent_drafts": {
                "theory_draft": state.get("theory_draft", ""),
                "quiz_draft": state.get("quiz_draft", ""),
                "feedback_draft": state.get("feedback_draft", ""),
                "qna_draft": state.get("qna_draft", "")
            }
        }
        
        # 세션 완료 시 추가 정보
        if session_complete:
            log_data["session_result"] = {
                "decision": state.get("session_decision_result", ""),
                "session_count": state.get("current_session_count", 1),
                "study_duration_minutes": self._calculate_session_duration(state)
            }
        
        return log_data
    
    def _format_conversations(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        대화 기록 포맷팅
        
        Args:
            conversations: 원본 대화 기록
        
        Returns:
            포맷된 대화 기록
        """
        formatted_conversations = []
        
        for idx, conv in enumerate(conversations):
            formatted_conv = {
                "message_sequence": idx + 1,
                "agent_name": conv.get("agent_name", "unknown"),
                "message_type": conv.get("message_type", "system"),
                "message_content": conv.get("message", ""),
                "timestamp": conv.get("timestamp", datetime.now()),
                "session_stage": conv.get("session_stage", "")
            }
            formatted_conversations.append(formatted_conv)
        
        return formatted_conversations
    
    def _format_quiz_info(self, state: TutorState) -> Dict[str, Any]:
        """
        퀴즈 정보 포맷팅
        
        Args:
            state: TutorState
        
        Returns:
            포맷된 퀴즈 정보
        """
        return {
            "question_type": state.get("current_question_type", ""),
            "question_number": state.get("current_question_number", 0),
            "question_content": state.get("current_question_content", ""),
            "user_answer": state.get("current_question_answer", ""),
            "is_answer_correct": state.get("is_answer_correct", 0),
            "evaluation_feedback": state.get("evaluation_feedback", ""),
            "hint_usage_count": state.get("hint_usage_count", 0)
        }
    
    def _calculate_session_duration(self, state: TutorState) -> int:
        """
        세션 진행 시간 계산 (분)
        
        Args:
            state: TutorState
        
        Returns:
            진행 시간 (분)
        """
        try:
            start_time = state.get("session_start_time", datetime.now())
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            duration = datetime.now() - start_time
            return int(duration.total_seconds() / 60)
            
        except Exception as e:
            print(f"세션 시간 계산 중 오류: {e}")
            return 0


# 전역 ChatLogger 인스턴스
chat_logger = ChatLogger()