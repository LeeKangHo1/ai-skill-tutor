# 🤖 AI 활용법 학습 튜터 (AI Skill Tutor)

> AI 활용법 학습 튜터는 학습자가 AI와 LLM(대형 언어 모델)을 이해하고 실용적으로 활용할 수 있도록 돕기 위해 개발된 멀티 에이전트 아키텍처 기반의 튜터링 시스템입니다.

- 개발 기간: 2025년 7월 28일 ~ 2025년 8월 31일 (약 1달)
- 개발 인원: 1인 풀스택 개발

[![Python](https://img.shields.io/badge/Python-3.13.5-blue.svg)](https://python.org)[![LangChain](https://img.shields.io/badge/LangChain-0.3.27-orange.svg)](https://langchain.com)[![LangGraph](https://img.shields.io/badge/LangGraph-0.6.3-red.svg)](https://langgraph.com)[![MySQL](https://img.shields.io/badge/MySQL-8.0.20-blue.svg)](https://mysql.com)[![Vue.js](https://img.shields.io/badge/Vue.js-3.0-green.svg)](https://vuejs.org)

## ✨ 주요 기능 (Key Features)

- **🧑‍🏫 사용자 맞춤형 학습 경로**: 최초 진단 퀴즈를 통해 'AI 입문자', '실무 응용형 사용자' 유형을 구분하고, 각기 다른 학습 컨텐츠를 제공합니다.
    
- **💬 대화형 학습 세션**: 개념 학습 → 퀴즈 풀이 → 평가 및 피드백으로 이어지는 1:1 튜터링 방식의 학습을 경험할 수 있습니다.
    
- **❓ 실시간 Q&A**: 학습 도중 발생하는 질문에 대해 Q&A 에이전트가 즉각적으로 답변하여 학습 몰입도를 높입니다.
    
- **🧠 멀티에이전트 시스템 (MAS)**: 6개의 전문 에이전트(학습 감독, 이론 교육, 퀴즈 생성 등)가 협력하여 학습 흐름을 유기적으로 관리합니다.
    
- **📈 학습 기록 관리**: 모든 학습 성과는 데이터베이스에 저장되어 언제든지 자신의 성장 과정을 확인할 수 있습니다.

### 사용자 진단
<img width="1199" height="877" alt="Snipaste_2025-11-09_22-18-46" src="https://github.com/user-attachments/assets/a18e0514-3268-4a12-b58f-4be12384bd1a" />

<img width="961" height="691" alt="Pasted image 20251109222019" src="https://github.com/user-attachments/assets/b6e8a431-99d4-4da4-93c5-f1162a54bebc" />

### 학습 화면
<img width="1162" height="979" alt="Snipaste_2025-11-09_22-25-28" src="https://github.com/user-attachments/assets/41ecd7a9-ca99-4919-a3db-b8a86e580daf" />


### 퀴즈

<img width="1163" height="734" alt="Snipaste_2025-11-09_22-27-11" src="https://github.com/user-attachments/assets/148e5b20-b267-46ad-83a5-d1db609980ed" />

- 객관식

<img width="1146" height="750" alt="Snipaste_2025-11-09_22-27-44" src="https://github.com/user-attachments/assets/af73c649-858f-4792-b67f-4193f5656960" />

- 채점 및 피드백

<img width="1146" height="810" alt="Snipaste_2025-11-09_22-30-39" src="https://github.com/user-attachments/assets/9eb862f3-23cd-44bb-831c-236ef194b9e9" />

- 주관식

### 채팅으로 실시간 질문

<img width="1163" height="966" alt="Snipaste_2025-11-09_22-35-57" src="https://github.com/user-attachments/assets/7aba97f7-5ea2-4921-99e3-c42c5f19288b" />

- 사용자의 채팅 내용을 분석해 다음 학습 과정으로 진행하거나 질문일 경우 질문에 대한 답변을 생성합니다.

### 대시보드

<img width="1109" height="995" alt="Snipaste_2025-11-09_22-38-14" src="https://github.com/user-attachments/assets/d824dd9a-6216-47ea-b983-756dd340dc76" />

---


## 🏛️ 시스템 아키텍처 (System Architecture)

### 1) 멀티에이전트 시스템 (MAS, Multi-Agent System)

<img width="1246" height="623" alt="Pasted image 20250910092537" src="https://github.com/user-attachments/assets/92bae1e7-7d54-4dfd-85e0-b524335f2e65" />

- 여러 명의 전문가가 협업하는 것처럼, 각자 다른 역할을 맡은 AI들이 함께 일하는 시스템입니다.
- 본 프로젝트는 LangGraph를 활용한 **중앙 감독관(Supervisor) 기반의 멀티에이전트 시스템**으로 설계되었습니다. 
- `LearningSupervisor`가 사용자의 채팅 내용을 받아 의도를 분석하고, 가장 적합한 전문 에이전트에게 작업을 위임하는 구조입니다.
### 🤖 에이전트 역할 분담

| 에이전트                        | 전문 영역    | 핵심 기능             |
| --------------------------- | -------- | ----------------- |
| **LearningSupervisor**      | 워크플로우 관리 | 중앙집중식 라우팅 및 응답 생성 |
| **SessionManager**          | 세션 관리    | 학습 내용 DB 저장       |
| **TheoryEducator**          | 개념 설명    | 사용자 유형별 맞춤 이론 교육  |
| **QuizGenerator**           | 문제 출제    | 퀴즈 생성 및 힌트 제공     |
| **EvaluationFeedbackAgent** | 평가 분석    | 통합 채점 및 개인화 피드백   |
| **QnAResolver**             | 실시간 Q&A  | 벡터 검색 기반 답변       |
### 2) RAG(Retrieval-Augmented Generation)
- AI가 답변하기 전에 먼저 관련 자료를 찾아보고 그 내용을 바탕으로 대답하는 시스템입니다.
- 직접 수집한 양질의 자료들을 벡터 DB에 저장 후 학습 내용 생성이나 사용자 질문에 대한 대답 생성 시 해당 자료를 참고해 양질의 답변을 생성합니다.
---

## 🔧 기술 스택

<img width="311" height="102" alt="Snipaste_2025-11-09_23-30-40" src="https://github.com/user-attachments/assets/84e8c1b2-70d6-47fa-95c3-b048b08cf348" />

| 구분           | 기술                                  |
| ------------ | ----------------------------------- |
| **Backend**  | Python, Flask, LangChain, LangGraph |
| **Frontend** | Vue 3, Pinia, Axios                 |
| **Database** | MySQL, ChromaDB (Vector DB)         |
| **Etc**      | JWT(인증), LangSmith (디버깅, 모니터링)      |

---

# 프로젝트 상세 내용

## <목차>
### 1. 프로젝트 설계
### 2. 주요 기능 상세 설명
### 3. 트러블 슈팅
### 4. 프로젝트 소감

---
## 1. 프로젝트 설계
### 1) 과목
- 수학, 영어
	- 영어의 경우 듀오링고, 산타토익 등 이미 시장에 나온 프로그램이 많은 상황
	- 수학 역시 중, 고등학교 수학 위주로 기존 프로그램이 많은 상황 
- 약학
	- 높은 도메인 지식 요구량
	- 실용성(수요) + 자료 접근성의 한계
	- 약학의 특성 상 학습 컨텐츠의 정확성이 매우 중요
- 일상 업무에서 AI 활용
	- 비전공자로서 AI 엔지니어링을 스스로 학습한 경험에서 착안
	- 오픈소스 자료 확보 용이 → **AI 학습에 적합하도록 정제·가공 후 콘텐츠 구성 가능**
	- 모든 직군 대상의 실무 활용 가능성 존재
### 2) 언어 모델, 벡터 DB, 임베딩 모델
- Gemini 2.5 Flash
	- 첫 고려 모델. 무료로 테스트 가능
	- Time to First Token (TTFT)이 너무 길어서 gpt-4o-mini로 교체
- gpt-4o-mini
	- 짧은 TTFT
	- 1M 토큰 당 입력 0.15\$, 출력 0.6$ -> 매우 저렴한 비용
	- 구형 모델이지만 여러 개의 에이전트로 협업 시 단독 사용보다 높은 퍼포먼스
- chromaDB
	- 무난한 검색 성능, 빠른 개발 가능, 무료
- text-embedding-3-large
	- 현재 벡터 DB 임베딩 모델로서 top급의 성능
	- 뛰어난 다국어 지원
	- small에 비해 비용이 비싸나 최초 벡터 DB 구축과 대규모 학습 자료 업데이트 이외에는 벡터 검색 쿼리 생성 정도로는 비용이 많지 않음
### 3) 기본 시스템 설계
- 랭그래프 state 설계
	- 상태 추적, 에이전트 간 정보 공유, 워크플로우 제어, 데이터 일관성 및 디버깅, 라우팅 시스템의 핵심
	- 학습 진행 상태 관리, 각 에이전트가 생성한 대본을 저장하여 공유하고 LearningSupervisor가 이를 참조하여 최종 대본 생성 가능
- DB 설계, API 엔드포인트 설계
- UI 설계
	- 메인 페이지, 모든 화면에 공통으로 쓰일 헤더
	- 대시보드(통계), 학습, 회원, 사용자 진단 페이지
	- 퀴즈 진행 시 퀴즈 답변 이외의 사용자 입력을 제한하여 오류 감소
	- 퀴즈 이외의 상황에서는 항상 채팅창이 활성화 되어 사용자가 언제든지 중간에 실시간 질문 가능
	- 1 사이클의 학습 완료 직전 학습 내용, 퀴즈, 피드백, 채팅창 모두를 확인하며 복습 가능
### 4) 문서 작업
- 다양한 코딩 에이전트를 활용할 때 이정표 역할
- 작업이 중단 되거나 다른 생성형 AI 모델 사용 시 문맥(context) 제공
- PRD, DB, API Docs, langgraph state, 프로젝트 폴더 구조, UI Design 등
---
## 2. 주요 기능 상세 설명

### 1) 학습 과정
- 가입 직후 사용자 진단을 거쳐 사용자 유형 선택
- 큰 챕터가 있고 각 챕터에 서브섹션이 존재
	- 1서브섹션 당 1학습 사이클 적용
- 개념 설명 -> 퀴즈 1회 -> 마무리 피드백 -> 다음 서브섹션 or 지금 서브섹션 복습 선택 -> DB에 학습 기록를 추가하고 다음 학습으로 진행
- 개념 설명 이후, 퀴즈 풀이 이후 채팅창에서 자유롭게 질문 가능
### 2) 학습 컨텐츠 준비
- 실무에서 ai를 활용하는 방법에 대한 책 조사
- gemini, gpt, cluade와 의논하면서 컨텐츠 구상
- 개발자 본인이 AI를 학습하면서 학습에 필요했던 내용이나 궁금했던 내용, 유용했던 내용들을 추가하면서 마무리
- 8챕터 34서브섹션으로 구성
### 3) 학습 컨텐츠 생성
```python
    # 사용자 유형별 기본 지침
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
```
- beginner와 advanced 2가지 유형에 대한 프롬프트가 각각 존재

```json
{
	"id": "chapter_2-section_1-chunk_1-gemini",
	"chunk_type": "core_concept",
	"chapter": 2,
	"section": 1,
	"user_type": ["beginner"],
	"primary_keywords": ["알렉스넷", "딥러닝", "GPU", "이미지 인식", "병렬 처리"],
	"content_category": "history",
	"content_quality_score": 98,
	"search_context_clues": ["딥러닝의 시작", "알렉스넷이란 무엇인가", "GPU가 AI에 중요한 이유"],
	"source_url": "<https://papers.nips.cc/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf>",
	"generated_by_llm_name": "Gemini",
	"content": "2012년은 인공지능 역사에서 '빅뱅'이 일어난 해로 기억됩니다. 바로 '알렉스넷(AlexNet)'이라는 딥러닝 모델이 세계 최대 이미지 인식 경진대회(ILSVRC)에서 압도적인 성능으로 우승하며 세상을 놀라게 한 사건 때문입니다. 이전 모델들의 오류율이 25% 이상이었던 반면, 알렉스넷은 15.3%라는 획기적인 오류율을 기록하며 딥러닝의 잠재력을 전 세계에 증명했습니다. 이 놀라운 성공의 핵심 비결은 바로 'GPU(Graphics Processing Unit)'의 활용에 있었습니다... 
},
```
- 직접 조사한 자료들을 위의 json형태로 가공하여 AI가 챕터와 섹션 번호로 빠르게 데이터를 찾고 chunk_type을 통해 해당 자료가 무슨 내용인지 파악할 수 있도록 설정
	- chunk_type
		- "core_concept", "analogy", "practical_example", "technical_detail"
- 벡터 검색으로 가져온 자료를 기반으로 AI가 내용을 덧붙여 최종 학습 컨텐츠를 생성
### 4) 퀴즈 생성 및 풀이 및 피드백
- 학습 컨텐츠 생성과 마찬가지로 beginner와 advanced 2가지 유형에 대한 프롬프트가 각각 존재
- 랭그래프 state에 저장된 학습 컨텐츠 내용을 기반으로 퀴즈 및 피드백 생성
### 5) 실시간 QnA 실행 원리
- AI가 채팅 내용을 보고 질문이라 판단하면 QnAResolver 에이전트를 호출
- 사용자 채팅을 분석하여 벡터 검색용 쿼리를 생성
	- 질문 내용에 따라 최대 3개의 쿼리를 생성
	- 예시) "트랜스포머와 제프리 힌튼이 뭐에요?" -> "트랜스포머란?" + "제프리 힌튼이 누구?"
- 생성한 쿼리로 벡터 DB에서 유사도 검색을 수행
	- 모든 쿼리를 병렬로 실행, 벡터 검색 시간 최소화
- 벡터 DB에서 가져온 내용을 기반으로 AI가 내용을 보충해서 답변을 생성

---
## 3. 트러블 슈팅
### 1) 실시간 QnA 답변 생성 시간(TTFT, Time to First Token) 감소
- 문제 상황: 복잡한 질문의 경우 답변 생성에 8초 이상 시간 소모
- 백엔드 개선
	- 답변의 모든 내용을 생성 후 프론트에 전송하는 것이 아니라 먼저 생성된 내용은 먼저 보내는 streaming 방식으로 전환
- 프론트엔드 개선
	- props, emit를 최소화 하고 Vue의 반응성(ref·computed) 위에 Pinia store(defineStore·actions)를 얹어, 상태 변화가 자동으로 UI에 반영되는 전역 상태 관리 시스템을 도입
- 결과
	- TTFT 시간을 3초 이상 단축, 사용자 체감 개선
### 2) 프로젝트 어려웠던 점
- 낮은 바이브 코딩 숙련도로 인한 문제
	- AI가 일관된 작업을 위한 context 제공의 중요성 인식 
	- 랭체인과 랭그래프의 경우 최신 라이브러리라 업데이트가 잦음
		- AI가 구형 문법을 사용하는 경우를 잘 체크해서 최신 문법으로 교정 필요
- 랭그래프 상태 관리에 대한 이해 부족
	- 개별 에이전트 구현 및 테스트를 완료했으나 랭그래프로 에이전트를 연결하여 통합 테스트에서 많은 오류 발생
	- 각 에이전트 코드를 다시 작성하며 많은 시간을 소모 

---
## 4. 프로젝트 소감 
- 개인 프로젝트로 소화하기 힘든 프로젝트 규모였으나 코딩 에이전트를 활용, 프로젝트의 모든 부분을 혼자서 개발이 가능해서 놀라웠습니다.
- 이론 공부를 하면서 부분적으로 구현했던 코드와 실제 프로젝트 코드는 많이 다른 것을 알 수 있었습니다.
- 바이브 코딩 숙련도 증가와 랭그래프로 구성하는 멀티 에이전트 시스템에 대한 이해도가 많이 올라 추후 유사한 프로젝트의 경우 개발 기간을 절반 가까이 단축할 수 있을 것으로 보입니다.

---
## Authors
- 이강호
- 깃허브 닉네임: LeeKangHo1
- [깃허브 프로필 링크](https://github.com/LeeKangHo1)
