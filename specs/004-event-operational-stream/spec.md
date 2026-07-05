# Feature Specification: Events, Topics, and Live Operational Stream

**Feature Branch**: `004-event-operational-stream`
**Created**: 2026-06-22
**Status**: Draft

## Overview

The Dunder Mifflin Package Manager must publish meaningful domain events when business
operations occur and display those events as a live operational stream in the UI. This
feature defines the event model, the topic categories, the relationship between audit
history and domain events, and the trainer-facing stream view.

Domain events serve two purposes: (1) real-time visibility for trainers and workshop
attendees, and (2) a stable, self-describing interface that future agents, MCP servers,
and agentic components can consume without requiring hidden workshop knowledge.

**Important distinction**: Audit history records every meaningful business change for
traceability. Domain events are published only when another part of the system may need
to react. Not every audit entry becomes a domain event.

---

## User Scenarios & Testing

### User Story 1 — Live Operational Stream (Priority: P1)

A trainer opens the operational stream view during a live workshop session. As attendees
take actions — creating packages, dispatching trucks, triggering reroutes, filing
complaints — the stream populates with live event entries in a readable format. The
trainer can point to events as they appear to narrate what is happening inside the
system. Attendees can see the relationship between their UI actions and the resulting
domain events.

**Why this priority**: The operational stream is the primary teaching tool for showing
event-driven system behavior. Without it, attendees have no visibility into what events
are being generated. This must work before anything else.

**Independent Test**: Open the operational stream view. Perform any write operation (e.g.
create a package). Verify a new event entry appears in the stream within a few seconds,
showing event type, actor, entity, timestamp, and summary. Verify the stream auto-updates
without a manual page refresh.

**Acceptance Scenarios**:

1. **Given** a trainer is viewing the operational stream, **when** any user performs a
   meaningful write operation, **then** a new event entry appears in the stream showing
   event type, human-readable summary, actor, entity type, entity ID, and occurred-at
   timestamp.

2. **Given** the stream is displaying events, **when** the trainer clicks Pause, **then**
   the stream stops adding new entries; **when** the trainer clicks Resume, **then** new
   entries appear again and no events are lost from history.

3. **Given** the stream is running, **when** the trainer clicks Clear, **then** the local
   display is reset to empty, but no stored event history is deleted.

4. **Given** an event entry is visible in the stream, **when** the trainer expands it,
   **then** the full event payload is visible in a readable format.

5. **Given** an event entry is visible, **when** the trainer clicks Copy, **then** the
   full event payload is copied to the clipboard.

6. **Given** an event entry references a package, truck, customer, or complaint, **when**
   the trainer clicks the entity link, **then** the relevant detail view opens.

---

### User Story 2 — Domain Event Model and Topics (Priority: P1)

When a meaningful business operation occurs, the system emits a domain event with a
consistent envelope. Each event is categorized into the most relevant topic so that
consumers — agents, dashboards, MCP servers — can subscribe to only the activity they
care about.

**Why this priority**: Agents and MCP components need a stable, self-describing event
interface to work in the agentic workshop exercises. Without a consistent envelope and
well-defined topics, downstream consumers cannot rely on the event stream.

**Independent Test**: Perform a package status change operation. Inspect the resulting
event. Verify it contains all required envelope fields: event ID, event type, topic,
occurred-at, actor (with persona and actor type), source, entity type, entity ID,
correlation ID, payload, and summary. Verify the event is categorized under the
`package-status` topic.

**Acceptance Scenarios**:

1. **Given** a package status changes, **when** the operation completes successfully,
   **then** the system publishes a `package.status.updated` event containing the previous
   status, new status, actor, reason (if provided), and a human-readable summary.

2. **Given** a truck is rerouted, **when** the reroute operation completes successfully,
   **then** the system publishes a `truck.rerouted` event on the `truck-reroute` topic
   containing the via-point name and coordinates, the reason, and the list of affected
   package IDs.

3. **Given** an invalid operation is attempted, **when** the operation fails, **then**
   the system does not publish a success event for that operation.

4. **Given** a demo scenario is triggered, **when** the scenario completes, **then** the
   system publishes a `demo.scenario.triggered` event with the scenario name, the actor,
   and a summary of what was changed.

