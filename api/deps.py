from fastapi import Request

from composition.container import Container
from features.dialog import DialogService


def get_container(request: Request) -> Container:
    container: Container = request.app.state.container
    return container


def get_dialog_service(request: Request) -> DialogService:
    return get_container(request).dialog_service
