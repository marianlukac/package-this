
from sqlmodel import Field, SQLModel


class Customer(SQLModel, table=True):
    __tablename__ = "customer"

    id: int | None = Field(default=None, primary_key=True)
    customer_id: str = Field(unique=True, index=True, max_length=100)
    name: str = Field(max_length=300)
    address: str = Field(default="", max_length=500)
    city: str = Field(default="Scranton", max_length=100)
    state: str = Field(default="PA", max_length=50)
    lat: float | None = Field(default=None)
    lng: float | None = Field(default=None)
    is_unhappy: bool = Field(default=False)
    contact_name: str = Field(default="", max_length=200)
    contact_email: str = Field(default="", max_length=200)
