# backend/app/tools/content/qna_tools_chatgpt_stream.py

import logging
import os
import json
from typing import Dict, Any, List, AsyncGenerator

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from app.tools.external.vector_search_tools import search_qna_materials


def qna_streaming_generation_tool(user_question: str, current_context: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
    """
    LangChain Agent 기반 QnA 답변 실시간 스트리밍 생성
    - astream 메서드 활용한 단어 단위 스트리밍
    - 기존 qna_tools_chatgpt.py 구조 참고하여 스트리밍 버전 구현
    
    Args:
        user_question: 사용자 질문
        current_context: 현재 학습 컨텍스트
        
    Returns:
        AsyncGenerator[str, None]: 단어 단위 스트리밍 청크
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("QnA 스트리밍 답변 생성 시작")
        print(f"[QnA 스트리밍] LangChain Agent 스트리밍 시작")
        
        # 1. QnA 컨텍스트 메타데이터 로드
        context_metadata = _load_qna_context_metadata()
        
        # 2. ChatGPT 모델 초기화 (스트리밍 활성화)
        model = _get_streaming_chatgpt_model()
        
        # 3. 프롬프트 템플릿 생성
        prompt_template = _create_streaming_agent_prompt_template(context_metadata, current_context)
        
        # 4. 벡터 검색 도구 리스트
        tools = [vector_search_qna_streaming_tool]
        
        # 5. LangChain Agent 생성
        agent = create_tool_calling_agent(model, tools, prompt_template)
        
        # 6. AgentExecutor 생성 (스트리밍 설정)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="force"
        )
        
        print(f"[QnA 스트리밍] Agent 스트리밍 실행 중... 질문: '{user_question}'")
        
        # 7. Agent astream 실행 - 비동기 스트리밍
        return _stream_agent_response(agent_executor, user_question)
        
    except Exception as e:
        logger.error(f"QnA 스트리밍 답변 생성 실패: {str(e)}")
        print(f"[QnA 스트리밍] Agent 실행 오류: {str(e)}")
        return _generate_error_stream(user_question, str(e))


async def _stream_agent_response(agent_executor: AgentExecutor, user_question: str) -> AsyncGenerator[str, None]:
    """
    Agent astream을 통한 실시간 응답 스트리밍
    
    Args:
        agent_executor: 설정된 AgentExecutor
        user_question: 사용자 질문
        
    Yields:
        str: 단어 단위 스트리밍 청크
    """
    try:
        print(f"[QnA 스트리밍] _stream_agent_response 시작")
        
        # Agent astream 실행
        async for chunk in agent_executor.astream({"input": user_question}):
            print(f"[QnA 스트리밍] 청크 수신: {chunk}")
            
            # Agent 실행 과정에서 다양한 형태의 청크가 올 수 있음
            if isinstance(chunk, dict):
                # 최종 답변이 포함된 청크 찾기
                if 'output' in chunk:
                    final_answer = chunk['output']
                    # 전체 답변을 단어 단위로 분할해서 스트리밍
                    async for word_chunk in _split_into_words(final_answer):
                        yield word_chunk
                        
                # 중간 단계 처리 (Agent 사고 과정)
                elif 'agent' in chunk:
                    agent_step = chunk.get('agent', {})
                    if 'log' in agent_step:
                        # Agent 사고 과정은 스킵 (최종 답변만 스트리밍)
                        continue
                        
                # Actions 처리 (도구 호출)
                elif 'actions' in chunk:
                    # 벡터 검색 등의 도구 호출 과정은 스킵
                    continue
                    
        print(f"[QnA 스트리밍] _stream_agent_response 완료")
        
    except Exception as e:
        print(f"[QnA 스트리밍] _stream_agent_response 오류: {str(e)}")
        # 오류 시 에러 메시지 스트리밍
        error_message = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
        async for word_chunk in _split_into_words(error_message):
            yield word_chunk


async def _split_into_words(text: str) -> AsyncGenerator[str, None]:
    """
    텍스트를 단어 단위로 분할하여 스트리밍
    - 개행 문자 보존
    - ## 과 ** 마크다운 문자 제거
    
    Args:
        text: 분할할 텍스트
        
    Yields:
        str: 단어 단위 청크
    """
    import asyncio
    
    if not text:
        return
    
    # 마크다운 제거 (## 과 ** 제거)
    clean_text = text.replace('##', '').replace('**', '')
    
    # 단어 단위로 분할 (공백 기준, 개행 보존)
    words = clean_text.split(' ')
    
    for i, word in enumerate(words):
        # 단어 간 공백 추가 (마지막 단어 제외)
        chunk = word
        if i < len(words) - 1:
            chunk += ' '
        
        yield chunk
        
        # 스트리밍 속도 조절 (너무 빠르지 않게)
        await asyncio.sleep(0.05)  # 50ms 딜레이


@tool
def vector_search_qna_streaming_tool(search_query: str) -> List[Dict[str, Any]]:
    """
    QnA 스트리밍용 벡터 검색 도구 (LangChain Tool for Agent)
    - 기존 vector_search_qna_tool과 동일한 기능
    
    Args:
        search_query: 검색할 쿼리 텍스트
        
    Returns:
        검색된 벡터 자료 리스트
    """
    logger = logging.getLogger(__name__)
    logger.info(f"[스트리밍] 벡터 검색 도구 호출 - 쿼리: {search_query[:50]}...")
    print(f"[벡터 검색] 스트리밍 Agent가 벡터 검색 시작 - 쿼리: '{search_query}'")
    
    try:
        # 기존 search_qna_materials() 함수 활용
        search_results = search_qna_materials(search_query)
        
        logger.info(f"[스트리밍] 벡터 검색 완료 - {len(search_results)}개 결과 반환")
        print(f"[벡터 검색] 스트리밍 성공 - {len(search_results)}개 결과 발견")
        
        # Agent가 이해하기 쉬운 형태로 반환
        agent_friendly_results = []
        for result in search_results:
            agent_result = {
                "content": result["content"],
                "type": result["chunk_type"],
                "keywords": result["primary_keywords"],
                "quality": result["content_quality_score"],
                "similarity": round(result["similarity_score"], 3),
                "source": f"챕터 {result['chapter']}-{result['section']}"
            }
            agent_friendly_results.append(agent_result)
        
        print(f"[벡터 검색] 스트리밍 Agent용 결과 변환 완료 - {len(agent_friendly_results)}개")
        return agent_friendly_results
        
    except Exception as e:
        logger.error(f"[스트리밍] 벡터 검색 도구 실패: {str(e)}")
        print(f"[벡터 검색] 스트리밍 오류: {str(e)}")
        return []


def _load_qna_context_metadata() -> Dict[str, Any]:
    """
    QnA용 컨텍스트 메타데이터 로드 (기존과 동일)
    """
    try:
        current_dir = os.path.dirname(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        metadata_path = os.path.join(backend_dir, "data", "qna_context_metadata.json")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"[QnA 스트리밍] 컨텍스트 메타데이터 로드 완료")
        return metadata
        
    except Exception as e:
        logging.getLogger(__name__).error(f"QnA 스트리밍 메타데이터 로드 실패: {str(e)}")
        return {"learning_context": {"curriculum_overview": "AI 활용법 학습 과정"}, "chapters": []}


def _create_streaming_agent_prompt_template(context_metadata: Dict[str, Any], current_context: Dict[str, Any] = None) -> ChatPromptTemplate:
    """
    스트리밍 Agent용 프롬프트 템플릿 생성 (기존과 유사)
    """
    learning_context_str = json.dumps(context_metadata, ensure_ascii=False, indent=2)
    learning_context_str = learning_context_str.replace("{", "{{").replace("}", "}}")
    
    current_chapter = current_context.get("chapter", "알 수 없음") if current_context else "알 수 없음"
    current_section = current_context.get("section", "알 수 없음") if current_context else "알 수 없음"
    
    system_message = f"""당신은 AI 활용법 학습 튜터의 QnA 전문 어시스턴트입니다.

=== 학습 커리큘럼 컨텍스트 ===
{learning_context_str}

현재 학습 위치: 챕터 {current_chapter}, 섹션 {current_section}

=== 스트리밍 응답 가이드라인 ===
- 친근하고 이해하기 쉬운 톤 사용
- 구체적인 예시와 함께 설명
- 실무에 활용할 수 있는 실용적인 정보 제공
- AI 입문자도 이해할 수 있는 수준으로 설명
- 답변 길이: 200-500자 정도 (적절한 길이)
- **마크다운 사용 금지**: ##, ** 등의 마크다운 문법 사용하지 마세요

=== 벡터 검색 사용 ===
필요시 vector_search_qna_streaming_tool을 사용하여 관련 자료를 검색하세요."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    return prompt


def _get_streaming_chatgpt_model() -> ChatOpenAI:
    """
    스트리밍용 ChatGPT 모델 초기화
    """
    model = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.3,
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '4096')),
        streaming=True  # 스트리밍 활성화
    )
    
    return model


async def _generate_error_stream(user_question: str, error_msg: str) -> AsyncGenerator[str, None]:
    """
    오류 발생 시 에러 메시지 스트리밍
    """
    error_text = f"죄송합니다. '{user_question}' 질문에 답변하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    async for chunk in _split_into_words(error_text):
        yield chunk