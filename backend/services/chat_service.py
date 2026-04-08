from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from backend.core.logging import get_logger
from backend.llm.ollama_client import OllamaClient, OllamaError
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.context_builder import build_citations, build_context, build_prompt
from backend.services.retrieval_service import retrieve_chunks

logger = get_logger(__name__)


class ChatServiceError(RuntimeError):
    pass


def _chat_debug_dir(request_id: str) -> Path:
    path = Path("data") / "chat" / request_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_debug_artifacts(
    request_id: str,
    question: str,
    retrieval_payload: dict,
    prompt: str,
    llm_payload: dict | None,
) -> None:
    debug_dir = _chat_debug_dir(request_id)
    (debug_dir / "question.txt").write_text(question, encoding="utf-8")
    (debug_dir / "retrieval.json").write_text(
        json.dumps(retrieval_payload, indent=2), encoding="utf-8"
    )
    (debug_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    if llm_payload is not None:
        (debug_dir / "llm_response.json").write_text(
            json.dumps(llm_payload, indent=2), encoding="utf-8"
        )


def generate_chat_response(payload: ChatRequest) -> ChatResponse:
    request_id = f"chat_{uuid4().hex[:12]}"
    logger.info("Chat request started request_id=%s top_k=%s", request_id, payload.top_k)

    try:
        retrieval = retrieve_chunks(
            query=payload.question,
            top_k=payload.top_k,
            collection_name=payload.collection_name,
        )
    except Exception as exc:
        logger.warning("Chat retrieval failed request_id=%s error=%s", request_id, exc)
        fallback = (
            "I could not retrieve indexed context for your question yet. "
            "Please complete ingestion and indexing, then try again."
        )
        _write_debug_artifacts(
            request_id=request_id,
            question=payload.question,
            retrieval_payload={"error": str(exc)},
            prompt="NO_CONTEXT",
            llm_payload=None,
        )
        return ChatResponse(
            answer=fallback,
            citations=[],
            mocked=False,
            request_id=request_id,
            model=None,
            retrieval_count=0,
        )

    matches = retrieval.matches
    logger.info("Chat retrieval request_id=%s matches=%s", request_id, len(matches))

    if not matches:
        fallback = (
            "I could not find relevant indexed context for your question yet. "
            "Please ingest and index a document, then try again."
        )
        _write_debug_artifacts(
            request_id=request_id,
            question=payload.question,
            retrieval_payload=retrieval.model_dump(),
            prompt="NO_CONTEXT",
            llm_payload=None,
        )
        return ChatResponse(
            answer=fallback,
            citations=[],
            mocked=False,
            request_id=request_id,
            model=None,
            retrieval_count=0,
        )

    context = build_context(matches)
    prompt = build_prompt(question=payload.question, context=context)
    logger.info("Chat context built request_id=%s chars=%s", request_id, len(context))

    client = OllamaClient()
    try:
        llm_result = client.generate(prompt)
    except OllamaError as exc:
        _write_debug_artifacts(
            request_id=request_id,
            question=payload.question,
            retrieval_payload=retrieval.model_dump(),
            prompt=prompt,
            llm_payload=None,
        )
        raise ChatServiceError(str(exc)) from exc

    citations = build_citations(matches)
    _write_debug_artifacts(
        request_id=request_id,
        question=payload.question,
        retrieval_payload=retrieval.model_dump(),
        prompt=prompt,
        llm_payload=llm_result.raw,
    )

    logger.info(
        "Chat completed request_id=%s citations=%s model=%s",
        request_id,
        len(citations),
        llm_result.model,
    )

    return ChatResponse(
        answer=llm_result.text,
        citations=citations,
        mocked=False,
        request_id=request_id,
        model=llm_result.model,
        retrieval_count=len(citations),
    )
