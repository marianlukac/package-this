import json
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from app.models.audit_log import AuditLog
from app.models.employee import Employee


class AuditLogger:
    @staticmethod
    def log(
        session: Session,
        actor: Employee,
        source: str,
        entity_type: str,
        entity_id: str,
        action: str,
        previous_value: Any = None,
        new_value: Any = None,
        reason: str | None = None,
        correlation_id: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            actor_id=actor.employee_id,
            actor_name=actor.name,
            timestamp=datetime.utcnow(),
            source=source,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            previous_value=json.dumps(previous_value) if previous_value is not None else None,
            new_value=json.dumps(new_value) if new_value is not None else None,
            reason=reason,
            correlation_id=correlation_id,
        )
        session.add(entry)

        # Emit audit.entry.created as a lightweight DomainEvent — persisted via the same session
        try:
            from app.models.domain_event import DomainEvent
            de = DomainEvent(
                event_id=str(uuid.uuid4()),
                event_type="audit.entry.created",
                topic="audit-log",
                occurred_at=datetime.utcnow(),
                actor_id=actor.employee_id,
                actor_name=actor.name,
                actor_persona=getattr(actor, "persona", None),
                actor_type="human",
                source=source,
                entity_type=entity_type,
                entity_id=entity_id,
                correlation_id=correlation_id,
                payload=json.dumps({
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "action": action,
                    "actor_id": actor.employee_id,
                }),
                summary=f"Audit: {action} on {entity_type}/{entity_id} by {actor.name}",
            )
            session.add(de)
        except Exception:
            pass

        return entry
