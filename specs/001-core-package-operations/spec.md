# Feature Specification: Core Package Operations

**Feature Branch**: `001-core-package-operations`
**Created**: 2026-06-19
**Status**: Draft
**Input**: User description: "Create a functional specification for Feature 1: Core Package Operations"

## Business Context

The Dunder Mifflin Package Manager is the core business system for tracking paper-product and
office-supply sales from order creation through delivery or terminal exception. This feature
establishes the foundational record-keeping, lifecycle management, and operational visibility
capabilities that every other system component depends on.

Sales create orders. Orders produce invoices and packages. Packages move through a defined
lifecycle. Along the way, operational events — delays, damage, returns, complaints — are
recorded with full history. Every meaningful action is auditable. Domain events notify other
parts of the system when lifecycle changes occur.

This feature is the stable baseline that workshop agents and MCP integrations will later
consume. Agent-readiness is a design constraint from the beginning, not a post-launch concern.

## User Scenarios & Testing

### User Story 1 - Create a Sale with Invoice and Packages (Priority: P1)

A salesperson records a new sale for a customer. The system generates exactly one invoice for
the sale. The salesperson then creates one or more packages for that sale, each containing one
or more line items representing specific paper products or office supplies.

**Why this priority**: This is the entry point for all other operations. No packages, history,
lifecycle management, or complaint records can exist without a sale. It delivers immediate,
demonstrable business value and unblocks all downstream user stories.

**Independent Test**: Create a sale for an existing customer, verify an invoice is generated,
add two packages to the sale each containing at least two line items (mixing paper products and
office supplies), confirm all records are visible in the system with correct linkages.

**Acceptance Scenarios**:

1. **Given** a logged-in salesperson, **When** they create a new sale for an existing
   customer, **Then** the system creates the sale record with the salesperson recorded, and
   automatically creates exactly one linked invoice associated with the same sale.

2. **Given** an existing sale with one invoice, **When** a salesperson creates a package for
   that sale, **Then** the package is linked to the sale and to the sale's invoice, begins in
   "order created" status, and a history entry is recorded for the package creation.

3. **Given** a package in "order created" status, **When** a salesperson adds a paper product
   line item, **Then** the line item is stored with its product name, category, quantity, unit
   description, product type (paper product), and fragile/special-handling flag.

4. **Given** a package in "order created" status, **When** a salesperson also adds an office
   supply line item, **Then** both line items coexist on the same package — one as paper
   product, one as office supply.

5. **Given** an existing sale, **When** a salesperson creates a second package for the same
   sale, **Then** both packages are linked to the same invoice and the same sale, and both
   appear when viewing the sale.

6. **Given** a package with no line items, **When** a user attempts to advance it beyond
   "order created" status, **Then** the system prevents the transition and displays a clear
   message requiring at least one line item.

---

### User Story 2 - View Package List and Package Detail with History (Priority: P1)

Any employee can view a list of recent packages with their current statuses. Any employee can
navigate to a package detail view that shows all package fields and the complete history of
events affecting that package.

**Why this priority**: Operational visibility is fundamental to every persona. Sales, accounting,
warehouse, and management all need to see current package state and full change history without
needing to modify anything. This is also the primary surface that workshop attendees will
observe agent behavior through.

**Independent Test**: Navigate to the package list, verify recent packages appear with current
status visible, open a package detail page, confirm all required fields are displayed, confirm
the history section shows all recorded events in reverse-chronological order.

**Acceptance Scenarios**:

1. **Given** any logged-in employee, **When** they navigate to the package list, **Then** they
   see packages sorted by most recently updated, each showing package ID, customer name,
   current status, priority, and last updated time.

2. **Given** any logged-in employee, **When** they open a package detail page, **Then** they
   see all of: package ID, sale ID, invoice ID, customer, salesperson, invoicing employee,
   current status, current location, destination, assigned truck, expected delivery time,
   priority, contents summary, fragile flag, all line items, created date, and last updated date.