5. **Given** a consumer subscribes to the `package-status` topic, **when** a package
   lifecycle change occurs, **then** the consumer receives the relevant event without
   receiving truck location or manager action events.

---

### User Story 3 — Event Filtering and Navigation (Priority: P2)

A trainer wants to focus the stream on a specific area of activity — for example, all
events related to a single truck, or all events triggered by a specific actor, or all
events for a given correlation group. The stream must support filters so trainers can
guide attendees through a specific narrative thread without being overwhelmed by
unrelated events.

**Why this priority**: Filtering is important for workshop clarity but does not block the
core stream from functioning. Once the stream works, filtering can be added to make it
more useful.

**Independent Test**: With multiple events in the stream, apply a filter by topic
(`package-status`). Verify only package status events are displayed. Clear the filter and
verify all events return. Apply a filter by actor name and verify only events from that
actor are shown.

**Acceptance Scenarios**:

1. **Given** the stream contains events from multiple topics, **when** the trainer filters
   by a specific topic (e.g. `truck-location`), **then** only events from that topic
   are displayed.

2. **Given** the stream contains events from multiple actors, **when** the trainer filters
   by actor, **then** only events attributed to that actor are displayed.

3. **Given** the stream contains events for multiple entities, **when** the trainer
   filters by package ID, **then** only events referencing that package ID are displayed.

4. **Given** the trainer applies multiple filters simultaneously, **when** events arrive,
   **then** only events matching all active filters are displayed.

5. **Given** the trainer filters by correlation ID, **when** a correlation group exists,
   **then** all events belonging to that group are displayed together.

---

### User Story 4 — Audit History and Event Relationship (Priority: P2)

Every meaningful write operation creates an audit history entry. Audit history provides
complete traceability for every business state change regardless of whether a domain event
was also published. The audit log is a separate concern from the event stream; it captures
a richer set of changes at a lower level of abstraction.

**Why this priority**: Audit history is a constitution requirement for every meaningful
write. The event stream is for reactive notification. Both must exist, but they serve
different consumers with different needs.

**Independent Test**: Perform a package status change. Verify an audit entry exists for
the change with actor, timestamp, previous value, and new value. Verify a domain event
was also published for the change (because status changes are meaningful to downstream
consumers). Then perform a minor field update (e.g. updating a package note) and verify
an audit entry exists but no domain event is required for minor changes.

**Acceptance Scenarios**:

1. **Given** any meaningful write operation occurs, **when** it completes successfully,
   **then** an audit history entry is created with actor, timestamp, source, entity type,
   entity ID, previous value (where applicable), new value (where applicable), and reason
   (where applicable).

2. **Given** an audit entry exists, **when** a trainer views audit history for a package,
   **then** all changes to that package are listed chronologically with full audit context.

3. **Given** a domain event is published for an operation, **when** that same operation
   creates an audit entry, **then** the audit entry and domain event share the same
   correlation ID so they can be linked.

4. **Given** an audit entry is created for an event that does not warrant a domain event
   (e.g. a minor field correction), **when** the audit log is queried, **then** the audit
   entry exists; no corresponding domain event exists in the stream.

---

### Edge Cases

- What happens when multiple operations share a correlation group? All events in the group
  must carry the same correlation ID so consumers can reconstruct the full operation.
- What happens when an operation fails partway through? Audit entries and events must only
  reflect operations that actually completed. Partial successes must not be represented as
  complete successes.
- What happens when the operational stream is paused and many events arrive? Events must
  still be captured and stored; the pause affects only the local display.
- What happens when a consumer subscribes to a topic and an event is emitted on a
  different topic? The consumer must not receive the event; topic boundaries must be
  enforced.
- What happens when the correlation ID is not provided by the caller? The system must
  generate one automatically for operations that naturally form a group.
- What happens when an actor type is not a human (e.g. simulation or agent)? The event
  envelope must identify the actor type so consumers can distinguish human actions from
  automated actions.

---

## Requirements

### Functional Requirements

**Event Envelope**

- **FR-001**: Every domain event MUST use a shared envelope containing: event ID (unique,
  system-generated), event type, topic, occurred-at timestamp, actor block, source,
  entity type, entity ID, correlation ID, payload, and human-readable summary.
