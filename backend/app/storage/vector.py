from app.schemas.item import Item


async def upsert(item_id: str, chunks: list[str], embeddings: list[list[float]]) -> None:
    raise NotImplementedError


async def search(
    embedding: list[float],
    k: int = 12,
    since: str | None = None,
    topic: str | None = None,
) -> list[Item]:
    raise NotImplementedError
