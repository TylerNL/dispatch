import httpx

from app.config import settings
from app.schemas.item import Item
from app.storage.models import EMBED_DIM

_OPENAI_URL = "https://api.openai.com/v1/embeddings"

async def embed_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            _OPENAI_URL,
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "input": texts,
                "model": settings.embed_model,
                "dimensions": EMBED_DIM,
            },
        )
        resp.raise_for_status()
    data = resp.json()
    ordered = sorted(data["data"], key=lambda x: x["index"])
    return [entry["embedding"] for entry in ordered]


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
