from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class PackageStatus(StrEnum):
    ORDER_CREATED = "order_created"
    BACKORDER = "backorder"
    PACKAGED = "packaged"
    READY_FOR_SHIPPING = "ready_for_shipping"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    DAMAGED = "damaged"
    RETURNED = "returned"


class PackagePriority(StrEnum):
    STANDARD = "standard"
    URGENT = "urgent"
    NEXT_DAY = "next_day"


TERMINAL_STATUSES: frozenset[PackageStatus] = frozenset({
    PackageStatus.DELIVERED,
    PackageStatus.CANCELLED,
    PackageStatus.DAMAGED,
    PackageStatus.RETURNED,
})


class Package(SQLModel, table=True):
    __tablename__ = "package"

    id: int | None = Field(default=None, primary_key=True)
    package_id: str = Field(unique=True, index=True, max_length=100)
    sale_id: str = Field(foreign_key="sale.sale_id", index=True, max_length=100)
    invoice_id: str = Field(foreign_key="invoice.invoice_id", index=True, max_length=100)
    customer_id: str = Field(foreign_key="customer.customer_id", index=True, max_length=100)
    salesperson_id: str = Field(foreign_key="employee.employee_id", max_length=100)
    invoicing_employee_id: str = Field(foreign_key="employee.employee_id", max_length=100)
    status: str = Field(default=PackageStatus.ORDER_CREATED, index=True, max_length=50)
    priority: str = Field(default=PackagePriority.STANDARD)
    contents_summary: str = Field(default="", max_length=1000)
    fragile: bool = Field(default=False)
    current_location: str | None = Field(default=None, max_length=200)
    current_lat: float | None = Field(default=None)
    current_lng: float | None = Field(default=None)
    destination: str = Field(default="", max_length=500)
    truck_id: str | None = Field(default=None, max_length=100)
    expected_delivery: datetime | None = Field(default=None)
    delay_reason: str | None = Field(default=None, max_length=1000)
    delay_duration_hours: float | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
