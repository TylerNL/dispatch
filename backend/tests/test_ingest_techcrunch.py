from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ingest_techcrunch_returns_items() -> None:
    resp = client.get("/api/debug/ingest-techcrunch")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0


def test_ingest_techcrunch_item_shape() -> None:
    resp = client.get("/api/debug/ingest-techcrunch")
    item = resp.json()[0]
    assert item["id"].startswith("techcrunch:")
    assert item["source"] == "TechCrunch"
    assert "techcrunch.com" in item["url"]
    assert item["title"]
    assert item["published_at"]
