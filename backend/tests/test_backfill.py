from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.pipeline import backfill


def _row(
    item_id: str,
    *,
    summary: str | None,
    topic: str | None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=item_id,
        source="test",
        external_id=item_id,
        url=f"https://example.com/{item_id}",
        title=f"Title {item_id}",
        author=None,
        published_at=datetime(2026, 10, 6, tzinfo=timezone.utc),
        summary=summary,
        topic=topic,
        score=None,
    )


@pytest.mark.asyncio
async def test_process_rows_only_generates_missing_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = [
        _row("both", summary=None, topic=None),
        _row("topic", summary="Existing summary", topic=None),
        _row("summary", summary=None, topic="labs"),
    ]
    calls: dict[str, list[str]] = {}

    async def summarize(items):
        calls["summarize"] = [item.id for item in items]
        return [f"Generated summary for {item.id}" for item in items]

    async def classify(items):
        calls["classify"] = [item.id for item in items]
        assert items[0].summary == "Generated summary for both"
        return [("tooling", 0.7) for _item in items]

    async def embed(item):
        calls.setdefault("embed", []).append(item.id)
        return ([item.title], [[0.0]])

    async def save(_session, item, _chunks, _embeddings):
        calls.setdefault("upsert", []).append(item.id)

    class FakeSession:
        committed = False

        async def commit(self) -> None:
            self.committed = True

    session = FakeSession()
    monkeypatch.setattr(backfill, "summarize_batch", summarize)
    monkeypatch.setattr(backfill, "classify_batch", classify)
    monkeypatch.setattr(backfill, "embed_item", embed)
    monkeypatch.setattr(backfill, "upsert", save)

    stats = await backfill.process_rows(session, rows)  # type: ignore[arg-type]

    assert calls == {
        "summarize": ["both", "summary"],
        "classify": ["both", "topic"],
        "embed": ["both", "summary"],
        "upsert": ["both", "summary"],
    }
    assert rows[0].summary == "Generated summary for both"
    assert rows[0].topic == "tooling"
    assert rows[1].summary == "Existing summary"
    assert rows[2].topic == "labs"
    assert session.committed
    assert stats == backfill.BackfillStats(
        processed=3,
        summarized=2,
        classified=2,
        reembedded=2,
    )
