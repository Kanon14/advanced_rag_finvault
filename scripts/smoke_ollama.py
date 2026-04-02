import os
import sys

import httpx
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()
    base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    target = f"{base_url.rstrip('/')}/api/tags"

    try:
        response = httpx.get(target, timeout=5)
        response.raise_for_status()
        payload = response.json()
        model_count = len(payload.get("models", [])) if isinstance(payload, dict) else 0
        print(f"OK: Ollama reachable at {base_url}")
        print(f"Models reported: {model_count}")
        return 0
    except Exception as exc:
        print(f"ERROR: Ollama check failed -> {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
