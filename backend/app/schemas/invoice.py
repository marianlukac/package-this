from datetime import datetime

from pydantic import BaseModel


class InvoiceResponse(BaseModel):
    id: int
    invoice_id: str
    sale_id: str
    created_by_id: str
    created_by_name: str
    created_at: datetime
    notes: str
