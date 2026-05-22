"""add search_vector tsvector column to items

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-22 00:00:00.000000

"""

from alembic import op

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE items ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(summary, '')), 'B')
        ) STORED
    """)
    op.execute(
        "CREATE INDEX ix_items_search_vector ON items USING gin(search_vector)"
    )


def downgrade() -> None:
    op.drop_index("ix_items_search_vector", table_name="items")
    op.execute("ALTER TABLE items DROP COLUMN search_vector")
