from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ingest_arxiv_returns_items() -> None:
    resp = client.get("/api/debug/ingest-arxiv")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0


def test_ingest_arxiv_item_shape() -> None:
    resp = client.get("/api/debug/ingest-arxiv")
    item = resp.json()[0]
    assert item["id"].startswith("arxiv:")
    assert item["source"] == "arXiv"
    assert "arxiv.org/abs/" in item["url"]
    assert item["title"]
    assert item["summary"]
    assert item["published_at"]
