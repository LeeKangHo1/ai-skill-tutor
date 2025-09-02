# backend/app/tools/content/quiz_tools_chatgpt.py

import logging
import json
from typing import Dict, Any

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class QuizSchema(BaseModel):
    """간소화된 퀴즈 응답 스키마"""
    quiz: Dict[str, Any] = Field(description="퀴즈 정보")


def quiz_generation_tool(
    section_data: Dict[str, Any],
    user_type: str,
    is_retry_session: bool = False,
    theory_content: str = "",
    content_source: str = "fallback"
) -> str:
    """
    ChatGPT를 활용한 사용자 맞춤형 퀴즈 생성 (LangChain LCEL 사용)
    
    Args:
        section_data: 특정 섹션 데이터 또는 메타데이터
        user_type: 사용자 유형 ("beginner" or "advanced")
        is_retry_session: 재학습 여부
        theory_content: 이론 설명 내용 (theory_draft)
        content_source: 데이터 소스 ("theory_draft" or "fallback")
        
    Returns:
        생성된 퀴즈 JSON 문자열
    """
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("ChatGPT 퀴즈 생성 도구 시작 (LCEL 파이프라인)")
        
        # 데이터 소스에 따른 퀴즈 타입 결정
        if content_source == "theory_draft":
            # theory_draft 기반: 섹션 데이터에서 퀴즈 타입 추출 (개선된 _load_section_data 활용)
            quiz_type = section_data.get('quiz_type', 'multiple_choice')
            logger.info(f"theory_draft 모드 - 섹션 데이터에서 퀴즈 타입 추출: {quiz_type}")
        else:
            # 폴백 모드: 기존 섹션 데이터에서 퀴즈 타입 추출
            quiz_type = section_data.get('quiz_type') or section_data.get('quiz', {}).get('type', 'multiple_choice')
            logger.info(f"폴백 모드 - 퀴즈 타입: {quiz_type}")
        
        # LangChain 구성 요소 초기화
        model = _get_chatgpt_model()
        parser = JsonOutputParser(pydantic_object=QuizSchema)
        prompt_template = _create_prompt_template(quiz_type, user_type, is_retry_session, content_source)
        
        # LCEL 파이프라인 구성: prompt | model | parser
        chain = prompt_template | model | parser
        
        # 입력 데이터 준비
        input_data = _prepare_input_data(section_data, quiz_type, theory_content, content_source)
        
        # 파이프라인 실행
        result = chain.invoke(input_data)
        
        logger.info("ChatGPT 퀴즈 생성 파이프라인 완료")
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"ChatGPT 퀴즈 생성 실패: {str(e)}")
        return _generate_fallback_response(section_data, quiz_type, str(e))


def _get_chatgpt_model() -> ChatOpenAI:
    """ChatGPT 모델 초기화"""
    import os
    
    return ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.4,
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
    )


