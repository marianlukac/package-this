"""Truck routing, map locations, and package GPS fields.

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- truck table: add new columns ---
    # current_route_id was INTEGER; change to VARCHAR via batch (SQLite compatible)
    with op.batch_alter_table("truck") as batch_op:
        batch_op.drop_column("current_route_id")
        batch_op.add_column(sa.Column("current_route_id", sa.String(200), nullable=True))
        batch_op.add_column(sa.Column("truck_number", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("delay_duration_hours", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("delay_started_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))

    # --- package table: add GPS coordinate fields ---
    with op.batch_alter_table("package") as batch_op:
        batch_op.add_column(sa.Column("current_lat", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("current_lng", sa.Float(), nullable=True))

    # --- Drop old stub truck_route table if it exists (created by SQLModel.create_all) ---
    # The migration 0001 created "truckroute"; SQLModel.create_all creates "truck_route".
    # Both are replaced by the new truck_route table below.
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "sqlite":
        existing = bind.execute(
            sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='truck_route'")
        ).fetchone()
        if existing:
            op.drop_table("truck_route")
        existing2 = bind.execute(
            sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='truckroute'")
        ).fetchone()
        if existing2:
            op.drop_table("truckroute")
    else:
        # SQL Server — use IF EXISTS pattern via execute
        bind.execute(sa.text("IF OBJECT_ID('truck_route', 'U') IS NOT NULL DROP TABLE truck_route"))
        bind.execute(sa.text("IF OBJECT_ID('truckroute', 'U') IS NOT NULL DROP TABLE truckroute"))

    # --- New truck_route table ---
    op.create_table(
        "truck_route",
        sa.Column("route_id", sa.String(200), nullable=False),
        sa.Column("truck_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.AutoString(), nullable=False, server_default="planned"),
        sa.Column("geometry", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_waypoint_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("route_id"),
    )
    op.create_index("ix_truck_route_truck_id", "truck_route", ["truck_id"])

    # --- route_stop table ---
    op.create_table(
        "route_stop",
        sa.Column("stop_id", sa.String(200), nullable=False),
        sa.Column("route_id", sa.String(200), nullable=False),
        sa.Column("customer_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("stop_order", sa.Integer(), nullable=False),
        sa.Column("estimated_arrival", sa.DateTime(), nullable=True),
        sa.Column("arrived_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["route_id"], ["truck_route.route_id"]),
        sa.PrimaryKeyConstraint("stop_id"),
    )
    op.create_index("ix_route_stop_route_id", "route_stop", ["route_id"])

    # --- via_point table ---
    op.create_table(
        "via_point",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.String(200), nullable=False),
        sa.Column("name", sqlmodel.AutoString(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("inserted_before_stop_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inserted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["route_id"], ["truck_route.route_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_via_point_route_id", "via_point", ["route_id"])

    # --- map_location table ---
    op.create_table(
        "map_location",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.AutoString(), nullable=False),
        sa.Column("location_type", sqlmodel.AutoString(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("description", sqlmodel.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_map_location_type", "map_location", ["location_type"])


def downgrade() -> None:
    op.drop_index("ix_map_location_type", "map_location")
    op.drop_table("map_location")
    op.drop_index("ix_via_point_route_id", "via_point")
    op.drop_table("via_point")
    op.drop_index("ix_route_stop_route_id", "route_stop")
    op.drop_table("route_stop")
    op.drop_index("ix_truck_route_truck_id", "truck_route")
    op.drop_table("truck_route")

    with op.batch_alter_table("package") as batch_op:
        batch_op.drop_column("current_lng")
        batch_op.drop_column("current_lat")

    with op.batch_alter_table("truck") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("delay_started_at")
        batch_op.drop_column("delay_duration_hours")
        batch_op.drop_column("truck_number")
        batch_op.drop_column("current_route_id")
        batch_op.add_column(sa.Column("current_route_id", sa.Integer(), nullable=True))
