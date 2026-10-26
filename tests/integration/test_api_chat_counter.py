from fastapi.testclient import TestClient


def test_three_messages_counter_increments(client: TestClient) -> None:
    """Главный путь: три сообщения — 1-я / 2-я / 3-я реплика."""
    tg_id = 42

    r1 = client.post("/chat", json={"telegram_id": tg_id, "text": "привет"})
    r2 = client.post("/chat", json={"telegram_id": tg_id, "text": "тест"})
    r3 = client.post("/chat", json={"telegram_id": tg_id, "text": "ещё раз"})

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 200
    assert r1.json() == {"reply": "видел, это твоя 1-я реплика"}
    assert r2.json() == {"reply": "видел, это твоя 2-я реплика"}
    assert r3.json() == {"reply": "видел, это твоя 3-я реплика"}


def test_duplicate_update_id_is_deduped(client: TestClient) -> None:
    """Повторный update_id не удваивает счётчик (защита от long-poll retry)."""
    tg_id = 77
    payload = {"telegram_id": tg_id, "text": "привет", "update_id": 1001}

    r1 = client.post("/chat", json=payload)
    r2 = client.post("/chat", json=payload)
    r3 = client.post("/chat", json={"telegram_id": tg_id, "text": "второе", "update_id": 1002})

    assert r1.json() == {"reply": "видел, это твоя 1-я реплика"}
    assert r2.json() == {"reply": ""}
    assert r3.json() == {"reply": "видел, это твоя 2-я реплика"}


def test_separate_users_have_separate_counters(client: TestClient) -> None:
    r_a = client.post("/chat", json={"telegram_id": 1, "text": "a"})
    r_b = client.post("/chat", json={"telegram_id": 2, "text": "b"})
    r_a2 = client.post("/chat", json={"telegram_id": 1, "text": "a2"})

    assert r_a.json() == {"reply": "видел, это твоя 1-я реплика"}
    assert r_b.json() == {"reply": "видел, это твоя 1-я реплика"}
    assert r_a2.json() == {"reply": "видел, это твоя 2-я реплика"}
