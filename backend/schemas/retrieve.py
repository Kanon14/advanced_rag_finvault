from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    collection_name: str | None = Field(default=None, max_length=128)


class RetrieveMatch(BaseModel):
    score: float
    chunk_id: str
    text: str
    metadata: dict[str, Any]


class RetrieveResponse(BaseModel):
    query: str
    top_k: int
    collection_name: str
    matches: list[RetrieveMatch]
