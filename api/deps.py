from fastapi import Request

from composition.container import Container
from features.consent import ConsentService
from features.dialog import DialogService


def get_container(request: Request) -> Container:
    container: Container = request.app.state.container
    return container


def get_dialog_service(request: Request) -> DialogService:
    return get_container(request).dialog_service


def get_consent_service(request: Request) -> ConsentService:
    return get_container(request).consent_service
