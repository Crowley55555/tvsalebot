from typing import Protocol

from domain.entities import Message


class ContextStore(Protocol):
    async def append_message(self, session_key: str, msg: Message) -> None: ...

    async def get_history_length(self, session_key: str) -> int: ...

    async def get_history(self, session_key: str, limit: int = 30) -> list[Message]:
        """Вернуть последние `limit` сообщений в хронологическом порядке."""
        ...

    async def mark_update_seen(self, update_id: int, ttl_s: int = 60) -> bool:
        """Вернуть True, если update_id увиден впервые; False — дубликат.

        Нужен для дедупа повторных Telegram update_id (long-poll retry).
        """
        ...
