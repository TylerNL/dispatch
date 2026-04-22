from collections.abc import AsyncIterator

from app.schemas.ask import AskResponse
from app.schemas.item import Item


async def generate(question: str, context: list[Item]) -> AskResponse:
    raise NotImplementedError


async def generate_stream(
    question: str, context: list[Item]
) -> AsyncIterator[str]:
    raise NotImplementedError
