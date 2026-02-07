from fastapi.testclient import TestClient

from tuda.api import app, get_db, get_gmail_service
from tuda.storage import EncryptedDB


class StubGmailService:
    def list_messages(self, user_id: str = "me", max_results: int = 10):
        return [
            {
                "id": "m1",
                "snippet": "hello",
                "internalDate": "100",
                "headers": {"Subject": "Hi", "From": "sender@example.com"},
            }
        ]


def make_db(tmp_path):
    db = EncryptedDB(str(tmp_path / "test.db"), "test-key")
    db.init_schema()
    return db


def test_messages_and_analysis(tmp_path):
    db = make_db(tmp_path)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_gmail_service] = lambda: StubGmailService()

    client = TestClient(app)

    response = client.get("/messages?limit=1")
    assert response.status_code == 200
    assert response.json()[0]["id"] == "m1"

    analysis = client.get("/analysis/m1")
    assert analysis.status_code == 200
    assert "SpamDetector" in analysis.json()["analysis"]

    app.dependency_overrides.clear()


def test_message_not_found(tmp_path):
    db = make_db(tmp_path)
    app.dependency_overrides[get_db] = lambda: db

    client = TestClient(app)
    response = client.get("/analysis/missing")
    assert response.status_code == 404

    app.dependency_overrides.clear()
