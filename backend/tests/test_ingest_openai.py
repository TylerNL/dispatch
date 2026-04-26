from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ingest_openai_returns_items() -> None:
    resp = client.get("/api/debug/ingest-openai")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0


def test_ingest_openai_item_shape() -> None:
    resp = client.get("/api/debug/ingest-openai")
    item = resp.json()[0]
    assert item["id"].startswith("openai:")
    assert item["source"] == "OpenAI"
    assert "openai.com" in item["url"]
    assert item["title"]
    assert item["published_at"]