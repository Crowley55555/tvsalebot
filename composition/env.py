from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, model_validator
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

    LLM_PROVIDER: Literal["gigachat"] = "gigachat"
    LLM_MODEL: str = "GigaChat-2-Pro"
    GIGACHAT_API_KEY: SecretStr | None = None
    GIGACHAT_SCOPE: str = "GIGACHAT_API_PERS"

    PROMPTS_DIR: Path = Path("prompts")
    MAX_HISTORY_MESSAGES: int = 30

    POLICY_VERSION: str = "v1-2026-10-26"
    PRIVACY_POLICY_URL: str = "https://example.com/privacy"

    @model_validator(mode="after")
    def _enforce_prod_llm_provider(self) -> "AppSettings":
        """Страховка под П7-б: в prod разрешены только РФ-провайдеры.

        Текущий Literal уже эквивалентен {"gigachat"}, валидатор добавлен
        «на вырост» — чтобы расширение Literal до {"gigachat", "yandex"}
        не открыло случайно доступ зарубежным провайдерам в проде.
        """
        if self.ENVIRONMENT == "prod" and self.LLM_PROVIDER not in {
            "gigachat",
            "yandex",
        }:
            raise ValueError(
                f"В prod разрешены только LLM_PROVIDER=gigachat или yandex; "
                f"получено: {self.LLM_PROVIDER!r} (ФЗ-152, П7-б)"
            )
        return self


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()  # type: ignore[call-arg]
