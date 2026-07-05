# Implementation Plan: Core Package Operations

**Branch**: `master` | **Date**: 2026-06-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-core-package-operations/spec.md`

## Summary

Build the official trainer baseline for the Dunder Mifflin Package Manager: a full-stack web
application that implements the core package lifecycle, sale and invoice management, complaint
handling, persona-based permissions, audit logging, and domain event publishing. The backend
exposes a FastAPI HTTP API with OpenAPI documentation and MCP-friendly endpoints. The frontend
is an Angular application with an Azure Maps delivery map, real-time updates via Azure Web
PubSub, and a demo control panel. Azure SQL and Azure Service Bus back the official trainer
deployment. Docker Compose enables local development with SQL Server in a container.

## Technical Context

**Language/Version**: Python 3.12 (backend) · TypeScript / Angular 18 (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Alembic, Pydantic-Settings (backend);
Angular, Tailwind CSS, Azure Maps JS SDK (frontend)
**Storage**: Azure SQL (trainer baseline) · SQL Server in Docker (local dev)
**Testing**: pytest with pytest-asyncio (backend)
**Target Platform**: Azure Container Apps (deployed) · Docker Compose (local dev)
**Project Type**: Full-stack web application (Angular SPA + Python REST API)
**Performance Goals**: Workshop demo quality — responsive to interactive use; not
production-scale benchmarking. Target: API responses under 500ms for any demo operation.
**Constraints**: `docker compose up` starts the full stack locally; no secrets committed;
state resettable via single command; all 12 employees seeded; devcontainer-ready.
**Scale/Scope**: ~12 predefined employees, ~10 customers, ~30 seed packages, 1 trainer team,
workshop cohort of ~20 attendees. Single-region Azure deployment.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. Workshop-First Clarity | ✅ | Plain service classes, descriptive module names, no DI frameworks |
| II. Enterprise-Translatable Design | ✅ | State machine, RBAC, event bus, audit log — all named for what they are |
| III. Separation of Spec / Implementation | ✅ | This plan references spec.md; no functional requirements added here |
| IV. API-First and Agent-Ready | ✅ | FastAPI + OpenAPI export; MCP-friendly endpoints; tags align to future MCP tools |
| V. Auditability by Default | ✅ | AuditLog table; every service write records an audit entry before returning |
| VI. Controlled State Changes | ✅ | VALID_TRANSITIONS dict in lifecycle/transitions.py; validator called before any write |
| VII. Event-Driven Where It Matters | ✅ | 8 domain topics; EventPublisher abstraction; simulation tick controls event rate |
| VIII. Secure by Default | ✅ | env vars for secrets; Pydantic validation on all writes; persona middleware server-side |
| IX. Accessible and Usable UI | ✅ | Tailwind with WCAG-compliant palette; Angular CDK for keyboard nav; empty states defined |
| X. Demo Reliability | ✅ | POST /demo/reset; POST /demo/scenarios/{name}; seed script; docker compose up |
| XI. Test the Core | ✅ | pytest suite for lifecycle, permissions, manager actions, audit, events, seed, API |
| XII. No Hidden Workshop Dependencies | ✅ | docker-compose.yml; .devcontainer; .env.example; documented shared Azure resources |
| XIII. Theme Supports Learning | ✅ | Themed seed data; enterprise concept named in docs; theme absent from error logic |

**Gate result: PASS — proceed to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/001-core-package-operations/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── api-endpoints.md
│   ├── event-envelope.md
│   └── persona-model.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── app.component.ts
│   │   ├── app.routes.ts
│   │   ├── components/
│   │   │   ├── persona-switcher/
│   │   │   ├── dashboard/
│   │   │   ├── package-list/
│   │   │   ├── package-detail/
│   │   │   ├── status-cards/
│   │   │   ├── map-view/
│   │   │   ├── truck-route-view/
│   │   │   ├── event-stream/
│   │   │   └── demo-controls/
│   │   ├── services/
│   │   │   ├── api.service.ts
│   │   │   ├── persona.service.ts
│   │   │   ├── realtime.service.ts
│   │   │   └── map.service.ts
│   │   └── models/
│   ├── environments/
│   └── styles.css
├── Dockerfile
├── nginx.conf
├── angular.json
├── tailwind.config.js
├── package.json
└── .env.example

backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── employee.py
│   │   ├── customer.py
│   │   ├── sale.py
│   │   ├── invoice.py
│   │   ├── package.py
│   │   ├── package_line_item.py
│   │   ├── package_history.py
│   │   ├── complaint.py
│   │   ├── truck.py
│   │   └── audit_log.py
│   ├── schemas/
│   │   ├── package.py
│   │   ├── sale.py
│   │   ├── invoice.py
│   │   ├── complaint.py
│   │   └── truck.py
│   ├── services/
│   │   ├── package_service.py
│   │   ├── sale_service.py
│   │   ├── invoice_service.py
│   │   ├── complaint_service.py
│   │   ├── truck_service.py
│   │   └── demo_service.py
│   ├── routers/
│   │   ├── packages.py
│   │   ├── sales.py
│   │   ├── invoices.py
│   │   ├── customers.py
│   │   ├── employees.py
│   │   ├── trucks.py
│   │   ├── routes.py
│   │   ├── events.py
│   │   ├── complaints.py
│   │   ├── manager_actions.py
│   │   └── demo.py
│   ├── lifecycle/
│   │   ├── transitions.py
│   │   └── validator.py
│   ├── persona/
│   │   ├── middleware.py
│   │   └── permissions.py
│   ├── events/
│   │   ├── publisher.py
│   │   ├── service_bus.py
│   │   ├── inmemory.py
│   │   └── envelope.py
│   ├── audit/
│   │   └── logger.py
│   └── simulation/
│       ├── engine.py
│       └── tick.py
├── migrations/
│   ├── env.py
│   ├── versions/
│   └── alembic.ini
├── tests/
│   ├── conftest.py
│   ├── test_lifecycle.py
│   ├── test_permissions.py
│   ├── test_manager_actions.py
│   ├── test_audit.py
│   ├── test_events.py
│   ├── test_seed.py
│   └── test_api_packages.py
├── seed/
│   └── seed_data.py
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── .env.example

infra/
├── main.bicep
├── modules/
│   ├── sql.bicep
│   ├── service-bus.bicep
│   ├── web-pubsub.bicep
│   ├── maps.bicep
│   ├── container-apps.bicep
│   └── key-vault.bicep
└── parameters/
    ├── trainer.bicepparam
    └── dev.bicepparam

scripts/
├── reset-seed.ps1
├── reset-seed.sh
└── export-openapi.sh

docs/
├── architecture.md
├── local-setup.md
├── azure-setup.md
├── persona-guide.md
├── seed-data.md
├── demo-scenarios.md
├── event-topics.md
├── openapi-usage.md
└── mcp-integration.md

.devcontainer/
└── devcontainer.json

.github/
└── workflows/
    └── ci.yml

docker-compose.yml
README.md
```

