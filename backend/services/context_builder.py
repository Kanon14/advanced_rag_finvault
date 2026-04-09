from __future__ import annotations

from backend.schemas.chat import Citation
from backend.schemas.retrieve import RetrieveMatch


def build_context_blocks(matches: list[RetrieveMatch]) -> list[str]:
    blocks: list[str] = []
    for match in matches:
        meta = match.metadata or {}
        block = "\n".join(
            [
                f"[Rank {match.retrieval_rank}]",
                f"chunk_id: {match.chunk_id}",
                f"score: {match.score:.4f}",
                f"document_id: {meta.get('document_id')}",
                f"filename: {meta.get('filename')}",
                f"page_number: {meta.get('page_number')}",
                f"chunk_index: {meta.get('chunk_index')}",
                f"snippet: {meta.get('snippet')}",
                "text:",
                match.text,
            ]
        )
        blocks.append(block)
    return blocks


def build_context(matches: list[RetrieveMatch]) -> str:
    return "\n\n---\n\n".join(build_context_blocks(matches))


def build_prompt(question: str, context: str) -> str:
    return (
        "You are a precise financial document assistant.\n"
        "Use only the provided context.\n"
        "If the answer is not in context, explicitly say that.\n"
        "Keep answer concise and factual.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )


def build_citations(matches: list[RetrieveMatch]) -> list[Citation]:
    citations: list[Citation] = []
    for match in matches:
        meta = match.metadata or {}
        citations.append(
            Citation(
                source_id=str(meta.get("source_id") or ""),
                title=str(meta.get("filename") or "unknown"),
                chunk_id=match.chunk_id,
                score=float(match.score),
                filename=meta.get("filename"),
                page_number=meta.get("page_number"),
                chunk_index=meta.get("chunk_index"),
                snippet=meta.get("snippet"),
                document_id=meta.get("document_id"),
                ingestion_job_id=meta.get("ingestion_job_id"),
                retrieval_rank=match.retrieval_rank,
                included_in_prompt=True,
                filtered_out_reason=None,
            )
        )
    return citations
