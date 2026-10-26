from dataclasses import dataclass

from composition.env import AppSettings
from domain.ports import ContextStore
from features.dialog import DialogService
from infrastructure.context import build_context_store


@dataclass
class Container:
    settings: AppSettings
    context_store: ContextStore
    dialog_service: DialogService

    async def aclose(self) -> None:
        close = getattr(self.context_store, "close", None)
        if close is not None:
            await close()


def build_container(settings: AppSettings) -> Container:
    context_store = build_context_store(settings)
    dialog_service = DialogService(store=context_store)
    return Container(
        settings=settings,
        context_store=context_store,
        dialog_service=dialog_service,
    )
