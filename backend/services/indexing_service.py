from __future__ import annotations

import json
import uuid
from pathlib import Path

from qdrant_client.http import models as qmodels

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.db.collections import ensure_collection
from backend.db.qdrant_client import get_qdrant_client
from backend.embeddings import build_embedder
from backend.schemas.indexing import IndexResponse

logger = get_logger(__name__)


class IndexingError(ValueError):
    pass


def _load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_paths(job_id: str) -> tuple[Path, Path]:
    base = Path("data") / "ingestion" / job_id
    chunks_path = base / "chunks.json"
    metadata_path = base / "metadata.json"
    if not chunks_path.exists():
        raise IndexingError(f"Missing chunks artifact: {chunks_path}")
    if not metadata_path.exists():
        raise IndexingError(f"Missing metadata artifact: {metadata_path}")
    return chunks_path, metadata_path


def index_job_artifacts(job_id: str, collection_name: str | None = None) -> IndexResponse:
    settings = get_settings()
    collection = collection_name or settings.qdrant_collection
    embedding_dim = settings.embedding_dimension

    chunks_path, metadata_path = _artifact_paths(job_id)
    chunks = _load_json(chunks_path)
    metadata = _load_json(metadata_path)

    if not isinstance(chunks, list):
        raise IndexingError("chunks.json must contain a list.")
    if not isinstance(metadata, dict):
        raise IndexingError("metadata.json must contain an object.")

    if len(chunks) == 0:
        raise IndexingError("No chunks to index.")

    client = get_qdrant_client()
    ensure_collection(client=client, collection_name=collection, vector_size=embedding_dim)

    embedder = build_embedder(dimension=embedding_dim)
    logger.info(
        "Indexing started job_id=%s collection=%s chunks=%s embedder=%s dim=%s",
        job_id,
        collection,
        len(chunks),
        embedder.provider_name,
        embedder.dimension,
    )

    points: list[qmodels.PointStruct] = []
    errors: list[str] = []

    for item in chunks:
        try:
            text = str(item.get("text", "")).strip()
            meta = item.get("metadata", {}) or {}
            chunk_id = str(item.get("chunk_id", meta.get("chunk_id", ""))).strip()
            chunk_index = int(item.get("chunk_index", meta.get("chunk_index", 0)))

            if not text:
                raise ValueError("chunk text is empty")
            if not chunk_id:
                raise ValueError("chunk_id is missing")

            vector = embedder.embed(text)

            payload = {
                "ingestion_job_id": job_id,
                "chunk_id": chunk_id,
                "chunk_index": chunk_index,
                "text": text,
                "document_id": meta.get("document_id"),
                "source_id": meta.get("source_id"),
                "filename": meta.get("filename"),
                "page_number": meta.get("page_number"),
                "section": meta.get("section"),
                "snippet": meta.get("snippet"),
                "metadata": meta,
            }

            points.append(
                qmodels.PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{job_id}:{chunk_id}")),
                    vector=vector,
                    payload=payload,
                )
            )
        except Exception as exc:
            errors.append(str(exc))

    if points:
        try:
            client.upsert(collection_name=collection, points=points, wait=True)
        except Exception as exc:
            raise IndexingError(f"Qdrant upsert failed: {exc}") from exc

    indexed_count = len(points)
    chunk_count = len(chunks)
    status = "completed" if indexed_count == chunk_count else "partial"

    summary = IndexResponse(
        job_id=job_id,
        document_id=str(metadata.get("filename", "unknown")).rsplit(".", 1)[0],
        collection_name=collection,
        chunk_count=chunk_count,
        indexed_count=indexed_count,
        embedding_provider=embedder.provider_name,
        embedding_dimension=embedder.dimension,
        status=status,
        errors=errors,
    )

    debug_dir = Path("data") / "indexing" / job_id
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / "index_summary.json").write_text(
        json.dumps(summary.model_dump(), indent=2),
        encoding="utf-8",
    )
    logger.info(
        "Indexing finished job_id=%s indexed=%s/%s collection=%s",
        job_id,
        indexed_count,
        chunk_count,
        collection,
    )

    return summary
