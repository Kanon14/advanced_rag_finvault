from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    collection_name: str | None = Field(default=None, max_length=128)
    min_score: float | None = Field(default=None, ge=-1.0, le=1.0)
    max_context_chars: int | None = Field(default=None, ge=200, le=20000)
    deduplicate: bool | None = None
    unique_pages: bool | None = None


class RetrieveMatch(BaseModel):
    score: float
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    retrieval_rank: int | None = None
    included_in_prompt: bool = True
    filtered_out_reason: str | None = None


class ExcludedMatch(BaseModel):
    chunk_id: str
    score: float
    reason: str


class RetrieveDiagnostics(BaseModel):
    provider: str
    embedding_dimension: int
    raw_candidate_count: int
    included_count: int
    excluded_count: int
    excluded_reasons: dict[str, int]


class RetrieveResponse(BaseModel):
    query: str
    top_k: int
    collection_name: str
    matches: list[RetrieveMatch]
    excluded: list[ExcludedMatch] = []
    diagnostics: RetrieveDiagnostics | None = None
