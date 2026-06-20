from datetime import datetime

from pydantic import BaseModel

from app.schemas.ask import Citation


class ConversationSummary(BaseModel):
    id: str
    title: str | None = None
    updated_at: datetime


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    citations: list[Citation] | None = None
    created_at: datetime


class ConversationDetail(BaseModel):
    id: str
    title: str | None = None
    messages: list[MessageOut]


class RenameRequest(BaseModel):
    title: str