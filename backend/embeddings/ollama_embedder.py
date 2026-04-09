from __future__ import annotations

import httpx


class OllamaEmbeddingError(RuntimeError):
    pass


class OllamaEmbedder:
    provider_name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: int = 60,
        expected_dimension: int | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._dimension: int | None = expected_dimension

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self.embed("dimension probe")
        if self._dimension is None:
            raise OllamaEmbeddingError("Unable to resolve embedding dimension from Ollama.")
        return self._dimension

    def embed(self, text: str) -> list[float]:
        endpoint = f"{self.base_url}/api/embed"
        payload = {"model": self.model, "input": [text]}

        try:
            response = httpx.post(endpoint, json=payload, timeout=self.timeout_seconds)
        except Exception as exc:
            raise OllamaEmbeddingError(
                f"Ollama embedding endpoint unreachable at {self.base_url}. "
                f"Start Ollama and pull embedding model '{self.model}'."
            ) from exc

        if response.status_code >= 400:
            raise OllamaEmbeddingError(
                f"Ollama embedding request failed ({response.status_code}): {response.text}"
            )

        body = response.json()
        vectors = body.get("embeddings", [])
        if not vectors:
            raise OllamaEmbeddingError("Ollama embedding response did not include embeddings.")

        vector = vectors[0]
        if not isinstance(vector, list) or len(vector) == 0:
            raise OllamaEmbeddingError("Ollama returned invalid embedding vector.")

        if self._dimension is None:
            self._dimension = len(vector)
        elif len(vector) != self._dimension:
            raise OllamaEmbeddingError(
                f"Embedding dimension mismatch. Expected {self._dimension}, got {len(vector)}."
            )

        return [float(x) for x in vector]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        endpoint = f"{self.base_url}/api/embed"
        payload = {"model": self.model, "input": texts}
        response = httpx.post(endpoint, json=payload, timeout=self.timeout_seconds)

        if response.status_code >= 400:
            raise OllamaEmbeddingError(
                f"Ollama embedding batch request failed ({response.status_code}): {response.text}"
            )

        body = response.json()
        vectors = body.get("embeddings", [])
        if len(vectors) != len(texts):
            raise OllamaEmbeddingError("Embedding batch size mismatch from Ollama.")

        if self._dimension is None and vectors:
            self._dimension = len(vectors[0])

        return [[float(x) for x in vec] for vec in vectors]
