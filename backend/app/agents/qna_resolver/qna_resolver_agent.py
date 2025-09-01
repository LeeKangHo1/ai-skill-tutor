# backend/app/agents/qna_resolver/qna_resolver_agent.py

from typing import Dict, Any
import os

from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.content.qna_tools_chatgpt import qna_generation_tool


class QnAResolverAgent:
    """
    QnA 답변 에이전트 v3.0 - LangChain Agent 기반 RAG 시스템
    - 사용자 질문을 분석하여 벡터 검색 기반 답변 생성
    - LangChain Agent가 Function calling을 완전히 실행
    - 순수 답변 대본만 생성 (사용자 대면 메시지 없음)
    """
    
    def __init__(self):
        self.agent_name = "qna_resolver"
    
    def process(self, state: TutorState) -> TutorState:
        """
        LangChain Agent 기반 QnA 답변 생성 메인 프로세스
        
        Args:
            state: 현재 TutorState
            
        Returns:
            업데이트된 TutorState (qna_draft 포함)
        """
        try:
            print(f"[{self.agent_name}] LangChain Agent 기반 QnA 답변 생성 시작")
            
            # 1. 사용자 질문 추출 (대화 기록에서 최근 user 메시지)
            user_question = self._extract_latest_user_message(state)
            
            print(f"[{self.agent_name}] 추출된 사용자 메시지: '{user_question}'")
            
            # 2. 현재 학습 컨텍스트 준비
            current_context = {
                "chapter": state.get("current_chapter"),
                "section": state.get("current_section"),
                "theory_draft": state.get("theory_draft")
            }
            
            # 3. LangChain Agent 기반 QnA 답변 생성 (완전한 Function Calling 실행)
            qna_response = qna_generation_tool(user_question, current_context)
            
            # 4. State 업데이트 - 기존과 동일
            # 4-1. 에이전트 draft 업데이트
            updated_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                qna_response
            )
            
            # 4-2. 현재 에이전트 전환 설정
            updated_state = state_manager.update_agent_transition(
                updated_state,
                self.agent_name
            )
            
            # 4-3. 대화 기록 추가 (처리 완료 로그)
            log_message = f"QnA Agent 답변 생성 완료 - 사용자 입력: '{user_question[:50]}{'...' if len(user_question) > 50 else ''}'"
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=log_message,
                message_type="system"
            )
            
            print(f"[{self.agent_name}] QnA Agent 답변 생성 완료")
            return updated_state
            
        except Exception as e:
            print(f"[{self.agent_name}] 오류 발생: {str(e)}")
            
            # 오류 시 State 업데이트
            error_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                self._create_error_response(str(e))
            )
            error_state = state_manager.update_agent_transition(
                error_state,
                self.agent_name
            )
            error_state = state_manager.add_conversation(
                error_state,
                agent_name=self.agent_name,
                message=f"QnA Agent 답변 생성 중 오류 발생: {str(e)}",
                message_type="system"
            )
            return error_state
        
    # === 🚀 NEW METHOD: 스트리밍용 State 관리 ===
    def process_streaming_state(self, temp_session_data: dict) -> dict:
        """
        스트리밍용 State 관리 전용 메서드
        - 실제 스트리밍은 qna_stream.py가 처리
        - State 업데이트만 담당 (대화 기록, 에이전트 전환, draft 업데이트)
        
        Args:
            temp_session_data: qna_stream.py에서 전달받은 세션 데이터
            
        Returns:
            업데이트된 state 정보
        """
        try:
            print(f"[{self.agent_name}] 스트리밍용 State 관리 시작")
            
            # 1. 원본 State 복원
            original_state = temp_session_data.get("original_state", {})
            user_message = temp_session_data.get("user_message", "")
            
            print(f"[{self.agent_name}] 스트리밍 질문: '{user_message}'")
            
            # 2. State 업데이트 - 에이전트 draft는 스트리밍 완료 후 업데이트 예정
            updated_state = state_manager.update_agent_transition(
                original_state,
                self.agent_name
            )
            
            # 3. 대화 기록 추가 - 스트리밍 시작 로그
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=f"QnA 스트리밍 시작 - 질문: '{user_message[:50]}{'...' if len(user_message) > 50 else ''}'",
                message_type="system"
            )
            
            # # 4. 스트리밍 진행 상황을 위한 임시 draft 설정 (선택적)
            # updated_state = state_manager.update_agent_draft(
            #     updated_state,
            #     self.agent_name,
            #     f"스트리밍 답변 생성 중... (질문: {user_message})"
            # )
            
            print(f"[{self.agent_name}] 스트리밍용 State 관리 완료")
            
            return {
                "success": True,
                "state": updated_state,
                "message": "QnA 스트리밍 State 업데이트 완료"
            }
            
        except Exception as e:
            print(f"[{self.agent_name}] 스트리밍 State 관리 오류: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "QnA 스트리밍 State 관리 실패"
            }
    
    # === 🚀 NEW METHOD: 스트리밍 완료 후 State 최종 업데이트 ===
    def finalize_streaming_state(self, temp_session_data: dict, final_qna_response: str) -> dict:
        """
        스트리밍 완료 후 State 최종 업데이트
        - 완성된 QnA 답변을 draft에 저장
        - 최종 대화 기록 추가
        
        Args:
            temp_session_data: 세션 데이터
            final_qna_response: 완성된 QnA 답변
            
        Returns:
            최종 업데이트된 state 정보
        """
        try:
            print(f"[{self.agent_name}] 스트리밍 완료 후 State 최종 업데이트 시작")
            
            # 1. 원본 State 복원
            original_state = temp_session_data.get("original_state", {})
            user_message = temp_session_data.get("user_message", "")
            
            # 2. 최종 QnA 답변을 draft에 업데이트
            updated_state = state_manager.update_agent_draft(
                original_state,
                self.agent_name,
                final_qna_response
            )
            
            # 3. 에이전트 전환 정보 업데이트
            updated_state = state_manager.update_agent_transition(
                updated_state,
                self.agent_name
            )
            
            # 4. 최종 대화 기록 추가
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=f"QnA 스트리밍 완료 - 답변 길이: {len(final_qna_response)}자",
                message_type="system"
            )
            
            # 5. 대화 로그 저장
            from app.utils.common.chat_logger import chat_logger
            chat_logger.save_session_log(updated_state, session_complete=False)
            
            print(f"[{self.agent_name}] 스트리밍 완료 후 State 최종 업데이트 완료")
            
            return {
                "success": True,
                "state": updated_state,
                "message": "QnA 스트리밍 최종 State 업데이트 완료"
            }
            
        except Exception as e:
            print(f"[{self.agent_name}] 스트리밍 최종 State 업데이트 오류: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "QnA 스트리밍 최종 State 업데이트 실패"
            }
    
    def _extract_latest_user_message(self, state: TutorState) -> str:
        """
        대화 기록에서 가장 최근 사용자 메시지 추출
        - agent_name이 "user"이고 message_type이 "user"인 것 중 가장 최근 것
        
        Args:
            state: 현재 TutorState
            
        Returns:
            최근 사용자 메시지 (없으면 빈 문자열)
        """
        try:
            conversations = state.get("current_session_conversations", [])
            
            if not conversations:
                print(f"[{self.agent_name}] 대화 기록이 없음")
                return ""
            
            print(f"[{self.agent_name}] 총 {len(conversations)}개의 대화 기록에서 최근 사용자 메시지 검색 중...")
            
            # 역순으로 검색하여 가장 최근 사용자 메시지 찾기
            for i, conv in enumerate(reversed(conversations)):
                agent_name = conv.get("agent_name", "")
                message_type = conv.get("message_type", "")
                
                # message_content와 message 필드 모두 확인 (호환성)
                message_content = conv.get("message_content", "") or conv.get("message", "")
                message_content = message_content.strip()
                
                print(f"[{self.agent_name}] 대화 기록 확인 - agent: '{agent_name}', type: '{message_type}', content: '{message_content[:50]}{'...' if len(message_content) > 50 else ''}'")
                
                # 사용자 메시지 조건: agent_name="user" AND message_type="user"
                if agent_name == "user" and message_type == "user" and message_content:
                    print(f"[{self.agent_name}] 최근 사용자 메시지 발견: '{message_content}'")
                    return message_content
            
            print(f"[{self.agent_name}] 사용자 메시지를 찾을 수 없음")
            return ""
            
        except Exception as e:
            print(f"[{self.agent_name}] 사용자 메시지 추출 중 오류: {str(e)}")
            return ""
    
    def _create_error_response(self, error_msg: str) -> str:
        """
        오류 발생 시 기본 대본 생성
        
        Args:
            error_msg: 오류 메시지
            
        Returns:
            오류 대본 텍스트
        """
        return f"""답변을 생성하는 중 문제가 발생했습니다.

오류: {error_msg}

죄송합니다. 잠시 후 다시 질문해주세요."""