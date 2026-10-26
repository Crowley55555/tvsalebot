from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    telegram_id: int = Field(..., description="Telegram user id")
    text: str = Field(..., min_length=1, max_length=4096)
    update_id: int | None = Field(
        default=None,
        description="Telegram update_id для дедупа повторных доставок (long-poll retry).",
    )


class ChatResponse(BaseModel):
    reply: str


class ErrorPayload(BaseModel):
    detail: str
