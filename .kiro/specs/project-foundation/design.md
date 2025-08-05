# Design Document

## Overview

AI 활용법 학습 튜터 MVP 프로젝트의 기본 구조를 구축하는 설계입니다. 포트폴리오 목적에 맞춰 빠른 개발과 간단한 배포를 고려하여, 로컬 개발 환경에서 효율적으로 작업할 수 있는 구조를 만듭니다.

## Architecture

### 전체 프로젝트 구조
```
ai-skill-tutor/
├── backend/                 # Python Flask API 서버
├── frontend/               # Vue.js 클라이언트 애플리케이션
├── docs/                   # 프로젝트 설계 문서 (기존 유지)
├── .kiro/                  # Kiro 설정 및 specs (기존 유지)
├── README.md               # 프로젝트 전체 가이드
└── .gitignore              # Git 무시 파일
```

### 백엔드 구조 (간소화된 Flask 구조)
```
backend/
├── app/
│   ├── __init__.py         # Flask 앱 팩토리
│   ├── config.py           # 설정 관리
│   ├── models/             # 데이터 모델 (추후 구현)
│   ├── routes/             # API 라우트 (추후 구현)
│   └── utils/              # 유틸리티 함수 (추후 구현)
├── requirements.txt        # Python 패키지 의존성
├── run.py                  # Flask 앱 실행 파일
├── .env.example            # 환경변수 템플릿
└── README.md               # 백엔드 실행 가이드
```

### 프론트엔드 구조 (기본 Vue 구조)
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── main.js             # Vue 앱 진입점
│   ├── App.vue             # 루트 컴포넌트
│   ├── router/             # Vue Router 설정
│   ├── stores/             # Pinia 상태 관리
│   ├── views/              # 페이지 컴포넌트 (추후 구현)
│   ├── components/         # 재사용 컴포넌트 (추후 구현)
│   └── services/           # API 서비스 (추후 구현)
├── package.json            # Node.js 패키지 의존성
├── vite.config.js          # Vite 설정
├── .env                    # 환경변수
└── README.md               # 프론트엔드 실행 가이드
```

## Components and Interfaces

### 1. Flask 애플리케이션 기본 구조

**app/__init__.py**
- Flask 앱 팩토리 패턴 사용
- CORS 설정으로 프론트엔드와 통신 가능
- 기본 라우트 설정

**app/config.py**
- 환경변수 기반 설정 관리
- 개발/운영 환경 구분 (MVP에서는 개발 환경만)

**run.py**
- Flask 애플리케이션 실행 진입점
- 디버그 모드 활성화

### 2. Vue.js 애플리케이션 기본 구조

**main.js**
- Vue 앱 초기화
- Pinia, Vue Router 설정
- 전역 스타일 import

**App.vue**
- 루트 컴포넌트
- 기본 레이아웃 구조
- 라우터 뷰 설정

**router/index.js**
- 기본 라우트 설정 (홈 페이지만)
- 추후 확장 가능한 구조

### 3. 개발 환경 설정

**환경변수 관리**
- Backend: .env 파일로 데이터베이스 URL, 시크릿 키 관리
- Frontend: .env 파일로 API 베이스 URL 관리

**패키지 관리**
- Backend: requirements.txt로 Python 패키지 관리
- Frontend: package.json으로 Node.js 패키지 관리

## Data Models

현재 단계에서는 데이터 모델을 구현하지 않고, 기본 구조만 준비합니다.

```python
# app/models/__init__.py (빈 파일로 생성)
# 추후 사용자, 세션, 퀴즈 모델 등이 추가될 예정
```

## Error Handling

### Flask 기본 에러 처리
```python
# app/__init__.py에 포함될 기본 에러 핸들러
@app.errorhandler(404)
def not_found(error):
    return {"error": "Not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error"}, 500
```

### Vue.js 기본 에러 처리
- 개발 단계에서는 브라우저 콘솔 에러 확인
- 추후 사용자 친화적 에러 메시지 구현 예정

## Testing Strategy

MVP 단계에서는 복잡한 테스트 설정보다는 수동 테스트에 집중합니다.

### 백엔드 테스트
- Flask 앱이 정상적으로 시작되는지 확인
- 기본 라우트가 응답하는지 확인
- CORS가 올바르게 설정되었는지 확인

### 프론트엔드 테스트
- Vue 개발 서버가 정상적으로 시작되는지 확인
- 기본 페이지가 렌더링되는지 확인
- API 호출이 가능한지 확인

### 통합 테스트
- 프론트엔드에서 백엔드 API 호출이 성공하는지 확인
- CORS 에러가 발생하지 않는지 확인

## Implementation Notes

### 개발 순서
1. 프로젝트 기본 폴더 구조 생성
2. Python 가상환경 설정 및 기본 패키지 설치
3. 백엔드 기본 Flask 앱 설정
4. 프론트엔드 기본 Vue 앱 설정
5. 환경변수 및 설정 파일 작성
6. README 파일 작성
7. 기본 동작 테스트

**참고**: 상세한 폴더 구조(models/, routes/, services/ 등)는 각 기능 spec 진행 시 점진적으로 추가됩니다.

### 주요 고려사항
- **간단함 우선**: 복잡한 설정보다는 빠른 개발에 집중
- **확장 가능성**: 추후 기능 추가가 쉬운 구조
- **포트폴리오 목적**: 코드 가독성과 구조의 명확성 중시
- **로컬 개발**: 복잡한 배포 설정 없이 로컬에서 쉽게 실행 가능

### 패키지 버전 관리
- 최신 버전으로 설치하여 최신 기능 활용
- 문제 발생 시 해당 패키지만 버전 다운그레이드
- Python 가상환경 사용으로 시스템 Python과 분리