from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from api.deps import get_dialog_service
from api.main import app
from features.dialog import DialogService
from infrastructure.context import InMemoryContextStore


@pytest.fixture
def dialog_service() -> DialogService:
    return DialogService(store=InMemoryContextStore())


@pytest.fixture
def client(dialog_service: DialogService) -> Iterator[TestClient]:
    app.dependency_overrides[get_dialog_service] = lambda: dialog_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
