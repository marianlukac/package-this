# Tasks: Events, Topics, and Live Operational Stream

**Feature**: 004-event-operational-stream
**Input**: Design documents from `specs/004-event-operational-stream/`
**Prerequisites**: plan.md ✓, spec.md ✓, data-model.md ✓, contracts/ ✓, research.md ✓, quickstart.md ✓

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks in same phase)
- **[Story]**: Which user story this task belongs to (US1–US4)
- Include exact file paths in all descriptions

---

## Phase 1: Setup (Core Models)

**Purpose**: Create the DomainEvent persistence layer — required before any publisher or router work.

- [X] T001 [P] Create DomainEvent SQLModel table in `backend/app/models/domain_event.py`
- [X] T002 [P] Create Alembic migration for domain_event table in `backend/migrations/versions/0003_domain_events.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend the event envelope with a structured ActorBlock and make every publisher persist to the database. Blocks all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Add `ActorBlock` Pydantic model to `backend/app/events/envelope.py` with fields `actor_id: str`, `actor_name: str`, `persona: str | None`, `actor_type: Literal["human","demo","agent","system"]`; replace `actor: str` on `EventEnvelope` with `actor: ActorBlock`
- [X] T004 Update `make_envelope()` in `backend/app/events/envelope.py` to accept `actor_id`, `actor_name`, `persona`, `actor_type` params and construct ActorBlock internally; default `actor_type` to `"human"` so existing callers are not broken
- [X] T005 [P] Extend `EventPublisher.publish()` in `backend/app/events/publisher.py` to persist a `DomainEvent` row to the database (using `with Session(engine) as session`) on every publish call
- [X] T006 [P] Extend `InMemoryEventPublisher.publish()` in `backend/app/events/inmemory.py` to also persist a `DomainEvent` row to the database for local dev parity
- [X] T007 Extend demo reset handler in `backend/app/services/demo_service.py` to `DELETE FROM domain_event` on reset so the stream starts fresh after a demo reset

**Checkpoint**: ActorBlock in envelope. Publisher persisting to DB. Demo reset clears events. User story work can now begin.

---

## Phase 3: User Story 2 — Domain Event Model and Topics (Priority: P1)

**Goal**: All 19 required event types are emitted with correct topics, structured actor blocks, and shared correlation IDs for grouped operations.

**Independent Test**: Perform a package status change. Query `GET /events`. Verify the returned event contains all envelope fields including the nested actor block (actor_id, actor_name, persona, actor_type), topic `package-status`, and a non-null correlation ID. Dispatch a truck and verify all resulting events share the same correlation ID.

### Implementation for User Story 2

- [X] T008 [P] [US2] Generate `correlation_id = str(uuid.uuid4())` at the start of `dispatch_truck()` in `backend/app/services/truck_service.py` and thread it through all `make_envelope()` calls within that operation (`truck.route.created` and all package status changes — note: there is no `truck.dispatched` event; `truck.route.created` serves as the dispatch-confirmation signal)
- [X] T009 [P] [US2] Generate `correlation_id` at the start of each demo scenario handler in `backend/app/services/demo_service.py` and thread it through all `make_envelope()` calls within each scenario execution
- [X] T010 [P] [US2] Generate `correlation_id` for the sale + invoice + package creation flow in `backend/app/services/package_service.py` (or the relevant router) and thread it through all `make_envelope()` calls in that operation
- [X] T011 [US2] Add or verify `package.updated` event (topic: `packages`) on package field update in `backend/app/services/package_service.py` or `backend/app/routers/packages.py`; add the publish call if it is missing
- [X] T012 [US2] Add or verify `package.returned` event (topic: `package-status`) on package return flow in `backend/app/services/package_service.py`; add the publish call if it is missing
- [X] T013 [US2] Add or verify `package.damaged` event (topic: `package-status`) on damage status update in `backend/app/services/package_service.py`; add the publish call if it is missing
- [X] T014 [P] [US2] Add `truck.route.created` event (topic: `truck-location`) when a truck route is calculated in `backend/app/services/truck_service.py` if not already present
- [X] T015 [P] [US2] Add/verify `demo.scenario.triggered` event (topic: `manager-actions`) on each scenario execution in `backend/app/services/demo_service.py` with payload including scenario name and summary of changes
- [X] T016 [US2] Emit `audit.entry.created` event (topic: `audit-log`) with lightweight payload (`entity_type`, `entity_id`, `action`, `actor_id`) wherever `AuditLog` entries are written in the service layer; do not duplicate the full previous/new value in the event payload
- [X] T017 [US2] Update all existing `publisher.publish()` call sites in `backend/app/services/` and `backend/app/routers/` to pass structured `actor_id`, `actor_name`, `persona`, `actor_type` args to `make_envelope()` instead of plain `actor: str`; verify AND add if missing: `package.created`, `package.status.updated`, `package.location.updated`, `package.assigned.to.truck`, `package.delivered`, `package.cancelled`, `package.delay.recorded`, `truck.location.updated`, `truck.rerouted`, `truck.returned.to.warehouse`, `manager.action.performed`, `complaint.created`, `complaint.updated` — each must have correct topic and a structured ActorBlock

**Checkpoint**: All 19 event types emitted. Events persisted to DomainEvent table. Grouped operations share correlation IDs.

---

## Phase 4: User Story 1 — Live Operational Stream (Priority: P1)

**Goal**: The UI displays live domain events newest-first with expand, copy, entity links, pause/resume, and clear. Events appear within 3 seconds of the triggering operation.

**Independent Test**: Open the Events tab. Perform a package status change. Within 3 seconds a new event entry appears showing event type, summary, actor name, entity, and timestamp. Click Pause, perform another operation, click Resume — verify no events are lost. Click Clear — verify the display is empty but `GET /events` still returns the events. Click an event to expand it and verify the full payload is shown. Click Copy and verify JSON is on the clipboard. Click the package entity link and verify the package detail opens.

### Implementation for User Story 1

- [X] T018 [US1] Rewrite `backend/app/routers/events.py` to query the `DomainEvent` table (not `AuditLog`), order by `occurred_at` DESC, and return the full event envelope JSON shape matching `contracts/api-events.md`
- [X] T019 [P] [US1] Extend `DomainEvent` interface and add `ActorBlock` interface in `frontend/src/app/models/event.model.ts` to match the full envelope shape: `event_id`, `event_type`, `topic`, `occurred_at`, `actor: ActorBlock`, `source`, `entity_type`, `entity_id`, `correlation_id`, `payload`, `summary`
- [X] T020 [P] [US1] Update `getEvents()` in `frontend/src/app/services/api.service.ts` to accept optional filter params (`topic`, `event_type`, `entity_id`, `actor_id`, `source`, `correlation_id`) and pass them as query parameters to `GET /events`
- [X] T021 [US1] Rewrite `frontend/src/app/components/event-stream/event-stream.component.ts` to load historical events from `GET /events` on init and merge with live real-time events from `RealtimeService.events$`, displaying newest-first
- [X] T022 [US1] Add Pause/Resume to `frontend/src/app/components/event-stream/event-stream.component.ts`: while paused, buffer incoming real-time events without showing them; on Resume flush buffer into the display in order so no events are lost
- [X] T023 [US1] Add Clear button to `frontend/src/app/components/event-stream/event-stream.component.ts`: clears the local `events` display array only; stored history in the database is not affected
- [X] T024 [US1] Add expand/collapse and copy-to-clipboard to each event entry in `frontend/src/app/components/event-stream/event-stream.component.ts`: clicking an entry toggles a detail section showing full formatted JSON payload, full actor block, and correlation ID; Copy button copies the full event JSON and shows a brief "Copied!" confirmation
- [X] T025 [US1] Add entity navigation links to event entries in `frontend/src/app/components/event-stream/event-stream.component.ts`: `entity_type === 'package'` → `/packages/{entity_id}`; `entity_type === 'truck'` → `/map`; `entity_type === 'complaint'` → complaint detail page
- [X] T026 [US1] Add accessibility to `frontend/src/app/components/event-stream/event-stream.component.ts`: apply `role="log"` and `aria-live="polite"` to the stream list; add descriptive `aria-label` to filter controls, Copy, and expand buttons; ensure full keyboard navigability

**Checkpoint**: Live stream operational. Events appear in real time. Pause/resume/clear work. Expand and copy work. Entity links navigate correctly.

---

## Phase 5: User Story 3 — Event Filtering and Navigation (Priority: P2)

**Goal**: Trainers can narrow the stream to a specific topic, event type, actor, entity, source, or correlation group. Server-side filtering on `GET /events` and client-side display filtering on the live stream both work.

**Independent Test**: With multiple events in the stream, select topic = `package-status` in the filter panel — verify only package status events are shown. Clear the filter — verify all events return. Type a specific actor name — verify only that actor's events appear. Paste a correlation ID — verify only events from that group are shown.

### Implementation for User Story 3

- [X] T027 [US3] Add query parameter filtering to `GET /events` in `backend/app/routers/events.py`: `limit` (int, default 50, max 500), `topic` (str), `event_type` (str), `entity_type` (str), `entity_id` (str), `actor_id` (str), `source` (str), `correlation_id` (str), `since` (ISO 8601 datetime); apply each as an optional WHERE clause on the DomainEvent query
- [X] T028 [US3] Add a collapsible filter panel to `frontend/src/app/components/event-stream/event-stream.component.ts` with labeled controls: topic (dropdown with the 8 defined topics + All), event type (free text or dropdown), entity ID (free text), actor (free text), source (dropdown: ui/api/demo/agent/system + All), correlation ID (free text)
- [X] T029 [US3] Implement client-side display filtering in `frontend/src/app/components/event-stream/event-stream.component.ts`: maintain an `activeFilters` state; when any filter changes, recompute the displayed events array as a filtered view of the full local events array; multiple filters combine with AND logic; filtering does not delete or reload events

**Checkpoint**: Filters work on the live display. Server-side filter params work on `GET /events`. Multiple active filters combine correctly.

---

## Phase 6: User Story 4 — Audit History and Event Relationship (Priority: P2)

**Goal**: Every meaningful write has an audit entry. Audit entries and domain events for the same operation share a correlation ID. Package audit history is complete and queryable.

**Independent Test**: Perform a package status change. Query `GET /packages/{id}/history` and verify an audit entry exists with actor, timestamp, previous status, and new status. Inspect the domain event returned by `GET /events?entity_id={id}` for the same operation and verify both share the same correlation ID.

### Implementation for User Story 4

- [X] T030 [US4] Audit all service-layer methods in `backend/app/services/` that write `AuditLog` entries to verify `correlation_id` is passed to both the audit entry and the corresponding `make_envelope()` call for the same operation; add the correlation ID parameter where it is missing
- [X] T031 [P] [US4] Verify `GET /packages/{id}/history` in `backend/app/routers/packages.py` returns a complete chronological audit history with all required fields (actor ID, actor name, persona, timestamp, source, entity type, entity ID, action, previous value, new value, reason, correlation ID); extend if any fields are missing; confirm that `GET /events` (with `actor_id`, `since`, `event_type`, `entity_id` params from T027) together with this endpoint satisfies Constitution Principle V's requirement that meaningful records be queryable by actor, entity, time range, and event type — domain events provide the operational query axes; audit history provides the entity-centric detail view

**Checkpoint**: Audit entries and domain events for the same operation share a correlation ID. Package audit history is complete and queryable.

---

## Phase 7: Tests

**Goal**: Verify envelope structure, event coverage, and stream API filtering behavior.

- [X] T032 [P] Create `backend/tests/test_event_envelope.py`: test `make_envelope()` returns a valid `EventEnvelope` with all required fields; test `ActorBlock.actor_type` defaults to `"human"` when not specified; test `correlation_id` is preserved when provided; test `eventId` is unique across two `make_envelope()` calls
- [X] T033 [P] Create `backend/tests/test_event_coverage.py`: for each of the 19 required event types trigger the corresponding operation and verify a `DomainEvent` row exists in the DB with correct `event_type` and `topic`; verify `dispatch_truck()` creates events with a shared `correlation_id`; verify `audit.entry.created` events are published when audit entries are written; verify a failed operation (e.g. assigning an in-transit package) does not create a `DomainEvent` row
- [X] T034 [P] Create `backend/tests/test_event_stream_api.py`: test `GET /events` returns events newest-first; test `?topic=package-status` filters by topic; test `?entity_id=PKG-001` returns only events for that entity; test `?correlation_id=...` returns only events in that correlation group; test `?limit=5` returns at most 5 results; test that after inserting the same event twice (simulated duplicate), `GET /events` de-duplicates by `event_id` (or confirm the DomainEvent table's UNIQUE constraint on `event_id` prevents duplicate rows)

---

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T035 Update `docs/demo-scenarios.md` with an "Event Stream" demo scenario covering: open Events tab → create package + advance status + dispatch truck → watch events appear → expand event → copy payload → filter by correlation ID → Kevin reroute and observe truck-reroute event → pause/resume → clear; include SC-001 as a manual acceptance test step: "Verify each event appears within 3 seconds of the triggering operation completing"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — T001 and T002 start immediately and run in parallel
- **Phase 2 (Foundational)**: Depends on Phase 1 — **BLOCKS all user stories**
- **Phase 3 (US2)**: Depends on Phase 2 — T008–T010 can run in parallel; T011–T013 sequential (same service file); T014–T015 parallel with T011–T013 (different files)
- **Phase 4 (US1)**: T018 depends on Phase 2; T019–T020 can run in parallel with T018 (different files); T021–T026 are sequential (all in event-stream.component.ts); benefits from US2 completion for meaningful test content
- **Phase 5 (US3)**: T027 must follow T018 (same router file); T028–T029 must follow T026 (same component file)
- **Phase 6 (US4)**: T030 depends on Phase 3 correlation ID work; T031 is independent (different file)
- **Phase 7 (Tests)**: Depends on all implementation phases; T032–T034 run in parallel (different test files)
- **Phase 8 (Polish)**: Depends on all phases complete

### User Story Dependencies

- **US2 (P1)**: Starts after Phase 2
- **US1 (P1)**: Backend (T018) starts after Phase 2; frontend (T019–T026) benefits from US2 complete but is not technically blocked by it
- **US3 (P2)**: T027 follows T018 (same file); T028–T029 follow T026 (same component file)
- **US4 (P2)**: T030 follows Phase 3 correlation ID work; T031 is independent

### Parallel Opportunities

- T001, T002 run in parallel (Phase 1)
- T005, T006, T007 run in parallel (Phase 2, after T003–T004)
- T008, T009, T010 run in parallel (Phase 3, different service files)
- T014, T015 run in parallel with T011–T013 (different service files)
- T018, T019, T020 run in parallel (Phase 4, different files)
- T032, T033, T034 run in parallel (Phase 7, different test files)

---

## Parallel Example: User Story 2

```
Phase 2 (run T003 then T004, then):
  Parallel: T005, T006, T007

