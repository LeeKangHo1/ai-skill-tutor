# Implementation Plan

- [ ] 1. 퀴즈 생성 에이전트 데이터 소스 개선
  - State의 theory_draft를 우선 참조하도록 process() 메서드 수정
  - chapters_metadata.json에서 챕터/섹션 제목을 로드하는 _load_section_metadata() 메서드 구현
  - theory_draft와 메타데이터를 결합한 퀴즈 생성 로직 추가
  - 기존 JSON 파일을 폴백 전략으로 활용하는 조건부 로직 구현
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 1.1 퀴즈 생성 에이전트 메타데이터 로더 구현
  - chapters_metadata.json 파일을 읽어서 특정 챕터/섹션의 제목 정보만 추출하는 _load_section_metadata() 메서드 작성
  - 메타데이터 파일 경로 설정 및 오류 처리 로직 포함
  - 이론 생성 에이전트의 동일한 메서드를 참고하여 구현
  - _Requirements: 1.2_

- [ ] 1.2 theory_draft 우선 참조 로직 구현
  - State에서 theory_draft 내용을 추출하는 _get_theory_draft_from_state() 메서드 작성
  - theory_draft 존재 여부를 확인하고 우선순위를 결정하는 조건부 로직 구현
  - theory_draft가 비어있거나 없을 경우 폴백 전략으로 전환하는 로직 추가
  - _Requirements: 1.1, 1.3_

- [ ] 1.3 퀴즈 도구 theory_draft 지원 추가
  - quiz_tools_chatgpt.py에서 theory_draft를 입력으로 받는 새로운 파라미터 추가
  - theory_draft 기반 퀴즈 생성을 위한 프롬프트 템플릿 작성
  - 기존 섹션 데이터 기반 프롬프트와 분기 처리하는 로직 구현
  - _Requirements: 1.2, 1.4_

- [ ] 2. QnA 에이전트 완전 재구현
  - 이론 생성 에이전트의 워크플로우 패턴을 참고하여 QnAResolverAgent 클래스 재작성
  - 사용자 질문을 최근 대화에서 추출하는 _extract_user_question() 메서드 구현
  - 벡터 검색 기반 답변 생성 로직 추가
  - 이론 생성 에이전트와 동일한 State 업데이트 패턴 적용
  - _Requirements: 2.1, 2.2, 2.6, 2.7_

- [ ] 2.1 QnA 에이전트 기본 구조 구현
  - 이론 생성 에이전트의 process() 메서드 구조를 참고하여 기본 틀 작성
  - 에이전트 이름, 경로 설정 등 기본 초기화 로직 구현
  - 오류 처리를 위한 _create_error_response() 메서드 작성
  - _Requirements: 2.1_

- [ ] 2.2 사용자 질문 추출 로직 구현
  - State의 current_session_conversations에서 최근 사용자 메시지를 찾는 _extract_user_question() 메서드 작성
  - 사용자 메시지 타입 필터링 및 유효성 검증 로직 포함
  - 질문이 없을 경우 기본 안내 메시지 처리
  - _Requirements: 2.2_

- [ ] 2.3 QnA 답변 생성 도구 구현
  - qna_tools_chatgpt.py 파일을 새로 생성하여 QnA 전용 답변 생성 도구 작성
  - 기존 search_qna_materials() 함수를 활용한 벡터 검색 로직 통합
  - LangChain Function Calling 또는 직접 호출 방식 중 하나 선택하여 구현
  - 벡터 검색 결과가 있을 때와 없을 때의 분기 처리 로직 작성
  - _Requirements: 2.3, 2.4, 2.5_

- [ ] 2.4 QnA 에이전트 State 업데이트 로직 구현
  - 답변 생성 완료 후 state_manager.update_agent_draft()로 qna_draft에 저장
  - state_manager.update_agent_transition()으로 현재 에이전트 설정
  - state_manager.add_conversation()으로 대화 기록 추가
  - 이론 생성 에이전트와 동일한 순서와 패턴으로 State 업데이트 수행
  - _Requirements: 2.6, 2.7_

- [ ] 3. 벡터 검색 통합 및 최적화
  - 기존 search_qna_materials() 함수를 QnA 에이전트에서 효율적으로 활용
  - 벡터 검색 결과의 품질 검증 및 confidence 임계값 적용
  - 검색 실패 시 LLM 기반 답변으로 자동 전환하는 폴백 로직 구현
  - 벡터 검색 결과를 터미널에 상세히 로깅하는 디버깅 지원 추가
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 3.1 벡터 검색 도구 통합 방식 결정
  - LangChain Function Calling 방식과 직접 호출 방식 중 하나 선택
  - 선택한 방식에 따라 qna_tools_chatgpt.py에서 search_qna_materials() 함수 활용
  - 벡터 검색 결과를 ChatGPT 프롬프트에 적절히 전달하는 로직 구현
  - _Requirements: 3.1, 3.2_

- [ ] 3.2 QnA 답변 품질 최적화
  - 벡터 검색 결과의 confidence 점수를 확인하여 품질 검증
  - confidence 0.9 이상의 결과만 사용하고 그 이하는 LLM 답변으로 전환
  - 검색된 자료의 chunk_type과 content_quality_score를 고려한 답변 생성
  - _Requirements: 3.5_

- [ ] 4. 기존 워크플로우 호환성 확보
  - 수정된 퀴즈 생성 에이전트가 기존 LangGraph 워크플로우에서 정상 동작하는지 검증
  - 새로 구현된 QnA 에이전트가 LearningSupervisor의 라우팅에서 올바르게 호출되는지 확인
  - State 필드 호환성 및 에이전트 간 전환 로직 검증
  - 기존 API 엔드포인트에서의 동작 확인
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 4.1 퀴즈 생성 에이전트 호환성 테스트
  - 기존 quiz_generation_tool() 함수 호출 방식과의 호환성 확인
  - State의 quiz 관련 필드들이 올바르게 업데이트되는지 검증
  - 퀴즈 파싱 및 저장 로직이 기존과 동일하게 동작하는지 테스트
  - _Requirements: 4.1, 4.2_

- [ ] 4.2 QnA 에이전트 워크플로우 통합 테스트
  - LearningSupervisor에서 QnA 에이전트로의 라우팅 테스트
  - QnA 에이전트 처리 후 다른 에이전트로의 전환 테스트
  - State 업데이트가 다른 에이전트들과 충돌하지 않는지 확인
  - _Requirements: 4.3_

- [ ] 5. 성능 테스트 및 품질 검증
  - 퀴즈 생성 품질 비교: theory_draft 기반 vs 기존 JSON 기반
  - QnA 답변 품질 비교: 벡터 검색 기반 vs LLM 일반 지식
  - 응답 시간 측정 및 성능 최적화
  - 다양한 질문 유형별 답변 정확도 테스트
  - _Requirements: 4.5_

- [ ] 5.1 퀴즈 생성 품질 테스트
  - theory_draft를 활용한 퀴즈와 기존 JSON 기반 퀴즈의 일관성 비교
  - 이론 설명과 퀴즈 간의 연관성 및 난이도 적절성 검증
  - 다양한 챕터/섹션에서의 퀴즈 생성 품질 테스트
  - _Requirements: 4.5_

- [ ] 5.2 QnA 답변 품질 및 성능 테스트
  - 벡터 검색 적중률 및 답변 정확도 측정
  - Function Calling 방식의 응답 시간 측정
  - 다양한 질문 유형(학습 관련, 일반 AI 질문)별 답변 품질 평가
  - 메모리 사용량 및 State 크기 모니터링
  - _Requirements: 4.5_