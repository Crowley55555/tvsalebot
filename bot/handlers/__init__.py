from aiogram import Router

from bot.handlers.callback import router as callback_router
from bot.handlers.start import router as start_router
from bot.handlers.text import router as text_router

router = Router()
router.include_router(start_router)
router.include_router(callback_router)
router.include_router(text_router)

__all__ = ["router"]
