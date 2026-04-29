from datetime import datetime
from typing import Literal

from pydantic import BaseModel


Topic = Literal["research", "labs", "startups", "community", "security", "signal"]


class Item(BaseModel):
    id: str
    source: str
    external_id: str | None = None
    url: str
    title: str
    author: str | None = None
    published_at: datetime
    summary: str | None = None
    topic: Topic | None = None
    score: float | None = None


class DigestSection(BaseModel):
    topic: Topic
    items: list[Item]


class Digest(BaseModel):
    date: str
    total_indexed: int
    sections: list[DigestSection]


class SourceStatus(BaseModel):
    name: str
    last_pulled_at: datetime | None = None
    items_today: int = 0
    healthy: bool = True
