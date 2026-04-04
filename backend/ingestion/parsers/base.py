from __future__ import annotations

from pathlib import Path
from typing import Protocol

from backend.ingestion.models import ParsedDocument


class ParserAdapter(Protocol):
    parser_name: str

    def parse(self, source_path: Path) -> ParsedDocument: ...
