from openai import AsyncOpenAI

from app.config import settings
from app.schemas.item import Item
from app.storage.models import EMBED_DIM

_client = AsyncOpenAI(api_key=settings.openai_api_key)


async def embed_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    resp = await _client.embeddings.create(
        input=texts,
        model=settings.embed_model,
        dimensions=EMBED_DIM,
    )
    return [entry.embedding for entry in resp.data]


async def embed_text(text: str) -> list[float]:
    results = await embed_batch([text])
    return results[0]


def chunk_item(item: Item) -> list[str]:
    text = item.title
    if item.summary:
        text += f"\n\n{item.summary}"
    return [text.strip()]


async def embed_item(item: Item) -> tuple[list[str], list[list[float]]]:
    chunks = chunk_item(item)
    embeddings = await embed_batch(chunks)
    return chunks, embeddings
