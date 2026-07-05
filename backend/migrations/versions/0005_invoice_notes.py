"""Add notes column to invoice table.

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-05
"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("invoice") as batch_op:
        batch_op.add_column(sa.Column("notes", sqlmodel.AutoString(), nullable=True, server_default=""))


def downgrade() -> None:
    with op.batch_alter_table("invoice") as batch_op:
        batch_op.drop_column("notes")
