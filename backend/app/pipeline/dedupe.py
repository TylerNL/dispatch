from app.schemas.item import Item


def canonical_url(url: str) -> str:
    raise NotImplementedError


def fingerprint(item: Item) -> str:
    raise NotImplementedError


async def is_duplicate(item: Item) -> bool:
    raise NotImplementedError
