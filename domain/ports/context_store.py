from typing import Literal, Protocol

from domain.entities import Message

DeletionReason = Literal["user_stop", "user_delete", "retention", "admin"]


class ContextStore(Protocol):
    async def append_message(self, session_key: str, msg: Message) -> None: ...

    async def get_history_length(self, session_key: str) -> int: ...

    async def get_history(self, session_key: str, limit: int = 30) -> list[Message]:
        """Вернуть последние `limit` сообщений в хронологическом порядке."""
        ...

    async def mark_update_seen(self, update_id: int, ttl_s: int = 60) -> bool:
        """Вернуть True, если update_id увиден впервые; False — дубликат."""
        ...

    async def grant_consent(self, telegram_id: int, policy_version: str) -> None: ...

    async def has_consent(self, telegram_id: int) -> bool: ...

    async def delete_user_data(self, telegram_id: int) -> int:
        """Удалить все ПДн пользователя. Вернуть число удалённых ключей."""
        ...

    async def append_deletion_log(
        self, telegram_id: int, reason: DeletionReason
    ) -> None:
        """Записать факт удаления (user_id + timestamp + reason), без содержимого."""
        ...
