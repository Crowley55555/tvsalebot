"""Формат Redis-ключей проекта.

Единое место, где собраны конструкторы имён ключей, чтобы один `grep`
по именованию находил все места использования. Чистые функции без побочных
эффектов и без зависимостей от внешних сервисов.
"""

from __future__ import annotations


def dialog_history_key(session_key: str) -> str:
    """Ключ списка истории реплик диалога.

    На v0 Walking Skeleton `session_key == str(telegram_id)`.
    Формат зафиксирован в architecture/04-потоки-данных.md.
    """
    return f"dialog:{session_key}:history"


def update_seen_key(update_id: int) -> str:
    """Ключ идемпотентности Telegram update_id (дедуп long-poll ретраев)."""
    return f"idempotency:update:{update_id}"


def consent_key(telegram_id: int) -> str:
    """Ключ факта согласия пользователя с политикой ПДн.

    Значение — строка `policy_version` (например, `v1-2026-10-26`).
    Формат зафиксирован в plans/2026-10-26-f7-consent-gate.md.
    """
    return f"consent:{telegram_id}"
