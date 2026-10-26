import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.core_api_client import CoreAPIClient, CoreAPIError
from bot.keyboards import CONSENT_CALLBACK_DATA

log = logging.getLogger("bot.handlers.callback")

router = Router()


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
            "Спасибо! Теперь можешь задавать вопросы по телевизорам."
        )
