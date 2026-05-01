"""initial schema

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-04-30 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

from app.storage.models import EMBED_DIM

revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET search_path TO public, embeddings")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector SCHEMA embeddings")

    op.create_table(
        "items",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("topic", sa.String(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("fingerprint", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source", "external_id", name="uq_items_source_external_id"),
    )
    op.create_index("ix_items_source", "items", ["source"])
    op.create_index("ix_items_fingerprint", "items", ["fingerprint"])
    op.create_index("ix_items_published_at", "items", ["published_at"])
    op.create_index("ix_items_topic_published", "items", ["topic", "published_at"])

    op.execute(f"""
        CREATE TABLE chunks (
            id VARCHAR NOT NULL,
            item_id VARCHAR NOT NULL,
            content TEXT NOT NULL,
            embedding embeddings.vector({EMBED_DIM}) NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX ix_chunks_item_id ON chunks (item_id)")
    op.execute(
        f"CREATE INDEX ix_chunks_embedding_hnsw ON chunks "
        f"USING hnsw (embedding embeddings.vector_cosine_ops)"
    )

    op.create_table(
        "sources",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("last_pulled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "items_today",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "healthy",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("name"),
    )

    op.create_table(
        "subscribers",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("topics", sa.Text(), nullable=True),
        sa.Column("sources", sa.Text(), nullable=True),
        sa.Column(
            "active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_subscribers_email", "subscribers", ["email"])


def downgrade() -> None:
    op.drop_index("ix_subscribers_email", table_name="subscribers")
    op.drop_table("subscribers")
    op.drop_table("sources")
    op.drop_index("ix_chunks_embedding_hnsw", table_name="chunks")
    op.drop_index("ix_chunks_item_id", table_name="chunks")
    op.drop_table("chunks")
    op.drop_index("ix_items_topic_published", table_name="items")
    op.drop_index("ix_items_published_at", table_name="items")
    op.drop_index("ix_items_fingerprint", table_name="items")
    op.drop_index("ix_items_source", table_name="items")
    op.drop_table("items")
