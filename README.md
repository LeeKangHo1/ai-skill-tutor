# AI 활용법 학습 튜터 (AI Skill Tutor)

## 프로젝트 개요
입사 포트폴리오용 MVP 프로젝트로, AI 입문자를 위한 학습 튜터 시스템입니다.

## 기술 스택
- **백엔드**: Python Flask, MySQL, LangChain/LangGraph
- **프론트엔드**: Vue 3, Vite, Pinia, Vue Router

## 개발 환경 설정

### Python 가상환경 설정

1. **가상환경 생성** (프로젝트 루트에서 실행)
   ```bash
   python -m venv venv
   ```

2. **가상환경 활성화**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

3. **가상환경 비활성화**
   ```bash
   deactivate
   ```

### 프로젝트 실행 방법

#### 백엔드 실행
```bash
# 가상환경 활성화 후
cd backend
pip install -r requirements.txt
python run.py
```

#### 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```

## 프로젝트 구조
```
ai-skill-tutor/
├── backend/                 # Python Flask API 서버
├── frontend/               # Vue.js 클라이언트 애플리케이션
├── docs/                   # 프로젝트 설계 문서
├── .kiro/                  # Kiro 설정 및 specs
├── venv/                   # Python 가상환경
├── README.md               # 프로젝트 가이드
└── .gitignore              # Git 무시 파일
```

## 개발 진행 상황
- [x] 프로젝트 기본 구조 설계
- [x] Python 가상환경 설정
- [x] 백엔드 Flask 기본 구조 구축
- [x] 프론트엔드 Vue 3 애플리케이션 구축
- [x] 기본 라우팅 및 상태 관리 설정
- [ ] 멀티에이전트 시스템 구현
- [ ] 사용자 인증 시스템
- [ ] AI 진단 기능
- [ ] 학습 세션 관리

## 주요 기능
- **개인화된 학습**: 사용자 수준 진단을 통한 맞춤형 학습 경로
- **멀티에이전트 시스템**: LangGraph 기반 전문화된 AI 에이전트들의 협력
- **실시간 피드백**: 학습 과정에서 즉시 제공되는 AI 피드백
- **진도 관리**: 체계적인 학습 진도 추적 및 성취도 분석

## 참고 문서
- [전체 PRD](docs/ai_skill_tutor_prd_v1_3.md)
- [랭그래프 State 설계](docs/langgraph_state_design_v1_3.md)
- [DB 설계](docs/db_design_v1_3.md)
- [API 설계](docs/api_docs_v1_3.md)
- [UI 설계](docs/ui_design_v1_3.md)
- [백엔드 폴더 구조](docs/backend_folder_structure.txt)
- [프론트엔드 폴더 구조](docs/frontend_folder_structure.md)

## 라이선스
이 프로젝트는 포트폴리오 목적으로 개발되었습니다.

---
**개발자**: AI 활용법 학습 튜터 프로젝트  
**개발 기간**: 2025년 1월 ~ 진행중  
**목적**: 입사 포트폴리오용 MVP