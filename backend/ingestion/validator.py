from __future__ import annotations

from pathlib import Path

from backend.schemas.ingest import IngestRequest


class IngestionValidationError(ValueError):
    pass


def _resolve_source_path(raw_value: str) -> Path | None:
    cleaned = raw_value.strip().strip('"').strip("'")
    incoming = Path(cleaned).expanduser()

    candidates: list[Path] = []
    if incoming.is_absolute():
        candidates.append(incoming)
    else:
        cwd = Path.cwd()
        candidates.extend(
            [
                cwd / incoming,
                cwd / "data" / incoming,
                cwd / "data" / incoming.name,
            ]
        )

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def validate_ingest_request(payload: IngestRequest) -> Path:
    if payload.source_type != "pdf":
        raise IngestionValidationError(
            "Stage 3 supports local PDF ingestion only. Use source_type='pdf'."
        )

    source_path = _resolve_source_path(payload.source_value)
    if source_path is None:
        raise IngestionValidationError(
            "Source file does not exist. Use an absolute path or a path relative to project root/data. "
            f"Received: {payload.source_value}"
        )
    if not source_path.is_file():
        raise IngestionValidationError(f"Source path is not a file: {source_path}")
    if source_path.suffix.lower() != ".pdf":
        raise IngestionValidationError("Unsupported file type. Only .pdf is allowed.")

    try:
        with source_path.open("rb"):
            pass
    except OSError as exc:
        raise IngestionValidationError(f"Unable to read file: {source_path}. Error: {exc}") from exc

    return source_path