def _create_prompt_template(quiz_type: str, user_type: str, is_retry_session: bool, content_source: str = "fallback") -> PromptTemplate:
    """
    퀴즈 타입과 사용자 유형에 따른 PromptTemplate 생성
    """
    
    # 재학습 지시사항
    retry_note = "이전에 어려워했으므로 더 쉬운 문제로 만들어주세요." if is_retry_session else ""
    
    # 공통 JSON 형식 지시
    format_instructions = """
반드시 유효한 JSON 형식으로만 응답해주세요. 다른 텍스트는 포함하지 마세요.
"""
    
    # theory_draft 기반 모드 처리
    if content_source == "theory_draft":
        if quiz_type == "auto":
            return _create_theory_draft_prompt_template(user_type, is_retry_session, retry_note, format_instructions)
        # quiz_type이 지정된 경우 아래 일반 로직으로 진행
    
    if quiz_type == "multiple_choice":
        # 객관식 템플릿
        json_format = """{{
  "quiz": {{
    "type": "multiple_choice",
    "question": "문제 내용",
    "options": [
        "1번 선택지 내용만", 
        "2번 선택지 내용만", 
        "3번 선택지 내용만", 
        "4번 선택지 내용만"
    ], // 중요: '1.'이나 'a.' 같은 접두사 없이 순수 텍스트만 포함해주세요.
    "correct_answer": 정답번호(1-4),
    "explanation": "정답 해설",
    "hint": "도움이 되는 힌트"
  }}
}}"""
        
        if user_type == "beginner":
            system_message = f"""당신은 AI 입문자를 위한 친근한 객관식 퀴즈 출제자입니다. {retry_note}

다음 지침에 따라 퀴즈를 만드세요:
- 친근하고 이해하기 쉬운 4지선다 문제
- 일상생활과 연관된 예시 활용
- 친근한 톤 사용 (이모지 활용)
- 그럴듯한 오답 3개와 명확한 정답 1개 구성

{json_format}

{format_instructions}"""
        else:  # advanced
            system_message = f"""당신은 실무 응용형 사용자를 위한 효율적인 객관식 퀴즈 출제자입니다. {retry_note}

다음 지침에 따라 퀴즈를 만드세요:
- 실무 적용 관점의 4지선다 문제
- 논리적이고 체계적인 문제 구성
- 핵심을 파악하는 능력 테스트
- 효율적이고 명확한 설명

{json_format}

{format_instructions}"""
    
    else:  # subjective
        # 주관식 템플릿
        json_format = """{{
  "quiz": {{
    "type": "subjective",
    "question": "프롬프트 작성 문제 내용",
    "sample_answer": "모범 답안 예시",
    "evaluation_criteria": ["평가기준1", "평가기준2", "평가기준3"],
    "hint": "도움이 되는 힌트"
  }}
}}"""
        
        if user_type == "beginner":
            system_message = f"""당신은 AI 입문자를 위한 친근한 프롬프트 작성 퀴즈 출제자입니다. {retry_note}

다음 지침에 따라 퀴즈를 만드세요:
- 간단하고 실용적인 프롬프트 작성 문제
- 일상생활에서 사용할 수 있는 예시 중심
- 친근하고 격려적인 톤 사용
- 구체적인 작성 방법 힌트 제공

{json_format}

{format_instructions}"""
        else:  # advanced
            system_message = f"""당신은 실무 응용형 사용자를 위한 고급 프롬프트 작성 퀴즈 출제자입니다. {retry_note}

다음 지침에 따라 퀴즈를 만드세요:
- 업무에 활용 가능한 복합적인 프롬프트 작성 문제
- 실무 시나리오 기반 문제 구성
- 효율성과 정확성에 중점
- 프롬프트 엔지니어링 기법 활용

{json_format}

{format_instructions}"""
    
    # PromptTemplate 생성
    template = f"""{system_message}

주제: "{{section_title}}"에 대한 {{quiz_type}} 퀴즈를 만들어주세요.

참고 문제: {{reference_question}}

위 내용을 바탕으로 새로운 문제를 만들어주세요.

{{theory_context}}"""
    
    return PromptTemplate(
        input_variables=["section_title", "quiz_type", "reference_question", "theory_context"],
        template=template
    )


