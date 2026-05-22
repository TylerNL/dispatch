import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone

from app.pipeline.embed import embed_text
from app.schemas.ask import TimeWindow
from app.schemas.item import Item
from app.storage.db import SessionLocal
from app.storage.vector import hydrate_items, keyword_search, vector_search

logger = logging.getLogger(__name__)

_RRF_K = 60  # rank-fusion constant

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


def _detect_sources(question: str) -> list[str] | None:
    q = question.lower()
    matched = [
        source
        for source, keywords in _SOURCE_KEYWORDS.items()
        if any(re.search(r'\b' + re.escape(kw) + r'\b', q) for kw in keywords)
    ]
    return matched or None


def _rrf_fuse(
    vec_results: list[tuple[str, float]],
    kw_results: list[tuple[str, float]],
    k: int,
) -> list[str]:
    # RRF Over the two ranked lists
    scores: dict[str, float] = {}

    for rank, (item_id, _) in enumerate(vec_results, start=1):
        scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (_RRF_K + rank)

    for rank, (item_id, _) in enumerate(kw_results, start=1):
        scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (_RRF_K + rank)

    fused = sorted(scores, key=scores.__getitem__, reverse=True)
    return fused[:k]


async def retrieve(
    question: str,
    window: TimeWindow = "all",
    topic: str | None = None,
    sources: list[str] | None = None,
    k: int = 12,
) -> list[Item]:
    if sources is None:
        sources = _detect_sources(question)

    delta = _WINDOW_DELTAS[window]
    since = datetime.now(timezone.utc) - delta if delta else None

    query_embedding = await embed_text(question)

    async def _vec():
        async with SessionLocal() as s:
            return await vector_search(s, query_embedding, k=k, since=since, topic=topic, sources=sources)

    async def _kw():
        async with SessionLocal() as s:
            return await keyword_search(s, question, k=k, since=since, topic=topic, sources=sources)

    vec_results, kw_results = await asyncio.gather(_vec(), _kw())

    logger.debug(
        "hybrid retrieval: %d vector hits, %d keyword hits",
        len(vec_results), len(kw_results),
    )

    fused_ids = _rrf_fuse(vec_results, kw_results, k)

    async with SessionLocal() as session:
        return await hydrate_items(session, fused_ids)
