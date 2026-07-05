from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class ComplaintStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class Complaint(SQLModel, table=True):
    __tablename__ = "complaint"

    id: int | None = Field(default=None, primary_key=True)
    complaint_id: str = Field(unique=True, index=True, max_length=100)
    sale_id: str = Field(foreign_key="sale.sale_id", index=True, max_length=100)
    description: str = Field(max_length=5000)
    status: str = Field(default=ComplaintStatus.OPEN, index=True, max_length=50)
    created_by_id: str = Field(foreign_key="employee.employee_id", max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: datetime | None = Field(default=None)
    source: str = Field(default="ui", max_length=50)


class ComplaintPackage(SQLModel, table=True):
    __tablename__ = "complaint_package"

    id: int | None = Field(default=None, primary_key=True)
    complaint_id: str = Field(foreign_key="complaint.complaint_id", index=True, max_length=100)
    package_id: str = Field(foreign_key="package.package_id", index=True, max_length=100)
