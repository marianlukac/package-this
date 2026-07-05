"""Domain event table for persisting all published domain events.

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "domain_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.String(36), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("topic", sa.String(100), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("actor_id", sa.String(200), nullable=False),
        sa.Column("actor_name", sa.String(200), nullable=False),
        sa.Column("actor_persona", sa.String(50), nullable=True),
        sa.Column("actor_type", sa.String(20), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(200), nullable=False),
        sa.Column("correlation_id", sa.String(36), nullable=True),
        sa.Column("payload", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_domain_event_event_id", "domain_event", ["event_id"], unique=True)
    op.create_index("ix_domain_event_event_type", "domain_event", ["event_type"])
    op.create_index("ix_domain_event_topic", "domain_event", ["topic"])
    op.create_index("ix_domain_event_occurred_at", "domain_event", ["occurred_at"])
    op.create_index("ix_domain_event_actor_id", "domain_event", ["actor_id"])
    op.create_index("ix_domain_event_source", "domain_event", ["source"])
    op.create_index("ix_domain_event_entity_type", "domain_event", ["entity_type"])
    op.create_index("ix_domain_event_entity_id", "domain_event", ["entity_id"])
    op.create_index("ix_domain_event_correlation_id", "domain_event", ["correlation_id"])


def downgrade() -> None:
    op.drop_index("ix_domain_event_correlation_id", "domain_event")
    op.drop_index("ix_domain_event_entity_id", "domain_event")
    op.drop_index("ix_domain_event_entity_type", "domain_event")
    op.drop_index("ix_domain_event_source", "domain_event")
    op.drop_index("ix_domain_event_actor_id", "domain_event")
    op.drop_index("ix_domain_event_occurred_at", "domain_event")
    op.drop_index("ix_domain_event_topic", "domain_event")
    op.drop_index("ix_domain_event_event_type", "domain_event")
    op.drop_index("ix_domain_event_event_id", "domain_event")
    op.drop_table("domain_event")
