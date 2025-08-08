# app/services/auth/register_service.py

import re
from typing import Dict, Any, Tuple
from datetime import datetime

from app.utils.database.connection import fetch_one, execute_query
from app.utils.database.transaction import execute_transaction
from app.utils.auth.password_handler import hash_password, validate_password_strength
from app.utils.common.exceptions import ValidationError, DuplicateError


class RegisterService:
    """회원가입 관련 비즈니스 로직을 처리하는 서비스"""
    
    @staticmethod
    def validate_registration_data(data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        회원가입 데이터 검증
        
        Args:
            data (dict): 회원가입 데이터
                - login_id: 로그인 ID
                - username: 사용자명
                - email: 이메일
                - password: 비밀번호
                
        Returns:
            tuple: (유효성 여부, 에러 정보 또는 정제된 데이터)
        """
        errors = {}
        
        # 필수 필드 검증
        required_fields = ['login_id', 'username', 'email', 'password']
        for field in required_fields:
            if not data.get(field) or not str(data[field]).strip():
                errors[field] = f"{field}은(는) 필수 입력 항목입니다."
        
        if errors:
            return False, {'field_errors': errors}
        
        # 개별 필드 검증
        login_id = str(data['login_id']).strip()
        username = str(data['username']).strip()
        email = str(data['email']).strip()
        password = str(data['password'])
        
        # 로그인 ID 검증 (4-20자, 영문+숫자+언더스코어)
        if not re.match(r'^[a-zA-Z0-9_]{4,20}$', login_id):
            errors['login_id'] = "로그인 ID는 4-20자의 영문, 숫자, 언더스코어만 사용 가능합니다."
        
        # 사용자명 검증 (2-50자)
        if len(username) < 2 or len(username) > 50:
            errors['username'] = "사용자명은 2-50자여야 합니다."
        
        # 이메일 검증
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors['email'] = "올바른 이메일 형식이 아닙니다."
        
        # 비밀번호 강도 검증
        is_strong, password_errors = validate_password_strength(password)
        if not is_strong:
            errors['password'] = password_errors
        
        if errors:
            return False, {'field_errors': errors}
        
        return True, {
            'login_id': login_id,
            'username': username,
            'email': email.lower(),  # 이메일은 소문자로 저장
            'password': password
        }
    
    @staticmethod
    def check_duplicates(login_id: str, email: str) -> Dict[str, str]:
        """
        로그인 ID와 이메일 중복 검사
        
        Args:
            login_id (str): 로그인 ID
            email (str): 이메일
            
        Returns:
            dict: 중복 필드별 에러 메시지
        """
        errors = {}
        
        # 로그인 ID 중복 검사
        existing_user = fetch_one(
            "SELECT user_id FROM users WHERE login_id = %s",
            (login_id,)
        )
        if existing_user:
            errors['login_id'] = "이미 사용 중인 로그인 ID입니다."
        
        # 이메일 중복 검사
        existing_email = fetch_one(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )
        if existing_email:
            errors['email'] = "이미 사용 중인 이메일입니다."
        
        return errors
    
    @staticmethod
    def create_user(validated_data: Dict[str, str]) -> Dict[str, Any]:
        """
        사용자 계정 생성 (트랜잭션으로 처리)
        
        Args:
            validated_data (dict): 검증된 사용자 데이터
            
        Returns:
            dict: 생성된 사용자 정보
            
        Raises:
            Exception: 사용자 생성 실패 시
        """
        # 비밀번호 해시화
        hashed_password = hash_password(validated_data['password'])
        
        # 트랜잭션으로 사용자 생성
        from app.utils.database.connection import get_db_connection
        
        with get_db_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    # 1. users 테이블에 기본 정보 삽입
                    cursor.execute(
                        """
                        INSERT INTO users (login_id, username, email, password_hash, user_type, diagnosis_completed)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            validated_data['login_id'],
                            validated_data['username'], 
                            validated_data['email'],
                            hashed_password,
                            'unassigned',  # 기본값
                            False  # 진단 미완료
                        )
                    )
                    user_id = cursor.lastrowid
                    
                    # 2. user_progress 테이블 초기화
                    cursor.execute(
                        "INSERT INTO user_progress (user_id, current_chapter) VALUES (%s, %s)",
                        (user_id, 1)  # 1챕터부터 시작
                    )
                    
                    # 3. user_statistics 테이블 초기화
                    cursor.execute(
                        "INSERT INTO user_statistics (user_id) VALUES (%s)",
                        (user_id,)
                    )
                    
                    # 트랜잭션 커밋
                    connection.commit()
                    
            except Exception as e:
                # 트랜잭션 롤백
                connection.rollback()
                raise e
        
        # 생성된 사용자 정보 반환
        return {
            'user_id': user_id,
            'login_id': validated_data['login_id'],
            'username': validated_data['username'],
            'email': validated_data['email'],
            'user_type': 'unassigned',
            'diagnosis_completed': False,
            'current_chapter': 1,
            'created_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def register_user(registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        회원가입 전체 프로세스 처리
        
        Args:
            registration_data (dict): 회원가입 요청 데이터
            
        Returns:
            dict: 회원가입 결과
            
        Raises:
            ValidationError: 입력값 검증 실패
            DuplicateError: 중복 데이터 존재
        """
        # 1. 입력값 검증
        is_valid, validation_result = RegisterService.validate_registration_data(registration_data)
        if not is_valid:
            raise ValidationError("입력값이 올바르지 않습니다.", validation_result)
        
        validated_data = validation_result
        
        # 2. 중복 검사
        duplicate_errors = RegisterService.check_duplicates(
            validated_data['login_id'], 
            validated_data['email']
        )
        if duplicate_errors:
            raise DuplicateError("중복된 정보가 있습니다.", {'field_errors': duplicate_errors})
        
        # 3. 사용자 생성
        try:
            user_info = RegisterService.create_user(validated_data)
            return {
                'success': True,
                'user_info': user_info,
                'message': '회원가입이 완료되었습니다.'
            }
        except Exception as e:
            raise Exception(f"사용자 생성 중 오류가 발생했습니다: {str(e)}")


# 편의를 위한 함수 형태 인터페이스
def register_user(registration_data: Dict[str, Any]) -> Dict[str, Any]:
    """회원가입 처리 편의 함수"""
    return RegisterService.register_user(registration_data)