**Structure Decision**: Web application (Option 2). Backend is a standalone Python/FastAPI
service. Frontend is a standalone Angular SPA. Both are containerized independently and
connected via docker-compose for local development. Azure Container Apps hosts both in the
trainer baseline. The `infra/`, `scripts/`, and `docs/` directories complete the monorepo.

## Implementation Phases

### Phase 1: Repository Structure and Development Environment

**Goal**: A working skeleton that every subsequent phase builds on.

- Create the full monorepo directory structure above.
- Write `docker-compose.yml`: services for `sqlserver` (mcr.microsoft.com/mssql/server),
  `backend` (Python/FastAPI), and `frontend` (Angular dev server / nginx).
- Write `.devcontainer/devcontainer.json` with Python 3.12, Node 20, Angular CLI, Azure CLI,
  Bicep CLI, and the Azure SQL ODBC driver.
- Write `.github/workflows/ci.yml` with basic lint and test steps.
- Write root `README.md` covering project purpose, workshop role, local setup (docker compose
  up), and links to docs/.
- Write `.env.example` files for backend and frontend with all variable names documented.

### Phase 2: Backend Domain Model, Migrations, and Seed Data

**Goal**: A working database schema with seeded reference data.

- Create `backend/app/config.py` using `pydantic-settings` to load all configuration from
  environment variables. No hardcoded values.
- Create `backend/app/database.py` with SQLModel engine setup, session factory, and a
  FastAPI `get_session` dependency.
- Create all SQLModel table models in `backend/app/models/` (see data-model.md).
- Set up Alembic: `alembic.ini`, `migrations/env.py` referencing all models.
- Generate and apply the initial migration (creates all tables).
- Create `backend/seed/seed_data.py`:
  - All 12 employees with correct persona assignments
  - 10 fictional Scranton-area customers
  - 3 trucks with Scranton coordinates
  - 5 sample sales with invoices and packages in varied lifecycle statuses
  - 3 active complaints in varied states
  - Package history entries for each package reflecting its journey so far
- Create `scripts/reset-seed.ps1` and `reset-seed.sh` that drop and re-run the seed.

### Phase 3: Core Package, Sale, Invoice, Customer, Employee, and Complaint APIs

**Goal**: Full CRUD and lifecycle APIs for all core entities.

- Create Pydantic schemas for all request and response models in `backend/app/schemas/`.
- Create service classes in `backend/app/services/` implementing business logic:
  - `PackageService`: create, get, list, update fields, delete (order_created only),
    advance lifecycle, record delay, record damage, cancel, get history.
  - `SaleService`: create sale (auto-creates invoice), get, list.
  - `InvoiceService`: get, list.
  - `ComplaintService`: create, update, close, get.
  - `CustomerService`: get, list.
  - `EmployeeService`: get, list.
