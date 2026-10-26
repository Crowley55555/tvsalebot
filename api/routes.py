import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_dialog_service
from api.schemas import ChatRequest, ChatResponse
from features.dialog import DialogService

log = logging.getLogger("api.routes")

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    dialog: Annotated[DialogService, Depends(get_dialog_service)],
) -> ChatResponse:
    try:
        reply = await dialog.handle_user_message(
            telegram_id=body.telegram_id,
            text=body.text,
            update_id=body.update_id,
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
    return ChatResponse(reply=reply)
