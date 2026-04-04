from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_ingest_upload_rejects_non_pdf() -> None:
    response = client.post(
        "/ingest/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        data={"metadata_json": "{}"},
    )
    assert response.status_code == 400


def test_ingest_upload_accepts_pdf_payload() -> None:
    minimal_pdf = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    response = client.post(
        "/ingest/upload",
        files={"file": ("sample.pdf", minimal_pdf, "application/pdf")},
        data={"metadata_json": '{"ticker":"MSFT"}'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["job_id"].startswith("job_")
    assert body["status"] == "queued"
