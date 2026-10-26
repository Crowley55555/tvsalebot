import logging

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

from bot.core_api_client import ConsentRequiredFromAPI, CoreAPIClient, CoreAPIError
from bot.keyboards import consent_keyboard

log = logging.getLogger("bot.handlers.text")

router = Router()

_FALLBACK_STORAGE_DOWN = "секунду не могу ответить, попробуй написать ещё раз через минуту"


@router.message(F.chat.type == ChatType.PRIVATE, F.text)
async def on_text(message: Message, core_api_client: CoreAPIClient) -> None:
    if message.from_user is None or message.text is None:
        return
    try:
        reply = await core_api_client.chat(
            telegram_id=message.from_user.id,
            text=message.text,
            update_id=message.message_id,
        )
    except ConsentRequiredFromAPI as exc:
        await message.answer(
            exc.user_message, reply_markup=consent_keyboard(exc.policy_url)
        )
        return
    except CoreAPIError as exc:
        log.error(
            "core_api_error telegram_id=%s status=%s detail=%s",
            message.from_user.id,
            exc.status_code,
            exc.detail,
        )
        await message.answer(_FALLBACK_STORAGE_DOWN)
        return

    if not reply:
        log.info("empty_reply skip telegram_id=%s", message.from_user.id)
        return
    await message.answer(reply)
