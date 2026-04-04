from fastapi import APIRouter, Path

from backend.core.logging import get_logger
from backend.schemas.common import ErrorResponse
from backend.schemas.ingest import IngestRequest, IngestResponse, IngestStatusResponse
from backend.services.mock_ingestion import get_ingestion_status, queue_ingestion

router = APIRouter(tags=["ingestion"])
logger = get_logger(__name__)


@router.post(
    "/ingest",
    response_model=IngestResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def ingest(payload: IngestRequest) -> IngestResponse:
    logger.info("Received mock ingest request source_type=%s", payload.source_type)
    response = queue_ingestion(payload)
    logger.info("Mock ingest queued with job_id=%s", response.job_id)
    return response


@router.get(
    "/ingest/{job_id}/status",
    response_model=IngestStatusResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def ingest_status(job_id: str = Path(min_length=4, max_length=64)) -> IngestStatusResponse:
    logger.info("Received status request for job_id=%s", job_id)
    return get_ingestion_status(job_id)
