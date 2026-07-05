
from pydantic import BaseModel


class StatusChangeRequest(BaseModel):
    status: str
    reason: str | None = None
    source: str = "ui"
    correlation_id: str | None = None


class DelayRequest(BaseModel):
    delay_reason: str
    delay_duration_hours: float
    source: str = "ui"
