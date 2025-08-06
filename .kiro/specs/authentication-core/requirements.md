# Requirements Document

## Introduction

AI 활용법 학습 튜터 프로젝트의 핵심 인증 시스템을 구현합니다. 이 시스템은 사용자 회원가입, 로그인, JWT 토큰 기반 인증/인가, 그리고 보안 관리를 담당하는 핵심 인프라입니다. 모든 다른 기능들이 이 인증 시스템을 기반으로 동작하므로, 안전하고 확장 가능한 구조로 설계되어야 합니다.

## Requirements

### Requirement 1

**User Story:** 신규 사용자로서, 계정을 생성하여 시스템에 접근할 수 있기를 원합니다.

#### Acceptance Criteria

1. WHEN 사용자가 유효한 회원가입 정보(login_id, username, email, password)를 제공하면 THEN 시스템은 새로운 계정을 생성해야 합니다
2. WHEN 사용자가 4-20자 범위의 고유한 login_id를 입력하면 THEN 시스템은 중복 검사를 수행하고 사용 가능 여부를 알려야 합니다
3. WHEN 사용자가 유효한 이메일 형식을 입력하면 THEN 시스템은 이메일 중복 검사를 수행해야 합니다
4. WHEN 사용자가 비밀번호를 입력하면 THEN 시스템은 bcrypt를 사용하여 안전하게 해시화하여 저장해야 합니다
5. WHEN 회원가입이 성공하면 THEN 시스템은 user_progress와 user_statistics 테이블에 기본 레코드를 생성해야 합니다

### Requirement 2

**User Story:** 기존 사용자로서, 내 계정으로 로그인하여 개인화된 학습을 이어갈 수 있기를 원합니다.

#### Acceptance Criteria

1. WHEN 사용자가 올바른 login_id와 password를 입력하면 THEN 시스템은 로그인을 허용하고 JWT 토큰을 발급해야 합니다
2. WHEN 사용자가 잘못된 인증 정보를 입력하면 THEN 시스템은 로그인을 거부하고 적절한 오류 메시지를 반환해야 합니다
3. WHEN 로그인이 성공하면 THEN 시스템은 기존 활성 토큰을 비활성화하고 새로운 refresh token을 생성해야 합니다
4. WHEN 로그인이 성공하면 THEN 시스템은 사용자의 기본 정보(user_id, username, user_type, diagnosis_completed)를 반환해야 합니다

### Requirement 3

**User Story:** 로그인한 사용자로서, 세션이 유지되어 매번 로그인하지 않고도 시스템을 사용할 수 있기를 원합니다.

#### Acceptance Criteria

1. WHEN 사용자가 유효한 JWT access token으로 API를 호출하면 THEN 시스템은 요청을 처리해야 합니다
2. WHEN access token이 만료되면 THEN 사용자는 refresh token을 사용하여 새로운 access token을 발급받을 수 있어야 합니다
3. WHEN refresh token이 유효하면 THEN 시스템은 새로운 access token과 refresh token을 발급해야 합니다
4. WHEN refresh token이 만료되거나 유효하지 않으면 THEN 시스템은 재로그인을 요구해야 합니다
5. WHEN 사용자가 로그아웃하면 THEN 시스템은 해당 사용자의 모든 활성 토큰을 비활성화해야 합니다

### Requirement 4

**User Story:** 시스템 관리자로서, 보안이 강화된 인증 시스템을 통해 사용자 데이터를 안전하게 보호하고 싶습니다.

#### Acceptance Criteria

1. WHEN 사용자가 동시에 여러 기기에서 로그인을 시도하면 THEN 시스템은 이전 세션을 자동으로 종료하고 새로운 세션만 유지해야 합니다
2. WHEN 비밀번호가 저장될 때 THEN 시스템은 bcrypt 해시를 사용하여 원본 비밀번호를 복구할 수 없도록 해야 합니다
3. WHEN JWT 토큰이 생성될 때 THEN 시스템은 적절한 만료 시간(access: 1시간, refresh: 30일)을 설정해야 합니다
4. WHEN 만료된 토큰이 정리될 때 THEN 시스템은 배치 작업을 통해 데이터베이스에서 자동으로 제거해야 합니다

