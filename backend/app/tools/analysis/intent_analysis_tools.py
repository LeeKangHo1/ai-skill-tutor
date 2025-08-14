# backend/app/tools/analysis/intent_analysis_tools.py

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import os
import re


class IntentAnalysisResult(BaseModel):
    """의도 분석 결과 스키마"""
    intent: str = Field(description="분류된 의도: 'next_step' 또는 'question'")
    confidence: float = Field(description="신뢰도 (0.0-1.0)")
    reasoning: str = Field(description="분류 근거 설명")


def user_intent_analysis_tool(user_message: str, current_stage: str, user_type: str) -> Dict[str, Any]:
    """
    사용자 의도 분석 도구 (빠른 경로 최적화)
    
    1차: 완전 일치 키워드 기반 빠른 분류
    2차: 애매한 경우에만 LLM 호출
    
    Args:
        user_message: 사용자 입력 메시지
        current_stage: 현재 세션 진행 단계
        user_type: 사용자 유형 (beginner/advanced)
        
    Returns:
        {
            "intent": "next_step" | "question",
            "confidence": float,
            "reasoning": str
        }
    """
    try:
        # 빈 메시지 처리
        if not user_message or not user_message.strip():
            return {
                "intent": "next_step",
                "confidence": 0.5,
                "reasoning": "빈 메시지로 인한 기본 처리"
            }
        
        # 1차: 빠른 경로 - 완전 일치 키워드 기반 분류
        fast_result = _analyze_with_exact_keywords(user_message)
        if fast_result:
            return fast_result
        
        # 2차: LLM 기반 정밀 분석 (애매한 경우에만)
        result = _analyze_intent_with_llm(user_message, current_stage, user_type)
        
        # 결과 검증 및 기본값 처리
        if not result or "intent" not in result:
            return _get_fallback_result(user_message)
        
        return result
        
    except Exception as e:
        print(f"의도 분석 중 오류: {e}")
        return _get_fallback_result(user_message)


def _analyze_with_exact_keywords(user_message: str) -> Dict[str, Any]:
    """
    완전 일치 키워드 기반 빠른 분석
    
    Args:
        user_message: 사용자 메시지
        
    Returns:
        확실한 경우에만 결과 반환, 애매하면 None
    """
    message = user_message.strip().lower()
    
    # 완전 일치하는 next_step 키워드들
    exact_next_keywords = [
        "다음", "다음 단계", "다음단계", "계속", "진행", "시작",
        "네", "예", "좋아", "좋아요", "알겠어", "알겠어요", "알겠습니다",
        "퀴즈", "문제", "끝", "완료", "ok",
        "next", "continue", "start", "proceed", "go",
        "okay", "yes", "sure", "quiz", "test", "done", "finished"
    ]
    
    # 완전 일치하는 question 키워드들
    exact_question_keywords = [
        "뭐예요", "뭔가요", "왜", "언제", "어디",
        "궁금해요", "모르겠어요", "이해 안 돼요",
        "what", "why", "when", "where"
    ]
    
    # 1. 완전 일치하는 next_step 확인
    if message in exact_next_keywords:
        return {
            "intent": "next_step",
            "confidence": 0.95,
            "reasoning": f"완전 일치하는 진행 키워드: '{message}' (빠른 경로)"
        }
    
    # 2. 완전 일치하는 question 확인
    if message in exact_question_keywords:
        return {
            "intent": "question",
            "confidence": 0.95,
            "reasoning": f"완전 일치하는 질문 키워드: '{message}' (빠른 경로)"
        }
    
    # 3. 매우 간단한 패턴만 확인 (오판 위험이 낮은 것들)
    simple_patterns = [
        (r'^\d+챕터$', "next_step", "챕터 시작 요청"),
        (r'^chapter\s*\d+$', "next_step", "챕터 시작 요청"),
        (r'^.{1,10}\?$', "question", "짧은 질문"),
        (r'^(뭐|무엇)\?*$', "question", "단일 의문사"),
        (r'^(what|how|why)\?*$', "question", "단일 의문사")
    ]
    
    for pattern, intent, reason in simple_patterns:
        if re.search(pattern, message):
            return {
                "intent": intent,
                "confidence": 0.9,
                "reasoning": f"{reason} (빠른 경로)"
            }
    
    # 4. 그 외 모든 경우 - LLM 분석 필요
    return None


