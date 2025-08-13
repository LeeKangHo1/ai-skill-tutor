# backend/app/tools/content/theory_tools_chatgpt.py

import logging
from typing import Dict, Any, List

from app.core.external.chatgpt_client import ChatGPTClient


def theory_generation_tool(
    section_data: Dict[str, Any],
    user_type: str,
    vector_materials: List[Dict[str, Any]] = None,
    is_retry_session: bool = False
) -> str:
    """
    ChatGPT를 활용한 사용자 맞춤형 이론 설명 대본 생성
    
    Args:
        section_data: 특정 섹션 데이터
        user_type: 사용자 유형 ("beginner" or "advanced")
        vector_materials: 벡터 DB에서 검색한 관련 자료 (사용 안함)
        is_retry_session: 재학습 여부
        
    Returns:
        생성된 이론 설명 대본 (일반 텍스트)
    """
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("ChatGPT 이론 생성 도구 시작")
        
        # ChatGPT 클라이언트 초기화
        chatgpt_client = ChatGPTClient()
        
        # 프롬프트 생성
        system_instruction, user_prompt = _create_prompts(
            section_data, user_type, is_retry_session
        )
        
        # AI 컨텐츠 생성
        generated_response = chatgpt_client.generate_content(
            prompt=user_prompt,
            system_instruction=system_instruction
        )
        
        logger.info("ChatGPT 이론 생성 도구 완료")
        return generated_response
    
    except Exception as e:
        logger.error(f"ChatGPT 이론 설명 생성 실패: {str(e)}")
        return _generate_fallback_response(section_data, str(e))


def _create_prompts(
    section_data: Dict[str, Any],
    user_type: str,
    is_retry_session: bool
) -> tuple:
    """
    시스템 instruction과 사용자 프롬프트 생성
    
    Args:
        section_data: 섹션 데이터
        user_type: 사용자 유형
        is_retry_session: 재학습 여부
        
    Returns:
        (system_instruction, user_prompt) 튜플
    """
    
    # 섹션 정보 추출
    section_title = section_data.get('title', '')
    section_content = section_data.get('theory', {}).get('content', '')
    
    # 재학습 지시사항
    retry_note = "이전에 어려워했으므로 더 쉽게 설명해주세요." if is_retry_session else ""
    
    # 사용자 유형별 시스템 instruction
    if user_type == "beginner":
        system_instruction = f"""당신은 AI 입문자를 위한 친근한 튜터입니다. {retry_note}

다음 지침에 따라 설명하세요:
- 친근하고 쉬운 언어 사용 (이모지 활용)
- 일상생활 비유로 설명
- 기술 용어는 쉬운 말로 풀어서 설명
- "~해보겠습니다", "~할게요" 친근한 톤"""
    else:  # advanced
        system_instruction = f"""당신은 실무 응용형 사용자를 위한 효율적인 튜터입니다. {retry_note}

다음 지침에 따라 설명하세요:
- 효율적이고 핵심적인 설명
- 실무 활용 관점 중심
- 논리적이고 체계적인 구조"""
    
    # 사용자 프롬프트
    user_prompt = f""""{section_title}"에 대해 설명해주세요.

참고 내용: {section_content}

위 내용을 바탕으로 새롭게 설명을 작성해주세요."""
    
    return system_instruction, user_prompt


def _generate_fallback_response(section_data: Dict[str, Any], error_msg: str) -> str:
    """오류 발생 시 기본 응답 생성"""
    
    section_title = section_data.get('title', '이론 학습')
    return f"""죄송합니다. "{section_title}" 설명을 생성하는 중 문제가 발생했습니다.

궁금한 점이 있으시면 언제든 질문해주세요!

오류: {error_msg}"""