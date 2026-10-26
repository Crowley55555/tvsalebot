from aiogram import Router

from bot.handlers.text import router as text_router

router = Router()
router.include_router(text_router)

__all__ = ["router"]
