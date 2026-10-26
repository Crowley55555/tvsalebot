"""Адаптер порта `LLMClient` для GigaChat 2 Pro через официальный SDK gigachat."""

from __future__ import annotations

import asyncio
import time

import httpx
from gigachat import GigaChat
from gigachat.exceptions import GigaChatException
from gigachat.models import Chat, Messages, MessagesRole

from domain.entities import ChatResult, Message
from domain.ports.llm import LLMBadResponse, LLMUnavailable


class GigaChatClient:
    """GigaChat 2 Pro — боевой адаптер `LLMClient` для РФ-контура."""

    def __init__(
        self,
        api_key: str,
        scope: str,
        model: str,
        verify_ssl_certs: bool = False,
    ) -> None:
        # verify_ssl_certs=False по умолчанию: api.gigachat.devices подписан
        # сертификатом Russian Trusted Root CA, которой нет в системных trust
        # stores дистрибутивов Linux/Windows по умолчанию. Это dev-режим;
        # на проде включается внешней конфигурацией (ca_bundle_file в .env).
        self._client = GigaChat(
            credentials=api_key,
            scope=scope,
            model=model,
            verify_ssl_certs=verify_ssl_certs,
        )
        self._model = model

    async def chat(
        self,
        system_prompt: str,
        history: list[Message],
        *,
        max_tokens: int = 1024,
        timeout_s: float = 10.0,
    ) -> ChatResult:
        messages: list[Messages] = [
            Messages(role=MessagesRole.SYSTEM, content=system_prompt)
        ]
        for msg in history:
            role = (
                MessagesRole.USER
                if msg.role == "user"
                else MessagesRole.ASSISTANT
            )
            messages.append(Messages(role=role, content=msg.text))

        payload = Chat(messages=messages, max_tokens=max_tokens)

        started = time.monotonic()
        try:
            # SDK's own `timeout` — это общий HTTP-таймаут клиента; здесь нужен
            # per-call таймаут, поэтому оборачиваем в asyncio.wait_for.
            response = await asyncio.wait_for(
                self._client.achat(payload), timeout=timeout_s
            )
        except asyncio.TimeoutError as exc:
            raise LLMUnavailable(
                f"GigaChat timeout after {timeout_s}s"
            ) from exc
        except GigaChatException as exc:
            raise LLMUnavailable(f"GigaChat SDK error: {exc}") from exc
        except httpx.HTTPError as exc:
            raise LLMUnavailable(f"GigaChat HTTP error: {exc}") from exc

        duration_ms = int((time.monotonic() - started) * 1000)

        if not response.choices:
            raise LLMBadResponse("GigaChat returned no choices")
        content = response.choices[0].message.content
        if not content:
            raise LLMBadResponse("GigaChat returned empty content")

        usage = response.usage
        total_tokens = usage.total_tokens if usage is not None else 0

        return ChatResult(
            text=content,
            tokens_used=total_tokens,
            provider="gigachat",
            duration_ms=duration_ms,
        )

    async def aclose(self) -> None:
        close = getattr(self._client, "aclose", None)
        if close is None:
            return
        await close()
