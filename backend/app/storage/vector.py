import logging
from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.pipeline.dedupe import fingerprint
from app.schemas.item import Item
from app.storage.models import ChunkRow, ItemRow

logger = logging.getLogger(__name__)


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


def _apply_filters(stmt, since, topic, sources):
    if since is not None:
        stmt = stmt.where(ItemRow.published_at >= since)
    if topic is not None:
        stmt = stmt.where(ItemRow.topic == topic)
    if sources:
        stmt = stmt.where(ItemRow.source.in_(sources))
    return stmt


async def vector_search(
    session: AsyncSession,
    embedding: list[float],
    k: int = 12,
    since: datetime | None = None,
    topic: str | None = None,
    sources: list[str] | None = None,
) -> list[tuple[str, float]]:
    """Cosine similarity search over chunk embeddings. Returns (item_id, distance)."""
    age_days = func.extract("epoch", func.now() - ItemRow.published_at) / 86400.0
    dist = (
        func.min(ChunkRow.embedding.cosine_distance(embedding)) + _RECENCY_DECAY * age_days
    ).label("vec_dist")

    stmt = (
        select(ChunkRow.item_id, dist)
        .join(ItemRow, ChunkRow.item_id == ItemRow.id)
    )
    stmt = _apply_filters(stmt, since, topic, sources)
    stmt = (
        stmt.group_by(ChunkRow.item_id, ItemRow.published_at)
        .order_by(text("vec_dist"))
        .limit(k)
    )

    rows = (await session.execute(stmt)).all()
    return [(row.item_id, row.vec_dist) for row in rows]


async def search(
    session: AsyncSession,
    embedding: list[float],
    k: int = 12,
    since: datetime | None = None,
    topic: str | None = None,
    sources: list[str] | None = None,
) -> list[Item]:
    """ranked vector from vector search"""
    ranked = await vector_search(session, embedding, k, since, topic, sources)
    if not ranked:
        return []
    item_ids = [r[0] for r in ranked]
    id_order = {iid: i for i, iid in enumerate(item_ids)}

    stmt = select(ItemRow).where(ItemRow.id.in_(item_ids))
    rows = (await session.execute(stmt)).scalars().all()
    rows.sort(key=lambda r: id_order.get(r.id, 0))

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


async def keyword_search(
    session: AsyncSession,
    query: str,
    k: int = 12,
    since: datetime | None = None,
    topic: str | None = None,
    sources: list[str] | None = None,
) -> list[tuple[str, float]]:
    """Returns (item_id, ts_rank_cd)."""
    tsquery = func.websearch_to_tsquery("english", query)

    rank = func.ts_rank_cd(ItemRow.search_vector, tsquery).label("kw_rank")

    stmt = (
        select(ItemRow.id, rank)
        .where(ItemRow.search_vector.op("@@")(tsquery))
    )
    stmt = _apply_filters(stmt, since, topic, sources)
    stmt = stmt.order_by(rank.desc()).limit(k)

    rows = (await session.execute(stmt)).all()
    return [(row.id, row.kw_rank) for row in rows]


async def recent_items(
    session: AsyncSession,
    since: datetime,
    until: datetime | None = None,
    limit: int = 200,
) -> list[Item]:
    """Items ingested in [since, until), best score first. Keyed on created_at
    (ingest time)."""
    stmt = select(ItemRow).where(ItemRow.created_at >= since)
    if until is not None:
        stmt = stmt.where(ItemRow.created_at < until)
    # First by score then date created
    stmt = stmt.order_by(
        ItemRow.score.desc().nulls_last(), ItemRow.created_at.desc()
    ).limit(limit)
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


async def hydrate_items(
    session: AsyncSession,
    item_ids: list[str],
) -> list[Item]:
    """Fetch full Item rows by ID, preserving input order."""
    if not item_ids:
        return []
    id_order = {iid: i for i, iid in enumerate(item_ids)}
    stmt = select(ItemRow).where(ItemRow.id.in_(item_ids))
    rows = (await session.execute(stmt)).scalars().all()
    rows.sort(key=lambda r: id_order.get(r.id, 0))
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