- **FR-002**: The actor block MUST include: actor ID, actor name, persona, and actor type.
  Actor type MUST distinguish between human, demo, agent, and system.
- **FR-003**: Source MUST be one of: `ui`, `api`, `demo`, `agent`, or `system`.
- **FR-004**: Payload MUST contain all business data relevant to the event. For state
  changes, payload MUST include previous value and new value where applicable.
- **FR-005**: Payload MUST be self-describing — consumers MUST NOT need to inspect UI
  state or make additional API calls to understand the event.
- **FR-006**: Related operations MUST share a correlation ID. The system MUST
  automatically generate correlation IDs for grouped operations where the caller does
  not provide one.

**Domain Topics**

- **FR-007**: The system MUST define these topics: `packages`, `package-status`,
  `package-location`, `truck-location`, `truck-reroute`, `manager-actions`,
  `complaints`, `audit-log`.
- **FR-008**: Each domain event MUST be categorized into exactly one topic that best
  matches the consumer's area of interest.
- **FR-009**: Topic boundaries MUST be enforced so consumers subscribed to one topic do
  not receive events from unrelated topics.

**Domain Events**

- **FR-010**: The system MUST publish `package.created` when a new package is created.
- **FR-011**: The system MUST publish `package.status.updated` when a package status
  changes, including previous status, new status, actor, and reason.
- **FR-012**: The system MUST publish `package.assigned.to.truck` when a package is
  assigned to a delivery truck.
- **FR-013**: The system MUST publish `package.location.updated` when a package's location
  changes while in transit.
- **FR-014**: The system MUST publish `package.delivered` when a package is marked
  delivered at a customer stop.
- **FR-015**: The system MUST publish `package.returned` when a returned package is
  processed.
- **FR-016**: The system MUST publish `package.cancelled` when a package is cancelled.
- **FR-017**: The system MUST publish `package.damaged` when a package is marked as
  damaged.
- **FR-018**: The system MUST publish `package.delay.recorded` when a delay is recorded
  for a package.
- **FR-019**: The system MUST publish `truck.location.updated` at controlled intervals
  while a truck is in transit (not on every GPS update, to avoid event spam).
- **FR-020**: The system MUST publish `truck.route.created` when a truck route is
  calculated and activated.
- **FR-021**: The system MUST publish `truck.rerouted` when a Kevin Hunger Reroute is
  applied, including the via-point details and list of affected packages.
- **FR-022**: The system MUST publish `truck.returned.to.warehouse` when a truck completes
  its route and returns to the warehouse.
- **FR-023**: The system MUST publish `manager.action.performed` for every manager action,
  including action type, entity affected, reason, and actor.
- **FR-024**: The system MUST publish `complaint.created` when a new complaint is filed.
- **FR-025**: The system MUST publish `complaint.updated` when a complaint is updated or
  closed.
- **FR-026**: The system MUST publish `demo.scenario.triggered` when a demo scenario is
  run, including the scenario name and what was changed.
- **FR-027**: The system MUST publish `audit.entry.created` on the `audit-log` topic for
  every audit entry, so audit activity is also observable in the event stream.
- **FR-028**: The system MUST NOT publish a success event for any operation that failed.

**Audit History**

- **FR-029**: Every meaningful write operation MUST create an audit entry regardless of
  whether a domain event is also published.
- **FR-030**: Audit entries MUST include: actor ID, actor name, persona, timestamp, source,
  entity type, entity ID, action, previous value (where applicable), new value (where
  applicable), reason (where applicable), and correlation ID.
- **FR-031**: Audit entries and corresponding domain events for the same operation MUST
  share the same correlation ID.
- **FR-032**: The audit log MUST be queryable by entity (package, truck, complaint) so
  trainers can view a complete change history for any entity. The broader queryability
  required by auditability principles — by actor, time range, and event type — is served
  by the domain event store (`GET /events`), which provides these query axes alongside the
  entity-centric audit history. Together, the two stores satisfy the full spectrum of
  operational query needs.

**Live Operational Stream**

- **FR-033**: The UI MUST include a live operational stream view that displays domain
  events in real time as they are published.
- **FR-034**: The stream MUST display events newest-first by default.
- **FR-035**: The stream MUST support filtering by: topic, event type, package ID, truck
  ID, customer ID, actor, source, and correlation ID.
