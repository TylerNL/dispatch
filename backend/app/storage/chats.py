# Ownership-scoped persistence for chat conversations + messages.


import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.models import ConversationRow, MessageRow


class NotOwner(Exception):
    """Raised when a conversation exists but belongs to another user."""


async def list_conversations(session: AsyncSession, user_id: str) -> list[ConversationRow]:
    result = await session.execute(
        select(ConversationRow)
        .where(ConversationRow.user_id == user_id)
        .order_by(ConversationRow.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_conversation(
    session: AsyncSession, user_id: str, conv_id: str
) -> ConversationRow | None:
    conv = await session.get(ConversationRow, conv_id)
    if conv is None or conv.user_id != user_id:
        return None
    return conv


async def list_messages(session: AsyncSession, conv_id: str) -> list[MessageRow]:
    result = await session.execute(
        select(MessageRow)
        .where(MessageRow.conversation_id == conv_id)
        .order_by(MessageRow.created_at)
    )
    return list(result.scalars().all())


async def count_messages(session: AsyncSession, conv_id: str) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(MessageRow)
        .where(MessageRow.conversation_id == conv_id)
    )
    return result.scalar_one()


async def get_or_create_conversation(
    session: AsyncSession, user_id: str, conv_id: str, title: str | None
) -> ConversationRow:
    """Fetch the conversation (verifying ownership) or create it with the given id.

    The id is client-generated so the URL can update optimistically; we trust it
    but scope it to the caller. Raises NotOwner if the id is taken by someone else.
    """
    existing = await session.get(ConversationRow, conv_id)
    if existing is not None:
        if existing.user_id != user_id:
            raise NotOwner(conv_id)
        return existing

    conv = ConversationRow(id=conv_id, user_id=user_id, title=title)
    session.add(conv)
    await session.commit()
    return conv


async def append_message(
    session: AsyncSession,
    conv_id: str,
    role: str,
    content: str,
    citations: list | None = None,
    parent_message_id: str | None = None,
) -> MessageRow:
    msg = MessageRow(
        id=uuid.uuid4().hex,
        conversation_id=conv_id,
        role=role,
        content=content,
        citations=citations,
        parent_message_id=parent_message_id,
    )
    session.add(msg)
    await session.commit()
    return msg


async def touch_conversation(session: AsyncSession, conv_id: str) -> None:
    await session.execute(
        update(ConversationRow)
        .where(ConversationRow.id == conv_id)
        .values(updated_at=func.now())
    )
    await session.commit()


async def rename_conversation(
    session: AsyncSession, user_id: str, conv_id: str, title: str
) -> bool:
    result = await session.execute(
        update(ConversationRow)
        .where(ConversationRow.id == conv_id, ConversationRow.user_id == user_id)
        .values(title=title)
    )
    await session.commit()
    return result.rowcount > 0


async def delete_conversation(session: AsyncSession, user_id: str, conv_id: str) -> bool:
    result = await session.execute(
        delete(ConversationRow).where(
            ConversationRow.id == conv_id, ConversationRow.user_id == user_id
        )
    )
    await session.commit()
    return result.rowcount > 0