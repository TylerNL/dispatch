import asyncio
import json
import logging
from typing import get_args

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.item import Item, Topic

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.openai_api_key)

_VALID_TOPICS = get_args(Topic)

_MAX_CONCURRENCY = 8  



async def classify(item: Item) -> tuple[Topic, float]:
    summary_line = f"Summary: {item.summary}" if item.summary else ""
    prompt = settings.classify_prompt.format(
        topics=", ".join(_VALID_TOPICS),
        title=item.title,
        source=item.source,
        summary_line=summary_line,
    )

    resp = await _client.chat.completions.create(
        model=settings.gen_model,
        max_tokens=64,
        messages=[{"role": "user", "content": prompt}],
    )

    text = resp.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    data = json.loads(text)

    topic = data["topic"]
    if topic not in _VALID_TOPICS:
        logger.warning("invalid topic %r for %s, defaulting to community", topic, item.id)
        topic = "community"

    score = max(0.0, min(1.0, float(data["score"])))
    return topic, score


async def classify_topic(item: Item) -> Topic:
    topic, _ = await classify(item)
    return topic


async def score_signal(item: Item) -> float:
    _, score = await classify(item)
    return score


async def classify_batch(items: list[Item]) -> list[tuple[Topic, float]]:
    sem = asyncio.Semaphore(_MAX_CONCURRENCY)

    async def _one(item: Item) -> tuple[Topic, float]:
        async with sem:
            try:
                return await classify(item)
            except Exception:
                logger.exception("classify failed for %s", item.id)
                return ("community", 0.5)

    return list(await asyncio.gather(*(_one(item) for item in items)))