def _create_theory_draft_prompt_template(user_type: str, is_retry_session: bool, retry_note: str, format_instructions: str) -> PromptTemplate:
    """
    theory_draft 기반 퀴즈 생성을 위한 전용 프롬프트 템플릿
    """
    
    # 자동 타입 결정을 위한 JSON 형식 (객관식/주관식 모두 가능)
    json_format_auto = """다음 중 하나의 형식으로 응답하세요:

객관식인 경우:
{{
  "quiz": {{
    "type": "multiple_choice",
    "question": "문제 내용",
    "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
    "correct_answer": 정답번호(1-4),
    "explanation": "정답 해설",
    "hint": "도움이 되는 힌트"
  }}
}}

주관식인 경우:
{{
  "quiz": {{
    "type": "subjective",
    "question": "프롬프트 작성 문제 내용",
    "sample_answer": "모범 답안 예시",
    "evaluation_criteria": ["평가기준1", "평가기준2", "평가기준3"],
    "hint": "도움이 되는 힌트"
  }}
}}"""
    
    if user_type == "beginner":
        system_message = f"""당신은 AI 입문자를 위한 친근한 퀴즈 출제자입니다. {retry_note}

다음 지침에 따라 퀴즈를 만드세요:
- 제공된 이론 설명 내용을 바탕으로 퀴즈 생성
- 이론 내용의 핵심 개념을 이해했는지 확인하는 문제
- 친근하고 이해하기 쉬운 문제 (이모지 활용)
- 일상생활과 연관된 예시 활용
- 이론 내용에 따라 객관식 또는 주관식(프롬프트 작성) 중 적절한 타입 선택

{json_format_auto}

{format_instructions}"""
    else:  # advanced
        system_message = f"""당신은 실무 응용형 사용자를 위한 효율적인 퀴즈 출제자입니다. {retry_note}

다음 지침에 따라 퀴즈를 만드세요:
- 제공된 이론 설명 내용을 바탕으로 퀴즈 생성
- 실무 적용 관점에서 이론을 활용할 수 있는지 확인하는 문제
- 논리적이고 체계적인 문제 구성
- 핵심을 파악하는 능력 테스트
- 이론 내용에 따라 객관식 또는 주관식(프롬프트 작성) 중 적절한 타입 선택

{json_format_auto}

{format_instructions}"""
    
    # theory_draft 전용 템플릿
    template = f"""{system_message}

주제: "{{section_title}}"에 대한 퀴즈를 만들어주세요.

학습한 이론 내용:
{{theory_content}}

위 이론 설명을 바탕으로 학습자가 핵심 개념을 제대로 이해했는지 확인할 수 있는 퀴즈를 만들어주세요.
이론 내용의 특성에 따라 객관식 또는 주관식(프롬프트 작성) 중 적절한 타입을 선택하세요."""
    
    return PromptTemplate(
        input_variables=["section_title", "theory_content"],
        template=template
    )


def _prepare_input_data(section_data: Dict[str, Any], quiz_type: str, theory_content, content_source: str = "fallback") -> Dict[str, str]:
    """
    PromptTemplate에 전달할 입력 데이터 준비
    """
    
    if content_source == "theory_draft":
        # theory_draft 기반 모드 - 개선된 섹션 데이터 활용
        section_title = section_data.get('section_title', '') or section_data.get('title', '')
        
        # theory_content가 딕셔너리인 경우 문자열로 변환
        theory_text = _convert_theory_dict_to_text(theory_content) if isinstance(theory_content, dict) else str(theory_content)
        
        if quiz_type == "auto":
            # 자동 결정 모드 (기존 로직 유지)
            return {
                "section_title": section_title,
                "theory_content": theory_text
            }
        else:
            # 특정 퀴즈 타입 지정 모드
            quiz_data = section_data.get('quiz', {})
            reference_question = quiz_data.get('question', '')
            
            # 이론 내용 컨텍스트 생성
            theory_context = f"\n학습한 이론 내용:\n{theory_text[:300]}..." if theory_text else ""
            
            return {
                "section_title": section_title,
                "quiz_type": quiz_type,
                "reference_question": reference_question,
                "theory_context": theory_context
            }
    else:
        # 폴백 모드 - 개선된 섹션 데이터 활용
        section_title = section_data.get('section_title', '') or section_data.get('title', '')
        quiz_data = section_data.get('quiz', {})
        reference_question = quiz_data.get('question', '')
        
        # 이론 내용 컨텍스트 생성
        theory_context = ""
        if theory_content:
            theory_context = f"\n학습한 이론 내용:\n{theory_content[:300]}..."
        
        return {
            "section_title": section_title,
            "quiz_type": quiz_type,
            "reference_question": reference_question,
            "theory_context": theory_context
        }


