from enum import StrEnum

from sqlmodel import Field, SQLModel


class LocationType(StrEnum):
    WAREHOUSE = "warehouse"
    CUSTOMER = "customer"
    FOOD = "food"
    DONUT = "donut"


class MapLocation(SQLModel, table=True):
    __tablename__ = "map_location"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=300)
    location_type: str = Field(index=True, max_length=50)
    lat: float = Field()
    lng: float = Field()
    description: str | None = Field(default=None, max_length=500)
