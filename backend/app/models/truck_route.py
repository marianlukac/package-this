from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class RouteStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    RETURNING = "returning"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TruckRoute(SQLModel, table=True):
    __tablename__ = "truck_route"

    route_id: str = Field(primary_key=True, max_length=200)
    truck_id: str = Field(foreign_key="truck.truck_id", index=True, max_length=100)
    status: str = Field(default=RouteStatus.PLANNED)
    # JSON array of [lat, lng] waypoints covering the full path between all stops
    geometry: str = Field(default="[]")
    estimated_duration_minutes: int = Field(default=0)
    current_waypoint_index: int = Field(default=0)
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RouteStop(SQLModel, table=True):
    __tablename__ = "route_stop"

    stop_id: str = Field(primary_key=True, max_length=200)
    route_id: str = Field(foreign_key="truck_route.route_id", index=True, max_length=200)
    customer_id: str = Field(max_length=200)
    stop_order: int = Field()
    estimated_arrival: datetime | None = Field(default=None)
    arrived_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    is_completed: bool = Field(default=False)


class ViaPoint(SQLModel, table=True):
    __tablename__ = "via_point"

    id: int | None = Field(default=None, primary_key=True)
    route_id: str = Field(foreign_key="truck_route.route_id", index=True, max_length=200)
    name: str = Field(max_length=200)
    lat: float = Field()
    lng: float = Field()
    reason: str = Field(default="", max_length=2000)
    inserted_before_stop_order: int = Field(default=0)
    inserted_at: datetime = Field(default_factory=datetime.utcnow)
