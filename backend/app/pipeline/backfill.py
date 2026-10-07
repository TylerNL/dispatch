import argparse
import asyncio
import logging
from dataclasses import dataclass
from typing import cast

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.pipeline.classify import classify_batch
from app.pipeline.embed import embed_item
from app.pipeline.summarize import summarize_batch
from app.schemas.item import Item, Topic
from app.storage.db import SessionLocal
from app.storage.models import ItemRow
from app.storage.vector import upsert

logger = logging.getLogger(__name__)


@dataclass
class BackfillStats:
    processed: int = 0
    summarized: int = 0
    classified: int = 0
    reembedded: int = 0

    def add(self, other: "BackfillStats") -> None:
        self.processed += other.processed
        self.summarized += other.summarized
        self.classified += other.classified
        self.reembedded += other.reembedded


async def process_rows(
    session: AsyncSession,
    rows: list[ItemRow],
    *,
    classify_ids: set[str] | None = None,
) -> BackfillStats:
    items = [_to_item(row) for row in rows]
    by_id = {row.id: row for row in rows}

    needs_summary = [item for item in items if item.summary is None]
    for item, summary in zip(needs_summary, await summarize_batch(needs_summary)):
        item.summary = summary
        by_id[item.id].summary = summary

    needs_topic = [
        item
        for item in items
        if item.topic is None or (classify_ids is not None and item.id in classify_ids)
    ]
    for item, (topic, score) in zip(needs_topic, await classify_batch(needs_topic)):
        item.topic = topic
        item.score = score
        by_id[item.id].topic = topic
        by_id[item.id].score = score

    reembedded = 0
    for item in needs_summary:
        try:
            chunks, embeddings = await embed_item(item)
            await upsert(session, item, chunks, embeddings)
            reembedded += 1
        except Exception:
            logger.exception("re-embed failed for %s", item.id)

    await session.commit()
    return BackfillStats(
        processed=len(items),
        summarized=len(needs_summary),
        classified=len(needs_topic),
        reembedded=reembedded,
    )


async def backfill_incomplete(
    *,
    batch_size: int = 25,
    limit: int | None = None,
) -> BackfillStats:
    total = BackfillStats()

    while limit is None or total.processed < limit:
        current_batch_size = min(batch_size, limit - total.processed) if limit else batch_size
        async with SessionLocal() as session:
            rows = list(
                (
                    await session.execute(
                        select(ItemRow)
                        .where(
                            or_(
                                ItemRow.summary.is_(None),
                                ItemRow.topic.is_(None),
                            )
                        )
                        .order_by(ItemRow.created_at, ItemRow.id)
                        .limit(current_batch_size)
                    )
                )
                .scalars()
                .all()
            )
            if not rows:
                break

            batch = await process_rows(session, rows)
            total.add(batch)
            logger.info(
                "backfill progress: processed=%d summarized=%d classified=%d reembedded=%d",
                total.processed,
                total.summarized,
                total.classified,
                total.reembedded,
            )

    return total


async def reclassify_fallbacks(*, batch_size: int = 25) -> BackfillStats:
    async with SessionLocal() as session:
        target_ids = list(
            (
                await session.execute(
                    select(ItemRow.id)
                    .where(ItemRow.topic == "tooling", ItemRow.score == 0.5)
                    .order_by(ItemRow.created_at, ItemRow.id)
                )
            )
            .scalars()
            .all()
        )

    total = BackfillStats()
    for offset in range(0, len(target_ids), batch_size):
        batch_ids = target_ids[offset : offset + batch_size]
        async with SessionLocal() as session:
            rows = list(
                (
                    await session.execute(
                        select(ItemRow).where(ItemRow.id.in_(batch_ids))
                    )
                )
                .scalars()
                .all()
            )
            batch = await process_rows(
                session,
                rows,
                classify_ids=set(batch_ids),
            )
            total.add(batch)
            logger.info(
                "reclassification progress: processed=%d classified=%d",
                total.processed,
                total.classified,
            )
    return total


def _to_item(row: ItemRow) -> Item:
    return Item(
        id=row.id,
        source=row.source,
        external_id=row.external_id,
        url=row.url,
        title=row.title,
        author=row.author,
        published_at=row.published_at,
        summary=row.summary,
        topic=cast(Topic | None, row.topic),
        score=row.score,
    )


async def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--reclassify-fallbacks", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    if args.reclassify_fallbacks:
        stats = await reclassify_fallbacks(batch_size=args.batch_size)
    else:
        stats = await backfill_incomplete(batch_size=args.batch_size, limit=args.limit)
    logger.info(
        "backfill complete: processed=%d summarized=%d classified=%d reembedded=%d",
        stats.processed,
        stats.summarized,
        stats.classified,
        stats.reembedded,
    )


if __name__ == "__main__":
    asyncio.run(_main())
