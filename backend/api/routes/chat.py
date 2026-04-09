from fastapi import APIRouter, HTTPException

from backend.core.logging import get_logger
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.schemas.common import ErrorResponse
from backend.services.chat_service import ChatServiceError, generate_chat_response

router = APIRouter(tags=["chat"])
logger = get_logger(__name__)


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def chat(payload: ChatRequest) -> ChatResponse:
    logger.info(
        "Received chat request session_id=%s collection_name=%s min_score=%s",
        payload.session_id,
        payload.collection_name,
        payload.min_score,
    )
    try:
        response = generate_chat_response(payload)
        logger.info("Returning chat response with %s citations", len(response.citations))
        return response
    except ChatServiceError as exc:
        logger.warning("Chat generation unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
