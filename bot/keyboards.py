from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CONSENT_CALLBACK_DATA = "consent:grant"
FUNNEL_CALLBACK_PREFIX = "funnel"


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


def _funnel_button(step: str, label: str, value: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=label, callback_data=f"{FUNNEL_CALLBACK_PREFIX}:{step}:{value}"
    )


def scenario_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _funnel_button("scenario", "🎬 Кино", "кино"),
                _funnel_button("scenario", "⚽ Спорт", "спорт"),
            ],
            [
                _funnel_button("scenario", "🎮 Игры", "игры"),
                _funnel_button("scenario", "📺 Фоновый ТВ", "фоновый ТВ"),
            ],
        ]
    )


def light_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _funnel_button("light", "☀️ Светло", "комната светлая"),
                _funnel_button(
                    "light", "🌥 Полумрак", "комната средней освещённости"
                ),
            ],
            [
                _funnel_button("light", "🌙 Темно", "комната тёмная"),
            ],
        ]
    )


def budget_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _funnel_button("budget", "до 50 тыс.", "бюджет до 50 тыс."),
                _funnel_button("budget", "50–100 тыс.", "бюджет 50–100 тыс."),
            ],
            [
                _funnel_button("budget", "100–150 тыс.", "бюджет 100–150 тыс."),
                _funnel_button("budget", "150+ тыс.", "бюджет свыше 150 тыс."),
            ],
        ]
    )


def console_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _funnel_button("console", "🎮 PS5 есть", "PS5 есть"),
                _funnel_button("console", "Нет консоли", "консоли нет"),
            ],
        ]
    )
