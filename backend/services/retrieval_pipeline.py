from __future__ import annotations

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.db.qdrant_client import get_qdrant_client
from backend.embeddings import build_embedder
from backend.schemas.retrieve import RetrieveDiagnostics, RetrieveMatch, RetrieveResponse
from backend.services.retrieval_filters import FilterOptions, filter_candidates

logger = get_logger(__name__)


def _to_matches(results: list) -> list[RetrieveMatch]:
    matches: list[RetrieveMatch] = []
    for idx, item in enumerate(results, start=1):
        payload = item.payload or {}
        matches.append(
            RetrieveMatch(
                score=float(item.score),
                chunk_id=str(payload.get("chunk_id", "")),
                text=str(payload.get("text", "")),
                retrieval_rank=idx,
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
    return matches


def retrieve_with_controls(
    *,
    query: str,
    top_k: int,
    collection_name: str | None,
    min_score: float | None,
    max_context_chars: int | None,
    deduplicate: bool | None,
    unique_pages: bool | None,
) -> RetrieveResponse:
    settings = get_settings()
    collection = collection_name or settings.qdrant_collection

    embedder = build_embedder()
    query_vector = embedder.embed(query)
    logger.info(
        "Retrieval start provider=%s dim=%s collection=%s top_k=%s",
        embedder.provider_name,
        embedder.dimension,
        collection,
        top_k,
    )

    client = get_qdrant_client()
    fetch_k = max(top_k * 4, top_k)
    response = client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=fetch_k,
        with_payload=True,
    )
    raw_matches = _to_matches(response.points)
    logger.info("Retrieval raw candidate count=%s", len(raw_matches))

    options = FilterOptions(
        min_score=min_score if min_score is not None else settings.retrieval_min_score,
        max_context_chars=(
            max_context_chars
            if max_context_chars is not None
            else settings.retrieval_max_context_chars
        ),
        deduplicate=deduplicate if deduplicate is not None else settings.retrieval_deduplicate,
        unique_pages=unique_pages if unique_pages is not None else settings.retrieval_unique_pages,
    )

    filtered, excluded, reasons = filter_candidates(raw_matches, options)
    final_matches = filtered[:top_k]

    logger.info(
        "Retrieval filtered included=%s excluded=%s reasons=%s",
        len(final_matches),
        len(excluded),
        reasons,
    )

    diagnostics = RetrieveDiagnostics(
        provider=embedder.provider_name,
        embedding_dimension=embedder.dimension,
        raw_candidate_count=len(raw_matches),
        included_count=len(final_matches),
        excluded_count=len(excluded),
        excluded_reasons=reasons,
    )

    return RetrieveResponse(
        query=query,
        top_k=top_k,
        collection_name=collection,
        matches=final_matches,
        excluded=excluded,
        diagnostics=diagnostics,
    )
