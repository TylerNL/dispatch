from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.pipeline.dedupe import fingerprint
from app.schemas.item import Item
from app.storage.models import ChunkRow, ItemRow


async def upsert(
    session: AsyncSession,
    item: Item,
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    fp = fingerprint(item)

    await session.execute(
        insert(ItemRow)
        .values(
            id=item.id,
            source=item.source,
            external_id=item.external_id,
            url=item.url,
            title=item.title,
            author=item.author,
            published_at=item.published_at,
            summary=item.summary,
            topic=item.topic,
            score=item.score,
            fingerprint=fp,
        )
        .on_conflict_do_update(
            index_elements=["id"],
            set_={"score": item.score, "summary": item.summary, "topic": item.topic},
        )
    )

    for idx, (content, embedding) in enumerate(zip(chunks, embeddings)):
        await session.execute(
            insert(ChunkRow)
            .values(
                id=f"{item.id}:{idx}",
                item_id=item.id,
                content=content,
                embedding=embedding,
            )
            .on_conflict_do_update(
                index_elements=["id"],
                set_={"content": content, "embedding": embedding},
            )
        )


_RECENCY_DECAY = 0.001  # +0.03 for a month-old article

async def search(
    session: AsyncSession,
    embedding: list[float],
    k: int = 12,
    since: datetime | None = None,
    topic: str | None = None,
    sources: list[str] | None = None,
) -> list[Item]:
    age_days = func.extract("epoch", func.now() - ItemRow.published_at) / 86400.0
    score = (
        func.min(ChunkRow.embedding.cosine_distance(embedding)) + _RECENCY_DECAY * age_days
    ).label("score")

    best = (
        select(ChunkRow.item_id, score)
        .join(ItemRow, ChunkRow.item_id == ItemRow.id)
    )

    if since is not None:
        best = best.where(ItemRow.published_at >= since)
    if topic is not None:
        best = best.where(ItemRow.topic == topic)
    if sources:
        best = best.where(ItemRow.source.in_(sources))

    best = (
        best.group_by(ChunkRow.item_id, ItemRow.published_at)
        .order_by(text("score"))
        .limit(k)
        .subquery()
    )

    stmt = select(ItemRow).join(best, ItemRow.id == best.c.item_id).order_by(best.c.score)
    rows = (await session.execute(stmt)).scalars().all()

    return [
        Item(
            id=r.id,
            source=r.source,
            external_id=r.external_id,
            url=r.url,
            title=r.title,
            author=r.author,
            published_at=r.published_at,
            summary=r.summary,
            topic=r.topic,
            score=r.score,
        )
        for r in rows
    ]
