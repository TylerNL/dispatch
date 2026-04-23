import asyncio
from collections.abc import AsyncIterator
from datetime import datetime, timezone

import httpx

from app.ingest.base import Source
from app.schemas.item import Item


class HackerNews(Source):
    name = "Hacker News"
    _base = "https://hacker-news.firebaseio.com/v0"
    _top_n = 10

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{self._base}/topstories.json")
            resp.raise_for_status()
            ids: list[int] = resp.json()[: self._top_n]
            raws = await self._fetch_items(client, ids)

        for raw in raws:
            item = self._parse(raw)
            if item is not None:
                yield item

    async def _fetch_items(self, client: httpx.AsyncClient, ids: list[int]) -> list[dict]:
        async def get_one(item_id: int) -> dict | None:
            try:
                r = await client.get(f"{self._base}/item/{item_id}.json")
                r.raise_for_status()
                return r.json()
            except Exception:
                return None

        results = await asyncio.gather(*[get_one(i) for i in ids])
        return [r for r in results if r is not None]

    def _parse(self, raw: dict) -> Item | None:
        if raw.get("type") != "story" or not raw.get("title"):
            return None

        hn_id = str(raw["id"])
        url = raw.get("url") or f"https://news.ycombinator.com/item?id={hn_id}"
        published_at = datetime.fromtimestamp(raw["time"], tz=timezone.utc)

        return Item(
            id=f"hn:{hn_id}",
            source=self.name,
            external_id=hn_id,
            url=url,
            title=raw["title"],
            author=raw.get("by"),
            published_at=published_at,
            score=float(raw.get("score", 0)),
        )


class Lobsters(Source):
    name = "Lobsters"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


class ArXiv(Source):
    name = "arXiv"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


class RedditML(Source):
    name = "r/MachineLearning"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


class TechCrunch(Source):
    name = "TechCrunch"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


class Crunchbase(Source):
    name = "Crunchbase"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


class AnthropicBlog(Source):
    name = "Anthropic"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


class OpenAIBlog(Source):
    name = "OpenAI"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


class DeepMindBlog(Source):
    name = "DeepMind"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


class Bluesky(Source):
    name = "Bluesky"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


REGISTRY: list[type[Source]] = [
    HackerNews,
    Lobsters,
    ArXiv,
    RedditML,
    TechCrunch,
    Crunchbase,
    AnthropicBlog,
    OpenAIBlog,
    DeepMindBlog,
    Bluesky,
]
