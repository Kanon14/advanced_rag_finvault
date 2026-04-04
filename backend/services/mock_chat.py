from backend.schemas.chat import ChatRequest, ChatResponse, Citation


def generate_mock_chat_response(payload: ChatRequest) -> ChatResponse:
    answer = (
        "This is a mocked Stage 1 response. "
        f"Your question was: '{payload.question}'. "
        "No retrieval or LLM inference is running yet."
    )

    citations = [
        Citation(
            source_id="mock_doc_001",
            title="Mock Financial Filing",
            chunk_id="chunk_01",
            score=0.92,
        ),
        Citation(
            source_id="mock_doc_002",
            title="Mock Earnings Call",
            chunk_id="chunk_07",
            score=0.86,
        ),
    ]

    return ChatResponse(answer=answer, citations=citations, mocked=True)
