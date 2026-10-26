from typing import Protocol

from domain.entities import TVModel


class TVCatalog(Protocol):
    async def all(self) -> list[TVModel]:
        """Все модели каталога в порядке объявления."""
        ...

    async def by_code(self, code: str) -> TVModel | None:
        """Найти модель по коду (регистронезависимо). None, если нет."""
        ...

    async def as_prompt_block(self) -> str:
        """Markdown-блок каталога для вставки в system-prompt LLM."""
        ...
