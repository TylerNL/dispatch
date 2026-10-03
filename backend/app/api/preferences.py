from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import AuthenticatedUser, get_authenticated_user
from app.schemas.subscriber import SubscriberPreferences
from app.storage import subscribers
from app.storage.db import get_session

router = APIRouter(tags=["preferences"])


@router.get("/preferences", response_model=SubscriberPreferences)
async def get_preferences(
    user: AuthenticatedUser = Depends(get_authenticated_user),
    session: AsyncSession = Depends(get_session),
) -> SubscriberPreferences:
    row = await subscribers.get_subscriber(session, user.id)
    return subscribers.to_preferences(row)


@router.put("/preferences", response_model=SubscriberPreferences)
async def update_preferences(
    preferences: SubscriberPreferences,
    user: AuthenticatedUser = Depends(get_authenticated_user),
    session: AsyncSession = Depends(get_session),
) -> SubscriberPreferences:
    if not user.email:
        raise HTTPException(status_code=422, detail="Account email is required")

    row = await subscribers.save_preferences(
        session,
        user_id=user.id,
        email=user.email,
        enabled=preferences.enabled,
        topics=preferences.topics,
    )
    return subscribers.to_preferences(row)
