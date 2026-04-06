from __future__ import annotations

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.db.qdrant_client import get_qdrant_client
from backend.embeddings import build_embedder
from backend.schemas.retrieve import RetrieveMatch, RetrieveResponse

logger = get_logger(__name__)


def retrieve_chunks(query: str, top_k: int, collection_name: str | None = None) -> RetrieveResponse:
    settings = get_settings()
    collection = collection_name or settings.qdrant_collection

    embedder = build_embedder(dimension=settings.embedding_dimension)
    query_vector = embedder.embed(query)

    client = get_qdrant_client()
    logger.info("Retrieval query collection=%s top_k=%s", collection, top_k)

    response = client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    results = response.points

    matches: list[RetrieveMatch] = []
    for item in results:
        payload = item.payload or {}
        matches.append(
            RetrieveMatch(
                score=float(item.score),
                chunk_id=str(payload.get("chunk_id", "")),
                text=str(payload.get("text", "")),
                metadata={
                    "document_id": payload.get("document_id"),
                    "source_id": payload.get("source_id"),
                    "filename": payload.get("filename"),
                    "page_number": payload.get("page_number"),
                    "section": payload.get("section"),
                    "chunk_index": payload.get("chunk_index"),
                    "snippet": payload.get("snippet"),
                    "ingestion_job_id": payload.get("ingestion_job_id"),
                },
            )
        )

    logger.info("Retrieval completed collection=%s returned=%s", collection, len(matches))
    return RetrieveResponse(
        query=query,
        top_k=top_k,
        collection_name=collection,
        matches=matches,
    )