def _analyze_intent_with_llm(user_message: str, current_stage: str, user_type: str) -> Dict[str, Any]:
    """
    LLM을 사용한 의도 분석 (애매한 경우에만 호출)
    
    Args:
        user_message: 사용자 메시지
        current_stage: 현재 진행 단계
        user_type: 사용자 유형
        
    Returns:
        분석 결과
    """
    # ChatOpenAI 모델 초기화
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # JSON 출력 파서 설정
    parser = JsonOutputParser(pydantic_object=IntentAnalysisResult)
    
    # 프롬프트 템플릿 정의
    prompt_template = PromptTemplate(
        template="""당신은 AI 학습 튜터 시스템의 사용자 의도 분석 전문가입니다.

사용자의 메시지를 분석하여 다음 2가지 의도 중 하나로 분류해주세요:

1. **next_step**: 학습을 계속 진행하고 싶은 의도
   - 다음 단계, 챕터 시작, 퀴즈 요청, 계속 진행 등
   - "네", "좋아요", "시작해주세요", "다음" 등의 긍정적 응답
   - 새로운 세션/챕터 시작 요청

2. **question**: 궁금한 것을 질문하는 의도  
   - 개념 설명 요청, 차이점 문의, 이해 안 되는 부분 질문
   - "뭐예요?", "어떻게?", "왜?", "차이가 뭔가요?" 등
   - 추가 설명이나 도움 요청

**현재 상황:**
- 진행 단계: {current_stage}
- 사용자 유형: {user_type}
- 사용자 메시지: "{user_message}"

**워크플로우 규칙:**
- **theory_completed**: 질문 OR 퀴즈 진행 (둘 다 가능)
- **quiz_and_feedback_completed**: 질문 OR 새 세션 시작 (둘 다 가능)

**단계별 분류 기준:**
- **theory_completed**: 이론 학습 직후이므로 질문이 많이 나올 수 있음
- **quiz_and_feedback_completed**: 추가 질문 또는 새 학습 시작
- **beginner**: 질문 성향이 높음, 불확실한 경우 question 가중치
- **advanced**: 빠른 진행 선호, 불확실한 경우 next_step 가중치

참고: 이 메시지는 키워드 기반 분류에서 애매하다고 판단된 복잡한 메시지입니다.

{format_instructions}""",
        input_variables=["user_message", "current_stage", "user_type"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # LCEL 파이프라인 구성
    chain = prompt_template | llm | parser
    
    # LLM 호출 및 결과 반환
    result = chain.invoke({
        "user_message": user_message,
        "current_stage": current_stage,
        "user_type": user_type
    })
    
    # LLM 분석 표시를 위해 reasoning에 추가
    if "reasoning" in result:
        result["reasoning"] += " (LLM 정밀 분석)"
    
    return result


def _get_fallback_result(user_message: str) -> Dict[str, Any]:
    """
    분석 실패 시 폴백 결과 반환
    
    Args:
        user_message: 사용자 메시지
        
    Returns:
        기본 분석 결과
    """
    message_lower = user_message.lower()
    
    # 간단한 질문 키워드 확인
    question_indicators = ["?", "뭐", "무엇", "어떻게", "왜", "언제", "어디", "차이", "설명"]
    
    if any(indicator in message_lower for indicator in question_indicators):
        return {
            "intent": "question",
            "confidence": 0.6,
            "reasoning": "분석 실패, 질문 키워드 기반 폴백 분류"
        }
    else:
        return {
            "intent": "next_step", 
            "confidence": 0.7,
            "reasoning": "분석 실패, 진행 요청으로 기본 분류"
        }