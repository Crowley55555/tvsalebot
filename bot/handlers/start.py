import logging
from pathlib import Path

from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards import consent_keyboard

log = logging.getLogger("bot.handlers.start")

router = Router()

_FALLBACK_GREETING = "Привет! Нажми кнопку, чтобы согласиться с политикой ПДн."


def _load_greeting(prompts_dir: Path) -> str:
    try:
        return (prompts_dir / "start_greeting.md").read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return _FALLBACK_GREETING


@router.message(CommandStart(), lambda m: m.chat.type == ChatType.PRIVATE)
async def on_start(message: Message, prompts_dir: Path, policy_url: str) -> None:
    greeting = _load_greeting(prompts_dir)
    await message.answer(greeting, reply_markup=consent_keyboard(policy_url))
