# Implementation Plan: Events, Topics, and Live Operational Stream

**Branch**: `004-event-operational-stream` | **Date**: 2026-06-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/004-event-operational-stream/spec.md`

## Summary

Formalize and complete the domain event system for the Dunder Mifflin Package Manager. The
backend gains a persisted `DomainEvent` table, a structured actor block in the event envelope,
correlation ID propagation through multi-step operations, and coverage of all 19 required event
types. The frontend event stream component is upgraded with full filtering, pause/resume/clear,
expandable payloads, copy-to-clipboard, and navigation links to related entities.

All technical decisions inherit from Feature 1. This feature completes event infrastructure that
was partially scaffolded in earlier features: the `EventPublisher` abstraction, `EventEnvelope`,
`GET /events` endpoint, and `EventStreamComponent` all exist but are not yet complete.

## Technical Context

**Language/Version**: Python 3.12 (backend) · TypeScript / Angular 18 (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Alembic, Pydantic-Settings (backend);
Angular, Tailwind CSS (frontend); Azure Service Bus (event transport, trainer baseline);
Azure Web PubSub (real-time delivery, trainer baseline)
**Storage**: Azure SQL (trainer baseline) · SQL Server in Docker (local dev)
**Testing**: pytest (backend)
**Target Platform**: Azure Container Apps (deployed) · Docker Compose (local dev)
**Project Type**: Full-stack web application — extending existing Feature 1–3 baseline
**Performance Goals**: Workshop demo quality. Event query response under 500ms for up to 500
stored events. Real-time stream latency under 3 seconds end-to-end.
**Constraints**: Same as Feature 1. Event persistence uses a new `DomainEvent` table alongside
the existing `AuditLog` table; these are separate concerns. No event replay from transport layer
required.
**Scale/Scope**: Up to 500 events per workshop session. All filtering is server-side via query
parameters. Client-side display filtering is an acceptable simplification for volume.

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| I. Workshop-First Clarity | ✅ | EventEnvelope fields use readable names; stream component shows human-readable summaries by default |
| II. Enterprise-Translatable Design | ✅ | Domain events vs audit history distinction maps to enterprise event-driven / CQRS patterns |
| III. Separation of Spec / Implementation | ✅ | This plan references spec.md; no functional requirements added here |
| IV. API-First and Agent-Ready | ✅ | `GET /events` is filterable by topic, type, entity, actor, correlation ID — fully consumable by agents without UI |
| V. Auditability by Default | ✅ | AuditLog unchanged; `audit.entry.created` events make audit activity observable without replacing the audit store |
| VI. Controlled State Changes | ✅ | Events only published after successful operations; no events on failed operations |
| VII. Event-Driven Where It Matters | ✅ | 19 event types defined and mapped to 8 topics; throttled truck location events from Feature 3 are preserved |
| VIII. Secure by Default | ✅ | `GET /events` is read-only; no new write endpoints introduced by this feature |
| IX. Accessible and Usable UI | ✅ | Stream filter panel uses labeled controls; events list is an ARIA live region; expand/copy are keyboard-accessible |
| X. Demo Reliability | ✅ | Demo reset also clears `DomainEvent` table so stream starts fresh; retained for session replay during training |
| XI. Test the Core | ✅ | Tests verify envelope structure, correlation ID propagation, event coverage, and stream filter endpoint behavior |
| XII. No Hidden Workshop Dependencies | ✅ | In-memory publisher emits events locally; Service Bus and WebPubSub are optional for full transport |
| XIII. Theme Supports Learning | ✅ | Event stream makes system behavior visible during workshop; events name real enterprise concepts |

**Gate result: PASS — proceed to implementation.**

### Existing Infrastructure Assessment

The following are already in place from Features 1–3:

- `app/events/envelope.py` — `EventEnvelope` Pydantic model and `make_envelope()` function.
  **Gap**: `actor` is a plain `str`; needs extending to a structured block with id, name,
  persona, and actor_type.
- `app/events/publisher.py` — `EventPublisher` abstraction with `InMemoryEventPublisher` and
  `ServiceBusPublisher`. **Gap**: Neither implementation persists events to the database.
- `app/routers/events.py` — `GET /events` returning audit log rows shaped as event-like dicts.
  **Gap**: Returns audit entries, not domain events; no topic/type/correlation filtering.
- `frontend/app/components/event-stream/event-stream.component.ts` — Basic stream showing
  audit-log rows polled from `GET /events`. **Gap**: No filter panel, no expand/copy, no
  links, no Clear button.

## Project Structure

### Documentation (this feature)

```text
specs/004-event-operational-stream/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api-events.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code Changes (extending Feature 1–3 structure)

