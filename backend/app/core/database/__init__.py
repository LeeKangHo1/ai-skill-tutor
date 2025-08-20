# backend/app/core/database/__init__.py
"""
⚠️ DEPRECATED - 이 모듈은 더 이상 사용되지 않습니다.
현재 프로젝트에서는 app.config.db_config 모듈을 사용합니다.

데이터베이스 관련 핵심 구성 요소 모듈
MySQL 클라이언트, 쿼리 빌더, 트랜잭션 관리자, 마이그레이션 실행기를 제공합니다.

⚠️ 사용 중단됨: 2025-08-20
대체 모듈: app.config.db_config
"""

# ⚠️ DEPRECATED - 사용하지 않음
# from .mysql_client import MySQLClient
# from .migration_runner import MigrationRunner
# from .query_builder import QueryBuilder, JSONQueryHelper
# from .transaction import TransactionManager, TransactionContext, BatchTransactionManager, with_transaction, execute_in_transaction

# __all__ = [
#     'MySQLClient', 
#     'MigrationRunner',
#     'QueryBuilder',
#     'JSONQueryHelper',
#     'TransactionManager',
#     'TransactionContext',
#     'BatchTransactionManager',
#     'with_transaction',
#     'execute_in_transaction'
# ]

# 현재 사용되는 데이터베이스 모듈로 리다이렉트
import warnings
warnings.warn(
    "app.core.database 모듈은 더 이상 사용되지 않습니다. "
    "app.config.db_config 모듈을 사용하세요.",
    DeprecationWarning,
    stacklevel=2
)

# 빈 __all__ 리스트로 export 방지
__all__ = []