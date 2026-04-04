from __future__ import annotations

from pathlib import Path

from backend.ingestion.models import ParsedDocument


class DoclingParser:
    parser_name = "docling"

    def __init__(self) -> None:
        try:
            import docling  # noqa: F401

            self.is_available = True
        except Exception:
            self.is_available = False

    def parse(self, source_path: Path) -> ParsedDocument:
        raise RuntimeError(
            "Docling parser adapter is not enabled in Stage 3 runtime. "
            "Install/configure Docling and extend this adapter before use."
        )
