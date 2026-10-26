import logging
from dataclasses import dataclass
from typing import Literal

from domain.ports import ContextStore

DeletionReason = Literal["user_stop", "user_delete", "retention", "admin"]

log = logging.getLogger("features.deletion")


@dataclass
class DeletionResult:
    deleted_keys: int
    reason: DeletionReason


class DeletionService:
    def __init__(self, store: ContextStore) -> None:
        self._store = store

    async def delete_user_data(
        self, telegram_id: int, reason: DeletionReason
    ) -> DeletionResult:
        deleted = await self._store.delete_user_data(telegram_id)
        await self._store.append_deletion_log(telegram_id, reason)
        log.info(
            "user_data_deleted telegram_id=%s reason=%s keys=%s",
            telegram_id,
            reason,
            deleted,
        )
        return DeletionResult(deleted_keys=deleted, reason=reason)
