from app.schemas.item import Item


async def summarize(item: Item) -> str:
    raise NotImplementedError


async def summarize_batch(items: list[Item]) -> list[str]:
    raise NotImplementedError
