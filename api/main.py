import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from composition.container import build_container
from composition.env import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    container = build_container(settings)
    app.state.container = container
    try:
        yield
    finally:
        await container.aclose()


app = FastAPI(title="tvsalebot-core-api", version="0.0.1", lifespan=lifespan)
app.include_router(router)
