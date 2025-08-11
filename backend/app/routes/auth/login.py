# app/routes/auth/login.py

from flask import Blueprint, request, jsonify
from app.services.auth.login_service import login_user
from app.services.auth.token_service import logout_user
from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
from app.utils.common.exceptions import ValidationError, AuthenticationError
from app.utils.response.formatter import success_response, error_response

# Blueprint 생성
login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['POST'])
def login():
    """
    로그인 API
    
    Request Body:
        {
            "login_id": "user123",
            "password": "password123"
        }
    
    Returns:
        200: 로그인 성공
        400: 입력값 검증 실패
        401: 인증 실패
        500: 서버 오류
    """
    try:
        # 요청 데이터 검증
        if not request.is_json:
            return error_response(
                code="INVALID_CONTENT_TYPE",
                message="Content-Type은 application/json이어야 합니다.",
                status_code=400
            )
        
        data = request.get_json()
        if not data:
            return error_response(
                code="EMPTY_REQUEST_BODY",
                message="요청 본문이 비어있습니다.",
                status_code=400
            )
        
        # 디바이스 정보 추출 (User-Agent)
        device_info = request.headers.get('User-Agent', 'Unknown Device')[:255]
        
        # 로그인 처리
        result = login_user(data, device_info)
        
        response = success_response(
            data={
                "access_token": result['access_token'],
                "user_info": {
                    "user_id": result['user_info']['user_id'],
                    "login_id": result['user_info']['login_id'],
                    "username": result['user_info']['username'],
                    "user_type": result['user_info']['user_type'],
                    "diagnosis_completed": result['user_info']['diagnosis_completed'],
                    "current_chapter": result['user_info']['current_chapter']
                }
            },
            message=result['message']
        )

        # HttpOnly 쿠키로 refresh_token 설정
        response.set_cookie(
            'refresh_token',
            result['refresh_token'],
            max_age=30*24*60*60,  # 30일
            httponly=True,
            secure=True,  # HTTPS에서만
            samesite='Strict'
        )

        return response
        
    except ValidationError as e:
        return error_response(
            code="VALIDATION_ERROR",
            message=e.message,
            details=e.details,
            status_code=400
        )
    
    except AuthenticationError as e:
        return error_response(
            code="AUTH_INVALID_CREDENTIALS",
            message=e.message,
            status_code=401
        )
    
    except Exception as e:
        print(f"로그인 오류: {str(e)}")
        
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )


@login_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    로그아웃 API
    
    Headers:
        Authorization: Bearer {access_token}
    
    Request Body:
        {
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Returns:
        200: 로그아웃 성공
        400: 잘못된 요청
        401: 인증 실패
        500: 서버 오류
    """
    try:
        # 현재 사용자 정보 확인
        current_user = get_current_user_from_request()
        if not current_user:
            return error_response(
                code="AUTH_TOKEN_INVALID",
                message="유효하지 않은 토큰입니다.",
                status_code=401
            )
        
        # 쿠키에서 refresh_token 읽기
        refresh_token = request.cookies.get('refresh_token')

        if not refresh_token:
            return error_response(
                code="MISSING_REFRESH_TOKEN",
                message="refresh_token 쿠키가 필요합니다.",
                status_code=400
            )
        
        # 로그아웃 처리
        result = logout_user(refresh_token)
        
        response = success_response(
            data=None,
            message=result['message']
        )

        # refresh_token 쿠키 삭제
        response.set_cookie(
            'refresh_token',
            '',
            expires=0,
            httponly=True,
            secure=True,
            samesite='Strict'
        )

        return response
        
    except Exception as e:
        print(f"로그아웃 오류: {str(e)}")
        
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )


@login_bp.route('/logout-all', methods=['POST'])
@require_auth
def logout_all():
    """
    모든 디바이스에서 로그아웃 API
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        200: 로그아웃 성공
        401: 인증 실패
        500: 서버 오류
    """
    try:
        # 현재 사용자 정보 확인
        current_user = get_current_user_from_request()
        if not current_user:
            return error_response(
                code="AUTH_TOKEN_INVALID",
                message="유효하지 않은 토큰입니다.",
                status_code=401
            )
        
        from app.services.auth.token_service import TokenService
        
        # 모든 디바이스에서 로그아웃
        result = TokenService.logout_all_devices(current_user['user_id'])
        
        response = success_response(
            data=None,
            message=result['message']
        )

        # refresh_token 쿠키 삭제
        response.set_cookie(
            'refresh_token',
            '',
            expires=0,
            httponly=True,
            secure=True,
            samesite='Strict'
        )

        return response
        
    except Exception as e:
        print(f"전체 로그아웃 오류: {str(e)}")
        
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )


@login_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    현재 사용자 정보 조회 API
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        200: 조회 성공
        401: 인증 실패
        500: 서버 오류
    """
    try:
        # 현재 사용자 정보 확인
        current_user = get_current_user_from_request()
        if not current_user:
            return error_response(
                code="AUTH_TOKEN_INVALID",
                message="유효하지 않은 토큰입니다.",
                status_code=401
            )
        
        # 최신 사용자 정보 조회 (DB에서)
        from app.utils.database.connection import fetch_one
        
        user_data = fetch_one(
            """
            SELECT 
                u.user_id, u.login_id, u.username, u.email,
                u.user_type, u.diagnosis_completed, u.created_at,
                up.current_chapter
            FROM users u
            LEFT JOIN user_progress up ON u.user_id = up.user_id
            WHERE u.user_id = %s
            """,
            (current_user['user_id'],)
        )
        
        if not user_data:
            return error_response(
                code="USER_NOT_FOUND",
                message="사용자를 찾을 수 없습니다.",
                status_code=404
            )
        
        return success_response(
            data={
                "user_id": user_data['user_id'],
                "login_id": user_data['login_id'],
                "username": user_data['username'],
                "email": user_data['email'],
                "user_type": user_data['user_type'],
                "diagnosis_completed": bool(user_data['diagnosis_completed']),
                "current_chapter": user_data['current_chapter'] or 1,
                "created_at": user_data['created_at'].isoformat() if user_data['created_at'] else None
            },
            message="사용자 정보 조회가 완료되었습니다."
        )
        
    except Exception as e:
        print(f"사용자 정보 조회 오류: {str(e)}")
        
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )