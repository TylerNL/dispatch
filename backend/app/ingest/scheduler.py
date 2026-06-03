import asyncio
import logging

from app.ingest.base import Source
from app.ingest.sources import LIVE_SOURCES
from app.pipeline.classify import classify_batch
from app.pipeline.dedupe import is_duplicate
from app.pipeline.embed import embed_item
from app.pipeline.summarize import summarize_batch
from app.schemas.item import Item
from app.storage.db import SessionLocal
from app.storage.vector import upsert

logger = logging.getLogger(__name__)


async def run_once(source: Source) -> int:
    """Fetch → dedupe → summarize → classify → embed → upsert for one source.

    Returns the number of fresh items embedded into the store. Items already
    present (by URL fingerprint) are skipped before any LLM call, so re-runs are
    cheap and idempotent.
    """
    items: list[Item] = []
    async for item in source.fetch():
        items.append(item)

    async with SessionLocal() as session:
        fresh = [item for item in items if not await is_duplicate(session, item)]
        if not fresh:
            logger.info("%s: fetched=%d fresh=0 (all duplicates)", source.name, len(items))
            return 0

        for item, summary in zip(fresh, await summarize_batch(fresh)):
            item.summary = summary
        for item, (topic, score) in zip(fresh, await classify_batch(fresh)):
            item.topic = topic
            item.score = score

        embedded = 0
        for item in fresh:
            try:
                chunks, embeddings = await embed_item(item)
                async with session.begin_nested():
                    await upsert(session, item, chunks, embeddings)
                embedded += 1
            except Exception:
                logger.exception("embed/upsert failed for %s", item.id)

        await session.commit()

    logger.info(
        "%s: fetched=%d fresh=%d embedded=%d",
        source.name, len(items), len(fresh), embedded,
    )
    return embedded


async def run_all() -> dict[str, int]:
    """Run the pipeline over every live source. Per-source failures are isolated."""
    results: dict[str, int] = {}
    for source_cls in LIVE_SOURCES:
        src = source_cls()
        try:
            results[src.name] = await run_once(src)
        except Exception:
            logger.exception("run_once failed for %s", src.name)
            results[src.name] = 0
    return results



async def _main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    results = await run_all()
    total = sum(results.values())
    logger.info("ingest complete: total=%d %s", total, results)


if __name__ == "__main__":
    asyncio.run(_main())