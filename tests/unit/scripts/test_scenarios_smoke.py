"""Smoke-тест прогонщика сценариев (F19 + F23).

Проверяет, что для каждого прогона из ``ALL_RUNS`` (эталонные
сценарии + провокации) скрипт делает ровно ``1 (consent) +
N (chat) + 1 (gdpr/stop)`` POST-вызовов — то есть не теряет и не
повторяет реплики, не забывает очистить ПДн между прогонами.

Боевой Core API не поднимается: ``httpx.AsyncClient`` подменяется
фейком, который считает вызовы по пути и возвращает фиксированный
``reply``. ``pytest-asyncio`` в проекте нет (новая либа — П6), поэтому
корутина запускается через ``asyncio.run`` в обычном sync-тесте.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from scripts import test_scenarios as runner


class _FakeResponse:
    status_code = 200

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload
        self.text = ""

    def json(self) -> dict[str, Any]:
        return self._payload


class _FakeAsyncClient:
    """Минимальный stub ``httpx.AsyncClient`` для подсчёта вызовов."""

    def __init__(self, *_: Any, **__: Any) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def __aenter__(self) -> "_FakeAsyncClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        return None

    async def post(
        self,
        url: str,
        *,
        json: dict[str, Any],
        headers: dict[str, str],  # noqa: ARG002
    ) -> _FakeResponse:
        # Нормализуем до пути: тесту неважен конкретный base_url.
        path = "/" + url.split("/", 3)[-1]
        self.calls.append((path, json))
        return _FakeResponse({"reply": f"fake-reply for {json.get('text', '')}"})


async def _noop_sleep(_seconds: float) -> None:
    return None


def test_runner_hits_consent_chat_gdpr_for_each_scenario(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    fake_client_holder: dict[str, _FakeAsyncClient] = {}

    def _factory(*args: Any, **kwargs: Any) -> _FakeAsyncClient:
        client = _FakeAsyncClient(*args, **kwargs)
        fake_client_holder["client"] = client
        return client

    monkeypatch.setattr(runner.httpx, "AsyncClient", _factory)
    # В тесте не ждём секунду между сценариями.
    monkeypatch.setattr(runner.asyncio, "sleep", _noop_sleep)

    exit_code = asyncio.run(runner._main_async())

    assert exit_code == 0
    client = fake_client_holder["client"]

    # Для каждого прогона: 1 consent/grant + len(user_messages) /chat + 1 /gdpr/stop.
    expected_total = sum(1 + len(sc.user_messages) + 1 for sc in runner.ALL_RUNS)
    assert len(client.calls) == expected_total

    # Проверим последовательность по каждому прогону: consent -> chat*N -> gdpr/stop.
    cursor = 0
    for scenario in runner.ALL_RUNS:
        consent_path, consent_body = client.calls[cursor]
        assert consent_path == "/consent/grant"
        assert consent_body == {"telegram_id": scenario.telegram_id}
        cursor += 1

        for user_msg in scenario.user_messages:
            chat_path, chat_body = client.calls[cursor]
            assert chat_path == "/chat"
            assert chat_body["telegram_id"] == scenario.telegram_id
            assert chat_body["text"] == user_msg
            cursor += 1

        stop_path, stop_body = client.calls[cursor]
        assert stop_path == "/gdpr/stop"
        assert stop_body == {
            "telegram_id": scenario.telegram_id,
            "reason": "user_delete",
        }
        cursor += 1

    # И транскрипты легли на диск под CWD.
    out_dirs = list((tmp_path / "transcripts").iterdir())
    assert len(out_dirs) == 1
    produced = sorted(p.name for p in out_dirs[0].iterdir())
    expected_files = sorted(f"{sc.name}.md" for sc in runner.ALL_RUNS)
    assert produced == expected_files
