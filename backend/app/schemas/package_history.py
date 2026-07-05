from datetime import datetime

from pydantic import BaseModel


class PackageHistoryResponse(BaseModel):
    id: int
    package_id: str
    event_type: str
    actor_id: str
    actor_name: str
    timestamp: datetime
    source: str
    entity_type: str
    entity_id: str
    previous_value: str | None
    new_value: str | None
    reason: str | None
    correlation_id: str | None


class PackageHistoryListResponse(BaseModel):
    package_id: str
    history: list[PackageHistoryResponse]
