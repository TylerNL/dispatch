from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.schemas.chat import (
    ConversationDetail,
    ConversationSummary,
    MessageOut,
    RenameRequest,
)
from app.storage import chats
from app.storage.db import get_session

router = APIRouter(tags=["chats"])


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ConversationSummary]:
    rows = await chats.list_conversations(session, user_id)
    return [
        ConversationSummary(id=r.id, title=r.title, updated_at=r.updated_at)
        for r in rows
    ]


@router.get("/conversations/{conv_id}", response_model=ConversationDetail)
async def get_conversation(
    conv_id: str,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ConversationDetail:
    conv = await chats.get_conversation(session, user_id, conv_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await chats.list_messages(session, conv_id)
    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        messages=[
            MessageOut(
                id=m.id,
                role=m.role,
                content=m.content,
                citations=m.citations,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


@router.patch("/conversations/{conv_id}", status_code=204)
async def rename_conversation(
    conv_id: str,
    req: RenameRequest,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    ok = await chats.rename_conversation(session, user_id, conv_id, req.title)
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.delete("/conversations/{conv_id}", status_code=204)
async def delete_conversation(
    conv_id: str,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    ok = await chats.delete_conversation(session, user_id, conv_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")