import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from api.deps import (
    get_consent_service,
    get_container,
    get_deletion_service,
    get_dialog_service,
)
from api.schemas import (
    ChatRequest,
    ChatResponse,
    ConsentGrantRequest,
    ConsentGrantResponse,
    ConsentRequiredResponse,
    GdprStopRequest,
    GdprStopResponse,
)
from composition.container import Container
from domain import ConsentRequired
from features.consent import ConsentService
from features.deletion import DeletionService
from features.dialog import DialogService

log = logging.getLogger("api.routes")

router = APIRouter()


@router.get("/health")
async def health(
    container: Annotated[Container, Depends(get_container)],
) -> Response:
    """Публичный health-check: проверяет живость Redis через порт ContextStore.

    Не требует консента, не читает ПДн — публичная ручка для UptimeRobot/compose.
    """
    try:
        await container.context_store.ping()
    except Exception as exc:
        log.warning("health_redis_down: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "redis": "unreachable"},
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "redis": "ok"},
    )


@router.post("/chat")
async def chat(
    body: ChatRequest,
    request: Request,
    dialog: Annotated[DialogService, Depends(get_dialog_service)],
) -> Response:
    try:
        reply = await dialog.handle_user_message(
            telegram_id=body.telegram_id,
            text=body.text,
            update_id=body.update_id,
        )
    except ConsentRequired:
        settings = request.app.state.container.settings
        payload = ConsentRequiredResponse(
            user_message=(
                "Нужно согласие на обработку персональных данных. "
                "Отправь /start и нажми кнопку «Согласен»."
            ),
            policy_url=settings.PRIVACY_POLICY_URL,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content=payload.model_dump()
        )
    except ConnectionError as exc:
        log.error("storage_unavailable: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="storage_unavailable",
        ) from exc
    except Exception as exc:
        log.exception("unexpected_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal_error",
        ) from exc
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ChatResponse(reply=reply).model_dump(),
    )


@router.post("/consent/grant", response_model=ConsentGrantResponse)
async def consent_grant(
    body: ConsentGrantRequest,
    consent: Annotated[ConsentService, Depends(get_consent_service)],
) -> ConsentGrantResponse:
    await consent.grant(body.telegram_id)
    return ConsentGrantResponse(granted=True, policy_version=consent.policy_version)


@router.post("/gdpr/stop", response_model=GdprStopResponse)
async def gdpr_stop(
    body: GdprStopRequest,
    deletion: Annotated[DeletionService, Depends(get_deletion_service)],
) -> GdprStopResponse:
    result = await deletion.delete_user_data(body.telegram_id, body.reason)
    return GdprStopResponse(
        deleted=True,
        deleted_keys=result.deleted_keys,
        reason=result.reason,
    )
