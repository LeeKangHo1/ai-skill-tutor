# backend/app/utils/common/helpers.py
"""
헬퍼 함수들
자주 사용되는 유틸리티 함수들을 정의합니다.
"""

import uuid
from datetime import datetime


def generate_unique_id():
    """
    고유 ID 생성
    UUID4를 사용하여 고유한 ID를 생성합니다.
    """
    return str(uuid.uuid4())


def get_current_timestamp():
    """
    현재 타임스탬프 반환
    현재 시간을 ISO 형식으로 반환합니다.
    """
    return datetime.now().isoformat()


def safe_get(dictionary, key, default=None):
    """
    안전한 딕셔너리 값 조회
    키가 존재하지 않을 경우 기본값을 반환합니다.
    """
    return dictionary.get(key, default)


def truncate_text(text, max_length=100, suffix="..."):
    """
    텍스트 자르기
    지정된 길이를 초과하는 텍스트를 자릅니다.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_duration(seconds):
    """
    시간 포맷팅
    초 단위 시간을 읽기 쉬운 형태로 변환합니다.
    """
    if seconds < 60:
        return f"{seconds}초"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}분"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}시간 {minutes}분"


def clean_text(text):
    """
    텍스트 정제
    불필요한 공백과 특수문자를 제거합니다.
    향후 구현될 예정입니다.
    """
    pass