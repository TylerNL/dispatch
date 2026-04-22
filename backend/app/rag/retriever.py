from app.schemas.ask import TimeWindow
from app.schemas.item import Item


async def retrieve(
    question: str,
    window: TimeWindow = "week",
    topic: str | None = None,
    k: int = 12,
) -> list[Item]:
    raise NotImplementedError
