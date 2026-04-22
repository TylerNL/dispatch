from collections.abc import AsyncIterator
from datetime import datetime

from app.ingest.base import Source
from app.schemas.item import Item


class HackerNews(Source):
    name = "Hacker News"

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        raise NotImplementedError


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
