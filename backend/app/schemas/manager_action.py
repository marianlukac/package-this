from typing import Any

from pydantic import BaseModel


class ManagerActionRequest(BaseModel):
    action: str
    entity_type: str
    entity_id: str
    payload: dict[str, Any] = {}
    reason: str
    source: str = "ui"
    correlation_id: str | None = None


class ManagerActionResponse(BaseModel):
    action: str
    status: str
    entity_id: str
