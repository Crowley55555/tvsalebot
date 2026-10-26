import types
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.deps import get_consent_service, get_deletion_service, get_dialog_service
from api.main import app
from features.consent import ConsentService
from features.deletion import DeletionService
from features.dialog import DialogService
from infrastructure.context import InMemoryContextStore
from infrastructure.llm.fake import FakeLLMClient
from infrastructure.tv_catalog import MarkdownTVCatalog

TEST_SYSTEM_PROMPT = "You are a test consultant for Samsung TVs."
TEST_POLICY_VERSION = "test-v1"
TEST_POLICY_URL = "https://test.example/privacy"

_TEST_CATALOG_MD = """# Тестовый каталог

```toml
[[models]]
code = "TEST-A"
trade_name = "Test Alpha"
tv_class = "neo_qled"
diagonals_inches = [55, 65]
refresh_hz = 120
brightness_nits_min = 1000
brightness_nits_max = 1500
hdmi_version = "2.1"
hdmi_ports = 4
backlight = "mini_led"
price_min = 100000
price_max = 200000
fits_short = "Тест-модель А"
honest_caveats = "Нет Dolby Vision"

[[models]]
code = "TEST-B"
trade_name = "Test Beta"
tv_class = "oled"
diagonals_inches = [55, 65, 77]
refresh_hz = 144
brightness_nits_min = 800
brightness_nits_max = 1200
hdmi_version = "2.1"
hdmi_ports = 4
backlight = "oled"
price_min = 150000
price_max = 300000
fits_short = "Тест-модель Б"
honest_caveats = "Нет Dolby Vision"
```

## Test Alpha

Описание A.

## Test Beta

Описание B.
"""


@pytest.fixture
def catalog_file(tmp_path: Path) -> Path:
    path = tmp_path / "models.md"
    path.write_text(_TEST_CATALOG_MD, encoding="utf-8")
    return path


@pytest.fixture
def catalog(catalog_file: Path) -> MarkdownTVCatalog:
    return MarkdownTVCatalog(catalog_file)


@pytest.fixture
def store() -> InMemoryContextStore:
    return InMemoryContextStore()


@pytest.fixture
def fake_llm() -> FakeLLMClient:
    return FakeLLMClient(programmed_reply="test-reply")


@pytest.fixture
def consent_service(store: InMemoryContextStore) -> ConsentService:
    return ConsentService(store=store, policy_version=TEST_POLICY_VERSION)


@pytest.fixture
def deletion_service(store: InMemoryContextStore) -> DeletionService:
    return DeletionService(store=store)


@pytest.fixture
def dialog_service(
    store: InMemoryContextStore,
    fake_llm: FakeLLMClient,
    consent_service: ConsentService,
    catalog: MarkdownTVCatalog,
) -> DialogService:
    return DialogService(
        store=store,
        llm=fake_llm,
        consent=consent_service,
        catalog=catalog,
        system_prompt=TEST_SYSTEM_PROMPT,
        max_history_messages=30,
    )


@pytest.fixture
def client(
    dialog_service: DialogService,
    consent_service: ConsentService,
    deletion_service: DeletionService,
) -> Iterator[TestClient]:
    app.state.container = types.SimpleNamespace(
        settings=types.SimpleNamespace(PRIVACY_POLICY_URL=TEST_POLICY_URL),
    )
    app.dependency_overrides[get_dialog_service] = lambda: dialog_service
    app.dependency_overrides[get_consent_service] = lambda: consent_service
    app.dependency_overrides[get_deletion_service] = lambda: deletion_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.state.container = None
