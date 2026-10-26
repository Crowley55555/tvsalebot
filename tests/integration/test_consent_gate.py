from fastapi.testclient import TestClient

from infrastructure.llm.fake import FakeLLMClient


def test_chat_blocked_without_consent(client: TestClient, fake_llm: FakeLLMClient) -> None:
    r = client.post("/chat", json={"telegram_id": 42, "text": "привет"})

    assert r.status_code == 409
    body = r.json()
    assert body["error"] == "consent_required"
    assert body["policy_url"].startswith("https://")
    assert "/start" in body["user_message"]
    assert len(fake_llm.calls) == 0


def test_grant_then_chat_works(client: TestClient, fake_llm: FakeLLMClient) -> None:
    g = client.post("/consent/grant", json={"telegram_id": 42})
    assert g.status_code == 200
    assert g.json() == {"granted": True, "policy_version": "test-v1"}

    r = client.post("/chat", json={"telegram_id": 42, "text": "привет"})

    assert r.status_code == 200
    assert r.json() == {"reply": "test-reply"}
    assert len(fake_llm.calls) == 1


def test_grant_is_idempotent(client: TestClient) -> None:
    r1 = client.post("/consent/grant", json={"telegram_id": 42})
    r2 = client.post("/consent/grant", json={"telegram_id": 42})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()


def test_separate_users_consent_isolated(
    client: TestClient, fake_llm: FakeLLMClient
) -> None:
    client.post("/consent/grant", json={"telegram_id": 1})
    r_ok = client.post("/chat", json={"telegram_id": 1, "text": "a"})
    r_blocked = client.post("/chat", json={"telegram_id": 2, "text": "b"})

    assert r_ok.status_code == 200
    assert r_blocked.status_code == 409
    assert len(fake_llm.calls) == 1
