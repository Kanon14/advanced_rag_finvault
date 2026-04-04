from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=128)
    top_k: int = Field(default=3, ge=1, le=10)


class Citation(BaseModel):
    source_id: str
    title: str
    chunk_id: str
    score: float = Field(ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    mocked: bool = True