- Create FastAPI routers in `backend/app/routers/` (one file per tag).
- Wire all routers into `backend/app/main.py` with correct tags.
- Include MCP-friendly summary endpoints:
  - `GET /operational-summary`
  - `GET /packages/at-risk`
  - `GET /packages/delayed`
  - `GET /packages/{id}/history`
  - `GET /deliveries/active`
  - `GET /customers/{id}/complaints`

### Phase 4: Persona Validation and Manager Actions

**Goal**: Server-side persona enforcement and all manager actions.

- Create `backend/app/persona/middleware.py`:
  - Reads `X-Persona-Id` header on every request.
  - Resolves the Employee record from the database.
  - Sets `request.state.current_user` (employee object).
  - Returns 401 if header is missing on write operations.
  - Returns 403 with a descriptive message if the employee persona does not have the
    required permission for the operation.
- Create `backend/app/persona/permissions.py`:
  - `PERSONA_PERMISSIONS` dict mapping each persona to allowed operations.
  - `require_permission(operation)` dependency for use in route handlers.
  - `require_manager()` dependency for manager-only routes.
- Create `backend/app/services/` — `ManagerActionsService`:
  - `approve_reroute`, `override_priority`, `mark_customer_unhappy`, `approve_return`,
    `approve_expensive_delivery`, `force_truck_reassignment`, `trigger_demo_scenario`.
  - Each method validates manager persona, records audit entry, records package history.
- Create `backend/app/routers/manager_actions.py` with `POST /manager-actions`.

### Phase 5: Frontend Shell and Core UI

**Goal**: A working Angular SPA with all primary views and persona switching.

- Initialize Angular 18 project in `frontend/` with standalone components.
- Configure Tailwind CSS with a WCAG-compliant color palette and DM-themed design tokens.
- Implement `PersonaSwitcherComponent`: dropdown of all 12 employees; stores selection in
  `PersonaService`; sends `X-Persona-Id` header on all subsequent API calls.
- Implement `DashboardComponent`: status summary cards, recent activity feed, quick-action
  links.
- Implement `PackageListComponent`: table of packages with status badges, priority indicators,
  filter by status, sort by last updated.
- Implement `PackageDetailComponent`: all package fields, line items table, full history
  timeline, action buttons (advance status, record delay, record damage, cancel — visibility
  driven by persona).
- Implement `StatusCardsComponent`: reusable count cards for each lifecycle status.
- Wire `ApiService` for all backend HTTP calls with `X-Persona-Id` header injection.
- All components: keyboard navigation, ARIA labels, empty states, error messages.

### Phase 6: Azure Maps Delivery Map and Truck Simulation

**Goal**: Live delivery map showing trucks, customers, and routes.

- Create `TruckService` and `RouteService` in the backend.
- Create `backend/app/simulation/engine.py`:
  - Background task (APScheduler or FastAPI lifespan) that ticks at a configurable interval.
  - Each tick: advance each active truck along its route by one step.
  - Emit `truck-location` event at each meaningful movement step (not every tick).
  - Emit `package-location` event when package location updates with truck.
  - Emit `truck-reroute` event when truck is rerouted.
  - Emit `package-status` event when truck delivers a package.
  - Persist truck state after each tick.
- Integrate Azure Maps route calculation: when a route is created or a truck is rerouted,
  call Azure Maps to calculate the polyline. Cache the result in `TruckRoute.azure_maps_route`.
- Implement `MapViewComponent` in Angular:
  - Azure Maps JS SDK embedded in Angular component.
  - Scranton area initial view, Dunder Mifflin office and warehouse markers.
  - Customer markers at fictional Scranton-area coordinates.
  - Truck markers updated via real-time events.
  - Active route polylines per truck.
  - Donut and food themed waypoint markers for the theme.
- Implement `TruckRouteViewComponent`: sidebar with route stops, ETA, current truck status.
- Add `GET /trucks/{id}/current-route` and `GET /trucks/{id}/current-location` endpoints.

### Phase 7: Event Publisher, Audit Log, and Azure Service Bus Integration

**Goal**: All meaningful events published; every write operation audited.

- Create `backend/app/events/envelope.py`: `EventEnvelope` Pydantic model with eventId,
  eventType, topic, occurredAt, actor, source, entityType, entityId, correlationId, payload,
  summary.
- Create `backend/app/events/publisher.py`: abstract `EventPublisher` base class with a
  single `async publish(event: EventEnvelope) -> None` method.
- Create `backend/app/events/inmemory.py`: `InMemoryEventPublisher` that logs to stdout.
  This is the default for local development without Service Bus.
