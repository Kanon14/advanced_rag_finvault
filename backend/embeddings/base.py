from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    provider_name: str
    dimension: int

    def embed(self, text: str) -> list[float]: ...

    def embed_many(self, texts: list[str]) -> list[list[float]]: ...
