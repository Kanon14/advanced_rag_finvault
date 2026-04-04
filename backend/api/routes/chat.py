from fastapi import APIRouter

from backend.core.logging import get_logger
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.schemas.common import ErrorResponse
from backend.services.mock_chat import generate_mock_chat_response

router = APIRouter(tags=["chat"])
logger = get_logger(__name__)


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def chat(payload: ChatRequest) -> ChatResponse:
    logger.info("Received chat request session_id=%s", payload.session_id)
    response = generate_mock_chat_response(payload)
    logger.info("Returning mock chat response with %s citations", len(response.citations))
    return response
