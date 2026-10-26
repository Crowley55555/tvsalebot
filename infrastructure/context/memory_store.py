"""In-memory адаптер `ContextStore` для юнит-тестов и локального dev.

Состояние хранится в АТРИБУТАХ ИНСТАНСА, а не в глобальных словарях уровня
модуля — это важно для правила П4 (никаких `dict[int, ...]` по `user_id`
на уровне модуля). Один инстанс = один изолированный «мок Redis».
"""

from __future__ import annotations

from domain.entities import Message


class InMemoryContextStore:
    """Простейшая реализация ContextStore в памяти процесса.

    Используется только в тестах. На проде/в dev-запуске живёт `RedisContextStore`.
    """

    def __init__(self) -> None:
        self._history: dict[str, list[Message]] = {}
        self._seen_updates: set[int] = set()
        self._consents: dict[int, str] = {}

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
        # ttl_s игнорируется: в памяти процесса TTL не моделируем,
        # для тестов достаточно факта «видели или нет».
        if update_id in self._seen_updates:
            return False
        self._seen_updates.add(update_id)
        return True

    async def grant_consent(self, telegram_id: int, policy_version: str) -> None:
        # Повторный вызов идемпотентен — перезаписываем ту же версию.
        self._consents[telegram_id] = policy_version

    async def has_consent(self, telegram_id: int) -> bool:
        return telegram_id in self._consents

    async def close(self) -> None:
        # В памяти закрывать нечего — симметрия с RedisContextStore.
        return None
