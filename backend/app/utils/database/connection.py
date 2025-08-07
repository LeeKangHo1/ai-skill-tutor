# backend/app/utils/database/connection.py

"""
데이터베이스 연결 관리
MySQL 데이터베이스 연결을 관리하는 유틸리티입니다.
"""


class DatabaseConnection:
    """
    데이터베이스 연결 클래스
    MySQL 연결의 생성, 관리, 해제를 담당합니다.
    """

    def __init__(self, config=None):
        """데이터베이스 연결 초기화"""
        self.config = config
        self.connection = None

    def connect(self):
        """
        데이터베이스 연결 생성
        향후 구현될 예정입니다.
        """
        pass

    def disconnect(self):
        """
        데이터베이스 연결 해제
        향후 구현될 예정입니다.
        """
        pass

    def is_connected(self):
        """
        연결 상태 확인
        향후 구현될 예정입니다.
        """
        pass

    def reconnect(self):
        """
        연결 재시도
        향후 구현될 예정입니다.
        """
        pass


# ================================
# ✅ 임시용 get_db_connection 추가
# ================================
def get_db_connection():
    """
    [임시 함수] 실제 DB 연결 전까지 오류 방지용 dummy 함수
    """
    class DummyCursor:
        def execute(self, *args, **kwargs):
            print("[DEBUG] DummyCursor.execute 호출됨", args, kwargs)
        def fetchone(self):
            return {}
        def fetchall(self):
            return []
        def close(self):
            pass

    class DummyConnection:
        def cursor(self):
            return DummyCursor()
        def commit(self):
            print("[DEBUG] DummyConnection.commit 호출됨")
        def close(self):
            print("[DEBUG] DummyConnection.close 호출됨")

    return DummyConnection()
