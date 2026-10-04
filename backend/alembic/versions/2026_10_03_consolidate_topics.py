"""consolidate community and signal into tooling

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-10-03 16:35:00.000000

"""

from alembic import op

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE items SET topic = 'tooling' WHERE topic IN ('community', 'signal')"
    )
    op.execute("""
        UPDATE subscribers AS subscriber
        SET topics = normalized.topics
        FROM (
            SELECT id, string_agg(topic, ',' ORDER BY first_position) AS topics
            FROM (
                SELECT
                    id,
                    CASE
                        WHEN selected_topic IN ('community', 'signal') THEN 'tooling'
                        ELSE selected_topic
                    END AS topic,
                    min(position) AS first_position
                FROM subscribers
                CROSS JOIN LATERAL unnest(string_to_array(topics, ','))
                    WITH ORDINALITY AS selected(selected_topic, position)
                GROUP BY id, topic
            ) AS deduplicated
            GROUP BY id
        ) AS normalized
        WHERE subscriber.id = normalized.id
          AND subscriber.topics SIMILAR TO '%(community|signal)%'
    """)


def downgrade() -> None:
    op.execute("UPDATE items SET topic = 'community' WHERE topic = 'tooling'")
    op.execute(
        "UPDATE subscribers "
        "SET topics = replace(topics, 'tooling', 'community') "
        "WHERE topics LIKE '%tooling%'"
    )
