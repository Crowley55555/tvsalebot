"""Адаптеры порта `LLMClient` + фабрика.

Публичный интерфейс пакета:
- `build_llm_client(settings)` — фабрика, по `AppSettings.LLM_PROVIDER` строит
  боевой адаптер (`GigaChatClient` на MVP).
- `FakeLLMClient` — заглушка для тестов (не требует установленного `gigachat`).
- `GigaChatClient` — реальный адаптер, экспортирован для type-hints.

Импорт `gigachat` SDK — ЛЕНИВЫЙ, внутри `build_llm_client`, чтобы
`FakeLLMClient` можно было использовать в тестах без установленного
пакета `gigachat`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .fake import FakeLLMClient

if TYPE_CHECKING:
    # Для статической типизации: не исполняется в рантайме,
    # поэтому не требует установленного `gigachat`.
    from composition.env import AppSettings
    from domain.ports.llm import LLMClient

    from .gigachat import GigaChatClient


__all__ = ["build_llm_client", "FakeLLMClient", "GigaChatClient"]


def build_llm_client(settings: AppSettings) -> LLMClient:
    """Собрать боевой LLM-клиент по `AppSettings.LLM_PROVIDER`.

    Импорт `GigaChatClient` отложен внутрь функции, чтобы импорт пакета
    `infrastructure.llm` (например, в тестах с `FakeLLMClient`) не требовал
    установленного `gigachat` SDK.
    """
    if settings.LLM_PROVIDER == "gigachat":
        if settings.GIGACHAT_API_KEY is None:
            raise RuntimeError("GIGACHAT_API_KEY не задан; добавь в .env")
        from .gigachat import GigaChatClient

        raw_cred = settings.GIGACHAT_API_KEY.get_secret_value()
        return GigaChatClient(
            api_key=raw_cred,
            scope=settings.GIGACHAT_SCOPE,
            model=settings.LLM_MODEL,
        )
    raise ValueError(f"unknown LLM_PROVIDER: {settings.LLM_PROVIDER}")
