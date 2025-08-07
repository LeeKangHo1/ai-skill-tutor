# backend/app/middleware/request/request_validator.py
"""
요청 검증 미들웨어 모듈
HTTP 요청의 유효성을 검증하고 필터링합니다.
"""

from functools import wraps
from flask import request, jsonify
from typing import Dict, Any, List, Optional, Callable
import json

class RequestValidator:
    """요청 검증 미들웨어 클래스"""
    
    def __init__(self):
        """요청 검증 미들웨어 초기화"""
        self.max_content_length = 10 * 1024 * 1024  # 10MB
        self.allowed_content_types = [
            'application/json',
            'application/x-www-form-urlencoded',
            'multipart/form-data'
        ]
    
    def validate_json(self, required_fields: Optional[List[str]] = None,
                     optional_fields: Optional[List[str]] = None):
        """
        JSON 요청 데이터를 검증하는 데코레이터입니다.
        
        Args:
            required_fields (Optional[List[str]]): 필수 필드 목록
            optional_fields (Optional[List[str]]): 선택적 필드 목록
            
        Returns:
            함수 데코레이터
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Content-Type 확인
                if not request.is_json:
                    return jsonify({
                        'success': False,
                        'message': 'Content-Type이 application/json이어야 합니다.'
                    }), 400
                
                # JSON 파싱 시도
                try:
                    data = request.get_json()
                except Exception:
                    return jsonify({
                        'success': False,
                        'message': '유효하지 않은 JSON 형식입니다.'
                    }), 400
                
                if data is None:
                    return jsonify({
                        'success': False,
                        'message': 'JSON 데이터가 필요합니다.'
                    }), 400
                
                # 필수 필드 확인
                if required_fields:
                    missing_fields = []
                    for field in required_fields:
                        if field not in data or data[field] is None:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        return jsonify({
                            'success': False,
                            'message': f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}'
                        }), 400
                
                # 허용되지 않은 필드 확인 (선택사항)
                if required_fields or optional_fields:
                    allowed_fields = set()
                    if required_fields:
                        allowed_fields.update(required_fields)
                    if optional_fields:
                        allowed_fields.update(optional_fields)
                    
                    extra_fields = set(data.keys()) - allowed_fields
                    if extra_fields:
                        return jsonify({
                            'success': False,
                            'message': f'허용되지 않은 필드입니다: {", ".join(extra_fields)}'
                        }), 400
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def validate_content_length(self, max_length: Optional[int] = None):
        """
        요청 크기를 검증하는 데코레이터입니다.
        
        Args:
            max_length (Optional[int]): 최대 허용 크기 (바이트)
            
        Returns:
            함수 데코레이터
        """
        actual_max_length = max_length or self.max_content_length
        
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                content_length = request.content_length
                
                if content_length and content_length > actual_max_length:
                    return jsonify({
                        'success': False,
                        'message': f'요청 크기가 너무 큽니다. 최대 {actual_max_length} 바이트까지 허용됩니다.'
                    }), 413
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def validate_query_params(self, required_params: Optional[List[str]] = None,
                            optional_params: Optional[List[str]] = None):
        """
        쿼리 파라미터를 검증하는 데코레이터입니다.
        
        Args:
            required_params (Optional[List[str]]): 필수 쿼리 파라미터 목록
            optional_params (Optional[List[str]]): 선택적 쿼리 파라미터 목록
            
        Returns:
            함수 데코레이터
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 필수 쿼리 파라미터 확인
                if required_params:
                    missing_params = []
                    for param in required_params:
                        if param not in request.args:
                            missing_params.append(param)
                    
                    if missing_params:
                        return jsonify({
                            'success': False,
                            'message': f'필수 쿼리 파라미터가 누락되었습니다: {", ".join(missing_params)}'
                        }), 400
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def validate_custom(self, validator_func: Callable[[Any], tuple]):
        """
        사용자 정의 검증 함수를 사용하는 데코레이터입니다.
        
        Args:
            validator_func (Callable): 검증 함수 (is_valid, error_message) 튜플 반환
            
        Returns:
            함수 데코레이터
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    is_valid, error_message = validator_func(request)
                    
                    if not is_valid:
                        return jsonify({
                            'success': False,
                            'message': error_message
                        }), 400
                    
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': f'요청 검증 중 오류가 발생했습니다: {str(e)}'
                    }), 500
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def sanitize_input(self, data: Any) -> Any:
        """
        입력 데이터를 정리합니다.
        
        Args:
            data (Any): 정리할 데이터
            
        Returns:
            Any: 정리된 데이터
        """
        if isinstance(data, str):
            # 기본적인 문자열 정리
            return data.strip()
        elif isinstance(data, dict):
            # 딕셔너리의 모든 값 재귀적으로 정리
            return {key: self.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            # 리스트의 모든 항목 재귀적으로 정리
            return [self.sanitize_input(item) for item in data]
        else:
            return data

# 전역 요청 검증 미들웨어 인스턴스
request_validator = RequestValidator()

# 편의를 위한 데코레이터 함수들
validate_json = request_validator.validate_json
validate_content_length = request_validator.validate_content_length
validate_query_params = request_validator.validate_query_params
validate_custom = request_validator.validate_custom