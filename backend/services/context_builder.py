from __future__ import annotations

from backend.schemas.chat import Citation
from backend.schemas.retrieve import RetrieveMatch


def build_context(matches: list[RetrieveMatch]) -> str:
    parts: list[str] = []
    for idx, match in enumerate(matches, start=1):
        meta = match.metadata or {}
        parts.append(
            "\n".join(
                [
                    f"[Source {idx}]",
                    f"chunk_id: {match.chunk_id}",
                    f"score: {match.score:.4f}",
                    f"document_id: {meta.get('document_id')}",
                    f"filename: {meta.get('filename')}",
                    f"page_number: {meta.get('page_number')}",
                    f"chunk_index: {meta.get('chunk_index')}",
                    f"snippet: {meta.get('snippet')}",
                    f"text: {match.text}",
                ]
            )
        )
    return "\n\n".join(parts)


def build_prompt(question: str, context: str) -> str:
    return (
        "You are a precise financial document assistant.\n"
        "Answer using only the provided context.\n"
        "If context is insufficient, say so clearly.\n\n"
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
            )
        )
    return citations
