import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class ActorBlock(BaseModel):
    actor_id: str
    actor_name: str
    persona: str | None = None
    actor_type: Literal["human", "demo", "agent", "system"] = "human"


class EventEnvelope(BaseModel):
    eventId: str
    eventType: str
    topic: str
    occurredAt: str
    actor: ActorBlock
    source: str
    entityType: str
    entityId: str
    correlationId: str | None
    payload: dict[str, Any]
    summary: str


def make_envelope(
    event_type: str,
    topic: str,
    actor_id: str,
    actor_name: str,
    source: str,
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any],
    summary: str,
    persona: str | None = None,
    actor_type: str = "human",
    correlation_id: str | None = None,
) -> EventEnvelope:
    return EventEnvelope(
        eventId=str(uuid.uuid4()),
        eventType=event_type,
        topic=topic,
        occurredAt=datetime.utcnow().isoformat() + "Z",
        actor=ActorBlock(
            actor_id=actor_id,
            actor_name=actor_name,
            persona=persona,
            actor_type=actor_type,
        ),
        source=source,
        entityType=entity_type,
        entityId=entity_id,
        correlationId=correlation_id,
        payload=payload,
        summary=summary,
    )
