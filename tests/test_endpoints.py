import importlib
import sys

from fastapi.testclient import TestClient


def create_test_client(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("CHROMA_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("KB_DIR", str(tmp_path / "kb"))
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "100")
    (tmp_path / "kb").mkdir()

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name)

    main = importlib.import_module("app.main")
    main.app.state.kb_service.search = lambda _message: "VIP services include priority support."
    return TestClient(main.app)


def test_message_endpoint_returns_intent_and_reply(monkeypatch, tmp_path):
    client = create_test_client(monkeypatch, tmp_path)

    response = client.post(
        "/message",
        json={"user_id": "u1", "name": "Test User", "message": "What is VIP?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "vip_question"
    assert body["user_segment"] == "vip_interest"
    assert body["needs_human_support"] is False
    assert body["reply"]


def test_empty_message_is_rejected(monkeypatch, tmp_path):
    client = create_test_client(monkeypatch, tmp_path)

    response = client.post(
        "/message",
        json={"user_id": "u1", "name": "Test User", "message": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Message cannot be empty"