```text
backend/
├── app/
│   ├── models/
│   │   └── domain_event.py        # NEW: DomainEvent table (persisted envelope)
│   ├── events/
│   │   ├── envelope.py            # EXTEND: add ActorBlock (id, name, persona, actor_type)
│   │   ├── publisher.py           # EXTEND: persist DomainEvent row on every publish()
│   │   └── inmemory.py            # EXTEND: also persists to DB (for local dev parity)
│   ├── routers/
│   │   └── events.py              # EXTEND: serve DomainEvent table; add filtering params
│   └── services/
│       └── demo_service.py        # EXTEND: clear DomainEvent table on reset
├── migrations/versions/
│   └── 0003_domain_events.py      # NEW: migration for domain_event table
└── tests/
    ├── test_event_envelope.py      # NEW
    ├── test_event_coverage.py      # NEW
    └── test_event_stream_api.py    # NEW

frontend/
└── src/app/
    ├── components/
    │   └── event-stream/
    │       └── event-stream.component.ts   # EXTEND: filter panel, expand, copy, clear, links
    ├── models/
    │   └── event.model.ts                  # EXTEND: DomainEvent interface with full envelope shape
    └── services/
        └── api.service.ts                  # EXTEND: update getEvents() to pass filter params
```

## Implementation Phases

### Phase 1: Structured Actor Block and Persisted Events (Backend Models)

**Goal**: The event envelope has a structured actor block; every published event is persisted.

- Extend `app/events/envelope.py`:
  - Add `ActorBlock` Pydantic model: `actor_id: str`, `actor_name: str`, `persona: str | None`,
    `actor_type: Literal["human", "demo", "agent", "system"]`.
  - Change `actor: str` field on `EventEnvelope` to `actor: ActorBlock`.
  - Update `make_envelope()` signature: `actor_id`, `actor_name`, `persona`, `actor_type`
    parameters; construct `ActorBlock` internally. Keep `actor_id` as a shortcut parameter
    for callers that only have an ID (derive name/persona from the ID where possible).
  - Add `actor_type` default to `"human"` so existing callers are not broken.

- Create `app/models/domain_event.py`:
  - `DomainEvent` SQLModel table: `id` (auto PK), `event_id` (unique str), `event_type` (str,
    indexed), `topic` (str, indexed), `occurred_at` (datetime, indexed), `actor_id` (str,
    indexed), `actor_name` (str), `actor_persona` (nullable str), `actor_type` (str), `source`
    (str, indexed), `entity_type` (str, indexed), `entity_id` (str, indexed), `correlation_id`
    (nullable str, indexed), `payload` (TEXT, JSON), `summary` (str).

- Create Alembic migration `0003_domain_events.py` for the `domain_event` table.

- Extend `app/events/publisher.py`:
  - `EventPublisher.publish()` now also writes a `DomainEvent` row to the database session
    before dispatching to the transport (Service Bus / in-memory channel).
  - Publisher needs a `Session` parameter or access to the session factory. Use a lightweight
    session-per-publish pattern with `with Session(engine) as session`.

### Phase 2: Correlation ID Propagation (Backend Services)

**Goal**: Related operations that form a logical group share one correlation ID.

- Identify the five grouped-operation patterns from the spec:
  1. Sale + invoice + package creation
  2. Package assignment to truck (multiple packages, same dispatch)
  3. Truck dispatch (route creation + package status changes)
  4. Delivery at a customer stop (package.delivered + route_stop update)
  5. Demo scenario trigger (all changes made by the scenario)

- For each pattern: generate a `correlation_id = str(uuid.uuid4())` at the entry point and
  pass it through to all `make_envelope()` calls within that operation.

- Update `app/services/truck_service.py` `dispatch_truck()` to generate one correlation ID and
  pass it to all package status change events and the `truck.route.created` event.

- Update `app/services/demo_service.py` scenario handlers to generate one correlation ID per
  scenario execution and pass it to all events within that scenario.

- Update `app/services/package_service.py` (or the sales router) to generate one correlation ID
  for the sale + invoice + package creation flow.

### Phase 3: Full Event Coverage (Backend Services)

**Goal**: All 19 required event types are emitted with correct topics.

Audit against the spec's event type list. Add any missing `publisher.publish()` calls:

| Event type | Topic | Where to emit |
|---|---|---|
| `package.created` | `packages` | package creation endpoint — verify present |
| `package.updated` | `packages` | package field update endpoint — add if missing |
| `package.status.updated` | `package-status` | lifecycle status change — verify present |
| `package.location.updated` | `package-location` | simulation tick for in-transit packages — verify present |
| `package.assigned.to.truck` | `package-status` | truck_service.assign_package — verify present |
| `package.delivered` | `package-status` | truck_service.record_delivery — verify present |
| `package.returned` | `package-status` | package return flow — add if missing |
| `package.cancelled` | `package-status` | cancel endpoint — verify present |
| `package.damaged` | `package-status` | damage status endpoint — add if missing |
| `package.delay.recorded` | `package-status` | delay recording — verify present |
| `truck.location.updated` | `truck-location` | simulation tick (throttled) — verify present |
| `truck.route.created` | `truck-location` | route calculation — verify/add |
| `truck.rerouted` | `truck-reroute` | kevin_reroute — verify present |
| `truck.returned.to.warehouse` | `truck-location` | route completion — verify present |
| `manager.action.performed` | `manager-actions` | manager actions — verify present |
| `complaint.created` | `complaints` | complaint creation — verify present |
| `complaint.updated` | `complaints` | complaint update/close — verify present |
| `demo.scenario.triggered` | `manager-actions` | demo scenario run — verify/add |
| `audit.entry.created` | `audit-log` | AuditLog write — add lightweight event |

