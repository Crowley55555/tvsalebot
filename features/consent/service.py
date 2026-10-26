from domain.ports import ContextStore


class ConsentService:
    def __init__(self, store: ContextStore, policy_version: str) -> None:
        self._store = store
        self._policy_version = policy_version

    @property
    def policy_version(self) -> str:
        return self._policy_version

    async def grant(self, telegram_id: int) -> None:
        await self._store.grant_consent(telegram_id, self._policy_version)

    async def has_consent(self, telegram_id: int) -> bool:
        return await self._store.has_consent(telegram_id)
