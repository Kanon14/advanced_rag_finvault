from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from backend.ingestion.models import ChunkRecord, ParsedPage


def ensure_job_dir(job_id: str) -> Path:
    job_dir = Path("data") / "ingestion" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_ingestion_artifacts(
    job_id: str,
    raw_pages: list[ParsedPage],
    normalized_markdown: str,
    chunks: list[ChunkRecord],
    metadata: dict[str, Any],
) -> dict[str, str]:
    job_dir = ensure_job_dir(job_id)

    raw_path = job_dir / "raw_pages.json"
    normalized_path = job_dir / "normalized.md"
    chunks_path = job_dir / "chunks.json"
    metadata_path = job_dir / "metadata.json"
    manifest_path = job_dir / "manifest.json"

    write_json(raw_path, [asdict(page) for page in raw_pages])
    normalized_path.write_text(normalized_markdown, encoding="utf-8")
    write_json(chunks_path, [asdict(chunk) for chunk in chunks])
    write_json(metadata_path, metadata)

    manifest = {
        "job_id": job_id,
        "artifacts": {
            "raw_pages": str(raw_path),
            "normalized_markdown": str(normalized_path),
            "chunks": str(chunks_path),
            "metadata": str(metadata_path),
        },
        "counts": {
            "pages": len(raw_pages),
            "chunks": len(chunks),
        },
    }
    write_json(manifest_path, manifest)

    return {
        "job_dir": str(job_dir),
        "raw_pages": str(raw_path),
        "normalized_markdown": str(normalized_path),
        "chunks": str(chunks_path),
        "metadata": str(metadata_path),
        "manifest": str(manifest_path),
    }
