# backend/app/tools/analysis/feedback_tools_chatgpt.py

import logging
import json
from typing import Dict, Any, Tuple

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class SubjectiveEvaluationSchema(BaseModel):
    """주관식 평가 응답 스키마"""
    evaluation: Dict[str, Any] = Field(description="평가 결과")
    feedback: Dict[str, str] = Field(description="피드백 내용")


def evaluate_subjective_with_feedback(
    quiz_data: Dict[str, Any],
    user_answer: str,
    user_type: str
) -> Tuple[int, str]:
    """
    ChatGPT를 활용한 주관식 답변 평가 및 피드백 생성 (간소화)
    
    Args:
        quiz_data: 퀴즈 JSON 데이터 (sample_answer, evaluation_criteria 포함)
        user_answer: 사용자 답변
        user_type: 사용자 유형 ("beginner" or "advanced")
        
    Returns:
        Tuple[점수(0-100), 피드백텍스트]
    """
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("ChatGPT 주관식 평가 및 피드백 생성 시작 (LCEL 파이프라인)")
        
        # LangChain 구성 요소 초기화
        model = _get_chatgpt_model()
        parser = JsonOutputParser(pydantic_object=SubjectiveEvaluationSchema)
        prompt_template = _create_evaluation_prompt_template(user_type)
        
        # LCEL 파이프라인 구성: prompt | model | parser
        chain = prompt_template | model | parser
        
        # 입력 데이터 준비
        input_data = _prepare_evaluation_input_data(quiz_data, user_answer)
        
        # 파이프라인 실행
        result = chain.invoke(input_data)
        
        # 점수 추출
        score = result.get('evaluation', {}).get('score', 0)
        
        # 피드백 텍스트 추출
        feedback_text = result.get('feedback', {}).get('content', '')
        
        logger.info(f"ChatGPT 주관식 평가 완료 - 점수: {score}")
        return score, feedback_text
        
    except Exception as e:
        logger.error(f"ChatGPT 주관식 평가 실패: {str(e)}")
        return _generate_fallback_evaluation(user_answer, str(e))


def generate_multiple_choice_feedback(
    quiz_data: Dict[str, Any],
    user_answer: str,
    is_correct: bool,
    user_type: str
) -> str:
    """
    ChatGPT를 활용한 객관식 피드백 생성 (간소화)
    
    Args:
        quiz_data: 퀴즈 JSON 데이터
        user_answer: 사용자 답변
        is_correct: 정답 여부
        user_type: 사용자 유형 ("beginner" or "advanced")
        
    Returns:
        생성된 피드백 텍스트
    """
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("ChatGPT 객관식 피드백 생성 시작")
        
        # LangChain 구성 요소 초기화
        model = _get_chatgpt_model()
        prompt_template = _create_multiple_choice_feedback_prompt(user_type)
        
        # 간단한 체인 구성: prompt | model
        chain = prompt_template | model
        
        # 입력 데이터 준비
        input_data = _prepare_mc_feedback_input_data(quiz_data, user_answer, is_correct)
        
        # 체인 실행
        result = chain.invoke(input_data)
        
        logger.info("ChatGPT 객관식 피드백 생성 완료")
        return result.content.strip()
        
    except Exception as e:
        logger.error(f"ChatGPT 객관식 피드백 생성 실패: {str(e)}")
        return _generate_fallback_mc_feedback(is_correct, user_type, quiz_data.get('explanation', ''))


def _get_chatgpt_model() -> ChatOpenAI:
    """ChatGPT 모델 초기화"""
    import os
    
    return ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.3,  # 평가의 일관성을 위해 낮은 온도
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
    )


def _create_evaluation_prompt_template(user_type: str) -> PromptTemplate:
    """
    사용자 유형별 주관식 평가 PromptTemplate 생성
    """
    
    # 사용자 유형별 피드백 스타일 설정
    if user_type == "beginner":
        feedback_style = """
친근하고 격려적인 톤으로 피드백을 작성해주세요:
- 긍정적인 부분을 먼저 언급하여 자신감을 높여주세요
- 개선점은 구체적인 예시와 함께 친절하게 설명해주세요
- 이모지를 적절히 활용하여 친근함을 표현해주세요
- "다음에는 이렇게 해보세요" 같은 격려형 표현 사용
"""
    else:  # advanced
        feedback_style = """
효율적이고 실무적인 톤으로 피드백을 작성해주세요:
- 핵심 개선점을 간결하고 명확하게 제시해주세요
- 실무에서 활용할 수 있는 구체적인 팁을 포함해주세요
- 시간 효율성과 결과 품질 개선에 중점을 두세요
- 전문적이고 직접적인 표현 사용
"""
    
    # JSON 응답 형식 정의
    json_format = """{{
  "evaluation": {{
    "score": 0-100점 사이의 정수,
    "criteria_analysis": {{
      "기준1": "분석 내용 및 부분 점수",
      "기준2": "분석 내용 및 부분 점수",
      "기준3": "분석 내용 및 부분 점수"
    }},
    "scoring_rationale": "점수 산정 근거"
  }},
  "feedback": {{
    "content": "피드백 내용 (격려, 잘한 점, 개선점 모두 포함)",
    "next_step_recommendation": "proceed 또는 retry"
  }}
}}"""
    
    system_message = f"""당신은 AI 활용법을 가르치는 전문 튜터입니다. 
사용자가 작성한 프롬프트를 평가하고 건설적인 피드백을 제공해주세요.

평가 기준:
- 각 기준을 샘플 답안과 비교하여 0-100점으로 평가
- 기준별 세부 분석과 함께 총점 산정
- 60점 이상이면 다음 단계 진행, 미만이면 재학습 권장

{feedback_style}

반드시 다음 JSON 형식으로만 응답해주세요:
{json_format}

다른 텍스트는 포함하지 마세요."""
    
    template = f"""{system_message}

**문제**: {{question}}

**평가 기준**: {{evaluation_criteria}}

**샘플 답안**: {{sample_answer}}

**사용자 답변**: {{user_answer}}

위 내용을 바탕으로 사용자 답변을 평가하고 피드백을 제공해주세요."""
    
    return PromptTemplate(
        input_variables=["question", "evaluation_criteria", "sample_answer", "user_answer"],
        template=template
    )


