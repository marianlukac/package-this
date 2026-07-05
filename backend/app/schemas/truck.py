from datetime import datetime

from pydantic import BaseModel


class TruckSummary(BaseModel):
    truck_id: str
    truck_number: int | None
    name: str
    status: str
    current_lat: float | None
    current_lng: float | None
    current_stop_index: int
    delay_reason: str | None
    delay_duration_hours: float | None
    current_route_id: str | None
    package_count: int = 0


class AssignedPackageSummary(BaseModel):
    package_id: str
    customer_name: str
    status: str
    stop_order: int


class TruckDetail(BaseModel):
    truck_id: str
    truck_number: int | None
    name: str
    status: str
    current_lat: float | None
    current_lng: float | None
    delay_reason: str | None
    delay_duration_hours: float | None
    delay_started_at: datetime | None
    current_route_id: str | None
    current_stop_index: int
    assigned_packages: list[AssignedPackageSummary] = []


class TruckLocationResponse(BaseModel):
    truck_id: str
    lat: float | None
    lng: float | None
    status: str
    updated_at: datetime | None


class ViaPointResponse(BaseModel):
    id: int
    name: str
    lat: float
    lng: float
    reason: str
    inserted_before_stop_order: int
    inserted_at: datetime


class RouteStopResponse(BaseModel):
    stop_id: str
    stop_order: int
    customer_id: str
    customer_name: str
    estimated_arrival: datetime | None
    arrived_at: datetime | None
    is_completed: bool


class TruckRouteResponse(BaseModel):
    route_id: str
    truck_id: str
    status: str
    geometry: list[list[float]]
    estimated_duration_minutes: int
    current_waypoint_index: int
    started_at: datetime | None
    completed_at: datetime | None
    stops: list[RouteStopResponse] = []
    via_points: list[ViaPointResponse] = []


class AssignPackageRequest(BaseModel):
    package_id: str


class DispatchTruckRequest(BaseModel):
    pass


class RerouteRequest(BaseModel):
    location_id: int
    reason: str
