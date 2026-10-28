from typing import Final

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CONSENT_CALLBACK_DATA = "consent:grant"
FUNNEL_CALLBACK_PREFIX = "funnel"

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


def scenario_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _funnel_button("scenario", "🎬 Кино", "movie"),
                _funnel_button("scenario", "⚽ Спорт", "sport"),
            ],
            [
                _funnel_button("scenario", "🎮 Игры", "games"),
                _funnel_button("scenario", "📺 Фоновый ТВ", "bg"),
            ],
        ]
    )


def light_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _funnel_button("light", "☀️ Светло", "bright"),
                _funnel_button("light", "🌥 Полумрак", "mid"),
            ],
            [
                _funnel_button("light", "🌙 Темно", "dark"),
            ],
        ]
    )


def budget_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _funnel_button("budget", "до 50 тыс.", "lt50"),
                _funnel_button("budget", "50–100 тыс.", "50-100"),
            ],
            [
                _funnel_button("budget", "100–150 тыс.", "100-150"),
                _funnel_button("budget", "150+ тыс.", "gt150"),
            ],
        ]
    )


def console_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _funnel_button("console", "🎮 PS5 есть", "ps5"),
                _funnel_button("console", "Нет консоли", "none"),
            ],
        ]
    )
