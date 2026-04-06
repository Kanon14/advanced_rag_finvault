from __future__ import annotations

import hashlib
import math
import re


class HashEmbedder:
    provider_name = "hash"

    def __init__(self, dimension: int = 256) -> None:
        if dimension <= 0:
            raise ValueError("Embedding dimension must be > 0.")
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        tokens = re.findall(r"\w+", text.lower())
        vector = [0.0] * self.dimension

        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for i in range(0, 16):
                offset = i * 2
                idx = int.from_bytes(digest[offset : offset + 2], "little") % self.dimension
                sign = -1.0 if (digest[(offset + 1) % len(digest)] & 1) else 1.0
                vector[idx] += sign

        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]
