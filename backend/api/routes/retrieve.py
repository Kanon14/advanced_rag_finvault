from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.core.logging import get_logger
from backend.schemas.common import ErrorResponse
from backend.schemas.retrieve import RetrieveRequest, RetrieveResponse
from backend.services.retrieval_service import retrieve_chunks

router = APIRouter(tags=["retrieval"])
logger = get_logger(__name__)


@router.post(
    "/retrieve",
    response_model=RetrieveResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def retrieve(payload: RetrieveRequest) -> RetrieveResponse:
    logger.info("Received retrieve request top_k=%s", payload.top_k)
    try:
        return retrieve_chunks(
            query=payload.query,
            top_k=payload.top_k,
            collection_name=payload.collection_name,
        )
    except Exception as exc:
        logger.warning("Retrieve failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
