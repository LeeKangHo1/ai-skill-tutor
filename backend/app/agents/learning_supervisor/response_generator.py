# backend/app/agents/learning_supervisor/response_generator.py

from typing import Dict, Any
from app.core.langraph.state_manager import TutorState, state_manager


class ResponseGenerator:
    """
    에이전트 대본을 사용자 친화적인 최종 응답으로 정제하는 클래스
    
    주요 역할:
    1. 각 에이전트가 생성한 대본(draft) 추출
    2. 사용자 유형(beginner/advanced)에 맞는 톤 체크
    3. 응답 형식 정제 및 표준화
    4. UI 모드에 맞는 응답 구조화
    """
    
    def __init__(self):
        pass
    
    def generate_final_response(self, state: TutorState) -> TutorState:
        """
        최종 응답 생성 메인 함수
        
        Args:
            state: 에이전트 대본이 포함된 TutorState
            
        Returns:
            정제된 최종 응답이 포함된 TutorState
        """
        try:
            # 현재 활성 에이전트 확인
            current_agent = state.get("current_agent", "")
            
            # 에이전트별 대본 추출 및 정제
            if "theory_educator" in current_agent:
                return self._process_theory_response(state)
            elif "quiz_generator" in current_agent:
                return self._process_quiz_response(state)
            elif "evaluation_feedback" in current_agent:
                return self._process_feedback_response(state)
            elif "qna_resolver" in current_agent:
                return self._process_qna_response(state)
            elif "session_manager" in current_agent:
                return self._process_session_response(state)
            else:
                # 기본 처리: 모든 대본 확인해서 가장 최근 내용 처리
                return self._process_default_response(state)
                
        except Exception as e:
            print(f"ResponseGenerator 처리 중 오류: {e}")
            return self._generate_error_response(state)
    
    def _process_theory_response(self, state: TutorState) -> TutorState:
        """
        이론 설명 응답 정제
        
        Args:
            state: TutorState
            
        Returns:
            정제된 응답이 포함된 TutorState
        """
        theory_draft = state.get("theory_draft", "")
        
        if not theory_draft:
            # 대본이 없으면 기본 응답
            final_response = self._generate_theory_fallback(state)
        else:
            # 이론 설명 대본 정제
            final_response = self._refine_theory_content(theory_draft, state)
        
        # 정제된 응답을 theory_draft에 다시 저장
        updated_state = state_manager.update_agent_draft(state, "theory_educator", final_response)
        
        return updated_state
    
    def _process_quiz_response(self, state: TutorState) -> TutorState:
        """
        퀴즈 문제 응답 정제
        
        Args:
            state: TutorState
            
        Returns:
            정제된 응답이 포함된 TutorState
        """
        quiz_draft = state.get("quiz_draft", "")
        
        if not quiz_draft:
            # 대본이 없으면 기본 응답
            final_response = self._generate_quiz_fallback(state)
        else:
            # 퀴즈 대본 정제
            final_response = self._refine_quiz_content(quiz_draft, state)
        
        # 정제된 응답을 quiz_draft에 다시 저장
        updated_state = state_manager.update_agent_draft(state, "quiz_generator", final_response)
        
        # 퀴즈 모드로 UI 전환
        updated_state = state_manager.update_ui_mode(updated_state, "quiz")
        
        return updated_state
    
    def _process_feedback_response(self, state: TutorState) -> TutorState:
        """
        평가 피드백 응답 정제
        
        Args:
            state: TutorState
            
        Returns:
            정제된 응답이 포함된 TutorState
        """
        feedback_draft = state.get("feedback_draft", "")
        
        if not feedback_draft:
            # 대본이 없으면 기본 응답
            final_response = self._generate_feedback_fallback(state)
        else:
            # 피드백 대본 정제
            final_response = self._refine_feedback_content(feedback_draft, state)
        
        # 정제된 응답을 feedback_draft에 다시 저장
        updated_state = state_manager.update_agent_draft(state, "evaluation_feedback_agent", final_response)
        
        # 채팅 모드로 UI 전환
        updated_state = state_manager.update_ui_mode(updated_state, "chat")
        
        return updated_state
    
    def _process_qna_response(self, state: TutorState) -> TutorState:
        """
        질문 답변 응답 정제
        
        Args:
            state: TutorState
            
        Returns:
            정제된 응답이 포함된 TutorState
        """
        qna_draft = state.get("qna_draft", "")
        
        if not qna_draft:
            # 대본이 없으면 기본 응답
            final_response = self._generate_qna_fallback(state)
        else:
            # QnA 대본 정제
            final_response = self._refine_qna_content(qna_draft, state)
        
        # 정제된 응답을 qna_draft에 다시 저장
        updated_state = state_manager.update_agent_draft(state, "qna_resolver", final_response)
        
        return updated_state
    
    def _process_session_response(self, state: TutorState) -> TutorState:
        """
        세션 완료 응답 정제
        
        Args:
            state: TutorState
            
        Returns:
            처리된 TutorState
        """
        # SessionManager는 이미 완료 메시지를 생성하므로 그대로 사용
        # 필요시 추가 정제 가능
        return state
    
    def _process_default_response(self, state: TutorState) -> TutorState:
        """
        기본 응답 처리 (에이전트가 명확하지 않은 경우)
        
        Args:
            state: TutorState
            
        Returns:
            처리된 TutorState
        """
        # 모든 대본을 확인해서 내용이 있는 것 찾기
        drafts = [
            ("theory_educator", state.get("theory_draft", "")),
            ("quiz_generator", state.get("quiz_draft", "")),
            ("evaluation_feedback_agent", state.get("feedback_draft", "")),
            ("qna_resolver", state.get("qna_draft", ""))
        ]
        
        for agent_name, draft_content in drafts:
            if draft_content and draft_content.strip():
                # 내용이 있는 첫 번째 대본 처리
                if "theory" in agent_name:
                    return self._process_theory_response(state)
                elif "quiz" in agent_name:
                    return self._process_quiz_response(state)
                elif "feedback" in agent_name:
                    return self._process_feedback_response(state)
                elif "qna" in agent_name:
                    return self._process_qna_response(state)
        
        # 모든 대본이 비어있으면 기본 메시지
        return self._generate_error_response(state)
    
    def _refine_theory_content(self, theory_draft: str, state: TutorState) -> str:
        """
        이론 설명 내용 정제
        
        Args:
            theory_draft: 원본 이론 설명 대본
            state: TutorState
            
        Returns:
            정제된 이론 설명
        """
        user_type = state.get("user_type", "beginner")
        current_chapter = state.get("current_chapter", 1)
        current_section = state.get("current_section", 1)
        
        # 기본 정제: 인사말 추가 및 형식 정리
        refined_content = theory_draft.strip()
        
        # 챕터/섹션 정보 추가
        intro = f"📚 {current_chapter}챕터 {current_section}섹션을 시작하겠습니다!\n\n"
        
        # 사용자 유형별 톤 체크
        if user_type == "beginner":
            # 초보자용: 친근하고 격려하는 톤
            if not any(word in refined_content for word in ["안녕", "환영", "함께"]):
                intro += "차근차근 함께 배워보시죠! 😊\n\n"
        else:
            # 고급자용: 효율적이고 전문적인 톤
            intro += "핵심 내용을 정리해서 설명드리겠습니다.\n\n"
        
        # 마무리 안내 추가
        outro = "\n\n💡 궁금한 점이 있으시면 언제든 질문해주세요. 이해하셨다면 '다음 단계'라고 말씀해주시면 퀴즈를 진행하겠습니다."
        
        return intro + refined_content + outro
    
    def _refine_quiz_content(self, quiz_draft: str, state: TutorState) -> str:
        """
        퀴즈 내용 정제
        
        Args:
            quiz_draft: 원본 퀴즈 대본
            state: TutorState
            
        Returns:
            정제된 퀴즈 내용
        """
        user_type = state.get("user_type", "beginner")
        quiz_type = state.get("current_question_type", "multiple_choice")
        
        # 기본 정제
        refined_content = quiz_draft.strip()
        
        # 퀴즈 시작 안내
        if quiz_type == "multiple_choice":
            intro = "📝 이제 퀴즈를 풀어보겠습니다! 정답을 선택해주세요.\n\n"
        else:
            intro = "📝 이제 실습 문제를 풀어보겠습니다! 자유롭게 답변해주세요.\n\n"
        
        # 사용자 유형별 격려 메시지
        if user_type == "beginner":
            intro += "천천히 생각해보세요. 틀려도 괜찮으니 편하게 답변해주시면 됩니다! 💪\n\n"
        
        # 답변 입력 안내 추가
        outro = "\n\n✏️ 답변을 입력해주세요!"
        
        return intro + refined_content + outro
    
    def _refine_feedback_content(self, feedback_draft: str, state: TutorState) -> str:
        """
        피드백 내용 정제
        
        Args:
            feedback_draft: 원본 피드백 대본
            state: TutorState
            
        Returns:
            정제된 피드백 내용
        """
        user_type = state.get("user_type", "beginner")
        is_correct = state.get("is_answer_correct", 0)
        session_decision = state.get("session_decision_result", "proceed")
        
        # 기본 정제
        refined_content = feedback_draft.strip()
        
        # 결과에 따른 이모지 및 격려 메시지 추가
        if isinstance(is_correct, int):
            if is_correct == 1 or is_correct >= 60:  # 정답 또는 60점 이상
                intro = "🎉 "
            else:
                intro = "💪 "
        else:
            intro = "📚 "
        
        # 세션 결정 결과에 따른 안내 추가
        if session_decision == "proceed":
            outro = "\n\n🚀 다음 학습으로 넘어갈 준비가 되었습니다! 추가 질문이 있으시면 언제든 물어보세요. 계속 진행하려면 '다음'이라고 말씀해주세요."
        elif session_decision == "retry":
            outro = "\n\n🔄 이 부분을 다시 한번 학습해보겠습니다. 질문이 있으시면 언제든 말씀해주세요."
        else:
            outro = "\n\n💬 궁금한 점이 있으시면 언제든 질문해주세요!"
        
        return intro + refined_content + outro
    
    def _refine_qna_content(self, qna_draft: str, state: TutorState) -> str:
        """
        QnA 내용 정제
        
        Args:
            qna_draft: 원본 QnA 대본
            state: TutorState
            
        Returns:
            정제된 QnA 내용
        """
        user_type = state.get("user_type", "beginner")
        
        # 기본 정제
        refined_content = qna_draft.strip()
        
        # 답변 시작 표시
        intro = "💬 "
        
        # 추가 도움 안내
        outro = "\n\n📚 더 궁금한 점이 있으시면 언제든 질문해주세요!"
        
        return intro + refined_content + outro
    
    def _generate_theory_fallback(self, state: TutorState) -> str:
        """이론 설명 대본이 없을 때 기본 응답"""
        chapter = state.get("current_chapter", 1)
        return f"죄송합니다. {chapter}챕터 이론 내용을 준비 중입니다. 잠시 후 다시 시도해주세요."
    
    def _generate_quiz_fallback(self, state: TutorState) -> str:
        """퀴즈 대본이 없을 때 기본 응답"""
        return "죄송합니다. 퀴즈 문제를 준비 중입니다. 잠시 후 다시 시도해주세요."
    
    def _generate_feedback_fallback(self, state: TutorState) -> str:
        """피드백 대본이 없을 때 기본 응답"""
        return "답변을 확인했습니다. 피드백을 준비 중이니 잠시만 기다려주세요."
    
    def _generate_qna_fallback(self, state: TutorState) -> str:
        """QnA 대본이 없을 때 기본 응답"""
        return "질문을 확인했습니다. 답변을 준비 중이니 잠시만 기다려주세요."
    
    def _generate_error_response(self, state: TutorState) -> TutorState:
        """
        오류 응답 생성
        
        Args:
            state: TutorState
            
        Returns:
            오류 응답이 포함된 TutorState
        """
        error_message = "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요."
        
        # 임시로 theory_draft에 오류 메시지 저장
        updated_state = state_manager.update_agent_draft(state, "theory_educator", error_message)
        
        return updated_state


# 전역 ResponseGenerator 인스턴스
response_generator = ResponseGenerator()