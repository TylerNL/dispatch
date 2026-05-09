from collections.abc import AsyncIterator

import anthropic

from app.config import settings
from app.rag.prompts import SYSTEM_PROMPT, build_user_prompt, format_context
from app.schemas.ask import AskResponse, Citation
from app.schemas.item import Item

_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


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

    resp = await _client.messages.create(
        model=settings.gen_model,
        max_tokens=1024,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_msg}],
    )

    return AskResponse(answer=resp.content[0].text, citations=_build_citations(context))


async def generate_stream(question: str, context: list[Item]) -> AsyncIterator[str]:
    user_msg = build_user_prompt(question, format_context(context))

    async with _client.messages.stream(
        model=settings.gen_model,
        max_tokens=1024,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_msg}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