3. **Given** a package with multiple history entries, **When** any employee views the package
   detail page, **Then** the full history is displayed in reverse-chronological order, each
   entry showing actor, timestamp, source, entity affected, previous value, new value, and
   reason.

4. **Given** the package list, **When** a user filters by a specific status, **Then** only
   packages currently in that status are shown.

5. **Given** a package in a terminal status (delivered, cancelled, damaged, or returned),
   **When** any employee views its detail page, **Then** the full history is visible and the
   terminal state is clearly indicated.

---

### User Story 3 - Advance a Package Through Its Lifecycle (Priority: P2)

A warehouse employee advances a package through its defined lifecycle statuses. The system
validates each transition, rejects invalid moves backward or to undefined states, and records
every status change as an immutable history entry and domain event.

**Why this priority**: Package lifecycle management is the core operational function of the
system. It demonstrates the controlled-state-change pattern that is central to the workshop's
enterprise-pattern learning goals.

**Independent Test**: Take a package from "order created" through each valid status to
"delivered." Verify each forward transition is accepted. Attempt a backward transition and
verify rejection. Record a delay and verify the status does not change to a terminal state.

**Acceptance Scenarios**:

1. **Given** a package in "order created" status, **When** a warehouse employee advances it
   to "packaged," **Then** the status updates, a history entry records actor, timestamp,
   source, previous status, new status, and optional reason, and a domain event is emitted.

2. **Given** a package in "packaged" status, **When** any user attempts to move it back to
   "order created," **Then** the system rejects the transition with a clear error message and
   no change is recorded.

3. **Given** a sale where stock is unavailable for fulfillment, **When** a warehouse employee
   marks a package as "backorder," **Then** the package status changes to "backorder" and a
   history entry is recorded. When stock becomes available and the package is advanced to
   "packaged," the system accepts the transition.

4. **Given** a package in "in transit" status, **When** a warehouse employee records a delay
   with a reason and a duration, **Then** the delay is stored as an operational attribute with
   a history entry, and the package status remains "in transit" — not a terminal state.

5. **Given** a package in "in transit" status with an active delay, **When** the delay
   condition resolves and the employee advances the package to "delivered," **Then** the
   transition is accepted normally.

6. **Given** a package in "delivered" status, **When** any user attempts to change its
   lifecycle status, **Then** the system rejects the change because "delivered" is a terminal
   status.

---

### User Story 4 - Record Operational Exceptions (Priority: P2)

A warehouse employee or manager records terminal exceptions — damage, cancellation, or return —
against a package. Once an exception is recorded, the package lifecycle is complete. No further
lifecycle changes are permitted. Further business action requires a new sale and package.

**Why this priority**: Real logistics operations encounter exceptions regularly. The system must
model these accurately to be a valid enterprise teaching reference, and must enforce immutability
of terminal states so agent consumers can trust the data.

**Independent Test**: Record each terminal exception type (damage, cancellation, return) on
separate packages, verify each package moves to the correct terminal status, verify no further
lifecycle changes are accepted, and verify a new sale and package must be created for follow-up
work.

**Acceptance Scenarios**:

1. **Given** a package in any non-terminal status, **When** a warehouse employee records
   damage with a reason, **Then** the package moves to "damaged" status, a history entry is
   created, and no further lifecycle transitions are permitted on that package.

2. **Given** a package in any non-terminal status, **When** an authorized user cancels the
   package with a reason, **Then** the package moves to "cancelled" status, a history entry is
   created, and no further lifecycle transitions are permitted.

3. **Given** a delivered package, **When** a manager approves a return, **Then** the original
   package moves to "returned" status, a history entry is recorded with the manager as actor,
   and no further lifecycle changes are permitted on that package.

4. **Given** a package in "in transit" status, **When** a return is initiated before delivery
   (package comes back in transit), **Then** the package can be moved to "returned" with
   manager approval, and a history entry is recorded.

5. **Given** any terminal package, **When** a follow-up business action is needed, **Then**
   a new sale and new package must be created. The original terminal package is not modified.

