from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

IngestionStatus = Literal[
    "queued",
    "validating",
    "parsing",
    "normalizing",
    "chunking",
    "completed",
    "failed",
]


@dataclass
class ParsedPage:
    page_number: int
    text: str
    section: str | None = None


@dataclass
class ParsedDocument:
    source_path: str
    filename: str
    pages: list[ParsedPage]


@dataclass
class ChunkRecord:
    chunk_id: str
    chunk_index: int
    text: str
    metadata: dict[str, Any]


@dataclass
class JobState:
    job_id: str
    status: IngestionStatus
    progress: int
    detail: str
    source_type: str
    source_value: str
    artifacts: dict[str, str] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