Phase 3:
  Parallel group A: T008, T009, T010  (different service files)
  Sequential:       T011 → T012 → T013  (same service file)
  Parallel with A/sequential: T014, T015  (different files from T011-T013)
  Sequential: T016 → T017
```

## Parallel Example: User Story 1

```
Phase 4:
  T018 (backend router — no frontend dependency)
  Parallel: T019, T020  (frontend model + service, different files)
  Sequential: T021 → T022 → T023 → T024 → T025 → T026  (all event-stream.component.ts)
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 + Phase 2 (models, migration, actor block, publisher persistence)
2. Complete Phase 3 (US2 — 19 event types, correlation IDs)
3. Complete Phase 4 (US1 — live stream with real-time display, pause/resume/clear, expand/copy/links)
4. **STOP and VALIDATE**: Open Events tab, perform operations, verify stream populates
5. Add Phase 5 (US3 — filters), Phase 6 (US4 — audit correlation) as enhancements

### Incremental Delivery

1. Phase 1 + Phase 2 → Foundation ready (models, migrations, publisher)
2. Phase 3 (US2) → All 19 event types emitted and persisted
3. Phase 4 (US1) → Live stream fully operational
4. Phase 5 (US3) → Filtering enables trainer-directed narration
5. Phase 6 (US4) → Audit-event correlation completes the traceability story
6. Phase 7 (Tests) → Automated verification of envelope, coverage, and API
7. Phase 8 (Polish) → Documentation

---

## Notes

- [P] tasks = different files, no dependency on incomplete tasks in the same phase
- [Story] label maps each task to a specific user story for traceability
- T003→T004 must be sequential; T005, T006, T007 can run in parallel after T003 completes
- T011–T013 may be in the same service file — treat as sequential to avoid conflicts
- T021–T029 all touch `event-stream.component.ts` — must execute sequentially
- T027 and T018 are in the same router file — T027 must follow T018
- Run tests with `py -3.12 -m pytest backend/tests/` (default python on this machine is 3.10 which lacks StrEnum)