def _generate_fallback_response(section_data: Dict[str, Any], quiz_type: str, error_msg: str) -> str:
    """오류 발생 시 기본 JSON 응답 생성"""
    
    section_title = section_data.get('title', '퀴즈')
    
    if quiz_type == "multiple_choice":
        fallback = {
            "quiz": {
                "type": "multiple_choice",
                "question": f"일시적인 문제로 '{section_title}' 퀴즈를 생성할 수 없습니다. 어떻게 하시겠습니까?",
                "options": [
                    "다시 시도하기",
                    "이론 설명 다시 보기", 
                    "질문하기",
                    "다음 단계로 넘어가기"
                ],
                "correct_answer": 1,
                "explanation": "시스템 문제가 발생했습니다. 다시 시도해 주세요.",
                "hint": "시스템에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
            }
        }
    else:  # subjective
        fallback = {
            "quiz": {
                "type": "subjective",
                "question": f"일시적인 문제로 '{section_title}' 프롬프트 작성 문제를 생성할 수 없습니다. 간단한 프롬프트를 작성해보세요.",
                "sample_answer": "죄송합니다. 샘플 답안을 생성할 수 없습니다.",
                "evaluation_criteria": ["시도 의지", "기본 이해도", "창의성"],
                "hint": "시스템에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
            }
        }
    
    return json.dumps(fallback, ensure_ascii=False, indent=2)


def _convert_theory_dict_to_text(theory_dict: Dict[str, Any]) -> str:
    """
    딕셔너리 형태의 이론 데이터를 텍스트로 변환
    
    Args:
        theory_dict: 구조화된 이론 데이터 딕셔너리
        
    Returns:
        프롬프트에 포함할 수 있는 텍스트 형태의 이론 내용
    """
    if not isinstance(theory_dict, dict):
        return str(theory_dict)
    
    text_parts = []
    
    # 챕터 정보와 제목
    chapter_info = theory_dict.get('chapter_info', '')
    title = theory_dict.get('title', '')
    
    if chapter_info:
        text_parts.append(f"챕터 정보: {chapter_info}")
    if title:
        text_parts.append(f"제목: {title}")
    
    # 섹션들 처리
    sections = theory_dict.get('sections', [])
    
    for i, section in enumerate(sections, 1):
        section_type = section.get('type', '')
        section_title = section.get('title', '')
        section_content = section.get('content', '')
        
        # 섹션 헤더
        if section_type == 'introduction':
            text_parts.append(f"\n[도입부]")
        elif section_type == 'definition':
            text_parts.append(f"\n[정의 및 핵심 개념]")
            if section_title:
                text_parts.append(f"소제목: {section_title}")
        elif section_type == 'examples':
            text_parts.append(f"\n[실생활 예시]")
            if section_title:
                text_parts.append(f"소제목: {section_title}")
        else:
            text_parts.append(f"\n[{section_type}]")
            if section_title:
                text_parts.append(f"소제목: {section_title}")
        
        # 섹션 내용
        if section_content:
            text_parts.append(f"내용: {section_content}")
        
        # 비유 설명 (analogy) 처리
        if 'analogy' in section:
            analogy = section['analogy']
            concept = analogy.get('concept', '')
            comparison = analogy.get('comparison', '')
            details = analogy.get('details', [])
            
            text_parts.append(f"비유 설명:")
            if concept and comparison:
                text_parts.append(f"  - {concept} → {comparison}")
            
            for detail in details:
                text_parts.append(f"  - {detail}")
        
        # 예시 항목들 (items) 처리
        if 'items' in section:
            items = section['items']
            text_parts.append(f"구체적 예시들:")
            
            for j, item in enumerate(items, 1):
                category = item.get('category', '')
                description = item.get('description', '')
                benefit = item.get('benefit', '')
                
                if category:
                    text_parts.append(f"  {j}. {category}")
                if description:
                    text_parts.append(f"     설명: {description}")
                if benefit:
                    text_parts.append(f"     효과: {benefit}")
    
    # 모든 텍스트 조합
    full_text = '\n'.join(text_parts)
    
    return full_text