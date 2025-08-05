# Requirements Document

## Introduction

AI 활용법 학습 튜터 MVP 프로젝트의 기본 프로젝트 구조와 개발 환경을 구축하는 기능입니다. 포트폴리오 목적의 빠른 개발을 위해 핵심 기능에 집중하고, 복잡한 배포 설정보다는 로컬 개발 환경에서 동작하는 것을 우선으로 합니다.

## Requirements

### Requirement 1

**User Story:** 개발자로서, 프로젝트 폴더 구조가 체계적으로 구성되어 있어야 하므로, 백엔드와 프론트엔드 폴더가 명확히 분리되고 각각의 하위 구조가 설계 문서대로 생성되기를 원합니다.

#### Acceptance Criteria

1. WHEN 프로젝트 루트에서 폴더 구조를 확인할 때 THEN backend/ 폴더가 존재해야 합니다
2. WHEN backend/ 폴더를 확인할 때 THEN app/, tests/, migrations/, data/, logs/, scripts/ 폴더가 존재해야 합니다
3. WHEN app/ 폴더를 확인할 때 THEN config/, models/, routes/, services/, agents/, tools/, utils/, core/, middleware/ 폴더가 존재해야 합니다
4. WHEN 프로젝트 루트에서 폴더 구조를 확인할 때 THEN frontend/ 폴더가 존재해야 합니다
5. WHEN frontend/ 폴더를 확인할 때 THEN public/, src/ 폴더가 존재해야 합니다
6. WHEN src/ 폴더를 확인할 때 THEN router/, stores/, views/, components/, composables/, services/, utils/, styles/, assets/ 폴더가 존재해야 합니다

### Requirement 2

**User Story:** 개발자로서, Python 백엔드 개발 환경이 준비되어 있어야 하므로, MVP에 필요한 핵심 패키지들이 설치되고 기본 Flask 애플리케이션이 실행 가능한 상태가 되기를 원합니다.

#### Acceptance Criteria

1. WHEN requirements.txt 파일을 확인할 때 THEN Flask, Flask-CORS, PyMySQL, python-dotenv, bcrypt, PyJWT 패키지가 포함되어야 합니다
2. WHEN pip install -r requirements.txt를 실행할 때 THEN 모든 패키지가 오류 없이 설치되어야 합니다
3. WHEN python run.py 파일을 실행할 때 THEN Flask 애플리케이션이 정상적으로 시작되어야 합니다
4. WHEN http://localhost:5000에 접속할 때 THEN "AI Skill Tutor API" 메시지를 받을 수 있어야 합니다

### Requirement 3

**User Story:** 개발자로서, Vue.js 프론트엔드 개발 환경이 준비되어 있어야 하므로, MVP에 필요한 핵심 패키지들이 설치되고 기본 Vue 애플리케이션이 실행 가능한 상태가 되기를 원합니다.

#### Acceptance Criteria

1. WHEN package.json 파일을 확인할 때 THEN Vue 3, Vite, Pinia, Vue Router, Axios, Sass 패키지가 포함되어야 합니다
2. WHEN npm install을 실행할 때 THEN 모든 패키지가 오류 없이 설치되어야 합니다
3. WHEN npm run dev를 실행할 때 THEN Vue 개발 서버가 정상적으로 시작되어야 합니다
4. WHEN http://localhost:5173에 접속할 때 THEN "AI 활용법 학습 튜터" 제목이 표시되어야 합니다

### Requirement 4

**User Story:** 개발자로서, 개발 환경 설정이 간단하게 관리되어야 하므로, 기본적인 환경변수 파일과 설정 파일들이 구성되기를 원합니다.

#### Acceptance Criteria

1. WHEN backend/ 폴더를 확인할 때 THEN .env.example 파일이 존재하고 DATABASE_URL, SECRET_KEY 환경변수 템플릿이 포함되어야 합니다
2. WHEN frontend/ 폴더를 확인할 때 THEN .env 파일이 존재하고 VITE_API_BASE_URL이 포함되어야 합니다
3. WHEN .gitignore 파일을 확인할 때 THEN .env, node_modules/, __pycache__/ 등이 포함되어야 합니다
4. WHEN vite.config.js 파일을 확인할 때 THEN 기본 설정이 포함되어야 합니다

### Requirement 5

**User Story:** 개발자로서, 프로젝트 실행 방법을 쉽게 알 수 있어야 하므로, 간단한 README 파일이 작성되어 있기를 원합니다.

#### Acceptance Criteria

1. WHEN 프로젝트 루트의 README.md를 확인할 때 THEN 프로젝트 개요, 기술 스택, 실행 방법이 포함되어야 합니다
2. WHEN backend/README.md를 확인할 때 THEN 백엔드 실행 방법과 주요 엔드포인트가 포함되어야 합니다
3. WHEN frontend/README.md를 확인할 때 THEN 프론트엔드 실행 방법이 포함되어야 합니다
4. WHEN docs/ 폴더를 확인할 때 THEN 기존 설계 문서들이 유지되어야 합니다