---

### User Story 5 - Manage Complaints (Priority: P2)

Any employee can create a complaint tied to a sale and optionally associated with one or more
of its packages. Complaints can be updated and closed. Complaints are permitted regardless of
the lifecycle status of the associated packages, including terminal states.

**Why this priority**: Customer complaints are a critical business record. They must be
trackable independently of package lifecycle state and must be associatable with terminal
packages. This also demonstrates cross-entity event propagation in the history model.

**Independent Test**: Create a complaint tied to a sale, associate it with two packages,
update the complaint, close it, and verify history entries appear on all associated packages
at each step.

**Acceptance Scenarios**:

1. **Given** an existing sale, **When** any employee creates a complaint, **Then** the
   complaint is linked to the sale, optionally linked to one or more of its packages, and a
   history entry is added to each associated package.

2. **Given** an open complaint, **When** an employee updates it with new information, **Then**
   the update is saved and a history entry is added to all associated packages reflecting the
   complaint update.

3. **Given** an open complaint, **When** an employee closes it, **Then** the complaint moves
   to closed status and a history entry is added to all associated packages.

4. **Given** a package in "delivered" status, **When** an employee creates a complaint
   referencing that package, **Then** the system allows the complaint because complaints are
   permitted against packages in any lifecycle status.

5. **Given** a complaint tied to multiple packages, **When** the complaint is updated, **Then**
   all associated packages reflect the complaint update in their individual package histories.

---

### User Story 6 - Manager Actions and Permission Enforcement (Priority: P3)

Michael Scott, as regional manager, can perform a defined set of manager-only actions. All
other employee personas are prevented from performing these actions server-side. Every manager
action is recorded in package history.

**Why this priority**: Persona-based authorization is a foundational enterprise security
pattern. This enforcement must be in place before workshop agents consume the API, so agents
cannot bypass permissions through direct API calls.

**Independent Test**: As Michael, perform each manager action and verify success. As a
non-manager employee, attempt each manager action and verify rejection. Verify manager actions
appear in package history.

**Acceptance Scenarios**:

1. **Given** a package requiring reroute, **When** Michael approves the reroute, **Then** the
   reroute is applied, and a history entry records "manager action performed," the specific
   action, actor (Michael), timestamp, and reason.

2. **Given** a package with standard priority, **When** Michael overrides the priority, **Then**
   the priority is updated and a history entry records the override with previous and new values.

3. **Given** a logged-in non-manager employee, **When** they attempt any manager-only action,
   **Then** the system rejects the action with a clear descriptive message and no change is
   recorded anywhere in the system.

4. **Given** a package requiring an expensive delivery option, **When** Michael approves the
   expensive delivery, **Then** the approval is recorded in package history with actor, timestamp,
   and reason.

5. **Given** Michael is logged in, **When** he triggers a demo scenario, **Then** the system
   executes the demo scenario and records a history entry on the affected package with event type
   "manager action performed" and source identified as the trigger origin.

---

### Edge Cases

- A sale with multiple packages where only some packages are backordered — the non-backordered
  packages must be able to proceed through the lifecycle independently.
- A package must have at least one line item. The system must prevent removal of the last
  remaining line item.
- Complaints may reference packages from the same sale that are in different lifecycle statuses,
  including a mix of active and terminal statuses.
- A package that already has an active delay record must replace — not accumulate — the delay
  when a new delay is recorded.
- An employee cannot assume another persona's permissions by altering their request. Permission
  enforcement is independent of request origin.
- Package history must be fully visible for terminal packages. Terminal status does not restrict
  history viewing.
- Multiple employees of the same persona may act on the same package; every action is
  individually attributed to the specific acting employee.
- The correlation ID on history entries is optional and the system must handle its absence
  gracefully.
- A delay may be recorded even while a package has a backorder status.

## Requirements

### Functional Requirements

#### Sale Management

- **FR-001**: The system MUST allow a salesperson to create a sale linked to an existing
  customer, recording the salesperson as the sale creator.
