from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.config import settings
from app.rag.prompts import SYSTEM_PROMPT, build_user_prompt, format_context
from app.schemas.ask import AskResponse, Citation
from app.schemas.item import Item

_client = AsyncOpenAI(api_key=settings.openai_api_key)


def _build_citations(items: list[Item]) -> list[Citation]:
    return [
        Citation(
            item_id=item.id,
            title=item.title,
            url=item.url,
            source=item.source,
            published_at=item.published_at,
        )
        for item in items
    ]


async def generate(question: str, context: list[Item]) -> AskResponse:
    user_msg = build_user_prompt(question, format_context(context))

    resp = await _client.chat.completions.create(
        model=settings.gen_model,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )

    return AskResponse(answer=resp.choices[0].message.content, citations=_build_citations(context))


async def generate_stream(question: str, context: list[Item]) -> AsyncIterator[str]:
    user_msg = build_user_prompt(question, format_context(context))

    stream = await _client.chat.completions.create(
        model=settings.gen_model,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
