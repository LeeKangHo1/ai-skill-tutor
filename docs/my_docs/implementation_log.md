# 구현 로그 (Implementation Log)

## 📦 사용 패키지 버전 (2025-08-13 기준)
- langchain==0.3.27
- langchain-core==0.3.72
- langgraph==0.6.3
- langsmith==0.4.13

## 📋 향후 개발 지침
**앞으로 모든 에이전트와 툴 작성 시 표준 패턴 적용:**
- **PromptTemplate**: 입력 변수 명확히 정의
- **LCEL 파이프라인**: `PromptTemplate | ChatOpenAI | OutputParser` 구조 
- **OutputParser**: JSON 출력은 `JsonOutputParser` + Pydantic 스키마, 텍스트는 `StrOutputParser`
- import는 "from langchain_core.prompts import PromptTemplate" , "from langchain_core.output_parsers import JsonOutputParser"
- db를 다루는 경우 backend/app/utils/database/connection.py, query_builder.py, transaction.py 파일의 유틸리티를 활용할 것
