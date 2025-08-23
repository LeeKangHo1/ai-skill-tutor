# 프론트엔드 API 연동 요구사항 문서

## 소개

현재 프론트엔드에는 데모 데이터로 구현된 LearningPage, MainContentArea, ChatInteraction, QuizInteraction 컴포넌트들이 있습니다. 이 컴포넌트들을 실제 백엔드 API와 연동하여 완전한 학습 시스템을 구현해야 합니다.

백엔드에는 LangGraph 기반의 멀티에이전트 시스템이 구현되어 있으며, 4가지 핵심 학습 세션 API를 통해 학습 흐름을 처리합니다.

**설계 제약사항:**
- 기존 컴포넌트 디자인을 무조건 유지해야 함
- 새로운 컴포넌트는 추가하지 않음
- 모바일/태블릿 관련 CSS는 작성하지 않음 (데스크톱 중심)

## 요구사항

### 요구사항 1: 학습 세션 시작 API 연동

**사용자 스토리:** 사용자로서 대시보드의 학습 시작 버튼이나 헤더의 학습하기 버튼을 클릭하면 현재 진행 중인 챕터/섹션의 학습 세션이 시작되어 이론 설명을 받을 수 있어야 한다.

#### 승인 기준

1. WHEN 사용자가 학습 시작 버튼을 클릭 THEN 시스템은 authStore에서 current_chapter와 current_section을 가져와 POST /api/v1/learning/session/start API를 호출해야 한다
2. WHEN API 호출이 성공 THEN 시스템은 LearningPage로 라우팅하고 이론 설명 컨텐츠를 표시해야 한다
3. WHEN API 응답에서 current_agent가 "theory_educator" THEN UI는 chat 모드로 전환되어야 한다
4. WHEN 세션이 시작 THEN tutorStore의 상태가 API 응답 데이터로 업데이트되어야 한다
5. IF API 호출이 실패 THEN 사용자에게 적절한 오류 메시지를 표시해야 한다

### 요구사항 2: 메시지 전송 및 에이전트 라우팅 API 연동

**사용자 스토리:** 사용자로서 이론 설명을 읽은 후 "다음 단계로 가주세요" 또는 질문을 입력하면 적절한 에이전트가 응답을 제공받을 수 있어야 한다.

#### 승인 기준

1. WHEN 사용자가 ChatInteraction에서 메시지를 입력 THEN 시스템은 POST /api/v1/learning/session/message API를 호출해야 한다
2. WHEN API 응답에서 current_agent가 "quiz_generator" THEN UI는 quiz 모드로 자동 전환되어야 한다
3. WHEN API 응답에서 current_agent가 "qna_resolver" THEN UI는 chat 모드를 유지하고 질문 답변을 표시해야 한다
4. WHEN 퀴즈가 생성 THEN QuizInteraction 컴포넌트에 문제, 선택지, 힌트가 표시되어야 한다
5. WHEN 메시지 전송 중 THEN 로딩 상태를 표시해야 한다

### 요구사항 3: 퀴즈 답변 제출 및 평가 API 연동

**사용자 스토리:** 사용자로서 퀴즈 문제에 답변을 제출하면 자동으로 채점되고 피드백을 받을 수 있어야 한다.

#### 승인 기준

1. WHEN 사용자가 QuizInteraction에서 답변을 제출 THEN 시스템은 POST /api/v1/learning/quiz/submit API를 호출해야 한다
2. WHEN API 응답에서 evaluation_result를 받음 THEN 정답 여부, 점수, 피드백을 표시해야 한다
3. WHEN 평가가 완료 THEN current_agent가 "evaluation_feedback_agent"로 변경되고 session_progress_stage가 "quiz_and_feedback_completed"로 업데이트되어야 한다
4. WHEN 피드백 표시 후 THEN 사용자에게 "다음 섹션으로 진행" 또는 "재학습" 선택 옵션을 제공해야 한다
5. IF 답변 제출이 실패 THEN 사용자가 다시 시도할 수 있도록 해야 한다

### 요구사항 4: 세션 완료 및 진행 상태 관리 API 연동

**사용자 스토리:** 사용자로서 학습 세션을 완료한 후 다음 섹션으로 진행하거나 현재 섹션을 재학습할 수 있어야 한다.

#### 승인 기준

1. WHEN 사용자가 "다음 섹션으로 진행" 선택 THEN 시스템은 POST /api/v1/learning/session/complete API를 "proceed" 파라미터로 호출해야 한다
2. WHEN 사용자가 "재학습" 선택 THEN 시스템은 POST /api/v1/learning/session/complete API를 "retry" 파라미터로 호출해야 한다
3. WHEN 세션 완료 API 성공 THEN 시스템은 사용자에게 "다음 학습 내용을 진행하시겠습니까? 아니면 대시보드로?" 선택 옵션을 제공해야 한다
4. WHEN 사용자가 "다음 학습 진행" 선택 THEN authStore에서 current_chapter와 current_section을 가져와 다음 챕터/섹션 세션을 시작해야 한다
5. WHEN 사용자가 "대시보드로" 선택 THEN 대시보드 페이지로 라우팅해야 한다

### 요구사항 5: 실시간 UI 상태 동기화

**사용자 스토리:** 사용자로서 백엔드 에이전트의 상태 변화에 따라 UI가 자동으로 적절한 모드로 전환되는 것을 경험할 수 있어야 한다.

#### 승인 기준

1. WHEN API 응답에서 ui_mode가 "chat" THEN ChatInteraction 컴포넌트가 활성화되어야 한다
2. WHEN API 응답에서 ui_mode가 "quiz" THEN QuizInteraction 컴포넌트가 활성화되어야 한다
3. WHEN current_agent가 변경 THEN MainContentArea의 에이전트별 테마가 적용되어야 한다
4. WHEN session_progress_stage가 업데이트 THEN 진행 상태 표시기가 반영되어야 한다
5. WHEN 세션이 완료 THEN tutorStore의 completedSteps가 업데이트되어야 한다

### 요구사항 6: 오류 처리

**사용자 스토리:** 사용자로서 API 오류가 발생했을 때 무슨 에러가 났는지 명확하게 알 수 있어야 한다.

#### 승인 기준

1. WHEN API 호출이 실패 THEN 사용자에게 구체적인 오류 메시지를 표시해야 한다
2. WHEN 로딩 중 THEN 적절한 로딩 인디케이터를 표시해야 한다

### 요구사항 7: 학습 데이터 영속성

**사용자 스토리:** 사용자로서 학습 진행 중 받아온 정보들이 브라우저 세션 동안 유지되어 새로고침해도 동일한 컨텐츠를 볼 수 있어야 한다.

#### 승인 기준

1. WHEN 학습 진행 중 받아온 모든 정보 THEN tutorStore에 저장되어야 한다
2. WHEN 사용자가 페이지를 새로고침 THEN store에 저장된 정보로 동일한 컨텐츠가 표시되어야 한다
3. WHEN 브라우저를 끄거나 로그아웃 THEN 사용자에게 "정보가 소실됩니다"라고 안내해야 한다