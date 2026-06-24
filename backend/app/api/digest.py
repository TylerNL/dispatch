from datetime import date

from fastapi import APIRouter, HTTPException

from app.digest.builder import build_for, today
from app.schemas.item import Digest

router = APIRouter(tags=["digest"])


@router.get("/digest/today", response_model=Digest)
async def digest_today() -> Digest:
    return await build_for(today())


@router.get("/digest/{date_str}", response_model=Digest)
async def digest_by_date(date_str: str) -> Digest:
    try:
        day = date.fromisoformat(date_str)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date, use YYYY-MM-DD") from exc
    return await build_for(day)