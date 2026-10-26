from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

MessageRole = Literal["user", "assistant"]

TVClass = Literal["neo_qled", "oled", "qled", "crystal_uhd", "lifestyle"]
Backlight = Literal[
    "mini_led", "oled", "full_array_led", "edge_led", "dual_led"
]


class Message(BaseModel):
    role: MessageRole
    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())


class ChatResult(BaseModel):
    text: str
    tokens_used: int = 0
    provider: str = "unknown"
    duration_ms: int = 0


class TVModel(BaseModel):
    """Спецификация одной модели Samsung TV.

    Поля — ориентир российского рынка 2024. Семантика полей и правила
    честности живут в `prompts/system.md` и `prompts/models.md`.
    """

    code: str
    trade_name: str
    tv_class: TVClass
    diagonals_inches: list[int]
    refresh_hz: int
    brightness_nits_min: int
    brightness_nits_max: int
    hdmi_version: str
    hdmi_ports: int
    backlight: Backlight
    price_min: int
    price_max: int
    fits_short: str
    honest_caveats: str
