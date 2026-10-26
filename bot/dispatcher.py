from aiogram import Dispatcher

from bot.handlers import router as root_router


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(root_router)
    return dp
