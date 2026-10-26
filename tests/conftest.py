from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from api.deps import get_dialog_service
from api.main import app
from features.dialog import DialogService
from infrastructure.context import InMemoryContextStore
from infrastructure.llm.fake import FakeLLMClient

TEST_SYSTEM_PROMPT = "You are a test consultant for Samsung TVs."


@pytest.fixture
def fake_llm() -> FakeLLMClient:
    return FakeLLMClient(programmed_reply="test-reply")


@pytest.fixture
def dialog_service(fake_llm: FakeLLMClient) -> DialogService:
    return DialogService(
        store=InMemoryContextStore(),
        llm=fake_llm,
        system_prompt=TEST_SYSTEM_PROMPT,
        max_history_messages=30,
    )


@pytest.fixture
def client(dialog_service: DialogService) -> Iterator[TestClient]:
    app.dependency_overrides[get_dialog_service] = lambda: dialog_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
