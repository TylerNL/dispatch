from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

from app.schemas.item import Item


class Source(ABC):
    name: str

    @abstractmethod
    async def fetch(self, since: datetime | None = None) -> AsyncIterator[Item]:
        ...