- **FR-036**: Multiple filters MUST be combinable; only events matching all active filters
  are shown.
- **FR-037**: The stream MUST support Pause — while paused, new events are not shown in
  the display but continue to be captured in storage.
- **FR-038**: The stream MUST support Resume — on resume, the display catches up and shows
  newly arrived events.
- **FR-039**: The stream MUST support Clear — clearing removes entries from the local
  display only; stored event history is not deleted.
- **FR-040**: Each event entry MUST be expandable to show the full payload in a readable
  format.
- **FR-041**: Each event entry MUST provide a Copy action that copies the full event
  payload to the clipboard.
- **FR-042**: Where an event references a package, truck, customer, or complaint, the
  event entry MUST include a navigation link to the relevant detail view.
- **FR-043**: The stream MUST NOT require a page refresh to show new events.

### Key Entities

- **Domain Event**: A record of something that happened that another part of the system
  may need to react to. Contains the standard envelope fields. Published after a
  successful operation. Not persisted if the triggering operation failed.
- **Event Envelope**: The shared structure wrapping every domain event. Contains event ID,
  type, topic, occurred-at, actor, source, entity type, entity ID, correlation ID,
  payload, and summary.
- **Actor**: Identifies who or what caused the event. Includes ID, name, persona, and
  actor type (human / demo / agent / system).
- **Topic**: A named category of related events. Consumers subscribe to topics. The eight
  defined topics partition the event space into distinct areas of concern.
- **Audit Entry**: A traceability record for every meaningful business change. Broader
  than domain events — captures all writes. Not all audit entries become domain events.
- **Correlation ID**: A shared identifier that groups related events and audit entries
  belonging to the same logical operation (e.g. dispatching a truck with multiple
  packages creates several events that all share one correlation ID).
- **Operational Stream**: The live UI component that displays published domain events in
  real time, with filtering and inspection capabilities.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: A trainer opening the operational stream sees new events appear within 3
  seconds of the triggering operation completing.
- **SC-002**: Every meaningful write operation in the system produces at least one audit
  entry; the audit log for any package shows a complete chronological change history.
- **SC-003**: Every domain event contains all required envelope fields and can be
  understood by a consumer without additional context from the UI or other API calls.
- **SC-004**: A consumer filtering by any single topic receives only events belonging to
  that topic and no events from unrelated topics.
- **SC-005**: The live stream displays events from all eight defined topics and correctly
  applies all supported filter combinations.
- **SC-006**: Pausing the stream and then resuming shows all events that arrived during
  the pause without gaps or duplicates in the stored history.
- **SC-007**: Related events from a single logical operation (e.g. dispatching a truck)
  all share the same correlation ID and can be grouped by it in the stream.
- **SC-008**: An agent or MCP server consuming published events can identify the actor
  type, persona, source, entity, and payload from the event alone — without calling any
  additional API endpoint to understand the event.

---

## Assumptions

- The event infrastructure (transport layer) is already partially in place from earlier
  features. This specification defines the event model, envelope, topics, and UI
  stream — not the underlying transport mechanism.
- Historical event data is queryable through stored records. The system does not need to
  support live message replay from the transport layer.
- The operational stream is intended primarily for workshop use and demo observation, not
  for high-volume production monitoring. Event volume during a workshop session is modest
  (tens to low hundreds of events per session).
- Actors identified as `system` (e.g. the simulation engine) do not have a human persona.
  The `persona` field for system actors may be omitted or set to a sentinel value.
- Clearing the stream display does not affect the ability to query historical events from
  stored records; storage is managed independently of the display.
- The `audit.entry.created` event on the `audit-log` topic is a lightweight notification
  that an audit entry was written; it does not duplicate the full payload of the primary
  domain event for the same operation.
- Event filtering in the stream is client-side display filtering, not server-side topic
  subscription filtering; all events arrive at the stream client and filtering narrows
  what is shown.
- A "minor" field update is one that generates an audit entry but does not warrant a
  domain event: specifically, a correction to a non-status, non-routing field with no
  meaningful downstream consequence — for example, correcting a typo in a package
  description or updating an internal notes field. Status changes, assignment changes, and
  any change that affects package lifecycle or routing always warrant domain events.
