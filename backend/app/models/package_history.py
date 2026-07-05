from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class PackageHistoryEventType(StrEnum):
    PACKAGE_CREATED = "package_created"
    LINE_ITEM_ADDED = "line_item_added"
    LINE_ITEM_CHANGED = "line_item_changed"
    STATUS_CHANGED = "status_changed"
    LOCATION_UPDATED = "location_updated"
    ASSIGNED_TO_TRUCK = "assigned_to_truck"
    TRUCK_REROUTED = "truck_rerouted"
    DELIVERED = "delivered"
    RETURNED = "returned"
    DAMAGED = "damaged"
    CANCELLED = "cancelled"
    COMPLAINT_CREATED = "complaint_created"
    COMPLAINT_UPDATED = "complaint_updated"
    MANAGER_ACTION_PERFORMED = "manager_action_performed"
    DELAY_RECORDED = "delay_recorded"


class EventSource(StrEnum):
    UI = "ui"
    API = "api"
    DEMO = "demo"
    AGENT = "agent"
    SYSTEM = "system"


class PackageHistory(SQLModel, table=True):
    __tablename__ = "package_history"

    id: int | None = Field(default=None, primary_key=True)
    package_id: str = Field(foreign_key="package.package_id", index=True, max_length=100)
    event_type: str = Field(max_length=100, index=True)
    actor_id: str = Field(max_length=100)
    actor_name: str = Field(max_length=200)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    source: str = Field(max_length=50)
    entity_type: str = Field(default="package", max_length=100)
    entity_id: str = Field(max_length=100)
    previous_value: str | None = Field(default=None)
    new_value: str | None = Field(default=None)
    reason: str | None = Field(default=None, max_length=2000)
    correlation_id: str | None = Field(default=None, max_length=200)
