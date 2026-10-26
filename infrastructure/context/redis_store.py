"""Redis-адаптер `ContextStore` (единственное место импорта `redis.asyncio`).

Реализует порт `domain.ports.context_store.ContextStore` поверх Redis 7.
Все обращения к Redis-ключам идут через чистые функции из `keys.py`.
"""

from __future__ import annotations

import redis.asyncio as aioredis

from domain.entities import Message

from .keys import dialog_history_key, update_seen_key


class RedisContextStore:
    """Хранилище состояния диалога поверх Redis.

    Конструктор принимает уже «распакованные» значения (строки/числа),
    чтобы не тащить сюда ни `AppSettings`, ни `pydantic.SecretStr` —
    настройки читаются одним местом в `composition/env.py`.
    """

    def __init__(
        self,
        url: str,
        password: str | None = None,
        ttl_s: int = 604800,
    ) -> None:
        self._r: aioredis.Redis = aioredis.from_url(
            url,
            password=password,
            decode_responses=True,
        )
        self._ttl_s: int = ttl_s

    async def append_message(self, session_key: str, msg: Message) -> None:
        key = dialog_history_key(session_key)
        payload = msg.model_dump_json()
        await self._r.rpush(key, payload)
        await self._r.expire(key, self._ttl_s)

    async def get_history_length(self, session_key: str) -> int:
        return await self._r.llen(dialog_history_key(session_key))

    async def get_history(self, session_key: str, limit: int = 30) -> list[Message]:
        key = dialog_history_key(session_key)
        raw: list[str] = await self._r.lrange(key, -limit, -1)
        return [Message.model_validate_json(item) for item in raw]

    async def mark_update_seen(self, update_id: int, ttl_s: int = 60) -> bool:
        """Атомарный SETNX: True — первый раз, False — дубликат."""
        key = update_seen_key(update_id)
        # `set(..., nx=True)` возвращает True при успешной установке
        # и None, если ключ уже существовал. Приводим к bool через `bool(...)`.
        result = await self._r.set(key, "1", ex=ttl_s, nx=True)
        return bool(result)

    async def close(self) -> None:
        """Закрыть пул соединений Redis."""
        await self._r.aclose()
