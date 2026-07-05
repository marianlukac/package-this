"""Initial schema — all DM Package Manager tables.

Revision ID: 0001
Revises:
Create Date: 2026-06-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employee",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.AutoString(), nullable=False),
        sa.Column("persona", sqlmodel.AutoString(), nullable=False),
        sa.Column("title", sqlmodel.AutoString(), nullable=True),
        sa.Column("email", sqlmodel.AutoString(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id"),
    )

    op.create_table(
        "customer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.AutoString(), nullable=False),
        sa.Column("address", sqlmodel.AutoString(), nullable=True),
        sa.Column("city", sqlmodel.AutoString(), nullable=True),
        sa.Column("state", sqlmodel.AutoString(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("is_unhappy", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("contact_name", sqlmodel.AutoString(), nullable=True),
        sa.Column("contact_email", sqlmodel.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id"),
    )

    op.create_table(
        "sale",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("customer_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("salesperson_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("notes", sqlmodel.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sale_id"),
    )

    op.create_table(
        "invoice",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("sale_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("created_by_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_id"),
        sa.UniqueConstraint("sale_id"),
    )

    op.create_table(
        "truck",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("truck_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.AutoString(), nullable=False),
        sa.Column("driver_name", sqlmodel.AutoString(), nullable=True),
        sa.Column("status", sqlmodel.AutoString(), nullable=False, server_default="available"),
        sa.Column("current_lat", sa.Float(), nullable=True),
        sa.Column("current_lng", sa.Float(), nullable=True),
        sa.Column("current_route_id", sa.Integer(), nullable=True),
        sa.Column("current_stop_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_delayed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("delay_reason", sqlmodel.AutoString(), nullable=True),
        sa.Column("last_location_update", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("truck_id"),
    )

    op.create_table(
        "truckroute",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("truck_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("stops_json", sa.Text(), nullable=False),
        sa.Column("azure_maps_route", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "package",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("package_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("sale_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("invoice_id", sqlmodel.AutoString(), nullable=True),
        sa.Column("customer_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("salesperson_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("invoicing_employee_id", sqlmodel.AutoString(), nullable=True),
        sa.Column("status", sqlmodel.AutoString(), nullable=False),
        sa.Column("current_location", sqlmodel.AutoString(), nullable=True),
        sa.Column("destination", sqlmodel.AutoString(), nullable=True),
        sa.Column("truck_id", sqlmodel.AutoString(), nullable=True),
        sa.Column("expected_delivery", sa.DateTime(), nullable=True),
        sa.Column("priority", sqlmodel.AutoString(), nullable=False, server_default="standard"),
        sa.Column("contents_summary", sqlmodel.AutoString(), nullable=True),
        sa.Column("fragile", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("delay_reason", sqlmodel.AutoString(), nullable=True),
        sa.Column("delay_duration_hours", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("package_id"),
    )

    op.create_table(
        "packagelineitem",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("package_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("product_name", sqlmodel.AutoString(), nullable=False),
        sa.Column("product_category", sqlmodel.AutoString(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_description", sqlmodel.AutoString(), nullable=True),
        sa.Column("product_type", sqlmodel.AutoString(), nullable=False, server_default="paper"),
        sa.Column("fragile", sa.Boolean(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "packagehistory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("package_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("event_type", sqlmodel.AutoString(), nullable=False),
        sa.Column("actor_id", sqlmodel.AutoString(), nullable=True),
        sa.Column("actor_name", sqlmodel.AutoString(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("source", sqlmodel.AutoString(), nullable=True),
        sa.Column("entity_type", sqlmodel.AutoString(), nullable=True),
        sa.Column("entity_id", sqlmodel.AutoString(), nullable=True),
        sa.Column("previous_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("reason", sqlmodel.AutoString(), nullable=True),
        sa.Column("correlation_id", sqlmodel.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "complaint",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("complaint_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("sale_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sqlmodel.AutoString(), nullable=False, server_default="open"),
        sa.Column("created_by_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("source", sqlmodel.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("complaint_id"),
    )

    op.create_table(
        "complaintpackage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("complaint_id", sqlmodel.AutoString(), nullable=False),
        sa.Column("package_id", sqlmodel.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "auditlog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sqlmodel.AutoString(), nullable=True),
        sa.Column("actor_name", sqlmodel.AutoString(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("source", sqlmodel.AutoString(), nullable=True),
        sa.Column("entity_type", sqlmodel.AutoString(), nullable=True),
        sa.Column("entity_id", sqlmodel.AutoString(), nullable=True),
        sa.Column("action", sqlmodel.AutoString(), nullable=True),
        sa.Column("previous_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("reason", sqlmodel.AutoString(), nullable=True),
        sa.Column("correlation_id", sqlmodel.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Indexes for common lookups
    op.create_index("ix_package_status", "package", ["status"])
    op.create_index("ix_package_customer", "package", ["customer_id"])
    op.create_index("ix_packagehistory_package", "packagehistory", ["package_id"])
    op.create_index("ix_auditlog_entity", "auditlog", ["entity_type", "entity_id"])
    op.create_index("ix_complaint_sale", "complaint", ["sale_id"])


def downgrade() -> None:
    op.drop_table("auditlog")
    op.drop_table("complaintpackage")
    op.drop_table("complaint")
    op.drop_table("packagehistory")
    op.drop_table("packagelineitem")
    op.drop_table("package")
    op.drop_table("truckroute")
    op.drop_table("truck")
    op.drop_table("invoice")
    op.drop_table("sale")
    op.drop_table("customer")
    op.drop_table("employee")
