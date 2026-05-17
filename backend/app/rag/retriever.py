from datetime import datetime, timedelta, timezone

from app.pipeline.embed import embed_text
from app.schemas.ask import TimeWindow
from app.schemas.item import Item
from app.storage.db import SessionLocal
from app.storage.vector import search

_WINDOW_DELTAS: dict[TimeWindow, timedelta | None] = {
    "today": timedelta(days=1),
    "week": timedelta(weeks=1),
    "month": timedelta(days=30),
    "year": timedelta(days=365),
    "all": None,
}


async def retrieve(
    question: str,
    window: TimeWindow = "all",
    topic: str | None = None,
    k: int = 12,
) -> list[Item]:
    query_embedding = await embed_text(question)

    delta = _WINDOW_DELTAS[window]
    since = datetime.now(timezone.utc) - delta if delta else None

    async with SessionLocal() as session:
        return await search(session, query_embedding, k=k, since=since, topic=topic)
