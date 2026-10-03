from pydantic import BaseModel, Field

from app.schemas.item import Topic


ALL_TOPICS: tuple[Topic, ...] = (
    "research",
    "labs",
    "startups",
    "security",
    "tooling",
)


class SubscriberPreferences(BaseModel):
    enabled: bool
    topics: list[Topic] = Field(min_length=1)
