import hashlib
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.item import Item
from app.storage.models import ItemRow

_UTM_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign",
    "utm_term", "utm_content", "ref", "source",
}


def canonical_url(url: str) -> str:
    parsed = urlparse(url.lower().rstrip("/"))
    qs = {k: v for k, v in parse_qs(parsed.query).items() if k not in _UTM_PARAMS}
    cleaned = parsed._replace(query=urlencode(qs, doseq=True), fragment="")
    return urlunparse(cleaned)


def fingerprint(item: Item) -> str:
    return hashlib.sha256(canonical_url(item.url).encode()).hexdigest()


async def is_duplicate(session: AsyncSession, item: Item) -> bool:
    fp = fingerprint(item)
    result = await session.execute(
        select(ItemRow.id).where(ItemRow.fingerprint == fp).limit(1)
    )
    return result.scalar() is not None
