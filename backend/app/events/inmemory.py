import json
from datetime import datetime

from sqlmodel import Session

from app.events.envelope import EventEnvelope
from app.events.publisher import EventPublisher


class InMemoryEventPublisher(EventPublisher):
    def __init__(self) -> None:
        self.published: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope, session=None) -> None:
        self.published.append(event)
        print(f"[EVENT] {event.topic}/{event.eventType} | {event.entityId} | {event.summary}")
        self._persist(event, session)

    def _persist(self, event: EventEnvelope, session=None) -> None:
        try:
            from app.models.domain_event import DomainEvent
            de = DomainEvent(
                event_id=event.eventId,
                event_type=event.eventType,
                topic=event.topic,
                occurred_at=datetime.fromisoformat(event.occurredAt.rstrip("Z")),
                actor_id=event.actor.actor_id,
                actor_name=event.actor.actor_name,
                actor_persona=event.actor.persona,
                actor_type=event.actor.actor_type,
                source=event.source,
                entity_type=event.entityType,
                entity_id=event.entityId,
                correlation_id=event.correlationId,
                payload=json.dumps(event.payload),
                summary=event.summary,
            )
            if session is not None:
                session.add(de)
                session.commit()
            else:
                from app.database import get_engine
                with Session(get_engine()) as s:
                    s.add(de)
                    s.commit()
        except Exception as exc:
            print(f"[EVENT] Failed to persist DomainEvent: {exc}")