- **FR-002**: The system MUST automatically create exactly one invoice when a sale is created.
- **FR-003**: The system MUST link every invoice to exactly one sale and prevent an invoice
  from existing without a sale reference.
- **FR-004**: The system MUST display a sale's invoice and all associated packages when a
  sale record is viewed.
- **FR-005**: The system MUST prevent creation of a sale without a linked customer.

#### Invoice Management

- **FR-006**: The system MUST allow any employee to view invoices.
- **FR-007**: The system MUST record which employee created the invoice on the invoice record.
- **FR-008**: The system MUST display the sale reference on every invoice.
- **FR-009**: The system MUST only allow invoice creation in the context of a sale; standalone
  invoices are not permitted.

#### Package Management

- **FR-010**: The system MUST allow creation of a package linked to an existing sale.
- **FR-011**: Every package MUST record: package ID, sale ID, invoice ID, customer,
  salesperson, invoicing employee, current status, current location, destination, assigned
  truck, expected delivery time, priority, contents summary, fragile flag, created date,
  and last updated date.
- **FR-012**: The system MUST prevent a package from advancing past "order created" status
  until it has at least one line item.
- **FR-013**: The system MUST allow any employee to view all packages belonging to a sale.
- **FR-014**: The system MUST allow editing a package's current location, destination, assigned
  truck, expected delivery time, priority, contents summary, and fragile flag while the package
  is in a non-terminal status.
- **FR-015**: The system MUST prevent editing of packages in terminal statuses except through
  explicitly permitted operations (complaints, manager actions).
- **FR-016**: The system MUST allow deletion of a package that is in "order created" status
  only.
- **FR-017**: The system MUST prevent deletion of a package that has progressed past "order
  created" status.

#### Package Line Items

- **FR-018**: The system MUST allow adding one or more line items to a package.
- **FR-019**: Each line item MUST record: product name, product category, quantity, unit
  description, product type (paper product or office supply), and fragile/special-handling flag.
- **FR-020**: The system MUST prevent removal of a line item if it is the last remaining line
  item on the package.
- **FR-021**: The system MUST allow editing line items on packages in non-terminal statuses.
- **FR-022**: Every line item addition or modification MUST produce a package history entry.

#### Package Lifecycle

- **FR-023**: The system MUST enforce the following permitted lifecycle transitions only:
  - order created → backorder
  - order created → packaged
  - backorder → packaged
  - packaged → ready for shipping
  - ready for shipping → shipped
  - shipped → in transit
  - in transit → delivered
  - any non-terminal status → cancelled
  - any non-terminal status → damaged
  - in transit → returned (with manager approval)
  - delivered → returned (with manager approval)
- **FR-024**: The system MUST reject any lifecycle transition not listed in FR-023, including
  any move that would take a package backward in the normal sequence.
- **FR-025**: The system MUST reject any lifecycle modification to a package already in a
  terminal status (delivered, cancelled, damaged, returned).
- **FR-026**: The system MUST allow recording a delay — with a reason and a duration — on any
  non-terminal package without changing the package status.
- **FR-027**: The system MUST store at most one active delay record per package. Recording a
  new delay replaces the existing active delay.

#### Status Change Behavior

- **FR-028**: Every status change MUST be recorded as a history entry conforming to FR-033.
  (FR-033 is the authoritative field list; this requirement asserts that status changes are
  not exempt from the general history contract.)
- **FR-029**: Every status change MUST produce an immutable package history entry before the
  change is considered complete.
- **FR-030**: The system MUST validate the transition as permitted before recording any history
  entry or emitting any event. A rejected transition produces no history and no event.
- **FR-031**: Every meaningful package lifecycle status change MUST emit a domain event
  consumable by other system components.

#### Package History

- **FR-032**: The system MUST record a history entry for each of the following event types:
  package created, line item added, line item changed, status changed, location updated,
  assigned to truck, truck rerouted, delivered, returned, damaged, cancelled, complaint
  created, complaint updated, manager action performed.
