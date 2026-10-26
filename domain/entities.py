from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

MessageRole = Literal["user", "assistant"]


class Message(BaseModel):
    role: MessageRole
    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())


class ChatResult(BaseModel):
    text: str
    tokens_used: int = 0
    provider: str = "unknown"
    duration_ms: int = 0
