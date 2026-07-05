from datetime import datetime

from sqlmodel import Field, SQLModel


class Sale(SQLModel, table=True):
    __tablename__ = "sale"

    id: int | None = Field(default=None, primary_key=True)
    sale_id: str = Field(unique=True, index=True, max_length=100)
    customer_id: str = Field(foreign_key="customer.customer_id", index=True, max_length=100)
    salesperson_id: str = Field(foreign_key="employee.employee_id", index=True, max_length=100)
    notes: str = Field(default="", max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
