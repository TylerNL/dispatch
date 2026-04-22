from fastapi import APIRouter

from app.schemas.item import SourceStatus

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=list[SourceStatus])
async def list_sources() -> list[SourceStatus]:
    raise NotImplementedError
