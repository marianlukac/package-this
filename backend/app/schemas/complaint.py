from datetime import datetime

from pydantic import BaseModel


class ComplaintCreate(BaseModel):
    sale_id: str
    package_ids: list[str] = []
    description: str
    source: str = "ui"


class ComplaintUpdate(BaseModel):
    description: str


class ComplaintResponse(BaseModel):
    id: int
    complaint_id: str
    sale_id: str
    description: str
    status: str
    created_by_id: str
    created_by_name: str
    package_ids: list[str]
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    source: str
