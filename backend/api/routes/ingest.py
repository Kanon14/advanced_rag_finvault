import json

from fastapi import APIRouter, File, Form, HTTPException, Path, UploadFile

from backend.core.logging import get_logger
from backend.ingestion.validator import IngestionValidationError
from backend.schemas.common import ErrorResponse
from backend.schemas.ingest import IngestRequest, IngestResponse, IngestStatusResponse
from backend.services.ingestion_service import (
    get_ingestion_status,
    save_uploaded_pdf,
    start_ingestion_job,
)

router = APIRouter(tags=["ingestion"])
logger = get_logger(__name__)


@router.post(
    "/ingest",
    response_model=IngestResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def ingest(payload: IngestRequest) -> IngestResponse:
    logger.info("Received ingest request source_type=%s", payload.source_type)
    try:
        response = start_ingestion_job(payload)
        logger.info("Ingestion job queued job_id=%s", response.job_id)
        return response
    except IngestionValidationError as exc:
        logger.warning("Ingest validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/ingest/upload",
    response_model=IngestResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def ingest_upload(
    file: UploadFile = File(...),
    metadata_json: str = Form(default="{}"),
) -> IngestResponse:
    logger.info("Received ingest upload request filename=%s", file.filename)
    try:
        metadata_obj = json.loads(metadata_json) if metadata_json else {}
        if not isinstance(metadata_obj, dict):
            raise IngestionValidationError("metadata_json must be a JSON object.")

        file_bytes = await file.read()
        stored_path = save_uploaded_pdf(file.filename or "uploaded.pdf", file_bytes)
        payload = IngestRequest(
            source_type="pdf",
            source_value=str(stored_path),
            metadata=metadata_obj,
        )
        response = start_ingestion_job(payload)
        logger.info(
            "Ingestion upload queued job_id=%s stored_path=%s", response.job_id, stored_path
        )
        return response
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="metadata_json must be valid JSON.") from exc
    except IngestionValidationError as exc:
        logger.warning("Ingest upload validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/ingest/{job_id}/status",
    response_model=IngestStatusResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def ingest_status(job_id: str = Path(min_length=4, max_length=64)) -> IngestStatusResponse:
    logger.info("Received status request for job_id=%s", job_id)
    return get_ingestion_status(job_id)
