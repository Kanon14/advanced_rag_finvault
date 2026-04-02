import os
import sys

from dotenv import load_dotenv
from qdrant_client import QdrantClient


def main() -> int:
    load_dotenv()
    qdrant_url = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY") or None

    try:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=5)
        collections = client.get_collections().collections
        print(f"OK: Qdrant reachable at {qdrant_url}")
        print(f"Collections found: {len(collections)}")
        return 0
    except Exception as exc:
        print(f"ERROR: Qdrant check failed -> {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
