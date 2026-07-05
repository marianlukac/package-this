from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class TruckStatus(StrEnum):
    AT_WAREHOUSE = "at_warehouse"
    LOADING = "loading"
    READY = "ready"
    ON_ROUTE = "on_route"
    REROUTED = "rerouted"
    RETURNING = "returning"
    COMPLETED = "completed"
    DELAYED = "delayed"
    IN_TRANSIT = "in_transit"  # legacy alias kept for backward compatibility


class Truck(SQLModel, table=True):
    __tablename__ = "truck"

    id: int | None = Field(default=None, primary_key=True)
    truck_id: str = Field(unique=True, index=True, max_length=100)
    truck_number: int | None = Field(default=None)
    name: str = Field(max_length=200)
    driver_name: str | None = Field(default=None, max_length=200)
    status: str = Field(default=TruckStatus.AT_WAREHOUSE)
    current_lat: float | None = Field(default=None)
    current_lng: float | None = Field(default=None)
    current_stop_index: int = Field(default=0)
    is_delayed: bool = Field(default=False)
    delay_reason: str | None = Field(default=None, max_length=2000)
    delay_duration_hours: float | None = Field(default=None)
    delay_started_at: datetime | None = Field(default=None)
    # Stored as VARCHAR — FK to truck_route.route_id (string PK)
    current_route_id: str | None = Field(
        default=None, sa_column=Column("current_route_id", String(200), nullable=True)
    )
    last_location_update: datetime | None = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
