
from pydantic import BaseModel


class MapLocationResponse(BaseModel):
    id: int
    name: str
    location_type: str
    lat: float
    lng: float
    description: str | None = None