def _create_multiple_choice_feedback_prompt(user_type: str) -> PromptTemplate:
    """
    객관식 피드백용 PromptTemplate 생성
    """
    
    if user_type == "beginner":
        feedback_style = """친근하고 격려적인 톤으로 피드백을 작성해주세요:
- 긍정적인 부분을 먼저 언급하여 자신감을 높여주세요
- 이모지를 적절히 활용하여 친근함을 표현해주세요
- 틀렸을 때도 격려하며 설명해주세요"""
    else:  # advanced
        feedback_style = """효율적이고 간결한 톤으로 피드백을 작성해주세요:
- 핵심 내용을 명확하게 전달해주세요
- 실무적 관점에서 설명해주세요
- 간결하지만 도움이 되는 정보를 제공해주세요"""
    
    system_message = f"""당신은 AI 활용법을 가르치는 전문 튜터입니다.
객관식 문제에 대한 간단하고 효과적인 피드백을 제공해주세요.

{feedback_style}

피드백은 간결하되 학습에 도움이 되도록 작성해주세요.
다음 단계 안내는 포함하지 말고, 순수한 평가 피드백만 작성해주세요."""
    
    template = f"""{system_message}

**퀴즈 정보**: {{quiz_data}}
**사용자 답변**: {{user_answer}}
**정답 여부**: {{is_correct}}

위 정보를 바탕으로 적절한 피드백을 작성해주세요."""
    
    return PromptTemplate(
        input_variables=["quiz_data", "user_answer", "is_correct"],
        template=template
    )


def _prepare_evaluation_input_data(quiz_data: Dict[str, Any], user_answer: str) -> Dict[str, str]:
    """
    주관식 평가용 입력 데이터 준비
    """
    
    question = quiz_data.get('question', '')
    sample_answer = quiz_data.get('sample_answer', '')
    evaluation_criteria = quiz_data.get('evaluation_criteria', [])
    
    # 평가 기준을 문자열로 변환
    criteria_str = "\n".join([f"- {criteria}" for criteria in evaluation_criteria])
    
    return {
        "question": question,
        "evaluation_criteria": criteria_str,
        "sample_answer": sample_answer,
        "user_answer": user_answer
    }


def _prepare_mc_feedback_input_data(
    quiz_data: Dict[str, Any], 
    user_answer: str,
    is_correct: bool
) -> Dict[str, str]:
    """
    객관식 피드백용 입력 데이터 준비
    """
    
    is_correct_text = "정답" if is_correct else "오답"
    
    return {
        "quiz_data": json.dumps(quiz_data, ensure_ascii=False, indent=2),
        "user_answer": str(user_answer),
        "is_correct": is_correct_text
    }


def _generate_fallback_evaluation(user_answer: str, error_msg: str) -> Tuple[int, str]:
    """주관식 평가 실패 시 기본 결과 생성"""
    
    fallback_feedback = "일시적인 시스템 문제로 상세한 피드백을 제공할 수 없습니다. 잠시 후 다시 시도해주세요. 괜찮습니다! 답변을 작성해주신 것만으로도 훌륭합니다. 계속 학습해보세요! 💪"
    
    return 50, fallback_feedback  # 중간 점수로 설정


def _generate_fallback_mc_feedback(is_correct: bool, user_type: str, explanation: str) -> str:
    """객관식 피드백 생성 실패 시 기본 피드백"""
    
    if is_correct:
        if user_type == "beginner":
            feedback = f"🎉 정답입니다! 훌륭해요!\n\n{explanation}"
        else:
            feedback = f"정답입니다.\n\n{explanation}"
    else:
        if user_type == "beginner":
            feedback = f"아쉽게도 틀렸어요. 😅 하지만 괜찮습니다!\n\n{explanation}"
        else:
            feedback = f"오답입니다.\n\n{explanation}"
    
    return feedback


def generate_simple_feedback(
    quiz_type: str,
    score: int,
    is_correct: bool = None,
    explanation: str = "",
    user_type: str = "beginner"
) -> str:
    """
    간단한 피드백 텍스트 생성 (ChatGPT 없이 로컬 생성)
    
    Args:
        quiz_type: 퀴즈 타입
        score: 점수
        is_correct: 정답 여부 (객관식만)
        explanation: 설명
        user_type: 사용자 유형
        
    Returns:
        피드백 텍스트
    """
    
    if quiz_type == "multiple_choice":
        # 객관식 기본 피드백
        return _generate_fallback_mc_feedback(is_correct, user_type, explanation)
    
    else:  # subjective
        # 주관식 기본 피드백
        if score >= 60:
            feedback = f"점수: {score}점 - 잘 작성해주셨습니다!"
        else:
            feedback = f"점수: {score}점 - 조금 더 구체적으로 작성해보세요."
    
    return feedback