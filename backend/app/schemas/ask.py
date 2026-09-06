import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


TimeWindow = Literal["today", "week", "month", "year", "all"]


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    window: TimeWindow = "all"
    topic: str | None = None
    sources: list[str] | None = None
    conversation_id: str | None = None
    title: str | None = Field(default=None, max_length=200)

    @field_validator("conversation_id")
    @classmethod
    def _valid_uuid(cls, v: str | None) -> str | None:
        if v is not None:
            uuid.UUID(v)  # raises ValueError (→ 422) on malformed ids
        return v


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
