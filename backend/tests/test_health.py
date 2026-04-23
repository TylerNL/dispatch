from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_sources() -> None:
    client = TestClient(app)
    resp = client.get("/api/sources")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