- **FR-033**: Each history entry MUST include: actor, timestamp, source (UI, API, demo, agent,
  or system), entity affected, previous value (where applicable), new value (where applicable),
  reason (where applicable), and correlation ID (where applicable).
- **FR-034**: History entries MUST be immutable once written. No operation may modify or
  delete a history entry.
- **FR-035**: The system MUST display package history on the package detail view in
  reverse-chronological order.

#### Complaints

- **FR-036**: The system MUST allow any employee to create a complaint tied to an existing sale.
- **FR-037**: A complaint MUST be associatable with one or more packages from the referenced
  sale.
- **FR-038**: The system MUST allow updating an open complaint.
- **FR-039**: The system MUST allow closing an open complaint.
- **FR-040**: Complaint creation and every subsequent complaint update MUST produce a history
  entry on all associated packages.
- **FR-041**: The system MUST allow complaints to be created against packages in any lifecycle
  status, including terminal statuses.

#### Permission Enforcement

- **FR-042**: The system MUST enforce persona-based permissions independently of any
  client-side or UI-level restriction. Server-side enforcement is the authoritative layer.
- **FR-043**: Manager-only actions MUST only be executable by the manager persona
  (Michael Scott).
- **FR-044**: The system MUST reject manager-only action requests from non-manager personas
  with a clear, descriptive error message, and MUST record no change as a result.
- **FR-045**: A salesperson MUST be able to: create sales, create packages, add and edit line
  items, view all packages, and create complaints.
- **FR-046**: An accounting employee MUST be able to: view invoices, view sales, view packages,
  and create complaints.
- **FR-047**: A warehouse employee MUST be able to: advance package lifecycle status, record
  delays, record damage, update package location, assign trucks, and create complaints.
- **FR-048**: The manager MUST be able to perform all operations available to all other personas,
  plus all manager-only actions.

#### Manager Actions

- **FR-049**: The system MUST allow the manager to approve a package reroute.
- **FR-050**: The system MUST allow the manager to override a package priority.
- **FR-051**: The system MUST allow the manager to mark a customer as unhappy.
- **FR-052**: The system MUST allow the manager to approve a package return.
- **FR-053**: The system MUST allow the manager to approve an expensive delivery option.
- **FR-054**: The system MUST allow the manager to force a truck reassignment.
- **FR-055**: The system MUST allow the manager to trigger a demo scenario.
- **FR-056**: Every manager action MUST produce a package history entry of type "manager action
  performed," capturing the specific action, actor, timestamp, and reason.

#### Domain Events

- **FR-057**: The system MUST emit domain events for the following package lifecycle changes:
  package created, status changed to any new status, package delivered, package cancelled,
  package damaged, package returned.
- **FR-058**: Each domain event MUST carry sufficient context for a consumer to react without
  querying the source system, including at minimum: entity ID, new state, actor, and timestamp.
- **FR-059**: The system MUST NOT emit domain events for trivial internal changes that have no
  consequence outside the immediate operation boundary.

### Key Entities

- **Sale**: A purchase of paper products and/or office supplies by a customer. Has exactly one
  invoice and one or more packages. Records the salesperson who initiated the sale.

- **Invoice**: A billing record automatically generated when a sale is created. Linked to
  exactly one sale. Records the accounting employee who created it.

- **Package**: A collection of one or more line items destined for the same customer, linked to
  exactly one sale and one invoice. Carries lifecycle status, location, destination, priority,
  fragile flag, and operational attributes including delay records and truck assignment.

- **Package Line Item**: A specific product within a package. Records product name, category,
  quantity, unit description, product type (paper product or office supply), and
  fragile/special-handling flag.

- **Customer**: An organization or individual that purchases from Dunder Mifflin. Referenced
  by sales and packages.

- **Employee**: A predefined Dunder Mifflin staff member assigned to exactly one persona (sales,
  accounting, warehouse, or manager). Every business event is attributed to an acting employee.

