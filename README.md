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
- [ ] 백엔드 Flask 애플리케이션 구축
- [ ] 프론트엔드 Vue 애플리케이션 구축
- [ ] 멀티에이전트 시스템 구현

## 참고 문서
- [전체 PRD](docs/ai_skill_tutor_prd_v1_3.md)
- [DB 설계](docs/db_design_v1_3.md)
- [API 설계](docs/api_docs_v1_3.md)
- [UI 설계](docs/ui_design_v1_3.md)