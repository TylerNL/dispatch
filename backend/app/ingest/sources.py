import asyncio
import calendar
from collections.abc import AsyncIterator
from datetime import datetime, timezone

import feedparser
import httpx
from bs4 import BeautifulSoup

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


class ArXiv(Source):
    name = "arXiv"
    _base = "https://export.arxiv.org/api/query"
    _categories = ["cs.LG", "cs.AI", "cs.CL", "cs.CV", "cs.CR"] # cs(ml), ai, nlp, comp vision, crypto
    _max_results = 15

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        # Build query string manually — httpx encodes colons as %3A which
        cats = "+OR+".join(f"cat:{c}" for c in self._categories)
        url = (
            f"{self._base}?search_query={cats}"
            f"&start=0&max_results={self._max_results}"
            f"&sortBy=submittedDate&sortOrder=descending"
        )
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        feed = feedparser.parse(resp.text)
        for entry in feed.entries:
            item = self._parse(entry)
            if item is not None:
                yield item

    def _parse(self, entry: feedparser.FeedParserDict) -> Item | None:
        try:
            arxiv_id = entry.id.split("/abs/")[-1].split("v")[0]
            url = f"https://arxiv.org/abs/{arxiv_id}"
            authors = ", ".join(a.name for a in entry.get("authors", []))
            # feedparser normalizes all dates to a time.struct_time in published_parsed
            published_at = datetime.fromtimestamp(
                calendar.timegm(entry.published_parsed), tz=timezone.utc
            )
            return Item(
                id=f"arxiv:{arxiv_id}",
                source=self.name,
                external_id=arxiv_id,
                url=url,
                title=entry.title.replace("\n", " ").strip(),
                author=authors or None,
                published_at=published_at,
                summary=entry.summary.replace("\n", " ").strip(),
            )
        except Exception:
            return None


class RedditML(Source):
    name = "r/MachineLearning"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


class TechCrunch(Source):
    name = "TechCrunch"
    _feed_url = "https://techcrunch.com/feed/"
    _max_entries = 15

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(self._feed_url)
            resp.raise_for_status()

        feed = feedparser.parse(resp.text)
        for entry in feed.entries[: self._max_entries]:
            item = self._parse(entry)
            if item is not None:
                yield item

    def _parse(self, entry: feedparser.FeedParserDict) -> Item | None:
        try:
            url = entry.link
            slug = url.rstrip("/").split("/")[-1]
            published_at = datetime.fromtimestamp(
                calendar.timegm(entry.published_parsed), tz=timezone.utc
            )
            raw_summary = entry.get("summary", "")
            summary = (
                BeautifulSoup(raw_summary, "html.parser").get_text(" ", strip=True)
                if raw_summary
                else None
            )
            return Item(
                id=f"techcrunch:{slug}",
                source=self.name,
                external_id=slug,
                url=url,
                title=entry.title.strip(),
                author=entry.get("author") or None,
                published_at=published_at,
                summary=summary or None,
            )
        except Exception:
            return None

#Will implement later if API found
class Crunchbase(Source):
    name = "Crunchbase"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


class AnthropicBlog(Source):
    name = "Anthropic"
    _base = "https://www.anthropic.com"
    _listing_url = "https://www.anthropic.com/engineering"
    # Anthropic exposes no native RSS, so we scrape the listing directly.
    _ua = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        async with httpx.AsyncClient(
            timeout=20.0, headers={"User-Agent": self._ua}
        ) as client:
            resp = await client.get(self._listing_url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all(
            "a",
            class_=lambda c: bool(c) and "__cardLink" in c,
            href=True,
        )
        for card in cards:
            item = self._parse(card)
            if item is not None:
                yield item

    def _parse(self, card) -> Item | None:
        try:
            href = card["href"]
            if not href.startswith("/engineering/"):
                return None
            slug = href.rstrip("/").split("/")[-1]
            url = f"{self._base}{href}"

            title_el = card.find(["h2", "h3"])
            if not title_el:
                return None
            title = title_el.get_text(" ", strip=True)

            date_el = card.find(
                lambda t: t.name == "div"
                and t.get("class")
                and any("__date" in cls for cls in t.get("class"))
            )
            if not date_el:
                # Featured post has no inline date; skip for now.
                return None
            published_at = datetime.strptime(
                date_el.get_text(strip=True), "%b %d, %Y"
            ).replace(tzinfo=timezone.utc)

            summary_el = card.find(
                lambda t: t.name == "p"
                and t.get("class")
                and any("__summary" in cls for cls in t.get("class"))
            )
            summary = summary_el.get_text(" ", strip=True) if summary_el else None

            return Item(
                id=f"anthropic:{slug}",
                source=self.name,
                external_id=slug,
                url=url,
                title=title,
                published_at=published_at,
                summary=summary,
            )
        except Exception:
            return None


class OpenAIBlog(Source):
    name = "OpenAI"
    _feed_url = "https://openai.com/news/rss.xml"
    _max_entries = 5

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(self._feed_url)
            resp.raise_for_status()

        feed = feedparser.parse(resp.text)
        for entry in feed.entries[: self._max_entries]:
            item = self._parse(entry)
            if item is not None:
                yield item

    def _parse(self, entry: feedparser.FeedParserDict) -> Item | None:
        try:
            url = entry.link
            slug = url.rstrip("/").split("/")[-1]
            published_at = datetime.fromtimestamp(
                calendar.timegm(entry.published_parsed), tz=timezone.utc
            )
            raw_summary = entry.get("summary", "")
            summary = (
                BeautifulSoup(raw_summary, "html.parser").get_text(" ", strip=True)
                if raw_summary
                else None
            )
            return Item(
                id=f"openai:{slug}",
                source=self.name,
                external_id=slug,
                url=url,
                title=entry.title.strip(),
                author=entry.get("author") or None,
                published_at=published_at,
                summary=summary or None,
            )
        except Exception:
            return None


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
    ArXiv,
    RedditML,
    TechCrunch,
    Crunchbase,
    AnthropicBlog,
    OpenAIBlog,
    DeepMindBlog,
    Bluesky,
]