- **Complaint**: A record of a customer concern. Linked to exactly one sale and optionally to
  one or more of its packages. Has open/closed status and a history of updates.

- **Package History Entry**: An immutable record of a meaningful business event affecting a
  package. Captures actor, timestamp, source, entity affected, previous value, new value,
  reason, and correlation ID.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A salesperson can create a complete sale — including one invoice and two packages
  each with at least two mixed line items — in under three minutes without requiring assistance.

- **SC-002**: All 12 predefined employee accounts are active in the system with persona
  assignments that correctly reflect their role-based capabilities.

- **SC-003**: One hundred percent of attempted invalid lifecycle transitions (backward moves,
  skipped statuses, modifications to terminal packages) are rejected before any data is
  written to the system.

- **SC-004**: Every meaningful business operation produces a visible, correctly attributed
  history entry accessible from the package detail view within the same interaction.

- **SC-005**: One hundred percent of manager-only action attempts by non-manager employees are
  rejected, with no change recorded in the system.

- **SC-006**: A package detail page — including full history of up to 50 entries — loads in
  under 2 seconds when accessed from the trainer machine running `docker compose up`.

- **SC-007**: The package list displays package_id, customer name, current status, priority,
  and last_updated for every package without horizontal scrolling at a 1280px-wide viewport.

- **SC-008**: All four terminal exception states (delivered, cancelled, damaged, returned) are
  enforced such that no further lifecycle transitions succeed after a package reaches one.

- **SC-009**: At least one domain event is emitted and verifiably receivable for each of the
  six defined lifecycle event categories, carrying sufficient context to act without additional
  queries.

- **SC-010**: The complaint lifecycle (create, update, close) is completable end-to-end without
  requiring the associated package to be in a specific lifecycle state.

## Assumptions

- **A-001**: Dwight Schrute is assigned the sales persona for this feature. His assistant-
  manager title may result in elevated permissions in a future feature but is out of scope here.

- **A-002**: Pam Beesly is assigned the accounting persona. Her office administrator role
  makes her the appropriate persona for invoice and sale record visibility.

- **A-003**: Creed Bratton is assigned the warehouse persona. Quality assurance is treated as
  an operational role for the purposes of this feature.

- **A-004**: Package deletion is permitted only while a package is in "order created" status.
  Any lifecycle progression makes deletion unavailable.

- **A-005**: The "backorder" status is an optional, incidental step. A package may skip
  backorder and proceed directly from "order created" to "packaged" if stock is available.

- **A-006**: A package carries at most one active delay record at a time. Recording a new delay
  replaces the previous active delay. The old delay values are preserved in package history.

- **A-007**: The "source" field on history entries (UI, API, demo, agent, system) is provided
  by the caller of the operation. The system stores it faithfully. Automatic detection of source
  is not required in this feature.

- **A-008**: "Expensive delivery" is a business judgment call by the manager. The system records
  the approval event but does not define or enforce a cost threshold for when approval is required.

- **A-009**: Customer records exist in the system before sale creation. Customer creation and
  management are out of scope for this feature.

- **A-010**: Truck records exist in the system before assignment. Fleet and truck management
  are out of scope for this feature.

- **A-011**: The specific content and behavior of each demo scenario triggered by the manager
  action "Trigger demo scenario" is defined in the demo reliability specification, not here.

- **A-012**: Cancellation of a package may be performed by any employee with appropriate access;
  the feature does not restrict cancellation to a specific persona unless a future business rule
  requires manager approval for cancellation, which is not specified in this feature.

- **A-013**: Truck simulation — including `TruckService`, `RouteService`, and the tick-based
  `SimulationEngine` — is a workshop-enhancement capability introduced in the technical plan.
  While A-010 states that truck record management (fleet CRUD) is out of functional scope, the
  simulation layer that moves trucks along routes and emits location events is in technical scope
  as a demo-reliability feature required for the live-map and event-stream workshop exercises.
  Agents and MCP servers in later modules consume the read-only truck and route endpoints.
