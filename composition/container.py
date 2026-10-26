from dataclasses import dataclass
from pathlib import Path

from composition.env import AppSettings
from domain.ports import ContextStore, LLMClient, TVCatalog
from features.consent import ConsentService
from features.deletion import DeletionService
from features.dialog import DialogService
from infrastructure.context import build_context_store
from infrastructure.llm import build_llm_client
from infrastructure.tv_catalog import build_tv_catalog


def _load_system_prompt(prompts_dir: Path) -> str:
    path = prompts_dir / "system.md"
    return path.read_text(encoding="utf-8")


@dataclass
class Container:
    settings: AppSettings
    context_store: ContextStore
    llm_client: LLMClient
    tv_catalog: TVCatalog
    consent_service: ConsentService
    deletion_service: DeletionService
    dialog_service: DialogService

    async def aclose(self) -> None:
        for component in (self.context_store, self.llm_client):
            close = getattr(component, "aclose", None) or getattr(component, "close", None)
            if close is not None:
                await close()


def build_container(settings: AppSettings) -> Container:
    context_store = build_context_store(settings)
    llm_client = build_llm_client(settings)
    tv_catalog = build_tv_catalog(settings)
    consent_service = ConsentService(
        store=context_store, policy_version=settings.POLICY_VERSION
    )
    deletion_service = DeletionService(store=context_store)
    system_prompt = _load_system_prompt(settings.PROMPTS_DIR)
    dialog_service = DialogService(
        store=context_store,
        llm=llm_client,
        consent=consent_service,
        catalog=tv_catalog,
        system_prompt=system_prompt,
        max_history_messages=settings.MAX_HISTORY_MESSAGES,
    )
    return Container(
        settings=settings,
        context_store=context_store,
        llm_client=llm_client,
        tv_catalog=tv_catalog,
        consent_service=consent_service,
        deletion_service=deletion_service,
        dialog_service=dialog_service,
    )
