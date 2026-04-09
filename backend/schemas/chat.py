from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=128)
    top_k: int = Field(default=3, ge=1, le=10)
    collection_name: str | None = Field(default=None, max_length=128)
    min_score: float | None = Field(default=None, ge=-1.0, le=1.0)
    max_context_chars: int | None = Field(default=None, ge=200, le=20000)
    deduplicate: bool | None = None
    unique_pages: bool | None = None


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
    retrieval_rank: int | None = None
    included_in_prompt: bool = True
    filtered_out_reason: str | None = None


class ChatDiagnostics(BaseModel):
    provider: str
    embedding_dimension: int
    raw_candidate_count: int
    included_count: int
    excluded_count: int
    excluded_reasons: dict[str, int]
    context_chars: int


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    mocked: bool = False
    request_id: str | None = None
    model: str | None = None
    retrieval_count: int = 0
    diagnostics: ChatDiagnostics | None = None
