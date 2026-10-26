from domain import Message
from domain.ports import ContextStore


class DialogService:
    def __init__(self, store: ContextStore) -> None:
        self._store = store

    async def handle_user_message(
        self,
        *,
        telegram_id: int,
        text: str,
        update_id: int | None = None,
    ) -> str:
        if update_id is not None:
            seen = await self._store.mark_update_seen(update_id)
            if not seen:
                return ""

        session_key = str(telegram_id)
        await self._store.append_message(
            session_key, Message(role="user", text=text)
        )
        n_user = await self._store.get_history_length(session_key)
        # история чередуется user/assistant: LLEN=1 -> 1-я, LLEN=3 -> 2-я, ...
        reply_number = (n_user + 1) // 2
        reply_text = f"видел, это твоя {reply_number}-я реплика"
        await self._store.append_message(
            session_key, Message(role="assistant", text=reply_text)
        )
        return reply_text
