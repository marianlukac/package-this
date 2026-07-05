from enum import StrEnum

from sqlmodel import Field, SQLModel


class PersonaType(StrEnum):
    SALES = "sales"
    ACCOUNTING = "accounting"
    WAREHOUSE = "warehouse"
    MANAGER = "manager"


class Employee(SQLModel, table=True):
    __tablename__ = "employee"

    id: int | None = Field(default=None, primary_key=True)
    employee_id: str = Field(unique=True, index=True, max_length=100)
    name: str = Field(max_length=200)
    persona: str = Field(max_length=50)
    title: str = Field(default="", max_length=200)
    email: str = Field(default="", max_length=200)
    is_active: bool = Field(default=True)
