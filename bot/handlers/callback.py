import contextlib
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.core_api_client import CoreAPIClient, CoreAPIError
from bot.keyboards import (
    CONSENT_CALLBACK_DATA,
    FUNNEL_BACK_CALLBACK_DATA,
    FUNNEL_CALLBACK_PREFIX,
    FUNNEL_RESTART_CALLBACK_DATA,
    FUNNEL_VALUES,
    POST_CONSENT_GREETING,
    keyboard_for_state,
    scenario_keyboard,
)
from bot.states import FunnelState, is_games_scenario, prev_state_of, state_name

log = logging.getLogger("bot.handlers.callback")

router = Router()

_FALLBACK_STORAGE_DOWN = "секунду не могу ответить, попробуй написать ещё раз через минуту"

# Ключ в state.data, который чистим при «⬅ Назад» из соответствующего state.
_STATE_DATA_KEY: dict[str, str] = {
    state_name(FunnelState.AWAIT_LIGHT): "light",
    state_name(FunnelState.AWAIT_DISTANCE): "distance",
    state_name(FunnelState.AWAIT_BUDGET): "budget",
    state_name(FunnelState.AWAIT_CONSOLE): "console",
}


@router.callback_query(F.data == CONSENT_CALLBACK_DATA)
async def on_consent_grant(
    callback: CallbackQuery, core_api_client: CoreAPIClient, state: FSMContext
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
    await state.set_state(FunnelState.AWAIT_SCENARIO)
    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            POST_CONSENT_GREETING,
            reply_markup=scenario_keyboard(),
        )


@router.callback_query(F.data == FUNNEL_BACK_CALLBACK_DATA)
async def on_back(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not isinstance(callback.message, Message):
        await callback.answer()
        return

    current = await state.get_state()
    # Из AWAIT_SCENARIO/COMPLETED/None назад идти некуда.
    if current is None or current in (
        state_name(FunnelState.AWAIT_SCENARIO),
        state_name(FunnelState.COMPLETED),
    ):
        await callback.answer()
        return

    prev = prev_state_of(current)
    if prev is None:
        await callback.answer()
        return

    # Чистим значение текущего шага, чтобы при повторном выборе оно перезаписалось.
    data_key = _STATE_DATA_KEY.get(current)
    if data_key is not None:
        data = await state.get_data()
        if data_key in data:
            data.pop(data_key)
            await state.set_data(data)

    await state.set_state(prev)

    with contextlib.suppress(Exception):
        await callback.message.edit_reply_markup(reply_markup=None)

    from bot.handlers.text import _state_name_short

    kb = keyboard_for_state(_state_name_short(state_name(prev)))
    await callback.message.answer(
        "⬅ Можно изменить выбор на предыдущем шаге:",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data == FUNNEL_RESTART_CALLBACK_DATA)
async def on_restart(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not isinstance(callback.message, Message):
        await callback.answer()
        return

    await state.clear()
    await state.set_state(FunnelState.AWAIT_SCENARIO)

    with contextlib.suppress(Exception):
        await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        POST_CONSENT_GREETING,
        reply_markup=scenario_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(f"{FUNNEL_CALLBACK_PREFIX}:"))
async def on_funnel_choice(
    callback: CallbackQuery, core_api_client: CoreAPIClient, state: FSMContext
) -> None:
    if (
        callback.from_user is None
        or callback.data is None
        or not isinstance(callback.message, Message)
    ):
        await callback.answer()
        return
    try:
        _, step, code = callback.data.split(":", 2)
    except ValueError:
        await callback.answer()
        return

    value = FUNNEL_VALUES.get((step, code), code)

    # Обновляем FSM ДО вызова /chat, чтобы к ответу прицепить правильную клавиатуру.
    if step == "scenario":
        await state.update_data(scenario=value)
        await state.set_state(FunnelState.AWAIT_LIGHT)
    elif step == "light":
        await state.update_data(light=value)
        await state.set_state(FunnelState.AWAIT_DISTANCE)
    elif step == "budget":
        await state.update_data(budget=value)
        data = await state.get_data()
        if is_games_scenario(data.get("scenario")):
            await state.set_state(FunnelState.AWAIT_CONSOLE)
        else:
            await state.set_state(FunnelState.COMPLETED)
    elif step == "console":
        await state.update_data(console=value)
        await state.set_state(FunnelState.COMPLETED)

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

    from bot.handlers.text import _sanitize_markdown, _state_name_short

    clean_reply = _sanitize_markdown(reply)
    new_state = await state.get_state()
    kb = keyboard_for_state(_state_name_short(new_state))
    await callback.message.answer(clean_reply, reply_markup=kb)
