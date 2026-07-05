from datetime import datetime

from pydantic import BaseModel

from app.schemas.package_line_item import LineItemResponse


class PackageCreate(BaseModel):
    sale_id: str
    destination: str
    priority: str = "standard"
    contents_summary: str = ""
    fragile: bool = False
    source: str = "ui"


class PackageUpdate(BaseModel):
    current_location: str | None = None
    destination: str | None = None
    truck_id: str | None = None
    expected_delivery: datetime | None = None
    priority: str | None = None
    contents_summary: str | None = None
    fragile: bool | None = None
    source: str = "ui"


class PackageListItem(BaseModel):
    package_id: str
    sale_id: str
    invoice_id: str
    customer_id: str
    customer_name: str
    salesperson_id: str
    salesperson_name: str
    invoicing_employee_id: str | None = None
    invoicing_employee_name: str | None = None
    status: str
    priority: str
    fragile: bool
    contents_summary: str
    current_location: str | None
    truck_id: str | None
    delay_reason: str | None
    expected_delivery: datetime | None
    created_at: datetime
    updated_at: datetime


class PackageResponse(PackageListItem):
    invoice_id: str
    invoicing_employee_id: str
    invoicing_employee_name: str
    destination: str
    delay_duration_hours: float | None
    line_items: list[LineItemResponse] = []
    open_complaint_count: int = 0
