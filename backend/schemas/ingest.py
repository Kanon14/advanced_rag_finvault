from typing import Any, Literal

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    source_type: Literal["pdf", "text", "url"]
    source_value: str = Field(min_length=1, max_length=2048)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    job_id: str
    status: Literal["queued"]
    message: str


class IngestStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    progress: int = Field(ge=0, le=100)
    detail: str
