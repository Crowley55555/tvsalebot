import logging
import re

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.core_api_client import ConsentRequiredFromAPI, CoreAPIClient, CoreAPIError
from bot.keyboards import consent_keyboard, keyboard_for_state
from bot.states import FunnelState

log = logging.getLogger("bot.handlers.text")

router = Router()

_FALLBACK_STORAGE_DOWN = "секунду не могу ответить, попробуй написать ещё раз через минуту"

_MD_BOLD_RE = re.compile(r"\*\*(.*?)\*\*")
_MD_ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def _sanitize_markdown(text: str) -> str:
    text = _MD_BOLD_RE.sub(r"\1", text)
    text = _MD_ITALIC_RE.sub(r"\1", text)
    return text


def _state_name_short(state_full: str | None) -> str | None:
    """«FunnelState:AWAIT_LIGHT» → «AWAIT_LIGHT». None/без ':' → None."""
    if state_full is None:
        return None
    _, _, tail = state_full.partition(":")
    return tail or None


@router.message(F.chat.type == ChatType.PRIVATE, F.text)
async def on_text(
    message: Message, core_api_client: CoreAPIClient, state: FSMContext
) -> None:
    if message.from_user is None or message.text is None:
        return

    current = await state.get_state()
    if current == FunnelState.AWAIT_DISTANCE.state:
        # Единственный шаг воронки со свободным вводом — расстояние в метрах.
        await state.update_data(distance=message.text)
        await state.set_state(FunnelState.AWAIT_BUDGET)
    # На других шагах воронки state не трогаем: клиент пишет текстом, LLM отвечает,
    # клавиатура прицепится по текущему state (клиент может продолжить и кнопкой).

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
    new_state = await state.get_state()
    kb = keyboard_for_state(_state_name_short(new_state))
    await message.answer(clean_reply, reply_markup=kb)
