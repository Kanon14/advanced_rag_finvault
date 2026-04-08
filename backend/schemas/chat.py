from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=128)
    top_k: int = Field(default=3, ge=1, le=10)
    collection_name: str | None = Field(default=None, max_length=128)


class Citation(BaseModel):
    source_id: str
    title: str
    chunk_id: str
    score: float = Field(ge=-1.0, le=1.0)
    filename: str | None = None
    page_number: int | None = None
    chunk_index: int | None = None
    snippet: str | None = None
    document_id: str | None = None
    ingestion_job_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    mocked: bool = False
    request_id: str | None = None
    model: str | None = None
    retrieval_count: int = 0
