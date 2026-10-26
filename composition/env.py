from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: Literal["dev", "prod"] = "dev"

    BOT_TOKEN: SecretStr | None = None

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: SecretStr | None = None
    REDIS_TTL_SECONDS: int = 604800

    CORE_API_URL: str = "http://127.0.0.1:8000"
    CORE_API_BEARER_TOKEN: SecretStr | None = None


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()  # type: ignore[call-arg]
