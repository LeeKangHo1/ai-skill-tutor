# backend/app/core/__init__.py
"""
핵심 시스템 구성 요소 모듈
LangGraph, 외부 서비스 연동 등 핵심 기능을 제공합니다.

⚠️ 데이터베이스 모듈은 더 이상 여기서 export하지 않습니다.
현재는 app.config.db_config와 app.utils.database를 사용하세요.
"""

from .langraph import StateManager, WorkflowExecutor, TutorGraphBuilder
# ⚠️ DEPRECATED - 데이터베이스 모듈은 더 이상 export하지 않음
# from .database import MySQLClient, MigrationRunner
from .external import VectorDBClient

__all__ = [
    'StateManager', 'WorkflowExecutor', 'TutorGraphBuilder',
    # 'MySQLClient', 'MigrationRunner',  # ⚠️ DEPRECATED
    'VectorDBClient',
]