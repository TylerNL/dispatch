from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Supabase transaction-pooler (:6543) does not support prepared statements.
# Setting prepare_threshold=None disables psycopg's statement cache so we don't
# get DuplicatePreparedStatement errors under load.
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"prepare_threshold": None},
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
