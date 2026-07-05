from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class DomainEvent(SQLModel, table=True):
    __tablename__ = "domain_event"

    id: int | None = Field(default=None, primary_key=True)
    event_id: str = Field(max_length=36, unique=True, index=True)
    event_type: str = Field(max_length=100, index=True)
    topic: str = Field(max_length=100, index=True)
    occurred_at: datetime = Field(index=True)
    actor_id: str = Field(max_length=200, index=True)
    actor_name: str = Field(max_length=200)
    actor_persona: str | None = Field(default=None, max_length=50)
    actor_type: str = Field(max_length=20)
    source: str = Field(max_length=50, index=True)
    entity_type: str = Field(max_length=100, index=True)
    entity_id: str = Field(max_length=200, index=True)
    correlation_id: str | None = Field(default=None, max_length=36, index=True)
    payload: str = Field(default="{}", sa_column=Column(Text, nullable=False))
    summary: str = Field(max_length=500)
