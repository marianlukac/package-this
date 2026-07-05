from datetime import datetime

from pydantic import BaseModel


class SaleCreate(BaseModel):
    customer_id: str
    notes: str = ""


class SaleResponse(BaseModel):
    id: int
    sale_id: str
    customer_id: str
    customer_name: str
    salesperson_id: str
    salesperson_name: str
    invoice_id: str
    notes: str
    package_count: int
    created_at: datetime
    updated_at: datetime
