import logging
import time

from fastapi import APIRouter
from pydantic import BaseModel

from app.ingest.sources import AnthropicBlog, ArXiv, HackerNews, OpenAIBlog, TechCrunch
from app.pipeline.embed import embed_item
from app.schemas.item import Item
from app.storage.db import SessionLocal
from app.storage.vector import upsert

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["debug"])


async def _collect(source_cls) -> list[Item]:
    items: list[Item] = []
    async for item in source_cls().fetch():
        items.append(item)
    return items


@router.get("/ingest-hn", response_model=list[Item])
async def ingest_hn() -> list[Item]:
    return await _collect(HackerNews)


@router.get("/ingest-arxiv", response_model=list[Item])
async def ingest_arxiv() -> list[Item]:
    return await _collect(ArXiv)


@router.get("/ingest-techcrunch", response_model=list[Item])
async def ingest_techcrunch() -> list[Item]:
    return await _collect(TechCrunch)


@router.get("/ingest-anthropic", response_model=list[Item])
async def ingest_anthropic() -> list[Item]:
    return await _collect(AnthropicBlog)


@router.get("/ingest-openai", response_model=list[Item])
async def ingest_openai() -> list[Item]:
    return await _collect(OpenAIBlog)


class SeedResult(BaseModel):
    source: str
    fetched: int
    embedded: int
    errors: int

class SeedResponse(BaseModel):
    total_embedded: int
    elapsed_ms: int
    sources: list[SeedResult]

_SEED_SOURCES = [HackerNews, ArXiv, TechCrunch, AnthropicBlog, OpenAIBlog]

# For debugging ingest
@router.post("/seed", response_model=SeedResponse)
async def seed() -> SeedResponse:
    t0 = time.perf_counter()
    results: list[SeedResult] = []

    async with SessionLocal() as session:
        for source_cls in _SEED_SOURCES:
            src = source_cls()
            items: list[Item] = []
            try:
                async for item in src.fetch():
                    items.append(item)
            except Exception:
                logger.exception("fetch failed for %s", src.name)

            embedded = 0
            errors = 0
            for item in items:
                try:
                    chunks, embeddings = await embed_item(item)
                    async with session.begin_nested():
                        await upsert(session, item, chunks, embeddings)
                    embedded += 1
                except Exception:
                    logger.exception("embed/upsert failed for %s", item.id)
                    errors += 1

            results.append(
                SeedResult(
                    source=src.name,
                    fetched=len(items),
                    embedded=embedded,
                    errors=errors,
                )
            )
            logger.info("%s: fetched=%d embedded=%d errors=%d", src.name, len(items), embedded, errors)

        await session.commit()

    total = sum(r.embedded for r in results)
    elapsed = int((time.perf_counter() - t0) * 1000)
    return SeedResponse(total_embedded=total, elapsed_ms=elapsed, sources=results)
