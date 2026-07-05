import json
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.domain_event import DomainEvent

router = APIRouter(prefix="/events", tags=["Events"])


def _serialize(de: DomainEvent) -> dict:
    return {
        "event_id": de.event_id,
        "event_type": de.event_type,
        "topic": de.topic,
        "occurred_at": de.occurred_at.isoformat() + "Z",
        "actor": {
            "actor_id": de.actor_id,
            "actor_name": de.actor_name,
            "persona": de.actor_persona,
            "actor_type": de.actor_type,
        },
        "source": de.source,
        "entity_type": de.entity_type,
        "entity_id": de.entity_id,
        "correlation_id": de.correlation_id,
        "payload": json.loads(de.payload) if de.payload else {},
        "summary": de.summary,
    }


@router.get("", response_model=list)
def get_events(
    limit: int = Query(default=50, ge=1, le=500),
    topic: str | None = None,
    event_type: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    actor_id: str | None = None,
    source: str | None = None,
    correlation_id: str | None = None,
    since: str | None = None,
    session: Session = Depends(get_session),
):
    query = select(DomainEvent).order_by(DomainEvent.occurred_at.desc()).limit(limit)

    if topic:
        query = query.where(DomainEvent.topic == topic)
    if event_type:
        query = query.where(DomainEvent.event_type == event_type)
    if entity_type:
        query = query.where(DomainEvent.entity_type == entity_type)
    if entity_id:
        query = query.where(DomainEvent.entity_id == entity_id)
    if actor_id:
        query = query.where(DomainEvent.actor_id == actor_id)
    if source:
        query = query.where(DomainEvent.source == source)
    if correlation_id:
        query = query.where(DomainEvent.correlation_id == correlation_id)
    if since:
        try:
            since_dt = datetime.fromisoformat(since.rstrip("Z"))
            query = query.where(DomainEvent.occurred_at >= since_dt)
        except ValueError:
            pass

    events = session.exec(query).all()
    return [_serialize(e) for e in events]
