from domain import ConsentRequired, Message
from domain.ports import ContextStore, LLMClient
from features.consent import ConsentService


class DialogService:
    def __init__(
        self,
        store: ContextStore,
        llm: LLMClient,
        consent: ConsentService,
        system_prompt: str,
        max_history_messages: int = 30,
    ) -> None:
        self._store = store
        self._llm = llm
        self._consent = consent
        self._system_prompt = system_prompt
        self._max_history = max_history_messages

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

        if not await self._consent.has_consent(telegram_id):
            raise ConsentRequired(telegram_id)

        session_key = str(telegram_id)
        await self._store.append_message(
            session_key, Message(role="user", text=text)
        )
        history = await self._store.get_history(session_key, limit=self._max_history)

        result = await self._llm.chat(
            system_prompt=self._system_prompt,
            history=history,
        )
        reply_text = result.text

        await self._store.append_message(
            session_key, Message(role="assistant", text=reply_text)
        )
        return reply_text