- For `audit.entry.created`: emit a lightweight event from `AuditLog` model or from the
  service layer where audit entries are written. Payload contains only: `entity_type`,
  `entity_id`, `action`, `actor_id` — not the full previous/new value (those stay in the
  audit row only).

### Phase 4: Events API Endpoint (Backend Router)

**Goal**: `GET /events` serves persisted `DomainEvent` rows with full filtering support.

- Rewrite `app/routers/events.py`:
  - Query `DomainEvent` table (not `AuditLog`).
  - Query parameters: `limit` (default 50, max 500), `topic`, `event_type`, `entity_type`,
    `entity_id`, `actor_id`, `source`, `correlation_id`, `since` (ISO timestamp).
  - Return the full envelope shape matching the `EventEnvelope` model.
  - Order by `occurred_at` descending (newest first).
  - Keep the existing `GET /events` path unchanged to avoid breaking api.service.ts.

- Extend `app/services/demo_service.py` reset handler to `DELETE FROM domain_event` so the
  stream starts fresh after a demo reset (mirrors audit log reset behaviour).

### Phase 5: Event Stream UI (Frontend)

**Goal**: The operational stream shows live events with filtering, expand, copy, and entity links.

- Extend `frontend/src/app/models/event.model.ts`:
  - `ActorBlock`: `actor_id`, `actor_name`, `persona`, `actor_type`.
  - `DomainEvent`: `event_id`, `event_type`, `topic`, `occurred_at`, `actor: ActorBlock`,
    `source`, `entity_type`, `entity_id`, `correlation_id`, `payload`, `summary`.
  - `EventFilter`: filter form state shape.

- Update `api.service.ts` `getEvents()` to accept optional filter params (`topic`,
  `event_type`, `entity_id`, `actor_id`, `source`, `correlation_id`) and pass them as query
  params to `GET /events`.

- Rewrite `event-stream.component.ts`:
  - **Data**: load historical events from `GET /events` on init; merge with live events from
    `RealtimeService.events$`; display newest-first.
  - **Pause / Resume**: while paused, buffer incoming real-time events; on resume flush buffer
    into the display.
  - **Clear**: clear local `events` array only; stored history in the database is not affected.
  - **Filter panel** (collapsible): dropdowns/inputs for topic, event type, entity ID (free
    text), actor, source, correlation ID; filters applied to the local display array (client-
    side, sufficient for workshop volume).
  - **Event entry**: one row per event showing `summary`, `actor.actor_name`, `source` badge,
    `entity_type + entity_id`, `occurred_at` (relative time). Clicking expands a detail section.
  - **Expand**: shows formatted JSON payload, correlation ID, full actor block.
  - **Copy**: copies the full event JSON to clipboard; shows brief "Copied!" confirmation.
  - **Entity links**: if `entity_type` is `package` → link to `/packages/{entity_id}`;
    if `truck` → link to `/map` (highlight truck); if `complaint` → link to complaint detail.
  - **Accessibility**: stream list uses `role="log"` and `aria-live="polite"`; filter controls
    have descriptive labels; expand/copy buttons have `aria-label`; keyboard-navigable
    throughout.

### Phase 6: Tests

**Goal**: Envelope structure, event coverage, and stream API are verified.

- `backend/tests/test_event_envelope.py`:
  - Verify `make_envelope()` returns a valid `EventEnvelope` with all required fields.
  - Verify `ActorBlock` actor_type defaults to `"human"` when not specified.
  - Verify `correlation_id` is preserved when provided.
  - Verify `eventId` is unique across two calls to `make_envelope()`.

- `backend/tests/test_event_coverage.py`:
  - For each of the 19 required event types, trigger the corresponding operation and verify
    a `DomainEvent` row is created in the database with the correct `event_type` and `topic`.
  - Verify dispatch operation creates events with shared `correlation_id`.
  - Verify `audit.entry.created` events are published when audit entries are written.
  - Verify failed operations do not create `DomainEvent` rows.

- `backend/tests/test_event_stream_api.py`:
  - Verify `GET /events` returns events newest-first.
  - Verify `GET /events?topic=package-status` filters by topic.
  - Verify `GET /events?entity_id=PKG-001` returns only events for that entity.
  - Verify `GET /events?correlation_id=...` returns only events in that correlation group.
  - Verify `GET /events?limit=5` returns at most 5 results.
