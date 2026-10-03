from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.item import Topic
from app.schemas.subscriber import ALL_TOPICS, SubscriberPreferences
from app.storage.models import SubscriberRow


def to_preferences(row: SubscriberRow | None) -> SubscriberPreferences:
    if row is None:
        return SubscriberPreferences(enabled=False, topics=list(ALL_TOPICS))

    valid_topics = set(ALL_TOPICS)
    topics = [
        cast(Topic, topic)
        for topic in (row.topics or "").split(",")
        if topic in valid_topics
    ]
    return SubscriberPreferences(
        enabled=row.active,
        topics=topics or list(ALL_TOPICS),
    )


async def get_subscriber(
    session: AsyncSession,
    user_id: str,
) -> SubscriberRow | None:
    return await session.get(SubscriberRow, user_id)


async def save_preferences(
    session: AsyncSession,
    *,
    user_id: str,
    email: str,
    enabled: bool,
    topics: list[Topic],
) -> SubscriberRow:
    row = await session.get(SubscriberRow, user_id)
    serialized_topics = ",".join(topics)

    if row is None:
        row = SubscriberRow(
            id=user_id,
            email=email,
            topics=serialized_topics,
            active=enabled,
        )
        session.add(row)
    else:
        row.email = email
        row.topics = serialized_topics
        row.active = enabled

    await session.commit()
    return row
