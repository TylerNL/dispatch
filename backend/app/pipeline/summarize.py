import asyncio
import logging

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.item import Item

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.openai_api_key)

_MIN_SUMMARY_LEN = 80

_MAX_CONCURRENCY = 8


def _needs_summary(item: Item) -> bool:
    return not item.summary or len(item.summary) < _MIN_SUMMARY_LEN


async def summarize(item: Item) -> str:
    if not _needs_summary(item):
        return item.summary  # type: ignore[return-value]

    body = item.summary or ""
    prompt = settings.summarize_prompt.format(
        title=item.title,
        source=item.source,
        body=f"Content: {body}" if body else "",
    )

    resp = await _client.chat.completions.create(
        model=settings.gen_model,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    return resp.choices[0].message.content.strip()


async def summarize_batch(items: list[Item]) -> list[str]:
    sem = asyncio.Semaphore(_MAX_CONCURRENCY)

    async def _one(item: Item) -> str:
        async with sem:
            try:
                return await summarize(item)
            except Exception:
                logger.exception("summarize failed for %s", item.id)
                return item.title

    return list(await asyncio.gather(*(_one(item) for item in items)))