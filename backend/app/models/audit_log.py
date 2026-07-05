from datetime import datetime

from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: int | None = Field(default=None, primary_key=True)
    actor_id: str = Field(max_length=100, index=True)
    actor_name: str = Field(max_length=200)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    source: str = Field(max_length=50)
    entity_type: str = Field(max_length=100, index=True)
    entity_id: str = Field(max_length=100, index=True)
    action: str = Field(max_length=200)
    previous_value: str | None = Field(default=None)
    new_value: str | None = Field(default=None)
    reason: str | None = Field(default=None, max_length=2000)
    correlation_id: str | None = Field(default=None, max_length=200)
