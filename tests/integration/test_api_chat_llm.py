from fastapi.testclient import TestClient

from infrastructure.llm.fake import FakeLLMClient


def _grant(client: TestClient, tg_id: int) -> None:
    assert client.post("/consent/grant", json={"telegram_id": tg_id}).status_code == 200


def test_single_message_returns_llm_reply(client: TestClient, fake_llm: FakeLLMClient) -> None:
    _grant(client, 42)

    r = client.post("/chat", json={"telegram_id": 42, "text": "привет"})

    assert r.status_code == 200
    assert r.json() == {"reply": "test-reply"}
    assert len(fake_llm.calls) == 1
    call = fake_llm.calls[0]
    assert "Samsung" in call["system_prompt"]
    assert len(call["history"]) == 1
    assert call["history"][0].role == "user"
    assert call["history"][0].text == "привет"


def test_history_grows_and_is_passed_to_llm(
    client: TestClient, fake_llm: FakeLLMClient
) -> None:
    _grant(client, 7)

    fake_llm.programmed_reply = "ответ-1"
    client.post("/chat", json={"telegram_id": 7, "text": "первое"})
    fake_llm.programmed_reply = "ответ-2"
    client.post("/chat", json={"telegram_id": 7, "text": "второе"})
    fake_llm.programmed_reply = "ответ-3"
    r3 = client.post("/chat", json={"telegram_id": 7, "text": "третье"})

    assert r3.json() == {"reply": "ответ-3"}
    third = fake_llm.calls[2]
    assert len(third["history"]) == 5
    assert [m.role for m in third["history"]] == [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
    ]
    assert [m.text for m in third["history"]] == [
        "первое",
        "ответ-1",
        "второе",
        "ответ-2",
        "третье",
    ]


def test_duplicate_update_id_is_deduped(client: TestClient, fake_llm: FakeLLMClient) -> None:
    _grant(client, 77)
    payload = {"telegram_id": 77, "text": "привет", "update_id": 1001}

    r1 = client.post("/chat", json=payload)
    r2 = client.post("/chat", json=payload)

    assert r1.json() == {"reply": "test-reply"}
    assert r2.json() == {"reply": ""}
    assert len(fake_llm.calls) == 1


def test_separate_users_have_separate_histories(
    client: TestClient, fake_llm: FakeLLMClient
) -> None:
    _grant(client, 1)
    _grant(client, 2)

    client.post("/chat", json={"telegram_id": 1, "text": "а"})
    client.post("/chat", json={"telegram_id": 2, "text": "б"})
    client.post("/chat", json={"telegram_id": 1, "text": "а2"})

    assert len(fake_llm.calls) == 3
    first_user1 = fake_llm.calls[0]
    second_user1 = fake_llm.calls[2]
    assert [m.text for m in first_user1["history"]] == ["а"]
    assert [m.text for m in second_user1["history"]] == ["а", "test-reply", "а2"]


def test_catalog_is_included_in_system_prompt(
    client: TestClient, fake_llm: FakeLLMClient
) -> None:
    _grant(client, 100)

    client.post("/chat", json={"telegram_id": 100, "text": "посоветуй тв"})

    assert len(fake_llm.calls) == 1
    system_prompt = fake_llm.calls[0]["system_prompt"]
    # базовый system-prompt остаётся
    assert "Samsung" in system_prompt
    # и к нему прилеплен тестовый каталог
    assert "TEST-A" in system_prompt
    assert "Test Alpha" in system_prompt
