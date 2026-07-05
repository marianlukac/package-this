from datetime import datetime

from sqlmodel import Field, SQLModel


class Invoice(SQLModel, table=True):
    __tablename__ = "invoice"

    id: int | None = Field(default=None, primary_key=True)
    invoice_id: str = Field(unique=True, index=True, max_length=100)
    sale_id: str = Field(foreign_key="sale.sale_id", unique=True, index=True, max_length=100)
    created_by_id: str = Field(foreign_key="employee.employee_id", max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: str = Field(default="", max_length=2000)
