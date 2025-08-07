# backend/tests/test_diagnosis.py

import json
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')  # config/testing.py를 사용하는 환경 가정
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_diagnosis_questions(client):
    """
    진단 문항 조회 API 테스트
    """
    response = client.get('/api/v1/diagnosis/questions')
    assert response.status_code == 200

    data = response.get_json()
    assert data['success'] is True
    assert 'questions' in data['data']
    assert isinstance(data['data']['questions'], list)

def test_submit_diagnosis(client, monkeypatch):
    """
    진단 제출 API 테스트
    """

    # 임의 사용자 반환하도록 monkeypatch 처리
    monkeypatch.setattr("app.utils.auth.jwt_handler.get_current_user", lambda: {
        "user_id": 1,
        "login_id": "test_user",
        "user_type": "unassigned",
        "diagnosis_completed": False
    })

    dummy_answers = {
        "answers": [
            {"question_id": 1, "answer": "option_2"},
            {"question_id": 2, "answer": "option_3"},
            {"question_id": 3, "answer": "option_4"},
            {"question_id": 4, "answer": "option_1"},
            {"question_id": 5, "answer": "option_2"}
        ]
    }

    response = client.post(
        '/api/v1/diagnosis/submit',
        data=json.dumps(dummy_answers),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'recommended_type' in data['data']

def test_select_user_type(client, monkeypatch):
    """
    사용자 유형 선택 API 테스트
    """

    # 사용자 인증 mock
    monkeypatch.setattr("app.utils.auth.jwt_handler.get_current_user", lambda: {
        "user_id": 1,
        "login_id": "test_user",
        "user_type": "unassigned",
        "diagnosis_completed": False
    })

    # DB 연결 dummy mock
    class DummyCursor:
        def __enter__(self):
            print("[DEBUG] DummyCursor.__enter__ 호출됨")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            print("[DEBUG] DummyCursor.__exit__ 호출됨")

        def execute(self, query, args):
            print(f"[DEBUG] DummyCursor.execute 호출됨: {query} {args}")


    class DummyConnection:
        def cursor(self):
            return DummyCursor()

        def commit(self):
            print("[DEBUG] DummyConnection.commit 호출됨")

        def rollback(self):
            print("[DEBUG] DummyConnection.rollback 호출됨")

        def close(self):
            print("[DEBUG] DummyConnection.close 호출됨")

    # 정확한 경로 monkeypatch 적용
    monkeypatch.setattr("app.routes.diagnosis.submit.get_db_connection", lambda: DummyConnection())


    response = client.post(
        '/api/v1/diagnosis/select-type',
        data=json.dumps({"selected_type": "beginner"}),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['recommended_type'] == 'beginner'

