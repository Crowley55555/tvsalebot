from typing import Final

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CONSENT_CALLBACK_DATA = "consent:grant"
FUNNEL_CALLBACK_PREFIX = "funnel"
FUNNEL_BACK_CALLBACK_DATA = "funnel:back"
FUNNEL_RESTART_CALLBACK_DATA = "funnel:restart"

# Общая проактивная фраза после /consent/grant и при «🔄 Начать заново».
# Хардкод здесь — короткая UX-подсказка (как _FALLBACK_STORAGE_DOWN),
# не бизнес-текст про Samsung-эксперта (тот живёт в prompts/system.md).
POST_CONSENT_GREETING = (
    "Спасибо! Начнём с главного: что в основном планируете смотреть "
    "— кино, спорт, игры или фоновый ТВ?"
)

# Telegram callback_data limit = 64 bytes (UTF-8). Храним короткие коды,
# полный ответ для LLM восстанавливается из FUNNEL_VALUES.
FUNNEL_VALUES: Final[dict[tuple[str, str], str]] = {
    ("scenario", "movie"): "кино",
    ("scenario", "sport"): "спорт",
    ("scenario", "games"): "игры",
    ("scenario", "bg"): "фоновый ТВ",
    ("light", "bright"): "комната светлая",
    ("light", "mid"): "комната средней освещённости",
    ("light", "dark"): "комната тёмная",
    ("budget", "lt50"): "бюджет до 50 тыс.",
    ("budget", "50-100"): "бюджет 50–100 тыс.",
    ("budget", "100-150"): "бюджет 100–150 тыс.",
    ("budget", "gt150"): "бюджет свыше 150 тыс.",
    ("console", "ps5"): "PS5 есть",
    ("console", "none"): "консоли нет",
}


def _back_row() -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            text="⬅ Назад", callback_data=FUNNEL_BACK_CALLBACK_DATA
        )
    ]


def consent_keyboard(policy_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Политика ПДн", url=policy_url),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Согласен", callback_data=CONSENT_CALLBACK_DATA
                ),
            ],
        ]
    )


def _funnel_button(step: str, label: str, code: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=label, callback_data=f"{FUNNEL_CALLBACK_PREFIX}:{step}:{code}"
    )


def scenario_keyboard(with_back: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            _funnel_button("scenario", "🎬 Кино", "movie"),
            _funnel_button("scenario", "⚽ Спорт", "sport"),
        ],
        [
            _funnel_button("scenario", "🎮 Игры", "games"),
            _funnel_button("scenario", "📺 Фоновый ТВ", "bg"),
        ],
    ]
    if with_back:
        rows.append(_back_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def light_keyboard(with_back: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            _funnel_button("light", "☀️ Светло", "bright"),
            _funnel_button("light", "🌥 Полумрак", "mid"),
        ],
        [
            _funnel_button("light", "🌙 Темно", "dark"),
        ],
    ]
    if with_back:
        rows.append(_back_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def budget_keyboard(with_back: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            _funnel_button("budget", "до 50 тыс.", "lt50"),
            _funnel_button("budget", "50–100 тыс.", "50-100"),
        ],
        [
            _funnel_button("budget", "100–150 тыс.", "100-150"),
            _funnel_button("budget", "150+ тыс.", "gt150"),
        ],
    ]
    if with_back:
        rows.append(_back_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def console_keyboard(with_back: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            _funnel_button("console", "🎮 PS5 есть", "ps5"),
            _funnel_button("console", "Нет консоли", "none"),
        ],
    ]
    if with_back:
        rows.append(_back_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def restart_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Начать заново",
                    callback_data=FUNNEL_RESTART_CALLBACK_DATA,
                )
            ]
        ]
    )


def keyboard_for_state(
    state_name: str | None,
) -> InlineKeyboardMarkup | None:
    """Диспетчер: по короткому имени состояния FSM отдаёт нужную клавиатуру.

    Принимает «AWAIT_SCENARIO» и т.п. (последнюю часть после ':').
    None/прочее → None (без клавиатуры).
    """
    if state_name == "AWAIT_SCENARIO":
        return scenario_keyboard(with_back=False)
    if state_name == "AWAIT_LIGHT":
        return light_keyboard(with_back=True)
    if state_name == "AWAIT_DISTANCE":
        return InlineKeyboardMarkup(inline_keyboard=[_back_row()])
    if state_name == "AWAIT_BUDGET":
        return budget_keyboard(with_back=True)
    if state_name == "AWAIT_CONSOLE":
        return console_keyboard(with_back=True)
    if state_name == "COMPLETED":
        return restart_keyboard()
    return None
