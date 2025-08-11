# app/routes/auth/register.py

from flask import Blueprint, request, jsonify, make_response
from app.services.auth.register_service import register_user
from app.utils.common.exceptions import ValidationError, DuplicateError
from app.utils.response.formatter import success_response, error_response

# Blueprint 생성
register_bp = Blueprint('register', __name__)


@register_bp.route('/register', methods=['POST'])
def register():
    """
    회원가입 API
    
    Request Body:
        {
            "login_id": "user123",
            "username": "홍길동", 
            "email": "user@example.com",
            "password": "password123"
        }
    
    Returns:
        201: 회원가입 성공
        400: 입력값 검증 실패
        409: 중복 데이터 존재
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
        
        # 회원가입 처리
        result = register_user(data)
        
        # 회원가입 성공 시 토큰 발급
        from app.utils.auth.jwt_handler import generate_access_token, generate_refresh_token
        from app.services.auth.token_service import TokenService
        
        user_info = result['user_info']
        
        # JWT 토큰 생성
        access_token = generate_access_token({
            'user_id': user_info['user_id'],
            'login_id': user_info['login_id'],
            'user_type': user_info['user_type']
        })
        refresh_token = generate_refresh_token(user_info['user_id'])
        
        # 리프레시 토큰을 데이터베이스에 저장
        TokenService.save_refresh_token(
            user_id=user_info['user_id'],
            refresh_token=refresh_token,
            device_info=request.headers.get('User-Agent', 'Unknown')
        )
        
        response_data, status_code = success_response(
            data={
                "user_id": user_info['user_id'],
                "login_id": user_info['login_id'],
                "username": user_info['username'],
                "user_type": user_info['user_type'],
                "diagnosis_completed": user_info['diagnosis_completed'],
                "access_token": access_token
            },
            message=result['message'],
            status_code=201
        )

        # Response 객체 생성
        response = make_response(response_data, status_code)

        # HttpOnly 쿠키로 refresh_token 설정
        response.set_cookie(
            'refresh_token',
            refresh_token,
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
    
    except DuplicateError as e:
        return error_response(
            code="DUPLICATE_DATA",
            message=e.message,
            details=e.details,
            status_code=409
        )
    
    except Exception as e:
        # 로그 기록 (실제 운영환경에서는 로깅 시스템 사용)
        print(f"회원가입 오류: {str(e)}")
        
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )


@register_bp.route('/check-availability', methods=['POST'])
def check_availability():
    """
    로그인ID/이메일 사용 가능 여부 확인 API
    
    Request Body:
        {
            "login_id": "user123",    # 선택적
            "email": "user@example.com"  # 선택적
        }
    
    Returns:
        200: 확인 완료
        400: 잘못된 요청
    """
    try:
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
        
        login_id = data.get('login_id')
        email = data.get('email')
        
        if not login_id and not email:
            return error_response(
                code="MISSING_REQUIRED_FIELDS",
                message="login_id 또는 email 중 하나는 필수입니다.",
                status_code=400
            )
        
        from app.services.auth.register_service import RegisterService
        
        # 중복 검사 수행
        duplicates = RegisterService.check_duplicates(
            login_id or "", 
            email or ""
        )
        
        # 결과 구성
        availability = {}
        if login_id:
            availability['login_id'] = {
                'available': 'login_id' not in duplicates,
                'message': duplicates.get('login_id', '사용 가능한 로그인 ID입니다.')
            }
        
        if email:
            availability['email'] = {
                'available': 'email' not in duplicates,
                'message': duplicates.get('email', '사용 가능한 이메일입니다.')
            }
        
        return success_response(
            data=availability,
            message="사용 가능 여부 확인이 완료되었습니다."
        )
        
    except Exception as e:
        print(f"사용 가능 여부 확인 오류: {str(e)}")
        
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )