from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class GenerationResult:
    text: str
    model: str
    raw: dict


class GenerationClient(Protocol):
    provider_name: str

    def generate(self, prompt: str) -> GenerationResult: ...
