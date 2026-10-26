"""Redis-адаптер `ContextStore` (единственное место импорта `redis.asyncio`).

Реализует порт `domain.ports.context_store.ContextStore` поверх Redis 7.
Все обращения к Redis-ключам идут через чистые функции из `keys.py`.
"""

from __future__ import annotations

import json
import time
from typing import Literal

import redis.asyncio as aioredis

from domain.entities import Message

from .keys import DELETION_LOG_KEY, consent_key, dialog_history_key, update_seen_key


class RedisContextStore:
    """Хранилище состояния диалога поверх Redis."""

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
        key = update_seen_key(update_id)
        result = await self._r.set(key, "1", ex=ttl_s, nx=True)
        return bool(result)

    async def grant_consent(self, telegram_id: int, policy_version: str) -> None:
        await self._r.set(consent_key(telegram_id), policy_version, ex=self._ttl_s)

    async def has_consent(self, telegram_id: int) -> bool:
        return await self._r.exists(consent_key(telegram_id)) > 0

    async def delete_user_data(self, telegram_id: int) -> int:
        session_key = str(telegram_id)
        keys = [dialog_history_key(session_key), consent_key(telegram_id)]
        deleted = await self._r.delete(*keys)
        return int(deleted)

    async def append_deletion_log(
        self,
        telegram_id: int,
        reason: Literal["user_stop", "user_delete", "retention", "admin"],
    ) -> None:
        entry = json.dumps(
            {"telegram_id": telegram_id, "ts": int(time.time()), "reason": reason}
        )
        await self._r.rpush(DELETION_LOG_KEY, entry)

    async def close(self) -> None:
        await self._r.aclose()
