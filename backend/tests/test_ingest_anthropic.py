from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ingest_anthropic_returns_items() -> None:
    resp = client.get("/api/debug/ingest-anthropic")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0


def test_ingest_anthropic_item_shape() -> None:
    resp = client.get("/api/debug/ingest-anthropic")
    item = resp.json()[0]
    assert item["id"].startswith("anthropic:")
    assert item["source"] == "Anthropic"
    assert "anthropic.com" in item["url"]
    assert item["title"]
    assert item["published_at"]
