from __future__ import annotations

from backend.schemas.retrieve import RetrieveResponse
from backend.services.retrieval_pipeline import retrieve_with_controls


def retrieve_chunks(
    query: str,
    top_k: int,
    collection_name: str | None = None,
    min_score: float | None = None,
    max_context_chars: int | None = None,
    deduplicate: bool | None = None,
    unique_pages: bool | None = None,
) -> RetrieveResponse:
    return retrieve_with_controls(
        query=query,
        top_k=top_k,
        collection_name=collection_name,
        min_score=min_score,
        max_context_chars=max_context_chars,
        deduplicate=deduplicate,
        unique_pages=unique_pages,
    )
