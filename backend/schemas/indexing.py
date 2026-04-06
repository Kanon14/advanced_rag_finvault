from __future__ import annotations

from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    collection_name: str | None = Field(default=None, max_length=128)


class IndexResponse(BaseModel):
    job_id: str
    document_id: str
    collection_name: str
    chunk_count: int
    indexed_count: int
    embedding_provider: str
    embedding_dimension: int
    status: str
    errors: list[str] = []
