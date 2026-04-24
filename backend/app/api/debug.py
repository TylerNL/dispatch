from fastapi import APIRouter

from app.ingest.sources import AnthropicBlog, ArXiv, HackerNews, TechCrunch
from app.schemas.item import Item

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
