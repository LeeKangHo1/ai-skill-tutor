# Implementation Plan

- [x] 1. 프로젝트 기본 폴더 구조 생성





  - 루트 디렉토리에 backend/, frontend/ 폴더 생성
  - 각 폴더에 기본 하위 구조 생성
  - .gitignore 파일 생성하여 불필요한 파일 제외 설정
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [ ] 2. Python 백엔드 환경 설정
- [x] 2.1 Python 가상환경 생성 및 활성화





  - 프로젝트 루트에서 python -m venv venv 실행
  - 가상환경 활성화 방법을 README에 문서화
  - _Requirements: 2.2_

- [x] 2.2 백엔드 패키지 설치 및 requirements.txt 생성





  - 가상환경 활성화 후 backend/ 폴더로 이동
  - Flask, Flask-CORS, PyMySQL, python-dotenv, bcrypt, PyJWT 패키지 설치
  - pip freeze > requirements.txt로 의존성 파일 생성
  - _Requirements: 2.1, 2.2_

- [x] 2.3 기본 Flask 애플리케이션 구조 생성






  - app/__init__.py에 Flask 앱 팩토리 함수 작성 (Blueprint 등록 준비)
  - app/config.py에 기본 설정 클래스 작성
  - app/routes/__init__.py에 기본 Blueprint 구조 준비
  - run.py에 애플리케이션 실행 코드 작성
  - _Requirements: 2.3, 2.4_

- [x] 3. Vue.js 프론트엔드 환경 설정






- [x] 3.1 Vue 프로젝트 초기화 및 패키지 설치


  - npm create vue@latest frontend 명령으로 프로젝트 생성
  - Vue 3, Vite, Pinia, Vue Router, Axios, Sass 패키지 설치
  - _Requirements: 3.1, 3.2_


- [x] 3.2 기본 Vue 애플리케이션 구조 설정


  - main.js에 Vue 앱 초기화 코드 작성
  - App.vue에 기본 레이아웃 구조 작성
  - router/index.js에 기본 라우트 설정
  - _Requirements: 3.3, 3.4_

- [x] 4. 환경변수 및 설정 파일 작성





- [x] 4.1 백엔드 환경변수 설정


  - .env.example 파일에 DATABASE_URL, SECRET_KEY 템플릿 작성
  - .env 파일 생성 및 실제 값 설정 (로컬 개발용)
  - _Requirements: 4.1_



- [x] 4.2 프론트엔드 환경변수 설정

  - .env 파일에 VITE_API_BASE_URL=http://localhost:5000 설정
  - vite.config.js에 기본 설정 추가


  - _Requirements: 4.2, 4.4_

- [x] 4.3 Git 설정 파일 작성


  - .gitignore에 .env, node_modules/, __pycache__/, venv/ 등 추가
  - 프로젝트 루트와 각 폴더별로 적절한 무시 규칙 설정
  - _Requirements: 4.3_

- [ ] 5. 기본 API 연동 테스트 구현
- [x] 5.1 백엔드 기본 라우트 구현






  - app/routes/main.py에 기본 Blueprint 생성
  - "/" 라우트 추가하여 "AI Skill Tutor API" 메시지 반환
  - Flask 앱에 Blueprint 등록 및 CORS 설정
  - _Requirements: 2.4_

- [x] 5.2 프론트엔드 API 호출 테스트





  - Axios를 사용하여 백엔드 API 호출하는 기본 코드 작성
  - App.vue에서 백엔드 연결 상태 확인하는 간단한 테스트 구현
  - _Requirements: 3.4_

- [x] 6. 문서화 및 README 작성





- [x] 6.1 프로젝트 루트 README.md 작성


  - 프로젝트 개요, 기술 스택, 전체 실행 방법 작성
  - 포트폴리오 목적과 MVP 범위 명시
  - _Requirements: 5.1_

- [x] 6.2 백엔드 README.md 작성


  - 가상환경 설정 방법, 패키지 설치 방법 작성
  - Flask 앱 실행 방법과 기본 엔드포인트 정보 작성
  - _Requirements: 5.2_

- [x] 6.3 프론트엔드 README.md 작성


  - npm 패키지 설치 방법, 개발 서버 실행 방법 작성
  - 환경변수 설정 방법 설명
  - _Requirements: 5.3_

- [x] 7. 전체 시스템 동작 테스트






- [x] 7.1 백엔드 단독 테스트




  - 가상환경에서 python run.py 실행하여 Flask 앱 시작 확인
  - http://localhost:5000 접속하여 기본 응답 확인
  - _Requirements: 2.3, 2.4_

- [x] 7.2 프론트엔드 단독 테스트


  - npm run dev 실행하여 Vue 개발 서버 시작 확인
  - http://localhost:5173 접속하여 기본 페이지 표시 확인
  - _Requirements: 3.3, 3.4_

- [x] 7.3 프론트엔드-백엔드 통합 테스트



  - 백엔드와 프론트엔드를 동시에 실행
  - 프론트엔드에서 백엔드 API 호출이 성공하는지 확인
  - CORS 에러가 발생하지 않는지 확인
  - _Requirements: 2.4, 3.4_