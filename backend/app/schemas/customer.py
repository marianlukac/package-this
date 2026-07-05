
from pydantic import BaseModel


class CustomerResponse(BaseModel):
    id: int
    customer_id: str
    name: str
    address: str
    city: str
    state: str
    lat: float | None
    lng: float | None
    is_unhappy: bool
    contact_name: str
    contact_email: str
