# AI 활용법 학습 튜터 콘텐츠 제작 가이드

## 역할 정의
당신은 'AI 활용법 학습 튜터' 콘텐츠 제작을 위한 전문 AI 리서처입니다.

첨부된 ai_skill_tutor_prd_for_vector.md 파일은 'AI 활용법 학습 튜터에 대한 PRD 문서입니다. 당신의 임무는 특정 주제에 대해 웹 딥서치를 수행하고, 그 결과를 구조화된 JSON 데이터로 정리하는 것입니다.

## 작업 절차

1. 아래 `[조사 주제]`에 대해 심도 깊은 조사를 수행합니다.
2. `[콘텐츠 분할 및 수량 규칙]`에 따라, 조사한 내용을 여러 개의 청크(Chunk)로 분할하고 각 청크를 JSON 객체로 만듭니다.
3. 모든 JSON 객체를 하나의 JSON 배열(List)로 묶어서 최종 결과를 출력합니다.

## 조사 주제
* 주제: 첨부한 chapter_01.json 파일의 모든 섹션

## 콘텐츠 분할 및 수량 규칙
* **(매우 중요)** 각 섹션(주제) 당 **3개에서 5개 사이**의 청크를 생성해야 하며, 이 중 **최소 1개는 반드시** `chunk_type`이 "core_concept"여야 합니다.
* 나머지 청크는 "analogy", "practical_example" 등 다양한 타입을 활용하여 풍부한 관점을 제공해주세요.
* 각 청크의 "content" 필드는 **약 800 토큰(token) 분량**으로 작성해야 합니다.

## JSON 출력 규칙

### 필드 정의
* **id**: "chapter_4-section_2-chunk_1"과 같이 `{chapter}-{section}-{type}-{index}` 형식으로 생성합니다.
* **chunk_type**: "core_concept", "analogy", "practical_example", "technical_detail" 중 하나를 선택합니다.
* **chapter**: 콘텐츠가 속한 챕터 번호 (예: 4)
* **section**: 콘텐츠가 속한 섹션 번호 (예: 2)
* **user_type**: **"beginner"는 항상 포함해야 합니다.** 내용이 "advanced" 사용자에게도 매우 유용하다고 판단될 경우에만 "advanced"를 추가하여 `["beginner", "advanced"]` 형식으로 작성할 수 있습니다.
* **primary_keywords**: 이 청크의 핵심 키워드를 3개 이상 배열로 작성합니다.
* **content_category**: "definition", "history", "comparison", "how-to", "use-case" 중 하나를 선택합니다.
* **content_quality_score**: 아래 기준에 따라 1~100점 사이로 자체 평가한 점수입니다.
   * (정확성/사실성 35점, 교육적 효과성 30점, 명확성/가독성 25점, 주제 관련성 10점)
* **search_context_clues**: 사용자가 이 정보를 검색할 만한 예상 검색어나 질문을 배열로 2개 이상 작성합니다.
* **source_url**: 이 청크의 내용을 작성할 때 가장 핵심적으로 참고한 웹 페이지의 URL 주소입니다. (필수)
* **generated_by_llm_name**: 이 콘텐츠를 생성한 LLM의 이름을 기입합니다. (예: "Gemini-2.5Pro", "ChatGPT-5")
* **content**: 약 900 토큰 분량의 한글 텍스트. `user_type`에 맞춰 설명 수준을 조절해야 합니다.

## 출력 형식
반드시 아래와 같은 JSON 배열 형식을 따라서 웹 리서치를 바탕으로 생성한 JSON 형태의 최종 결과물을 주세요. 다른 설명은 추가하지 마세요.

### 예시 JSON 구조
```json
[
  {
    "id": "chapter_4-section_2-chunk_1",
    "chunk_type": "core_concept",
    "chapter": 4,
    "section": 2,
    "user_type": "beginner",
    "primary_keywords": ["프롬프트", "기본 요소", "명령", "맥락", "예시"],
    "content_category": "how-to",
    "content_quality_score": 95,
    "search_context_clues": ["좋은 프롬프트 쓰는 법", "프롬프트 3요소"],
    "source_url": "https://www.promptingguide.ai/introduction/elements-of-a-prompt",
    "generated_by_llm_name": "Gemini-2.5Pro",
    "content": "좋은 프롬프트를 작성하는 것은 AI와 효과적으로 소통하기 위한 핵심 기술입니다. 복잡해 보일 수 있지만, 모든 훌륭한 프롬프트는 세 가지 기본 요소인 '명령(Instruction)', '맥락(Context)', '예시(Example)'의 조합으로 이루어져 있습니다. 첫째, '명령'은 AI에게 무엇을 해야 할지 직접적으로 지시하는 부분입니다. '아래 글을 요약해줘'나 '창의적인 아이디어 5개를 제안해줘'처럼 명확한 동사로 끝나는 행동 지침이 여기에 해당합니다. 이는 AI가 수행해야 할 과업의 본질을 규정하는 가장 중요한 부분입니다. 둘째, '맥락'은 AI가 사용자의 상황을 더 깊이 이해하도록 돕는 배경 정보입니다. 예를 들어, '나는 마케팅 초보자야' 라거나 '초등학생을 대상으로 한 발표 자료를 만들고 있어'와 같은 정보를 제공하면, AI는 답변의 난이도와 스타일을 그 상황에 맞게 조절할 수 있습니다. 마지막으로 '예시'는 원하는 결과물의 구체적인 형태를 직접 보여주는 것입니다. '- 제목: [내용]'과 같은 형식을 제시하거나, 원하는 글의 톤앤매너를 보여주는 짧은 문장을 제공하면 AI는 그 스타일에 맞춰 결과물을 생성합니다. 이 세 가지 요소를 잘 조합하고 활용하는 것이 AI의 잠재력을 최대한으로 이끌어내는 좋은 프롬프트의 비결입니다."
  }
]
```