from logging.config import fileConfig

from sqlalchemy import create_engine

from alembic import context
from app.config import settings
from app.storage.models import Base

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

_raw_url = settings.database_url_direct or settings.database_url

def _psycopg3_url(u: str) -> str:
    for prefix in ("postgresql://", "postgres://"):
        if u.startswith(prefix):
            return "postgresql+psycopg://" + u[len(prefix):]
    return u

url = _psycopg3_url(_raw_url)


def run_migrations_offline() -> None:
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        url, connect_args={"options": "-csearch_path=public,extensions"}
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
