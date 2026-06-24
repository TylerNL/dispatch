import json
import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.auth import get_current_user
from app.rag.generator import _build_citations, generate, generate_stream
from app.rag.retriever import retrieve
from app.rag.titler import generate_title
from app.schemas.ask import AskRequest, AskResponse
from app.storage import chats
from app.storage.db import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ask"])


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/ask", response_model=AskResponse)
async def ask(
    req: AskRequest,
    user_id: str = Depends(get_current_user),
) -> AskResponse:
    t0 = time.perf_counter()
    context = await retrieve(req.question, window=req.window, topic=req.topic, sources=req.sources)
    resp = await generate(req.question, context)
    resp.latency_ms = int((time.perf_counter() - t0) * 1000)
    return resp


@router.post("/ask/stream")
async def ask_stream(
    req: AskRequest,
    user_id: str = Depends(get_current_user),
) -> StreamingResponse:
    if not req.conversation_id:
        raise HTTPException(status_code=422, detail="conversation_id is required")

    context = await retrieve(
        req.question, window=req.window, topic=req.topic, sources=req.sources
    )
    cites_json = [c.model_dump(mode="json") for c in _build_citations(context)]

    async def event_stream():
        async with SessionLocal() as session:
            try:
                conv = await chats.get_or_create_conversation(
                    session, user_id, req.conversation_id, req.title
                )
            except chats.NotOwner:
                yield _sse({"type": "error", "error": "forbidden"})
                yield "data: [DONE]\n\n"
                return

            is_first = await chats.count_messages(session, conv.id) == 0
            await chats.append_message(session, conv.id, "user", req.question)
            yield _sse({"type": "meta", "conversation_id": conv.id})

            parts: list[str] = []
            persisted = False
            try:
                async for chunk in generate_stream(req.question, context):
                    parts.append(chunk)
                    yield _sse({"type": "delta", "text": chunk})

                answer = "".join(parts)
                yield _sse({"type": "citations", "citations": cites_json})
                await chats.append_message(
                    session, conv.id, "assistant", answer, citations=cites_json
                )
                await chats.touch_conversation(session, conv.id)
                persisted = True

                if is_first and answer:
                    try:
                        title = await generate_title(req.question, answer)
                        await chats.rename_conversation(session, user_id, conv.id, title)
                        yield _sse({"type": "title", "title": title})
                    except Exception:
                        logger.exception("title generation failed for %s", conv.id)

                yield "data: [DONE]\n\n"
            finally:
                # Client disconnected mid-stream — save whatever we generated.
                if not persisted and parts:
                    try:
                        await chats.append_message(
                            session, conv.id, "assistant", "".join(parts), citations=cites_json
                        )
                        await chats.touch_conversation(session, conv.id)
                    except Exception:
                        logger.exception("failed to persist partial answer for %s", conv.id)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
