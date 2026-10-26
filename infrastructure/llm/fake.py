"""In-memory заглушка `LLMClient` для юнит- и интеграционных тестов."""

from __future__ import annotations

from typing import Any

from domain.entities import ChatResult, Message


class FakeLLMClient:
    """Детерминированный `LLMClient` для тестов: не ходит в сеть.

    - Возвращает заранее заданный текст.
    - Фиксирует все вызовы `chat(...)` в `self.calls` для последующих ассертов.
    """

    def __init__(
        self,
        programmed_reply: str = "stub-reply",
        tokens_used: int = 42,
    ) -> None:
        self.programmed_reply = programmed_reply
        self.tokens_used = tokens_used
        self.calls: list[dict[str, Any]] = []

    def set_next_reply(self, text: str) -> None:
        self.programmed_reply = text

    async def chat(
        self,
        system_prompt: str,
        history: list[Message],
        *,
        max_tokens: int = 1024,
        timeout_s: float = 10.0,
    ) -> ChatResult:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "history": list(history),
                "max_tokens": max_tokens,
                "timeout_s": timeout_s,
            }
        )
        return ChatResult(
            text=self.programmed_reply,
            tokens_used=self.tokens_used,
            provider="fake",
            duration_ms=0,
        )

    async def aclose(self) -> None:
        return None