- Create `backend/app/events/service_bus.py`: `ServiceBusEventPublisher` using the Azure
  Service Bus SDK. Reads connection string or managed identity from config.
- Create `backend/app/audit/logger.py`: `AuditLogger` service that writes an `AuditLog`
  record for every meaningful write operation. Called from every service method.
- Wire `EventPublisher` and `AuditLogger` into all service classes via FastAPI dependency
  injection.
- Publish events for: package created, status changed, package delivered, package cancelled,
  package damaged, package returned, location updated, manager action performed, complaint
  created, complaint updated.
- Azure Service Bus topics (created in Bicep): `packages`, `package-status`,
  `package-location`, `truck-location`, `truck-reroute`, `manager-actions`, `complaints`,
  `audit-log`.

### Phase 8: Live Updates with Azure Web PubSub and Local WebSocket Fallback

**Goal**: Frontend receives real-time updates without polling.

- Create `backend/app/realtime/` module:
  - `pubsub.py`: Azure Web PubSub client; publishes group messages when events are emitted.
  - `websocket.py`: FastAPI WebSocket endpoint at `/ws` for local development fallback.
  - `broadcaster.py`: `RealtimeBroadcaster` abstraction used by services; routes to
    PubSub or WebSocket based on config.
- Wire `RealtimeBroadcaster` into: package status changes, truck location, reroutes, manager
  actions, complaint changes.
- Implement `RealtimeService` in Angular:
  - Connects to Azure Web PubSub (production) or `/ws` WebSocket (local dev) based on env.
  - Emits typed observables for each event category.
  - Components subscribe to the observables they care about.
- Wire real-time updates into: `PackageListComponent` (status badge updates), `MapViewComponent`
  (truck position), `PackageDetailComponent` (history timeline), `EventStreamComponent`
  (all events chronologically).

### Phase 9: Demo Controls and Reset Scenarios

**Goal**: Trainers can reset state and trigger scripted scenarios live.

- Create `backend/app/services/demo_service.py`:
  - `reset()`: truncates all data tables in dependency order, re-runs seed script.
  - Pre-scripted scenarios, each a sequence of service calls that create a realistic story:
    - `delayed-delivery`: package in transit, delay recorded, truck rerouted.
    - `damaged-in-transit`: package marked damaged with reason.
    - `happy-customer`: package delivered on time, customer marked happy.
    - `manager-reroute`: Michael overrides truck assignment and approves reroute.
    - `complaint-and-return`: complaint created, return approved, terminal state reached.
- Expose `POST /demo/reset` and `POST /demo/scenarios/{scenarioName}` in
  `backend/app/routers/demo.py`.
- Implement `DemoControlsComponent` in Angular:
  - Reset button with confirmation dialog.
  - Scenario buttons with descriptive labels.
  - Visible only when Michael Scott is the active persona.

### Phase 10: Tests, OpenAPI Export, Documentation, Containers, and Bicep

**Goal**: A tested, documented, containerized, deployable baseline.

**Tests** (`backend/tests/`):
- `test_lifecycle.py`: every valid and invalid transition in VALID_TRANSITIONS.
- `test_permissions.py`: every persona against every operation; authorized and unauthorized.
- `test_manager_actions.py`: every manager action with manager and non-manager actors.
- `test_audit.py`: every service write produces a correctly structured audit entry.
- `test_events.py`: every meaningful event produces a correctly structured EventEnvelope.
- `test_seed.py`: reset produces correct employee count, package count, and statuses.
- `test_api_packages.py`: key endpoint smoke tests (create, get, advance, delay, history).

**OpenAPI export**: `scripts/export-openapi.sh` starts the backend, fetches `/openapi.json`,
and writes `openapi.yaml` to the repository root as a workshop artifact.

**Documentation** (`docs/`): all files listed in the Project Structure above.

**Containers**:
- `backend/Dockerfile`: multi-stage; builds Python env, copies app, runs with uvicorn.
- `frontend/Dockerfile`: multi-stage; builds Angular dist, serves with nginx.
- `docker-compose.yml`: all three services (sqlserver, backend, frontend) with correct
  environment variable wiring. A single `docker compose up` starts the full stack.

**Bicep** (`infra/`): provisions Azure SQL, Service Bus (with all 8 topics and subscriptions),
Web PubSub, Azure Maps, Container Apps environment, frontend and backend container apps,
managed identities for passwordless auth to SQL and Service Bus, and Key Vault for any
remaining secrets.

## Complexity Tracking

No constitution violations requiring justification. All design choices are the simplest
approach that satisfies the corresponding functional requirement.

The Azure service tier (Service Bus, Web PubSub, Azure Maps) adds surface area compared to
a minimal local-only stack, but each service maps directly to an enterprise pattern that
attendees need to observe and consume during the workshop. The InMemory and WebSocket
fallbacks ensure local development remains straightforward.
