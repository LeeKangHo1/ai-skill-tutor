# backend/app/tools/content/qna_tools_chatgpt.py

import logging
import os
from typing import Dict, Any, List

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.tools.external.vector_search_tools import search_qna_materials


@tool
def vector_search_qna_tool(query: str) -> List[Dict[str, Any]]:
    """
    QnA용 벡터 검색 도구 (LangChain Tool)
    
    Args:
        query: 검색할 질문 텍스트
        
    Returns:
        검색된 벡터 자료 리스트
    """
    logger = logging.getLogger(__name__)
    logger.info(f"벡터 검색 도구 호출 - 질문: {query[:50]}...")
    print(f"[QnA 도구] 벡터 검색 시작 - 질문: {query[:100]}...")
    
    try:
        # 기존 search_qna_materials() 함수 활용
        search_results = search_qna_materials(query)
        
        logger.info(f"벡터 검색 완료 - {len(search_results)}개 결과 반환")
        
        # 벡터 검색 결과 상세 로깅
        if search_results:
            print(f"[QnA 도구] 벡터 검색 성공 - {len(search_results)}개 결과 발견")
            print(f"[QnA 도구] === 벡터 검색 결과 상세 ===")
            for i, result in enumerate(search_results, 1):
                chunk_type = result.get('chunk_type', 'unknown')
                quality_score = result.get('content_quality_score', 0)
                similarity_score = result.get('similarity_score', 0)
                keywords = result.get('primary_keywords', [])
                content_preview = result.get('content', '')[:150]
                
                print(f"[QnA 도구] 결과 {i}:")
                print(f"  - 타입: {chunk_type}")
                print(f"  - 품질점수: {quality_score}")
                print(f"  - 유사도: {similarity_score:.3f}")
                print(f"  - 키워드: {', '.join(keywords) if keywords else '없음'}")
                print(f"  - 내용: {content_preview}...")
                print()
            print(f"[QnA 도구] === 벡터 검색 결과 끝 ===")
        else:
            print(f"[QnA 도구] 벡터 검색 결과 없음")
        
        # 검색 결과를 ChatGPT가 이해하기 쉬운 형태로 가공
        processed_results = []
        for result in search_results:
            processed_result = {
                "content": result["content"],
                "chunk_type": result["chunk_type"],
                "quality_score": result["content_quality_score"],
                "keywords": result["primary_keywords"],
                "source": result["source_url"],
                "chapter": result["chapter"],
                "section": result["section"],
                "similarity": round(result["similarity_score"], 3)
            }
            processed_results.append(processed_result)
        
        return processed_results
        
    except Exception as e:
        logger.error(f"벡터 검색 도구 실패: {str(e)}")
        print(f"[QnA 도구] 벡터 검색 오류: {str(e)}")
        return []


def qna_generation_tool(user_question: str, current_context: Dict[str, Any] = None) -> str:
    """
    LangChain Function Calling을 활용한 QnA 답변 생성
    
    Args:
        user_question: 사용자 질문
        current_context: 현재 학습 컨텍스트 (챕터, 섹션, theory_draft 등)
        
    Returns:
        생성된 답변 텍스트
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("QnA 답변 생성 도구 시작 (Function Calling)")
        print(f"[QnA 도구] Function Calling 방식 답변 생성 시작 - 질문: {user_question[:100]}...")
        
        # ChatGPT 모델 초기화 (Function Calling 지원)
        model = _get_chatgpt_model_with_tools()
        
        # 시스템 메시지 생성
        system_message = _create_system_message(current_context)
        
        # 사용자 질문 메시지 생성
        human_message = HumanMessage(content=user_question)
        
        print(f"[QnA 도구] ChatGPT Function Calling 실행 중...")
        
        # Function Calling 실행
        messages = [system_message, human_message]
        response = model.invoke(messages)
        
        # 응답에서 최종 답변 추출
        final_answer = _extract_final_answer(response)
        
        logger.info("QnA 답변 생성 완료")
        print(f"[QnA 도구] Function Calling 답변 생성 완료 - 길이: {len(final_answer)}자")
        return final_answer
        
    except Exception as e:
        logger.error(f"QnA 답변 생성 실패: {str(e)}")
        print(f"[QnA 도구] Function Calling 오류: {str(e)}")
        return _generate_error_response(user_question, str(e))


def _get_chatgpt_model_with_tools() -> ChatOpenAI:
    """
    Function Calling을 지원하는 ChatGPT 모델 초기화
    """
    
    # 벡터 검색 도구를 바인딩한 모델 생성
    model = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.3,  # QnA는 일관성 있는 답변이 중요
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
    )
    
    # 벡터 검색 도구 바인딩
    model_with_tools = model.bind_tools([vector_search_qna_tool])
    
    return model_with_tools


def _create_system_message(current_context: Dict[str, Any] = None) -> SystemMessage:
    """
    QnA 시스템 메시지 생성
    """
    
    # 기본 시스템 프롬프트
    base_prompt = """당신은 AI 활용법 학습 튜터의 QnA 전문 어시스턴트입니다.

