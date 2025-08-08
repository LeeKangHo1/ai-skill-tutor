# app/utils/auth/password_handler.py

import bcrypt


class PasswordHandler:
    """비밀번호 암호화 및 검증을 담당하는 클래스"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        비밀번호를 bcrypt로 해시화
        
        Args:
            password (str): 평문 비밀번호
            
        Returns:
            str: 해시화된 비밀번호
        """
        # 비밀번호를 바이트로 인코딩
        password_bytes = password.encode('utf-8')
        
        # bcrypt로 해시화 (salt 자동 생성)
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        
        # 문자열로 디코딩하여 반환
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        비밀번호 검증
        
        Args:
            password (str): 검증할 평문 비밀번호
            hashed_password (str): 저장된 해시 비밀번호
            
        Returns:
            bool: 비밀번호 일치 여부
        """
        try:
            # 비밀번호를 바이트로 인코딩
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            
            # bcrypt로 비밀번호 검증
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            # 해시 형식이 잘못되었거나 기타 오류 시 False 반환
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list[str]]:
        """
        비밀번호 강도 검증
        
        Args:
            password (str): 검증할 비밀번호
            
        Returns:
            tuple[bool, list[str]]: (유효성 여부, 오류 메시지 리스트)
        """
        errors = []
        
        # 길이 검증 (8자 이상)
        if len(password) < 8:
            errors.append("비밀번호는 8자 이상이어야 합니다.")
        
        # 최대 길이 검증 (50자 이하)
        if len(password) > 50:
            errors.append("비밀번호는 50자 이하여야 합니다.")
        
        # 영문자 포함 검증
        if not any(c.isalpha() for c in password):
            errors.append("비밀번호에 영문자가 포함되어야 합니다.")
        
        # 숫자 포함 검증
        if not any(c.isdigit() for c in password):
            errors.append("비밀번호에 숫자가 포함되어야 합니다.")
        
        # 공백 검증
        if ' ' in password:
            errors.append("비밀번호에 공백을 포함할 수 없습니다.")
        
        return len(errors) == 0, errors


# 편의를 위한 함수 형태 인터페이스
def hash_password(password: str) -> str:
    """비밀번호 해시화 편의 함수"""
    return PasswordHandler.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """비밀번호 검증 편의 함수"""
    return PasswordHandler.verify_password(password, hashed_password)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """비밀번호 강도 검증 편의 함수"""
    return PasswordHandler.validate_password_strength(password)