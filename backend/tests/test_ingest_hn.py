from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ingest_hn_returns_items() -> None:
    resp = client.get("/api/debug/ingest-hn")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0


def test_ingest_hn_item_shape() -> None:
    resp = client.get("/api/debug/ingest-hn")
    item = resp.json()[0]
    assert item["id"].startswith("hn:")
    assert item["source"] == "Hacker News"
    assert item["url"]
    assert item["title"]
    assert item["published_at"]
