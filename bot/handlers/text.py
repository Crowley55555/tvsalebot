import logging
import re

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import InlineKeyboardMarkup, Message

from bot.core_api_client import ConsentRequiredFromAPI, CoreAPIClient, CoreAPIError
from bot.keyboards import (
    budget_keyboard,
    consent_keyboard,
    console_keyboard,
    light_keyboard,
    scenario_keyboard,
)

log = logging.getLogger("bot.handlers.text")

router = Router()

_FALLBACK_STORAGE_DOWN = "секунду не могу ответить, попробуй написать ещё раз через минуту"

_MD_BOLD_RE = re.compile(r"\*\*(.*?)\*\*")
_MD_ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def _sanitize_markdown(text: str) -> str:
    text = _MD_BOLD_RE.sub(r"\1", text)
    text = _MD_ITALIC_RE.sub(r"\1", text)
    return text


_SCENARIO_RE = re.compile(
    r"кино.*спорт.*игр|что.*планируете смотреть|основ(ное|ной).*(назнач|сценар)",
    re.IGNORECASE,
)
_LIGHT_RE = re.compile(
    r"освещ[её]н|светл|полумрак|насколько.*свет", re.IGNORECASE
)
_BUDGET_RE = re.compile(
    r"бюджет|ориентир.*(по )?цене|какая.*сумм", re.IGNORECASE
)
_CONSOLE_RE = re.compile(r"PS5|приставк|консол", re.IGNORECASE)
_DISTANCE_RE = re.compile(
    r"метров?.*(от )?дивана|расстояни.*экран", re.IGNORECASE
)


def _pick_funnel_keyboard(reply: str) -> InlineKeyboardMarkup | None:
    # Расстояние — свободный ввод (кнопок не прилепляем).
    if _DISTANCE_RE.search(reply):
        return None
    if _SCENARIO_RE.search(reply):
        return scenario_keyboard()
    if _LIGHT_RE.search(reply):
        return light_keyboard()
    if _BUDGET_RE.search(reply):
        return budget_keyboard()
    if _CONSOLE_RE.search(reply):
        return console_keyboard()
    return None


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
    clean_reply = _sanitize_markdown(reply)
    funnel_kb = _pick_funnel_keyboard(clean_reply)
    await message.answer(clean_reply, reply_markup=funnel_kb)
