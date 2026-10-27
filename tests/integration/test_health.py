"""Интеграционные тесты публичного эндпоинта `GET /health`.

Эндпоинт — публичный, не требует консента, не читает ПДн.
Проверяет только живость хранилища (порт ContextStore.ping).
"""

from __future__ import annotations

import types
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from api.deps import get_container
from api.main import app
from infrastructure.context import InMemoryContextStore


class _FailingPingStore(InMemoryContextStore):
    """ContextStore, у которого `ping` бросает `ConnectionError`.

    Остальные методы — унаследованные от InMemoryContextStore (не трогаем).
    """

    async def ping(self) -> None:  # type: ignore[override]
        raise ConnectionError("redis is down")


def _make_client(context_store: InMemoryContextStore) -> TestClient:
    """Собрать TestClient с минимальным контейнером под /health.

    Для /health достаточно одного поля `context_store`.
    """
    container = types.SimpleNamespace(context_store=context_store)
    app.state.container = container
    app.dependency_overrides[get_container] = lambda: container
    return TestClient(app)


@pytest.fixture
def health_client_ok() -> Iterator[TestClient]:
    client = _make_client(InMemoryContextStore())
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
        app.state.container = None


@pytest.fixture
def health_client_down() -> Iterator[TestClient]:
    client = _make_client(_FailingPingStore())
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
        app.state.container = None


def test_health_ok(health_client_ok: TestClient) -> None:
    r = health_client_ok.get("/health")

    assert r.status_code == 200
    assert r.json() == {"status": "ok", "redis": "ok"}


def test_health_redis_down(health_client_down: TestClient) -> None:
    r = health_client_down.get("/health")

    assert r.status_code == 503
    assert r.json() == {"status": "degraded", "redis": "unreachable"}
