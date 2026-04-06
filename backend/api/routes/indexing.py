from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path

from backend.core.logging import get_logger
from backend.schemas.common import ErrorResponse
from backend.schemas.indexing import IndexRequest, IndexResponse
from backend.services.indexing_service import IndexingError, index_job_artifacts

router = APIRouter(tags=["indexing"])
logger = get_logger(__name__)


@router.post(
    "/index/{job_id}",
    response_model=IndexResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def index_job(
    job_id: str = Path(min_length=4, max_length=64),
    payload: IndexRequest | None = None,
) -> IndexResponse:
    logger.info("Received index request job_id=%s", job_id)
    try:
        collection_name = payload.collection_name if payload else None
        return index_job_artifacts(job_id=job_id, collection_name=collection_name)
    except IndexingError as exc:
        logger.warning("Indexing failed validation job_id=%s error=%s", job_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
