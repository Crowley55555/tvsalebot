from fastapi.testclient import TestClient

from infrastructure.context import InMemoryContextStore
from infrastructure.llm.fake import FakeLLMClient


def test_stop_removes_consent_and_history(
    client: TestClient, store: InMemoryContextStore, fake_llm: FakeLLMClient
) -> None:
    client.post("/consent/grant", json={"telegram_id": 42})
    client.post("/chat", json={"telegram_id": 42, "text": "привет"})

    assert store._history.get("42") is not None  # noqa: SLF001
    assert 42 in store._consents  # noqa: SLF001

    r = client.post("/gdpr/stop", json={"telegram_id": 42, "reason": "user_stop"})

    assert r.status_code == 200
    body = r.json()
    assert body["deleted"] is True
    assert body["deleted_keys"] == 2
    assert body["reason"] == "user_stop"
    assert "42" not in store._history  # noqa: SLF001
    assert 42 not in store._consents  # noqa: SLF001


def test_stop_is_idempotent_when_nothing_to_delete(client: TestClient) -> None:
    r = client.post("/gdpr/stop", json={"telegram_id": 999, "reason": "user_stop"})
    assert r.status_code == 200
    body = r.json()
    assert body["deleted"] is True
    assert body["deleted_keys"] == 0


def test_stop_logs_the_fact(
    client: TestClient, store: InMemoryContextStore
) -> None:
    client.post("/gdpr/stop", json={"telegram_id": 42, "reason": "user_delete"})

    assert len(store._deletion_log) == 1  # noqa: SLF001
    entry = store._deletion_log[0]  # noqa: SLF001
    assert entry["telegram_id"] == 42
    assert entry["reason"] == "user_delete"
    assert entry["ts"] > 0


def test_chat_blocked_again_after_stop(
    client: TestClient, fake_llm: FakeLLMClient
) -> None:
    client.post("/consent/grant", json={"telegram_id": 42})
    client.post("/gdpr/stop", json={"telegram_id": 42})

    r = client.post("/chat", json={"telegram_id": 42, "text": "ещё"})

    assert r.status_code == 409
    assert r.json()["error"] == "consent_required"
