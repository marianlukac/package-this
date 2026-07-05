# Data Model: Events, Topics, and Live Operational Stream

**Feature**: 004-event-operational-stream | **Date**: 2026-06-22

## New Table

### `domain_event`

Persists every published domain event for querying and stream display.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `event_id` | VARCHAR(36) UNIQUE | UUID generated at publish time |
| `event_type` | VARCHAR(100) | e.g. `package.status.updated`; indexed |
| `topic` | VARCHAR(100) | One of the 8 defined topics; indexed |
| `occurred_at` | DATETIME | UTC timestamp; indexed for newest-first queries |
| `actor_id` | VARCHAR(200) | indexed |
| `actor_name` | VARCHAR(200) | |
| `actor_persona` | VARCHAR(50) | nullable (system actors have no persona) |
| `actor_type` | VARCHAR(20) | `human` / `demo` / `agent` / `system` |
| `source` | VARCHAR(50) | `ui` / `api` / `demo` / `agent` / `system`; indexed |
| `entity_type` | VARCHAR(100) | e.g. `package`, `truck`; indexed |
| `entity_id` | VARCHAR(200) | e.g. `PKG-2026-ABCD`; indexed |
| `correlation_id` | VARCHAR(36) | nullable; indexed for correlation group queries |
| `payload` | TEXT | JSON blob |
| `summary` | VARCHAR(500) | human-readable one-liner |

## Modified Types

### `EventEnvelope` (Pydantic model — not a DB table)

Replaces the flat `actor: str` field with a structured `ActorBlock`.

```
EventEnvelope:
  eventId: str (UUID)
  eventType: str
  topic: str
  occurredAt: str (ISO 8601)
  actor: ActorBlock
  source: str
  entityType: str
  entityId: str
  correlationId: str | None
  payload: dict
  summary: str

ActorBlock:
  actor_id: str
  actor_name: str
  persona: str | None
  actor_type: "human" | "demo" | "agent" | "system"
```

## Unchanged Tables

- `audit_log` — unchanged; remains the authoritative traceability store.
- `package_history` — unchanged; package-specific audit view.
- All other existing tables — unchanged.

## Relationships

```
domain_event
  ↔ audit_log      [shared correlation_id links events to audit entries for the same operation]
  ↔ package        [entity_id = package_id when entity_type = 'package']
  ↔ truck          [entity_id = truck_id when entity_type = 'truck']
  ↔ complaint      [entity_id = complaint_id when entity_type = 'complaint']
```

No foreign key constraints are used for entity references — the event store is intentionally
loosely coupled so events remain valid even if the entity is later modified or deleted.

## Topic-to-Event Mapping

| Topic | Event Types |
|---|---|
| `packages` | `package.created`, `package.updated` |
| `package-status` | `package.status.updated`, `package.assigned.to.truck`, `package.delivered`, `package.returned`, `package.cancelled`, `package.damaged`, `package.delay.recorded` |
| `package-location` | `package.location.updated` |
| `truck-location` | `truck.location.updated`, `truck.route.created`, `truck.returned.to.warehouse` |
| `truck-reroute` | `truck.rerouted` |
| `manager-actions` | `manager.action.performed`, `demo.scenario.triggered` |
| `complaints` | `complaint.created`, `complaint.updated` |
| `audit-log` | `audit.entry.created` |
