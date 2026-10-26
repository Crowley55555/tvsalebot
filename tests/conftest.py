import types
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from api.deps import get_consent_service, get_dialog_service
from api.main import app
from features.consent import ConsentService
from features.dialog import DialogService
from infrastructure.context import InMemoryContextStore
from infrastructure.llm.fake import FakeLLMClient

TEST_SYSTEM_PROMPT = "You are a test consultant for Samsung TVs."
TEST_POLICY_VERSION = "test-v1"
TEST_POLICY_URL = "https://test.example/privacy"


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
def dialog_service(
    store: InMemoryContextStore,
    fake_llm: FakeLLMClient,
    consent_service: ConsentService,
) -> DialogService:
    return DialogService(
        store=store,
        llm=fake_llm,
        consent=consent_service,
        system_prompt=TEST_SYSTEM_PROMPT,
        max_history_messages=30,
    )


@pytest.fixture
def client(
    dialog_service: DialogService,
    consent_service: ConsentService,
) -> Iterator[TestClient]:
    app.state.container = types.SimpleNamespace(
        settings=types.SimpleNamespace(PRIVACY_POLICY_URL=TEST_POLICY_URL),
    )
    app.dependency_overrides[get_dialog_service] = lambda: dialog_service
    app.dependency_overrides[get_consent_service] = lambda: consent_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.state.container = None
