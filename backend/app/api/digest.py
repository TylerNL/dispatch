from fastapi import APIRouter

from app.schemas.item import Digest

router = APIRouter(tags=["digest"])


@router.get("/digest/today", response_model=Digest)
async def digest_today() -> Digest:
    raise NotImplementedError


@router.get("/digest/{date}", response_model=Digest)
async def digest_by_date(date: str) -> Digest:
    raise NotImplementedError
