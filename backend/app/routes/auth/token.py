# app/routes/auth/token.py

from flask import Blueprint, request, jsonify
from app.services.auth.token_service import refresh_access_token, TokenService
from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
from app.utils.common.exceptions import AuthenticationError
from app.utils.response.formatter import success_response, error_response

# Blueprint 생성
token_bp = Blueprint('token', __name__)


@token_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    토큰 갱신 API
    
    Request Body:
        {
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Returns:
        200: 토큰 갱신 성공
        400: 잘못된 요청
        401: 토큰 검증 실패
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
        
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return error_response(
                code="MISSING_REFRESH_TOKEN",
                message="refresh_token이 필요합니다.",
                status_code=400
            )
        
        # 토큰 갱신 처리
        result = refresh_access_token(refresh_token)
        
        return success_response(
            data={
                "access_token": result['access_token'],
                "refresh_token": result['refresh_token'],
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
        
    except AuthenticationError as e:
        return error_response(
            code="AUTH_REFRESH_TOKEN_INVALID",
            message=e.message,
            status_code=401
        )
    
    except Exception as e:
        print(f"토큰 갱신 오류: {str(e)}")
        
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )


@token_bp.route('/verify', methods=['POST'])
def verify():
    """
    토큰 검증 API
    
    Request Body:
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Returns:
        200: 토큰 유효함
        400: 잘못된 요청
        401: 토큰 무효함
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
        
        access_token = data.get('access_token')
        if not access_token:
            return error_response(
                code="MISSING_ACCESS_TOKEN",
                message="access_token이 필요합니다.",
                status_code=400
            )
        
        # 토큰 검증
        user_info = TokenService.verify_access_token(access_token)
        
        if not user_info:
            return error_response(
                code="AUTH_TOKEN_INVALID",
                message="유효하지 않은 토큰입니다.",
                status_code=401
            )
        
        return success_response(
            data={
                "valid": True,
                "user_info": user_info
            },
            message="토큰이 유효합니다."
        )
        
    except Exception as e:
        print(f"토큰 검증 오류: {str(e)}")
        
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )


@token_bp.route('/sessions', methods=['GET'])
@require_auth
def get_sessions():
    """
    활성 세션 목록 조회 API
    
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
        
        # 활성 세션 조회
        result = TokenService.get_active_sessions(current_user['user_id'])
        
        # 응답 데이터 포맷팅
        sessions = []
        for session in result['data']['active_sessions']:
            sessions.append({
                "token_id": session['token_id'],
                "device_info": session['device_info'],
                "created_at": session['created_at'].isoformat() if session['created_at'] else None,
                "expires_at": session['expires_at'].isoformat() if session['expires_at'] else None
            })
        
        return success_response(
            data={
                "active_sessions": sessions,
                "total_count": result['data']['total_count']
            },
            message="활성 세션 목록 조회가 완료되었습니다."
        )
        
    except Exception as e:
        print(f"세션 목록 조회 오류: {str(e)}")
        
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )


@token_bp.route('/revoke/<int:token_id>', methods=['DELETE'])
@require_auth
def revoke_session(token_id):
    """
    특정 세션 무효화 API
    
    Headers:
        Authorization: Bearer {access_token}
    
    Path Parameters:
        token_id (int): 무효화할 토큰 ID
    
    Returns:
        200: 무효화 성공
        401: 인증 실패
        403: 권한 없음
        404: 세션 없음
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
        
        from app.utils.database.connection import fetch_one
        
        # 해당 토큰이 현재 사용자의 것인지 확인
        token_data = fetch_one(
            "SELECT user_id FROM user_auth_tokens WHERE token_id = %s AND is_active = TRUE",
            (token_id,)
        )
        
        if not token_data:
            return error_response(
                code="SESSION_NOT_FOUND",
                message="해당 세션을 찾을 수 없습니다.",
                status_code=404
            )
        
        if token_data['user_id'] != current_user['user_id']:
            return error_response(
                code="ACCESS_DENIED",
                message="해당 세션에 접근할 권한이 없습니다.",
                status_code=403
            )
        
        # 토큰 무효화
        TokenService.deactivate_token(token_id)
        
        return success_response(
            data=None,
            message="세션이 무효화되었습니다."
        )
        
    except Exception as e:
        print(f"세션 무효화 오류: {str(e)}")
        
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )