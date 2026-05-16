import json
import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.rag.generator import _build_citations, generate, generate_stream
from app.rag.retriever import retrieve
from app.schemas.ask import AskRequest, AskResponse

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    t0 = time.perf_counter()
    context = await retrieve(req.question, window=req.window, topic=req.topic)
    resp = await generate(req.question, context)
    resp.latency_ms = int((time.perf_counter() - t0) * 1000)
    return resp


@router.post("/ask/stream")
async def ask_stream(req: AskRequest) -> StreamingResponse:
    context = await retrieve(req.question, window=req.window, topic=req.topic)

    async def event_stream():
        async for chunk in generate_stream(req.question, context):
            yield f"data: {json.dumps({'type': 'delta', 'text': chunk})}\n\n"
        cites = [c.model_dump(mode="json") for c in _build_citations(context)]
        yield f"data: {json.dumps({'type': 'citations', 'citations': cites})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
