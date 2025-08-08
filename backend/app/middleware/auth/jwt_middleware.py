# app/middleware/auth/jwt_middleware.py

from functools import wraps
from flask import request, jsonify, g, current_app
from app.utils.auth.jwt_handler import extract_user_from_token
from app.utils.database.connection import fetch_one
from app.utils.response.formatter import error_response


class JWTMiddleware:
    """JWT 토큰 검증 및 사용자 정보 관리 미들웨어"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 미들웨어 초기화"""
        app.before_request(self.load_user_from_token)
    
    def load_user_from_token(self):
        """
        요청 헤더에서 JWT 토큰을 추출하고 사용자 정보를 g 객체에 저장
        모든 요청에 대해 실행되지만, 토큰이 없어도 에러를 발생시키지 않음
        """
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')
        
        # 기본값 설정
        g.current_user = None
        g.current_user_id = None
        g.is_authenticated = False
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return  # 토큰이 없으면 그냥 진행 (인증이 필요한 라우트에서 별도 처리)
        
        try:
            # Bearer 토큰 추출
            token = auth_header.split(' ')[1]
            
            # 토큰에서 사용자 정보 추출
            user_info = extract_user_from_token(token)
            
            if user_info and user_info.get('user_id'):
                # 데이터베이스에서 최신 사용자 정보 확인
                db_user = self.get_user_from_db(user_info['user_id'])
                
                if db_user:
                    # g 객체에 사용자 정보 저장
                    g.current_user = {
                        'user_id': db_user['user_id'],
                        'login_id': db_user['login_id'],
                        'username': db_user['username'],
                        'user_type': db_user['user_type'],
                        'diagnosis_completed': bool(db_user['diagnosis_completed']),
                        'current_chapter': db_user['current_chapter'] or 1
                    }
                    g.current_user_id = db_user['user_id']
                    g.is_authenticated = True
                    
                    # 로깅을 위한 사용자 ID 저장
                    current_app.logger.debug(f"Authenticated user: {db_user['login_id']}")
        
        except Exception as e:
            # 토큰 파싱 오류 시 로그 기록하고 인증되지 않은 상태로 진행
            current_app.logger.warning(f"JWT 토큰 처리 오류: {str(e)}")
    
    def get_user_from_db(self, user_id):
        """
        데이터베이스에서 사용자 정보 조회
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            dict | None: 사용자 정보 또는 None
        """
        try:
            user_data = fetch_one(
                """
                SELECT 
                    u.user_id, u.login_id, u.username, u.user_type, 
                    u.diagnosis_completed, up.current_chapter
                FROM users u
                LEFT JOIN user_progress up ON u.user_id = up.user_id
                WHERE u.user_id = %s
                """,
                (user_id,)
            )
            return user_data
        except Exception as e:
            current_app.logger.error(f"사용자 정보 조회 오류: {str(e)}")
            return None


def require_auth(f):
    """
    인증이 필요한 라우트에 사용하는 데코레이터
    
    Usage:
        @require_auth
        def protected_route():
            current_user = g.current_user
            # ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('is_authenticated', False):
            return error_response(
                code="AUTH_TOKEN_REQUIRED",
                message="인증이 필요합니다.",
                status_code=401
            )
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_user_type(*allowed_types):
    """
    특정 사용자 유형만 접근 가능한 라우트에 사용하는 데코레이터
    
    Args:
        allowed_types: 허용할 사용자 유형들 ('beginner', 'advanced', 'unassigned')
    
    Usage:
        @require_user_type('beginner', 'advanced')
        def user_type_specific_route():
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('is_authenticated', False):
                return error_response(
                    code="AUTH_TOKEN_REQUIRED",
                    message="인증이 필요합니다.",
                    status_code=401
                )
            
            current_user = g.get('current_user')
            if not current_user or current_user['user_type'] not in allowed_types:
                return error_response(
                    code="ACCESS_DENIED",
                    message="접근 권한이 없습니다.",
                    details={'required_user_types': list(allowed_types)},
                    status_code=403
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_diagnosis_completed(f):
    """
    진단 완료가 필요한 라우트에 사용하는 데코레이터
    
    Usage:
        @require_diagnosis_completed
        def diagnosis_required_route():
            # ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('is_authenticated', False):
            return error_response(
                code="AUTH_TOKEN_REQUIRED",
                message="인증이 필요합니다.",
                status_code=401
            )
        
        current_user = g.get('current_user')
        if not current_user or not current_user['diagnosis_completed']:
            return error_response(
                code="DIAGNOSIS_NOT_COMPLETED",
                message="진단을 먼저 완료해주세요.",
                details={'redirect_url': '/diagnosis'},
                status_code=403
            )
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    """
    선택적 인증이 필요한 라우트에 사용하는 데코레이터
    인증된 사용자는 추가 정보를 볼 수 있지만, 인증되지 않아도 접근 가능
    
    Usage:
        @optional_auth
        def optional_auth_route():
            if g.is_authenticated:
                # 인증된 사용자용 로직
            else:
                # 비인증 사용자용 로직
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 인증 상태와 관계없이 실행
        return f(*args, **kwargs)
    
    return decorated_function


# 편의를 위한 헬퍼 함수들
def get_current_user():
    """현재 인증된 사용자 정보 반환"""
    return g.get('current_user')


def get_current_user_id():
    """현재 인증된 사용자 ID 반환"""
    return g.get('current_user_id')


def is_authenticated():
    """현재 요청이 인증되었는지 여부 반환"""
    return g.get('is_authenticated', False)


def check_permission(required_user_type=None, require_diagnosis=False):
    """
    권한 확인 헬퍼 함수
    
    Args:
        required_user_type (str, optional): 필요한 사용자 유형
        require_diagnosis (bool): 진단 완료 필요 여부
        
    Returns:
        tuple: (권한 있음 여부, 에러 응답 또는 None)
    """
    if not is_authenticated():
        return False, error_response(
            code="AUTH_TOKEN_REQUIRED",
            message="인증이 필요합니다.",
            status_code=401
        )
    
    current_user = get_current_user()
    
    if required_user_type and current_user['user_type'] != required_user_type:
        return False, error_response(
            code="ACCESS_DENIED", 
            message="접근 권한이 없습니다.",
            status_code=403
        )
    
    if require_diagnosis and not current_user['diagnosis_completed']:
        return False, error_response(
            code="DIAGNOSIS_NOT_COMPLETED",
            message="진단을 먼저 완료해주세요.",
            status_code=403
        )
    
    return True, None