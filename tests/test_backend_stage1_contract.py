from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.main import app
from backend.schemas.chat import ChatResponse

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "finvault-backend"


def test_ingest_endpoint_returns_job_id() -> None:
    payload = {
        "source_type": "pdf",
        "source_value": "C:/data/mock-report.pdf",
        "metadata": {"ticker": "AAPL"},
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["job_id"].startswith("job_")
    assert body["status"] == "queued"


def test_ingest_endpoint_validation_error() -> None:
    payload = {"source_type": "pdf", "source_value": ""}
    response = client.post("/ingest", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"


def test_chat_endpoint_returns_structured_payload() -> None:
    mocked_response = ChatResponse(answer="ok", citations=[], mocked=False, retrieval_count=0)
    with patch("backend.api.routes.chat.generate_chat_response", return_value=mocked_response):
        response = client.post("/chat", json={"question": "What changed this quarter?", "top_k": 2})
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert "citations" in body
    assert "mocked" in body
