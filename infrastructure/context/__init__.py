"""Адаптеры порта `ContextStore` + фабрика.

Публичный интерфейс пакета:
- `build_context_store(settings)` — фабрика, по `AppSettings` строит
  основной `RedisContextStore` (единственный боевой адаптер на MVP).
- `InMemoryContextStore` — для юнит-тестов.
- `RedisContextStore` — экспортирован для type-hints и прямых проверок.

Импорт `redis.asyncio` — ЛЕНИВЫЙ, внутри `build_context_store`, чтобы
`InMemoryContextStore` можно было использовать в тестах без установленного
пакета `redis`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .memory_store import InMemoryContextStore

if TYPE_CHECKING:
    # Для статической типизации: не исполняется в рантайме,
    # поэтому не требует установленного `redis`.
    from composition.env import AppSettings
    from domain.ports.context_store import ContextStore

    from .redis_store import RedisContextStore


__all__ = ["build_context_store", "InMemoryContextStore", "RedisContextStore"]


def build_context_store(settings: "AppSettings") -> "ContextStore":
    """Собрать боевой `RedisContextStore` по настройкам приложения.

    Импорт `redis_store` отложен внутрь функции, чтобы импорт пакета
    `infrastructure.context` (например, в тестах с `InMemoryContextStore`)
    не требовал установленного `redis`.
    """
    from .redis_store import RedisContextStore

    password = (
        settings.REDIS_PASSWORD.get_secret_value()
        if settings.REDIS_PASSWORD is not None
        else None
    )
    return RedisContextStore(
        url=settings.REDIS_URL,
        password=password,
        ttl_s=settings.REDIS_TTL_SECONDS,
    )
