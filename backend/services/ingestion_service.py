from __future__ import annotations

import re
from pathlib import Path
from threading import Thread
from uuid import uuid4

from backend.core.logging import get_logger
from backend.ingestion.artifacts import write_ingestion_artifacts
from backend.ingestion.chunker import build_chunks
from backend.ingestion.job_store import JobStore
from backend.ingestion.normalizer import normalize_document
from backend.ingestion.parsers import build_parser
from backend.ingestion.validator import IngestionValidationError, validate_ingest_request
from backend.schemas.ingest import IngestRequest, IngestResponse, IngestStatusResponse

logger = get_logger(__name__)
job_store = JobStore()


def save_uploaded_pdf(filename: str, content: bytes) -> Path:
    safe_name = Path(filename).name
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", safe_name)
    if not safe_name.lower().endswith(".pdf"):
        raise IngestionValidationError("Uploaded file must have .pdf extension.")
    if not content:
        raise IngestionValidationError("Uploaded file is empty.")

    upload_dir = Path("data") / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_path = upload_dir / f"upload_{uuid4().hex[:10]}_{safe_name}"
    stored_path.write_bytes(content)
    return stored_path.resolve()


def start_ingestion_job(payload: IngestRequest) -> IngestResponse:
    if payload.source_type != "pdf":
        raise IngestionValidationError("Only source_type='pdf' is supported in Stage 3.")

    job_id = f"job_{uuid4().hex[:12]}"
    job_store.create(
        job_id=job_id, source_type=payload.source_type, source_value=payload.source_value
    )

    worker = Thread(target=_run_ingestion_pipeline, args=(job_id, payload), daemon=True)
    worker.start()

    logger.info("Ingestion job created job_id=%s source_value=%s", job_id, payload.source_value)
    return IngestResponse(
        job_id=job_id,
        status="queued",
        message="Ingestion job accepted and queued.",
    )


def get_ingestion_status(job_id: str) -> IngestStatusResponse:
    state = job_store.get(job_id)
    if state is None:
        return IngestStatusResponse(
            job_id=job_id,
            status="failed",
            progress=0,
            detail="Job not found.",
            error="unknown_job_id",
        )

    return IngestStatusResponse(
        job_id=state.job_id,
        status=state.status,
        progress=state.progress,
        detail=state.detail,
        artifacts=state.artifacts or None,
        summary=state.summary or None,
        error=state.error,
    )


def _run_ingestion_pipeline(job_id: str, payload: IngestRequest) -> None:
    try:
        job_store.update(
            job_id,
            status="validating",
            progress=15,
            detail="Validating source path and file type.",
        )
        source_path = validate_ingest_request(payload)
        logger.info("Job %s validated source=%s", job_id, source_path)

        job_store.update(
            job_id,
            status="parsing",
            progress=35,
            detail="Parsing PDF into page text.",
        )
        parser = build_parser()
        parsed = parser.parse(source_path)
        logger.info(
            "Job %s parsed pages=%s parser=%s", job_id, len(parsed.pages), parser.parser_name
        )

        job_store.update(
            job_id,
            status="normalizing",
            progress=55,
            detail="Normalizing parsed content.",
        )
        normalized_pages, normalized_markdown = normalize_document(parsed)

        job_store.update(
            job_id,
            status="chunking",
            progress=75,
            detail="Splitting document into chunks.",
        )
        document_id = Path(parsed.filename).stem.lower().replace(" ", "_")
        source_id = document_id
        chunks = build_chunks(
            pages=normalized_pages,
            document_id=document_id,
            source_id=source_id,
            filename=parsed.filename,
        )

        metadata = {
            "job_id": job_id,
            "parser": parser.parser_name,
            "source_type": payload.source_type,
            "source_value": payload.source_value,
            "filename": parsed.filename,
            "page_count": len(parsed.pages),
            "chunk_count": len(chunks),
            "metadata": payload.metadata,
        }
        artifacts = write_ingestion_artifacts(
            job_id=job_id,
            raw_pages=parsed.pages,
            normalized_markdown=normalized_markdown,
            chunks=chunks,
            metadata=metadata,
        )

        summary = {
            "parser": parser.parser_name,
            "page_count": len(parsed.pages),
            "chunk_count": len(chunks),
            "document_id": document_id,
            "source_id": source_id,
        }
        job_store.update(
            job_id,
            status="completed",
            progress=100,
            detail="Ingestion completed. Artifacts written to local storage.",
            artifacts=artifacts,
            summary=summary,
            error=None,
        )
        logger.info("Job %s completed chunks=%s", job_id, len(chunks))
    except Exception as exc:
        logger.exception("Job %s failed during ingestion", job_id)
        job_store.update(
            job_id,
            status="failed",
            progress=100,
            detail="Ingestion failed.",
            error=str(exc),
        )
