from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class FunnelState(StatesGroup):
    """Шаги inline-воронки бота. Хранится в MemoryStorage aiogram.

    П4 это не нарушает: это UX-состояние клавиатур, а не LLM-контекст
    диалога (тот живёт в Redis через ContextStore).
    """

    AWAIT_SCENARIO = State()
    AWAIT_LIGHT = State()
    AWAIT_DISTANCE = State()
    AWAIT_BUDGET = State()
    AWAIT_CONSOLE = State()
    COMPLETED = State()


def state_name(s: State) -> str:
    """Полное имя связанного состояния («FunnelState:AWAIT_LIGHT»).

    `State.state` типизирован как `Optional[str]` (None разрешён только для
    несвязанных или wildcard-состояний); у наших связанных это всегда строка.
    """
    name = s.state
    assert name is not None, "bound State must have a non-empty name"
    return name


_PREV_MAP: dict[str, State] = {
    state_name(FunnelState.AWAIT_LIGHT): FunnelState.AWAIT_SCENARIO,
    state_name(FunnelState.AWAIT_DISTANCE): FunnelState.AWAIT_LIGHT,
    state_name(FunnelState.AWAIT_BUDGET): FunnelState.AWAIT_DISTANCE,
    state_name(FunnelState.AWAIT_CONSOLE): FunnelState.AWAIT_BUDGET,
}


def prev_state_of(current: str | None) -> State | None:
    """Возвращает предыдущий шаг воронки.

    Для AWAIT_SCENARIO и COMPLETED назад идти некуда — возвращаем None.
    На вход принимает полное имя состояния вида «FunnelState:AWAIT_LIGHT»
    (как возвращает FSMContext.get_state).
    """
    if current is None:
        return None
    return _PREV_MAP.get(current)


def is_games_scenario(value: str | None) -> bool:
    """True если сохранённый сценарий содержит «игры» (нужно для ветки консоли)."""
    if not value:
        return False
    return "игры" in value.lower()
