from uuid import uuid4

from backend.schemas.ingest import IngestRequest, IngestResponse, IngestStatusResponse


def queue_ingestion(_payload: IngestRequest) -> IngestResponse:
    job_id = f"job_{uuid4().hex[:12]}"
    return IngestResponse(
        job_id=job_id,
        status="queued",
        message="Mock ingestion accepted and queued.",
    )


def get_ingestion_status(job_id: str) -> IngestStatusResponse:
    if not job_id.startswith("job_") or len(job_id) < 8:
        return IngestStatusResponse(
            job_id=job_id,
            status="failed",
            progress=0,
            detail="Unknown job id format in mock backend.",
        )

    states = [
        ("queued", 10, "Waiting for worker slot (mock)."),
        ("processing", 55, "Parsing and chunking documents (mock)."),
        ("completed", 100, "Ingestion completed successfully (mock)."),
    ]
    idx = sum(ord(ch) for ch in job_id) % len(states)
    state, progress, detail = states[idx]
    return IngestStatusResponse(job_id=job_id, status=state, progress=progress, detail=detail)
