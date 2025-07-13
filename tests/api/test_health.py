from starlette.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_docs_ok() -> None:
    """OpenAPI JSON отдаётся и даёт код 200."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
