from __future__ import annotations

from backend.ingestion.models import ChunkRecord, ParsedPage


def _window_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start += step
    return chunks


def build_chunks(
    pages: list[ParsedPage],
    document_id: str,
    source_id: str,
    filename: str,
    chunk_size: int = 900,
    overlap: int = 120,
) -> list[ChunkRecord]:
    records: list[ChunkRecord] = []
    chunk_index = 0

    for page in pages:
        for part in _window_text(page.text, chunk_size=chunk_size, overlap=overlap):
            chunk_id = f"{document_id}_chunk_{chunk_index:04d}"
            metadata = {
                "document_id": document_id,
                "source_id": source_id,
                "filename": filename,
                "page_number": page.page_number,
                "section": page.section,
                "chunk_id": chunk_id,
                "chunk_index": chunk_index,
                "snippet": part[:160],
            }
            records.append(
                ChunkRecord(
                    chunk_id=chunk_id,
                    chunk_index=chunk_index,
                    text=part,
                    metadata=metadata,
                )
            )
            chunk_index += 1

    return records
