# Research: Events, Topics, and Live Operational Stream

**Feature**: 004-event-operational-stream | **Date**: 2026-06-22

## Decision: Persisting Domain Events Separately from Audit Log

**Decision**: Create a `DomainEvent` table alongside the existing `AuditLog` table.

**Rationale**: Audit log and domain events serve different consumers. The audit log is the
immutable traceability record — every meaningful write, regardless of whether any consumer
needs to react. Domain events are the reactive notification layer — emitted only when another
system part needs to know. Merging them would either pollute the audit log with transport
concerns or force audit entries into the domain event shape, losing information in both
directions.

**Alternatives considered**:
- Serve audit log rows as events (current state of `GET /events`): Rejected. Audit rows lack
  the full envelope (no topic, no correlation ID as a first-class field, no actor_type). The
  event API would expose internal audit detail that callers should not depend on.
- Use only in-memory event storage (no DB table): Rejected. Events are lost on restart, making
  the stream useless for replaying recent history when a workshop session pauses and resumes.

---

## Decision: Actor Block Structure

**Decision**: Add `ActorBlock` as a nested object in `EventEnvelope` containing `actor_id`,
`actor_name`, `persona`, and `actor_type` (human / demo / agent / system).

**Rationale**: A plain `actor: str` (current state) is not self-describing. Workshop agents
need to distinguish human actions from simulation ticks from demo scenarios without additional
API calls. The actor block makes every event self-contained for agent consumers (spec FR-005).

**Alternatives considered**:
- Keep `actor` as a string and add separate `actor_type` field: Rejected. Flat fields without
  grouping are harder to extend and less readable when agents consume the envelope JSON.

---

## Decision: Client-Side vs Server-Side Event Filtering in the Stream

**Decision**: Server-side filtering for `GET /events` (historical load); client-side display
filtering for the live stream (incoming real-time events).

**Rationale**: Historical queries hit the database and must be filtered server-side for
efficiency. Live events arrive via WebPubSub/WebSocket already; filtering those in the client
is equivalent (workshop volume is low — tens to low hundreds of events). Duplicating all server-
side filter logic client-side is unnecessary; one clear pattern per data path is simpler.

**Alternatives considered**:
- Full server-side filtering only (no client filtering): Would require a round-trip to the
  server for every filter change on the live stream. Adds latency and complexity for low
  workshop event volumes.
- Full client-side only: Would require loading all events from the server on every page load.
  Acceptable at workshop scale but less correct for larger retained histories.

---

## Decision: Correlation ID Generation Point

**Decision**: Correlation IDs are generated at the service operation entry point (e.g., the
beginning of `dispatch_truck()`). A single ID is threaded through all `make_envelope()` calls
within the same logical operation.

**Rationale**: Callers (e.g., the router) should not need to know about correlation groups.
The service layer owns the business operation boundary and is the right place to define what
constitutes a related group.

**Alternatives considered**:
- Let every `make_envelope()` call generate its own ID: Rejected. Defeats the purpose — events
  within the same operation would be unrelated to each other in the stream.
- Generate at the router layer and pass to service: Workable but pushes correlation logic above
  the business layer, which means agents calling the service directly would not get correlation.

---

## Decision: `audit.entry.created` Event Payload

**Decision**: Emit only a lightweight payload: `entity_type`, `entity_id`, `action`, `actor_id`.
Do not duplicate the `previous_value` / `new_value` from the audit row.

**Rationale**: The `audit.entry.created` event signals that audit activity happened. Consumers
who need the full audit detail can query `GET /packages/{id}/history` or equivalent. Duplicating
large JSON payloads in the event would inflate event storage and obscure the distinction between
the notification channel and the authoritative audit store.