### Requirement 5

**User Story:** API 개발자로서, 다른 기능들이 사용할 수 있는 일관된 인증 미들웨어를 제공받고 싶습니다.

#### Acceptance Criteria

1. WHEN 보호된 API 엔드포인트가 호출되면 THEN 인증 미들웨어는 JWT 토큰의 유효성을 자동으로 검증해야 합니다
2. WHEN 토큰이 유효하면 THEN 미들웨어는 사용자 정보를 request 객체에 추가하여 다음 핸들러로 전달해야 합니다
3. WHEN 토큰이 유효하지 않으면 THEN 미들웨어는 401 Unauthorized 응답을 반환해야 합니다
4. WHEN 인증이 필요한 라우트가 정의되면 THEN 데코레이터를 통해 쉽게 보호할 수 있어야 합니다

### Requirement 6

**User Story:** 프론트엔드 개발자로서, 사용자 인증 상태를 관리하고 자동으로 토큰을 갱신할 수 있는 클라이언트 시스템을 원합니다.

#### Acceptance Criteria

1. WHEN 사용자가 로그인하면 THEN 클라이언트는 토큰을 안전하게 저장하고 인증 상태를 업데이트해야 합니다
2. WHEN API 요청 시 access token이 만료되면 THEN 클라이언트는 자동으로 refresh token을 사용하여 토큰을 갱신해야 합니다
3. WHEN 토큰 갱신이 실패하면 THEN 클라이언트는 사용자를 로그인 페이지로 리다이렉트해야 합니다
4. WHEN 사용자가 로그아웃하면 THEN 클라이언트는 저장된 토큰을 제거하고 인증 상태를 초기화해야 합니다
5. WHEN 페이지가 새로고침되면 THEN 클라이언트는 저장된 토큰을 확인하여 인증 상태를 복원해야 합니다

### Requirement 7

**User Story:** 최종 사용자로서, 직관적이고 사용하기 쉬운 회원가입 및 로그인 페이지를 통해 시스템에 접근하고 싶습니다.

#### Acceptance Criteria

1. WHEN 사용자가 회원가입 페이지에 접근하면 THEN 시스템은 login_id, username, email, password 입력 필드가 있는 폼을 제공해야 합니다
2. WHEN 사용자가 회원가입 폼을 작성하면 THEN 시스템은 실시간으로 입력 유효성 검사(login_id 중복, 이메일 형식 등)를 수행해야 합니다
3. WHEN 회원가입이 성공하면 THEN 시스템은 성공 메시지를 표시하고 로그인 페이지로 이동해야 합니다
4. WHEN 사용자가 로그인 페이지에서 올바른 인증 정보를 입력하면 THEN 시스템은 대시보드 또는 진단 페이지로 리다이렉트해야 합니다
5. WHEN 로그인 실패 시 THEN 시스템은 명확한 오류 메시지를 표시하고 입력 필드를 초기화하지 않아야 합니다

### Requirement 8

**User Story:** 개발자로서, 인증 시스템의 모든 기능이 정상적으로 작동하는지 실제 페이지를 통해 테스트할 수 있기를 원합니다.

#### Acceptance Criteria

1. WHEN 개발자가 회원가입 페이지에서 새 계정을 생성하면 THEN 데이터베이스에 올바른 형태로 사용자 정보가 저장되어야 합니다
2. WHEN 개발자가 생성한 계정으로 로그인하면 THEN JWT 토큰이 발급되고 인증된 페이지에 접근할 수 있어야 합니다
3. WHEN 개발자가 브라우저를 새로고침하면 THEN 로그인 상태가 유지되어야 합니다
4. WHEN 개발자가 로그아웃하면 THEN 보호된 페이지에 접근할 수 없어야 합니다
5. WHEN 개발자가 토큰 만료 상황을 시뮬레이션하면 THEN 자동 토큰 갱신이 정상적으로 작동해야 합니다