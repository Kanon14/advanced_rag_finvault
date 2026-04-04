from __future__ import annotations

import re

from backend.ingestion.models import ParsedDocument, ParsedPage


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_document(parsed: ParsedDocument) -> tuple[list[ParsedPage], str]:
    normalized_pages: list[ParsedPage] = []
    markdown_parts: list[str] = []

    for page in parsed.pages:
        normalized_text = _normalize_text(page.text)
        normalized_pages.append(
            ParsedPage(page_number=page.page_number, text=normalized_text, section=page.section)
        )
        markdown_parts.append(f"## Page {page.page_number}\n\n{normalized_text}")

    markdown = "\n\n".join(markdown_parts).strip()
    return normalized_pages, markdown
