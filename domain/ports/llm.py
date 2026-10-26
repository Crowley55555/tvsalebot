from typing import Protocol

from domain.entities import ChatResult, Message


class LLMClient(Protocol):
    async def chat(
        self,
        system_prompt: str,
        history: list[Message],
        *,
        max_tokens: int = 1024,
        timeout_s: float = 10.0,
    ) -> ChatResult: ...


class LLMUnavailable(RuntimeError):
    """LLM-провайдер недоступен после всех ретраев."""


class LLMBadResponse(RuntimeError):
    """LLM вернул ответ, который невозможно использовать."""
