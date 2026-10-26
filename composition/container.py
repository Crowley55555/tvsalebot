from dataclasses import dataclass
from pathlib import Path

from composition.env import AppSettings
from domain.ports import ContextStore, LLMClient
from features.dialog import DialogService
from infrastructure.context import build_context_store
from infrastructure.llm import build_llm_client


def _load_system_prompt(prompts_dir: Path) -> str:
    path = prompts_dir / "system.md"
    return path.read_text(encoding="utf-8")


@dataclass
class Container:
    settings: AppSettings
    context_store: ContextStore
    llm_client: LLMClient
    dialog_service: DialogService

    async def aclose(self) -> None:
        for component in (self.context_store, self.llm_client):
            close = getattr(component, "aclose", None) or getattr(component, "close", None)
            if close is not None:
                await close()


def build_container(settings: AppSettings) -> Container:
    context_store = build_context_store(settings)
    llm_client = build_llm_client(settings)
    system_prompt = _load_system_prompt(settings.PROMPTS_DIR)
    dialog_service = DialogService(
        store=context_store,
        llm=llm_client,
        system_prompt=system_prompt,
        max_history_messages=settings.MAX_HISTORY_MESSAGES,
    )
    return Container(
        settings=settings,
        context_store=context_store,
        llm_client=llm_client,
        dialog_service=dialog_service,
    )
