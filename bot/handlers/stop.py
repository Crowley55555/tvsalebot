import logging

from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from bot.core_api_client import CoreAPIClient, CoreAPIError

log = logging.getLogger("bot.handlers.stop")

router = Router()

_SUCCESS = (
    "Твои данные удалены. Если захочешь вернуться — отправь /start."
)
_FAIL = "Не получилось удалить данные прямо сейчас, попробуй ещё раз через минуту."


@router.message(
    Command("stop", "удалить_данные"),
    lambda m: m.chat.type == ChatType.PRIVATE,
)
async def on_stop(message: Message, core_api_client: CoreAPIClient) -> None:
    if message.from_user is None:
        return
    try:
        deleted_keys = await core_api_client.gdpr_stop(
            telegram_id=message.from_user.id, reason="user_stop"
        )
    except CoreAPIError as exc:
        log.error(
            "gdpr_stop_failed telegram_id=%s status=%s",
            message.from_user.id,
            exc.status_code,
        )
        await message.answer(_FAIL)
        return

    log.info(
        "gdpr_stop_ok telegram_id=%s deleted_keys=%s",
        message.from_user.id,
        deleted_keys,
    )
    await message.answer(_SUCCESS)
