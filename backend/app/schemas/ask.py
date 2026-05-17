from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


TimeWindow = Literal["today", "week", "month", "year", "all"]


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    window: TimeWindow = "all"
    topic: str | None = None


class Citation(BaseModel):
    item_id: str
    title: str
    url: str
    source: str
    published_at: datetime | None = None
    snippet: str | None = None


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    latency_ms: int | None = None
