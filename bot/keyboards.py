from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CONSENT_CALLBACK_DATA = "consent:grant"


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
