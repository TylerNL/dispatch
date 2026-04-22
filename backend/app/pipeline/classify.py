from app.schemas.item import Item, Topic


async def classify_topic(item: Item) -> Topic:
    raise NotImplementedError


async def score_signal(item: Item) -> float:
    raise NotImplementedError
