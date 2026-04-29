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


async def search(
    session: AsyncSession,
    embedding: list[float],
    k: int = 12,
    since: str | None = None,
    topic: str | None = None,
) -> list[Item]:
    raise NotImplementedError
