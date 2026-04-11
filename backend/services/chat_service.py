from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from backend.core.logging import get_logger
from backend.llm.ollama_client import OllamaClient, OllamaError
from backend.schemas.chat import ChatDiagnostics, ChatRequest, ChatResponse
from backend.services.context_builder import (
    build_citations,
    build_context,
    build_context_blocks,
    build_prompt,
)
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
    diagnostics_payload: dict,
) -> None:
    debug_dir = _chat_debug_dir(request_id)
    (debug_dir / "question.txt").write_text(question, encoding="utf-8")
    (debug_dir / "retrieval.json").write_text(
        json.dumps(retrieval_payload, indent=2), encoding="utf-8"
    )
    (debug_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    (debug_dir / "diagnostics.json").write_text(
        json.dumps(diagnostics_payload, indent=2), encoding="utf-8"
    )
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
            min_score=payload.min_score,
            max_context_chars=payload.max_context_chars,
            deduplicate=payload.deduplicate,
            unique_pages=payload.unique_pages,
        )
    except Exception as exc:
        logger.warning("Chat retrieval failed request_id=%s error=%s", request_id, exc)
        _write_debug_artifacts(
            request_id=request_id,
            question=payload.question,
            retrieval_payload={"error": str(exc)},
            prompt="NO_CONTEXT",
            llm_payload=None,
            diagnostics_payload={"reason": "retrieval_error"},
        )
        raise ChatServiceError(
            "Retrieval failed before generation: "
            f"{exc}. Check collection/indexing and embedding configuration."
        ) from exc

    matches = retrieval.matches
    retrieval_diag = retrieval.diagnostics
    logger.info(
        "Chat retrieval request_id=%s raw=%s included=%s excluded=%s reasons=%s",
        request_id,
        retrieval_diag.raw_candidate_count if retrieval_diag else 0,
        len(matches),
        retrieval_diag.excluded_count if retrieval_diag else 0,
        retrieval_diag.excluded_reasons if retrieval_diag else {},
    )

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
            diagnostics_payload={"reason": "no_matches_after_filtering"},
        )
        return ChatResponse(
            answer=fallback,
            citations=[],
            mocked=False,
            request_id=request_id,
            model=None,
            retrieval_count=0,
            diagnostics=ChatDiagnostics(
                provider=retrieval_diag.provider if retrieval_diag else "unknown",
                embedding_dimension=retrieval_diag.embedding_dimension if retrieval_diag else 0,
                raw_candidate_count=retrieval_diag.raw_candidate_count if retrieval_diag else 0,
                included_count=0,
                excluded_count=retrieval_diag.excluded_count if retrieval_diag else 0,
                excluded_reasons=retrieval_diag.excluded_reasons if retrieval_diag else {},
                context_chars=0,
            ),
        )

    context_blocks = build_context_blocks(matches)
    context = build_context(matches)
    prompt = build_prompt(question=payload.question, context=context)
    logger.info(
        "Chat context built request_id=%s chars=%s blocks=%s",
        request_id,
        len(context),
        len(context_blocks),
    )

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
            diagnostics_payload={
                "error": str(exc),
                "context_block_count": len(context_blocks),
            },
        )
        raise ChatServiceError(str(exc)) from exc

    citations = build_citations(matches)
    chat_diag = ChatDiagnostics(
        provider=retrieval_diag.provider if retrieval_diag else "unknown",
        embedding_dimension=retrieval_diag.embedding_dimension if retrieval_diag else 0,
        raw_candidate_count=retrieval_diag.raw_candidate_count if retrieval_diag else len(matches),
        included_count=len(matches),
        excluded_count=retrieval_diag.excluded_count if retrieval_diag else 0,
        excluded_reasons=retrieval_diag.excluded_reasons if retrieval_diag else {},
        context_chars=len(context),
    )

    _write_debug_artifacts(
        request_id=request_id,
        question=payload.question,
        retrieval_payload=retrieval.model_dump(),
        prompt=prompt,
        llm_payload=llm_result.raw,
        diagnostics_payload=chat_diag.model_dump(),
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
        diagnostics=chat_diag,
    )
