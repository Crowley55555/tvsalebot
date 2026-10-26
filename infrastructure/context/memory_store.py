"""In-memory адаптер `ContextStore` для юнит-тестов и локального dev."""

from __future__ import annotations

import time
from typing import Any, Literal

from domain.entities import Message


class InMemoryContextStore:
    """Простейшая реализация ContextStore в памяти процесса (только тесты)."""

    def __init__(self) -> None:
        self._history: dict[str, list[Message]] = {}
        self._seen_updates: set[int] = set()
        self._consents: dict[int, str] = {}
        self._deletion_log: list[dict[str, Any]] = []

    async def append_message(self, session_key: str, msg: Message) -> None:
        self._history.setdefault(session_key, []).append(msg)

    async def get_history_length(self, session_key: str) -> int:
        return len(self._history.get(session_key, []))

    async def get_history(self, session_key: str, limit: int = 30) -> list[Message]:
        full = self._history.get(session_key, [])
        if limit <= 0:
            return []
        return list(full[-limit:])

    async def mark_update_seen(self, update_id: int, ttl_s: int = 60) -> bool:
        if update_id in self._seen_updates:
            return False
        self._seen_updates.add(update_id)
        return True

    async def grant_consent(self, telegram_id: int, policy_version: str) -> None:
        self._consents[telegram_id] = policy_version

    async def has_consent(self, telegram_id: int) -> bool:
        return telegram_id in self._consents

    async def delete_user_data(self, telegram_id: int) -> int:
        session_key = str(telegram_id)
        count = 0
        if session_key in self._history:
            del self._history[session_key]
            count += 1
        if telegram_id in self._consents:
            del self._consents[telegram_id]
            count += 1
        return count

    async def append_deletion_log(
        self,
        telegram_id: int,
        reason: Literal["user_stop", "user_delete", "retention", "admin"],
    ) -> None:
        self._deletion_log.append(
            {"telegram_id": telegram_id, "ts": int(time.time()), "reason": reason}
        )

    async def close(self) -> None:
        return None
