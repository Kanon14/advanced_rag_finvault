from __future__ import annotations

import httpx

from backend.core.config import get_settings
from backend.llm.base import GenerationResult


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    provider_name = "ollama"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.ollama_base_url.rstrip("/")
        self.model = self.settings.ollama_model
        self.timeout_seconds = self.settings.ollama_timeout_seconds

    def generate(self, prompt: str) -> GenerationResult:
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = httpx.post(endpoint, json=payload, timeout=self.timeout_seconds)
        except Exception as exc:
            raise OllamaError(
                f"Ollama is unreachable at {self.base_url}. "
                f"Start Ollama and pull model '{self.model}'."
            ) from exc

        if response.status_code >= 400:
            raise OllamaError(f"Ollama request failed ({response.status_code}): {response.text}")

        body = response.json()
        text = str(body.get("response", "")).strip()
        if not text:
            raise OllamaError("Ollama returned an empty response.")

        return GenerationResult(text=text, model=self.model, raw=body)
