import asyncio
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from bot.core_api_client import CoreAPIClient
from bot.dispatcher import build_dispatcher
from composition.env import get_settings

log = logging.getLogger("bot.main")


def _resolve_bearer(settings_obj) -> str | None:  # type: ignore[no-untyped-def]
    raw = settings_obj.CORE_API_BEARER_TOKEN
    if raw is None:
        return None
    return raw.get_secret_value()


async def _main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    settings = get_settings()
    if settings.BOT_TOKEN is None:
        raise RuntimeError("BOT_TOKEN не задан; добавь в .env")

    tg_cred = settings.BOT_TOKEN.get_secret_value()
    auth = _resolve_bearer(settings)

    core_api_client = CoreAPIClient(
        base_url=settings.CORE_API_URL,
        bearer_token=auth,
    )
    bot = Bot(tg_cred, default=DefaultBotProperties(parse_mode=None))

    dp = build_dispatcher()
    dp["core_api_client"] = core_api_client

    try:
        log.info("bot_started env=%s core_api=%s", settings.ENVIRONMENT, settings.CORE_API_URL)
        await dp.start_polling(bot)
    finally:
        await core_api_client.aclose()
        await bot.session.close()


def run() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    run()
