# 개선이 필요한 부분

### 벡터 DB용 데이터 만들 때 주의 사항
 - 자료 조사 + JSON 파싱(구조화된 데이터 추출)를 1번에 하면 안 된다.
 - 자료 조사를 따로 하고 그 내용을 바탕으로 json으로 변환했어야 한다.

현재 프로젝트의 벡터 DB 구조를 분석해보니, 직접 ChromaDB 클라이언트를 사용하고 있는 것을 확인했습니다. LangChain Retriever를 사용하면 몇 가지 중요한 장점들이 있습니다:

## 🎯 LangChain Retriever 사용의 장점

### 1. **표준화된 인터페이스**
```python
# 현재 방식 (직접 ChromaDB 호출)
def search_theory_materials(chapter_number, section_number, search_query="", max_results=5):
    collection = get_chroma_collection()
    results = collection.query(
        query_texts=[search_query] if search_query else [f"챕터 {chapter_number}"],
        n_results=max_results,
        where={"chapter_number": chapter_number}
    )
    return results

# Retriever 방식 (표준화된 인터페이스)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
docs = retriever.invoke("챕터 1 AI 개념")
```

### 2. **LCEL 파이프라인 통합**
```python
# 현재 방식: 별도 함수 호출 후 프롬프트 조합
vector_materials = search_theory_materials(chapter, section)
prompt = theory_prompt_template.format(materials=vector_materials)

# Retriever 방식: 파이프라인 내 자동 통합
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | theory_prompt_template 
    | model 
    | StrOutputParser()
)
```

### 3. **고급 검색 기능**
```python
# Multi-query retriever (다양한 쿼리 변형)
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=ChatOpenAI(temperature=0)
)

# Self-query retriever (메타데이터 필터링 자동화)
self_query_retriever = SelfQueryRetriever.from_llm(
    llm, vectorstore, document_content_description, metadata_field_info
)

# Parent Document Retriever (청크 → 전체 문서 검색)
parent_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=docstore,
    child_splitter=child_splitter
)
```

### 4. **QnA 에이전트에서의 활용**
```python
# 현재 QnA 에이전트에서 Retriever 통합 예시
from langchain.tools.retriever import create_retriever_tool

# 리트리버를 도구로 변환
retriever_tool = create_retriever_tool(
    retriever,
    "search_learning_materials",
    "학습 자료를 검색합니다. AI, 머신러닝, 프롬프트 관련 질문에 사용하세요."
)

# Agent에 도구 추가
agent = create_tool_calling_agent(model, [retriever_tool], prompt_template)
```

## 🔧 현재 프로젝트에 적용하기 좋은 개선안

### 1. **단계적 도입 전략**
```python
# backend/app/core/external/chroma_retriever.py
from langchain_chroma import Chroma
from langchain.retrievers import MultiQueryRetriever

class ChromaRetrieverManager:
    def __init__(self):
        self.vectorstore = Chroma(
            collection_name="ai_skill_tutor",
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
            persist_directory="backend/data/chroma_db"
        )
    
    def get_theory_retriever(self):
        """이론 생성용 리트리버"""
        base_retriever = self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 5, "score_threshold": 0.8}
        )
        return MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=ChatOpenAI(temperature=0)
        )
    
    def get_qna_retriever(self):
        """QnA용 리트리버"""
        return self.vectorstore.as_retriever(
            search_type="mmr",  # Maximal Marginal Relevance
            search_kwargs={"k": 3, "fetch_k": 10}
        )
```

### 2. **기존 코드와 호환성 유지**
```python
# vector_search_tools.py 업그레이드
def search_theory_materials_v2(chapter_number, section_number, search_query=""):
    """리트리버 방식과 기존 방식 혼용"""
    try:
        # 새로운 리트리버 방식 시도
        retriever = get_theory_retriever()
        docs = retriever.invoke(f"챕터 {chapter_number} {search_query}")
        return format_retriever_results(docs)
    except Exception as e:
        # 실패 시 기존 방식으로 폴백
        print(f"Retriever 실패, 기존 방식 사용: {e}")
        return search_theory_materials(chapter_number, section_number, search_query)
```

## 🚀 **권장사항**

### **즉시 적용 가능한 개선**
1. **QnA 에이전트**: 현재 Function Calling에서 Retriever Tool로 전환하면 더 간단해집니다
2. **이론 생성**: MultiQueryRetriever로 다양한 관점의 자료를 자동으로 수집할 수 있습니다

### **장기적 개선**
1. **Self-Query Retriever**: 메타데이터 필터링을 LLM이 자동으로 수행
2. **Parent Document Retriever**: 청크 검색 후 전체 컨텍스트 제공으로 품질 향상

