네, 지금까지 진행한 리팩토링 작업을 개발일지로 정리했습니다.

---

## **프론트엔드 학습 페이지 리팩토링 개발일지**

**날짜**: 2025년 8월 27일

### ## **1. 프로젝트 목표** 🎯

Vue 컴포넌트 간의 복잡한 `props` 전달 및 `emit` 이벤트 구조를 제거하고, **Pinia Store를 단일 정보 출처(Single Source of Truth)로 사용하는 중앙 집중식 상태 관리 아키텍처로 전환**하는 것을 목표로 함. 이를 통해 코드의 예측 가능성을 높이고 유지보수성을 향상시킴.

### ## **2. 주요 아키텍처 변경 사항** 🏗️

* **Pinia Store 중심 설계**: 기존에 각 컴포넌트에 흩어져 있던 API 호출, 데이터 상태, UI 제어 로직을 `learningStore.js`로 모두 이전함.
* **단방향 데이터 흐름 확립**: `컴포넌트 (사용자 입력)` → `Store 액션 호출` → `API 요청` → `Store 상태 변경` → `컴포넌트 자동 리렌더링`으로 이어지는 명확한 데이터 흐름을 구축함.
* **컴포넌트 역할 재정의**: Vue 컴포넌트의 역할을 Store의 데이터를 화면에 보여주는 **'View'**와 사용자의 입력을 Store에 전달하는 **'전달자'**로 단순화함.

### ## **3. 컴포넌트별 리팩토링 내역** 🛠️

* **`learningStore.js` (상태 관리 허브)**
    * 학습 세션과 관련된 모든 상태(`currentUIMode`, `chatHistory`, `quizData`, `isContentLoading` 등)를 중앙에서 관리하도록 재설계함.
    * `startNewSession`, `sendMessage`, `completeSession` 등 API 통신을 전담하는 액션(Action)들을 구현함.
    * '콘텐츠 다시 보기' 기능 지원을 위해 `contentMode`, `completedSteps` 상태를 추가함.
    * `authStore`의 사용자 진행 상황(`currentChapter` 등)을 실시간으로 반영하기 위해 `sessionInfo`를 `computed` 속성으로 변경하여 데이터 불일치 문제를 해결함.

* **`HeaderComponent.vue` (페이지 진입점)**
    * 초기에는 '학습하기' 버튼 클릭 시 API를 먼저 호출했으나, 사용자 경험 개선을 위해 **단순 페이지 이동(`<router-link>`) 역할**로 최종 수정함. API 호출 책임은 `LearningPage`로 이관됨.

* **`LearningPage.vue` (메인 컨테이너)**
    * 자식 컴포넌트로 전달하던 모든 `props`를 제거함.
    * 페이지 진입 시(`onMounted` 훅) `learningStore`의 `startNewSession` 액션을 호출하여 '페이지 이동 후 데이터 요청' 흐름을 구현함.
    * Store의 `uiMode` 상태를 감시하여 `ChatInteraction`과 `QuizInteraction` 컴포넌트를 조건부로 렌더링함.
    * 초기에는 전체 화면 로딩을 사용했으나, 이후 자식 컴포넌트의 부분 로딩을 지원하는 구조로 변경함.

* **`MainContentArea.vue` (컨텐츠 표시 영역)**
    * `props`를 모두 제거하고 Store의 `currentAgent`, `contentMode` 등 다양한 상태를 직접 참조하여 상황에 맞는 컨텐츠(`Theory`, `Quiz`, `Feedback`)를 동적으로 렌더링하도록 수정함.
    * '이론/퀴즈 다시 보기' 버튼들의 UI 로직을 Store의 `completedSteps` 및 `contentMode` 상태와 연동함.

* **진행 중인 컴포넌트 (`TheoryContent`, `ChatInteraction`, `QuizInteraction` 등)**
    * **`TheoryContent.vue`**: `props`를 제거하고 Store의 `mainContent` 상태를 직접 구독하여 이론 데이터를 표시하도록 수정함. API의 중첩된 JSON 구조를 올바르게 파싱하는 로직을 적용함.
    * **`ChatInteraction.vue`**: `props`와 `emit`을 제거. Store의 `chatHistory`를 직접 렌더링하고, 메시지 전송 및 '재학습/다음' 버튼 클릭 시 Store의 액션을 직접 호출하도록 수정함. 원본의 모든 UI(말풍선, 입력 힌트 등)를 보존하는 방향으로 최종 수정.
    * **`QuizInteraction.vue`**: `props` 제거. Store의 `quizData`를 받아 퀴즈 선택지를 렌더링하고, 답안 제출 시 Store 액션을 호출하도록 수정 진행 중.

### ## **4. 주요 이슈 및 해결 과정** 🔍

* **문제**: `uiMode` 상태가 Store에서는 `'chat'`인데 화면에는 '퀴즈'로 표시되는 등 반응성 유실 문제 발생.
    * **해결**: `storeToRefs` 사용 시 변수명 불일치(`currentUIMode: uiMode`)를 찾아내고, `storeToRefs`의 올바른 사용법을 적용하여 해결함.

* **문제**: 비동기 데이터가 도착하기 전에 컴포넌트가 렌더링되려다 `null` 에러를 발생시키며 앱이 중단됨.
    * **해결**: `LearningPage`에서 `isContentLoading` 상태를 이용, 핵심 컨텐츠 영역의 렌더링을 데이터 로드가 완료된 이후로 지연시켜 렌더링 시점을 제어함으로써 문제 해결.

* **문제**: 초기 리팩토링 시 기능(입력 힌트, 다시 보기 버튼 등)이 누락되고 디자인이 변경되는 회귀(Regression) 발생.
    * **해결**: 사용자의 피드백을 반영하여, 원본 컴포넌트의 템플릿과 스타일을 100% 유지하는 것을 원칙으로 재설정하고, 스크립트 로직만 Store와 연동되도록 꼼꼼하게 재작업함.

### ## **5. 다음 단계** ➡️

* `QuizContent.vue` 및 `FeedbackContent.vue` 리팩토링 완료.
* 전체 학습 흐름(이론 → 퀴즈 → 피드백 → 다음 세션)에 대한 сквозное тестирование(End-to-End) 진행.
* 디버깅을 위해 추가했던 임시 코드 및 콘솔 로그 정리.