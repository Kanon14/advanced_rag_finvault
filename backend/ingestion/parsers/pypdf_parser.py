from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from backend.ingestion.models import ParsedDocument, ParsedPage


class PyPdfParser:
    parser_name = "pypdf"

    def parse(self, source_path: Path) -> ParsedDocument:
        reader = PdfReader(str(source_path))
        pages: list[ParsedPage] = []

        for index, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append(ParsedPage(page_number=index + 1, text=text))

        return ParsedDocument(source_path=str(source_path), filename=source_path.name, pages=pages)