주요 역할:
1. 사용자의 AI 관련 질문에 정확하고 친근하게 답변
2. 필요시 벡터 검색을 통해 관련 학습 자료 참조
3. 학습 맥락에 맞는 실용적인 답변 제공

답변 가이드라인:
- 친근하고 이해하기 쉬운 톤 사용 (이모지 활용)
- 구체적인 예시와 함께 설명
- 실무에 활용할 수 있는 실용적인 정보 제공
- 복잡한 개념은 단계별로 설명
- AI 입문자도 이해할 수 있는 수준으로 설명

벡터 검색 활용:
- 사용자 질문이 특정 AI 개념이나 기술에 관한 것이면 vector_search_qna_tool을 사용하여 관련 자료를 검색하세요
- 검색된 자료가 있으면 해당 내용을 참고하여 더 정확하고 상세한 답변을 제공하세요
- 검색 결과가 없거나 일반적인 질문이면 당신의 지식을 바탕으로 답변하세요
- 간단한 인사말이나 감사 표현에는 벡터 검색을 사용하지 마세요"""
    
    # 현재 학습 컨텍스트 추가
    if current_context:
        context_info = ""
        
        if current_context.get('chapter') and current_context.get('section'):
            context_info += f"\n현재 학습 중인 챕터: {current_context['chapter']}장 {current_context['section']}절"
        
        if current_context.get('theory_draft'):
            theory_preview = current_context['theory_draft'][:200]
            context_info += f"\n최근 학습한 이론 내용: {theory_preview}..."
        
        if context_info:
            base_prompt += f"\n\n현재 학습 컨텍스트:{context_info}"
    
    return SystemMessage(content=base_prompt)


def _extract_final_answer(response) -> str:
    """
    ChatGPT 응답에서 최종 답변 추출
    Function Calling이 있었다면 도구 호출 결과를 포함한 최종 답변 반환
    """
    
    try:
        # 응답이 문자열인 경우 (도구 호출 없음)
        if isinstance(response, str):
            return response
        
        # AIMessage 객체인 경우
        if hasattr(response, 'content'):
            # 도구 호출이 있었는지 확인
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # 도구 호출 결과를 포함한 답변이 content에 있음
                return response.content
            else:
                # 일반 답변
                return response.content
        
        # 기타 경우 문자열 변환
        return str(response)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"응답 추출 실패: {str(e)}")
        return "죄송합니다. 답변을 처리하는 중 문제가 발생했습니다. 다시 질문해 주세요."


def _generate_error_response(user_question: str, error_msg: str) -> str:
    """
    오류 발생 시 기본 응답 생성
    """
    
    return f"""죄송합니다. 질문에 답변하는 중 일시적인 문제가 발생했습니다. 😅

**질문**: {user_question}

**문제 상황**: 시스템에 일시적인 오류가 발생했습니다.

**해결 방법**:
1. 잠시 후 다시 질문해 주세요
2. 질문을 다르게 표현해서 다시 시도해 보세요
3. 더 구체적인 질문으로 바꿔서 물어보세요

다른 질문이 있으시면 언제든 말씀해 주세요! 🤖✨"""


