from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import router as root_router


def build_dispatcher() -> Dispatcher:
    # MemoryStorage хранит FSM-клавиатур воронки в памяти процесса бота.
    # Это НЕ ContextStore для LLM-истории (та по-прежнему в Redis, П4).
    # Trade-off: при рестарте бота пользователи вернутся в AWAIT_SCENARIO
    # (им придётся переначать воронку через /start) — осознанный компромисс для MVP.
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(root_router)
    return dp