### **MVP 단계에서는**
- 현재 방식도 충분히 잘 작동하고 있습니다
- QnA 에이전트만 우선적으로 Retriever로 전환하는 것을 추천합니다
- 이론/퀴즈 생성은 현재 방식 유지 후 성능 개선이 필요할 때 적용하세요

현재 구조가 이미 잘 설계되어 있어서 Retriever 도입이 선택사항이지만, QnA 시스템의 품질 향상에는 확실히 도움이 될 것 같습니다.

## 추가 개발이 필요한 미해결 이슈들

## AI 응용 프로그램은 if로 분기 설정이 아니라 ai가 모든 것을 통제해야 한다.
 - 현재 사용자 진단은 내가 정한 내부 기준 점수가 있다.
 - 사용자 질문과 제출한 답변을 토대로 ai가 판단하여 ai 입문, 실무 응용 2가지 사용자 유형을 자동으로 선택하게 해야 한다.
 - 추천은 해주되 유형 자동 선택보다는 사용자가 선택하도록 의도하긴 했으나 지금은 다시 해당 내용 고려 필요.

### quiz 생성에서 벡터 db 내용 활용하지 않음

### 학습 관련 페이지는 리팩터링이 되어 있지 않음 (08-25)
 - 모바일 css제거
 - 부트스트랩 적용
 - scss nesting 문법
 - 전역 변수(variables.scss)활용

## 학습 관련 페이지 로직은 정리할 필요가 있습니다. (08-25)
 - learningStore.js, learningService.js
 - 로컬 스토리지 저장과 pinia store 저장 등이 혼합되어 문제가 많은 상태.
 - 무슨 조건인지 모르겠는데 대시보드 갔다가 학습하기 누르면 학습 데이터 오기 전에 로딩 중 인디케이터가 떠야 하는데 어느 폴백 데이터인지 몰라도 다른 내용 표시되다가 원래 내용으로 갑작스럽게 교체

### 1. 세션 횟수 영속성 문제

**문제**: `current_session_count`가 데이터베이스에 저장되지 않음
- `current_session_count` 필드가 TutorState(메모리)에만 존재
- SessionService가 세션 완료 후 사용자 상태를 지우면 카운트가 0으로 초기화됨
- 사용자가 새 세션을 시작하여 세션 제한(섹션당 최대 1회 재학습)을 우회할 수 있음

**영향**:
- 세션 재시도 제한 적용이 무효화됨
- 사용자가 적절한 추적 없이 동일한 섹션을 반복적으로 재시도할 수 있음
- 세션 통계가 부정확해짐

**필요한 해결책**:
- `user_progress` 테이블에 `current_session_count` 컬럼 추가
- SessionManager가 세션 카운트를 데이터베이스에 저장하도록 업데이트
- SessionService가 세션 시작 시 데이터베이스에서 세션 카운트를 로드하도록 수정

---

### 2. 세션 요약 연속성 문제

**문제**: `recent_sessions_summary`가 세션 간에 보존되지 않음
- 세션 요약이 TutorState 메모리에만 저장됨
- SessionService가 세션 완료 후 `self._clear_user_state()`를 호출하여 모든 요약 손실
- 다음 세션이 이전 세션 기록에 대한 정보 없이 시작됨

**영향**:
- 세션 간 연속성 손실
- QnA 에이전트가 이전 학습 맥락을 참조할 수 없음
- 사용자가 최근 학습 진행 상황을 추적하지 못함

**필요한 해결책**:
- `user_session_summaries` 데이터베이스 테이블 생성
- 최근 5개 세션 요약을 데이터베이스에 저장
- 새 세션 상태 초기화 시 최근 요약 로드
- 대안: `user_progress` 테이블에 요약용 JSON 컬럼 추가

---

### 3. State 관리 아키텍처 격차

**근본 원인**: Stateful LangGraph 워크플로우와 Stateless 세션 관리 간의 불일치
- LangGraph 워크플로우는 상호작용 간 지속적인 상태를 기대
- SessionService는 메모리 정리와 함께 상태 없는 접근 방식을 구현
- 데이터베이스 스키마가 모든 상태 지속성 요구사항을 지원하지 않음

**권장 아키텍처 검토**:
- 하이브리드 접근법 평가: 중요한 상태 필드를 데이터베이스에 저장
- 복잡한 워크플로우 연속성을 위한 세션 상태 직렬화 고려
- 각 세션 후 완전한 상태 정리가 필요한지 검토

---

*최종 업데이트: 2025-08-23*  
*우선순위: 높음 - 이러한 문제들은 핵심 기능과 사용자 경험에 영향을 미침*