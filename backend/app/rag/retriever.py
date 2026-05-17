import re
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

_SOURCE_KEYWORDS: dict[str, list[str]] = {
    "Anthropic": ["anthropic", "claude"],
    "OpenAI": ["openai", "gpt", "chatgpt"],
    "Hacker News": ["hacker news", "hackernews", "hn"],
    "arXiv": ["arxiv", "paper", "papers", "research"],
    "TechCrunch": ["techcrunch", "tc"],
}
# Find relevant keywords to filter sources
def _detect_sources(question: str) -> list[str] | None:
    q = question.lower()
    matched = [
        source
        for source, keywords in _SOURCE_KEYWORDS.items()
        if any(re.search(r'\b' + re.escape(kw) + r'\b', q) for kw in keywords)
    ]
    return matched or None


async def retrieve(
    question: str,
    window: TimeWindow = "all",
    topic: str | None = None,
    sources: list[str] | None = None,
    k: int = 12,
) -> list[Item]:
    if sources is None:
        sources = _detect_sources(question)

    query_embedding = await embed_text(question)

    delta = _WINDOW_DELTAS[window]
    since = datetime.now(timezone.utc) - delta if delta else None

    async with SessionLocal() as session:
        return await search(session, query_embedding, k=k, since=since, topic=topic, sources=sources)
