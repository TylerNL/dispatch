from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.ask import AskRequest, AskResponse

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    raise NotImplementedError


@router.post("/ask/stream")
async def ask_stream(req: AskRequest) -> StreamingResponse:
    raise NotImplementedError
