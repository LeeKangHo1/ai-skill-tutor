# backend/app/routes/__init__.py
# API 라우트 모듈 초기화 파일

# 시스템 관련 Blueprint 리스트 import
from .system import system_blueprints

# 진단 관련 Blueprint 리스트 import  
from .diagnosis import diagnosis_blueprints

# 대시보드 관련 Blueprint 리스트 import
from .dashboard import dashboard_blueprints

# 외부에서 사용할 Blueprint 리스트들 노출
__all__ = ['system_blueprints', 'diagnosis_blueprints', 'dashboard_blueprints']