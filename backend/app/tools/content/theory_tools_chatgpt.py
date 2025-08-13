# backend/app/tools/content/theory_tools_chatgpt.py

import logging
from typing import Dict, Any, List

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


def theory_generation_tool(
    section_data: Dict[str, Any],
    user_type: str,
    vector_materials: List[Dict[str, Any]] = None,
    is_retry_session: bool = False
) -> str:
    """
    ChatGPT를 활용한 사용자 맞춤형 이론 설명 대본 생성 (LangChain LCEL 사용)
    
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
        logger.info("ChatGPT 이론 생성 도구 시작 (LCEL 파이프라인)")
        
        # LangChain 구성 요소 초기화
        model = _get_chatgpt_model()
        parser = StrOutputParser()
        prompt_template = _create_prompt_template(user_type, is_retry_session)
        
        # LCEL 파이프라인 구성: prompt | model | parser
        chain = prompt_template | model | parser
        
        # 입력 데이터 준비
        input_data = _prepare_input_data(section_data)
        
        # 파이프라인 실행
        result = chain.invoke(input_data)
        
        logger.info("ChatGPT 이론 생성 파이프라인 완료")
        return result
        
    except Exception as e:
        logger.error(f"ChatGPT 이론 설명 생성 실패: {str(e)}")
        return _generate_fallback_response(section_data, str(e))


def _get_chatgpt_model() -> ChatOpenAI:
    """ChatGPT 모델 초기화"""
    import os
    
    return ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.7,
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
    )


def _create_prompt_template(user_type: str, is_retry_session: bool) -> PromptTemplate:
    """
    사용자 유형에 따른 PromptTemplate 생성
    """
    
    # 재학습 지시사항
    retry_note = "이전에 어려워했으므로 더 쉽게 설명해주세요." if is_retry_session else ""
    
    if user_type == "beginner":
        system_message = f"""당신은 AI 입문자를 위한 친근한 튜터입니다. {retry_note}

다음 지침에 따라 설명하세요:
- 친근하고 쉬운 언어 사용 (이모지 활용)
- 일상생활 비유로 설명
- 기술 용어는 쉬운 말로 풀어서 설명
- "~해보겠습니다", "~할게요" 친근한 톤
- 단계별로 차근차근 설명
- 예시를 많이 들어서 이해하기 쉽게 만들기"""
    else:  # advanced
        system_message = f"""당신은 실무 응용형 사용자를 위한 효율적인 튜터입니다. {retry_note}

다음 지침에 따라 설명하세요:
- 효율적이고 핵심적인 설명
- 실무 활용 관점 중심
- 논리적이고 체계적인 구조
- 기술적 원리와 메커니즘 설명
- 실제 업무에서 어떻게 활용할 수 있는지 포함"""
    
    # PromptTemplate 생성
    template = f"""{system_message}

주제: "{{section_title}}"에 대해 설명해주세요.

참고 내용: {{section_content}}

위 내용을 바탕으로 새롭게 설명을 작성해주세요. 
참고 내용을 그대로 복사하지 말고, 위의 지침에 따라 새로운 방식으로 설명해주세요."""
    
    return PromptTemplate(
        input_variables=["section_title", "section_content"],
        template=template
    )


def _prepare_input_data(section_data: Dict[str, Any]) -> Dict[str, str]:
    """
    PromptTemplate에 전달할 입력 데이터 준비
    """
    
    section_title = section_data.get('title', '')
    section_content = section_data.get('theory', {}).get('content', '')
    
    return {
        "section_title": section_title,
        "section_content": section_content
    }


def _generate_fallback_response(section_data: Dict[str, Any], error_msg: str) -> str:
    """오류 발생 시 기본 응답 생성"""
    
    section_title = section_data.get('title', '이론 학습')
    return f"""죄송합니다. "{section_title}" 설명을 생성하는 중 문제가 발생했습니다.

궁금한 점이 있으시면 언제든 질문해주세요!

오류: {error_msg}"""