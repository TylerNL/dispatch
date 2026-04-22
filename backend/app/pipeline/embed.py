from app.schemas.item import Item


async def embed_text(text: str) -> list[float]:
    raise NotImplementedError


async def embed_batch(texts: list[str]) -> list[list[float]]:
    raise NotImplementedError


async def embed_item(item: Item) -> list[float]:
    raise NotImplementedError
