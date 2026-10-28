import contextlib
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.core_api_client import CoreAPIClient, CoreAPIError
from bot.keyboards import (
    CONSENT_CALLBACK_DATA,
    FUNNEL_CALLBACK_PREFIX,
    scenario_keyboard,
)

log = logging.getLogger("bot.handlers.callback")

router = Router()

_FALLBACK_STORAGE_DOWN = "секунду не могу ответить, попробуй написать ещё раз через минуту"


@router.callback_query(F.data == CONSENT_CALLBACK_DATA)
async def on_consent_grant(
    callback: CallbackQuery, core_api_client: CoreAPIClient
) -> None:
    if callback.from_user is None:
        await callback.answer()
        return
    try:
        version = await core_api_client.grant_consent(callback.from_user.id)
    except CoreAPIError as exc:
        log.error(
            "consent_grant_failed telegram_id=%s status=%s",
            callback.from_user.id,
            exc.status_code,
        )
        await callback.answer("Не получилось, попробуй ещё раз", show_alert=True)
        return

    log.info(
        "consent_granted telegram_id=%s policy_version=%s",
        callback.from_user.id,
        version,
    )
    await callback.answer()
    if callback.message is not None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            "Спасибо! Начнём с главного: что в основном планируете смотреть "
            "— кино, спорт, игры или фоновый ТВ?",
            reply_markup=scenario_keyboard(),
        )


@router.callback_query(F.data.startswith(f"{FUNNEL_CALLBACK_PREFIX}:"))
async def on_funnel_choice(
    callback: CallbackQuery, core_api_client: CoreAPIClient
) -> None:
    if (
        callback.from_user is None
        or callback.data is None
        or not isinstance(callback.message, Message)
    ):
        await callback.answer()
        return
    try:
        _, step, value = callback.data.split(":", 2)
    except ValueError:
        await callback.answer()
        return

    # Эхо-ответ клиента (как будто он написал value текстом) — для прозрачности UX.
    with contextlib.suppress(Exception):
        await callback.message.answer(value)

    # Снимаем inline-клавиатуру с предыдущего сообщения — чтобы клиент не кликал второй раз.
    with contextlib.suppress(Exception):
        await callback.message.edit_reply_markup(reply_markup=None)

    try:
        reply = await core_api_client.chat(
            telegram_id=callback.from_user.id,
            text=value,
            update_id=callback.message.message_id,
        )
    except CoreAPIError as exc:
        log.error(
            "funnel_chat_failed telegram_id=%s step=%s status=%s",
            callback.from_user.id,
            step,
            exc.status_code,
        )
        await callback.message.answer(_FALLBACK_STORAGE_DOWN)
        await callback.answer()
        return

    await callback.answer()
    if not reply:
        return

    # Используем те же утилиты из text handler.
    from bot.handlers.text import _pick_funnel_keyboard, _sanitize_markdown

    clean_reply = _sanitize_markdown(reply)
    funnel_kb = _pick_funnel_keyboard(clean_reply)
    await callback.message.answer(clean_reply, reply_markup=funnel_kb)
