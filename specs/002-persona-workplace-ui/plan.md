# Implementation Plan: Persona-Based Workplace UI

**Branch**: `002-persona-workplace-ui` | **Date**: 2026-06-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002-persona-workplace-ui/spec.md`

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
specs/002-persona-workplace-ui/
├── plan.md              # This file
└── spec.md              # Feature specification
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
│   ├── schemas/
│   ├── services/
│   ├── routers/
│   ├── lifecycle/
│   ├── persona/
│   ├── events/
│   ├── audit/
│   └── simulation/
├── migrations/
├── tests/
├── seed/
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── .env.example

infra/
├── main.bicep
├── modules/
└── parameters/

scripts/
docs/
.devcontainer/
.github/
docker-compose.yml
README.md
```

## Implementation Phases

### Phase 1: Repository Structure and Development Environment

**Goal**: A working skeleton that every subsequent phase builds on.

- Create the full monorepo directory structure above.
- Write `docker-compose.yml`: services for `sqlserver`, `backend`, and `frontend`.
- Write `.devcontainer/devcontainer.json` with Python 3.12, Node 20, Angular CLI, Azure CLI,
  Bicep CLI, and the Azure SQL ODBC driver.
- Write `.github/workflows/ci.yml` with basic lint and test steps.
- Write root `README.md` covering project purpose, workshop role, local setup, and links to docs/.
- Write `.env.example` files for backend and frontend with all variable names documented.

### Phase 2: Backend Domain Model, Migrations, and Seed Data

**Goal**: A working database schema with seeded reference data.

- Create `backend/app/config.py` using `pydantic-settings`.
- Create `backend/app/database.py` with SQLModel engine setup and `get_session` dependency.
- Create all SQLModel table models in `backend/app/models/`.
- Set up Alembic and generate the initial migration.
- Create `backend/seed/seed_data.py` with all 12 employees, 10 customers, 3 trucks, seed packages, and complaints.
- Create `scripts/reset-seed.ps1` and `reset-seed.sh`.

### Phase 3: Core Package, Sale, Invoice, Customer, Employee, and Complaint APIs

**Goal**: Full CRUD and lifecycle APIs for all core entities.

- Create Pydantic schemas and service classes for all core entities.
- Create FastAPI routers and wire into `main.py`.
- Include MCP-friendly summary endpoints.

### Phase 4: Persona Validation and Manager Actions

**Goal**: Server-side persona enforcement and all manager actions.

- Create `PersonaMiddleware` reading `X-Persona-Id` header.
- Create `PERSONA_PERMISSIONS` dict and `require_permission()` / `require_manager()` dependencies.
- Create `ManagerActionsService` with all 7 manager actions.
- Expose `POST /manager-actions`.

### Phase 5: Frontend Shell and Core UI

**Goal**: A working Angular SPA with all primary views and persona switching.

- Initialize Angular 18 with standalone components and Tailwind CSS.
- Implement `PersonaSwitcherComponent` with all 12 employees, storing selection in `PersonaService`.
- Implement persona-aware `DashboardComponent`:
  - Sales view: emphasizes salesperson's packages, customer satisfaction, delays and complaints.
  - Accounting view: emphasizes invoices, financial exception packages.
  - Warehouse view: emphasizes ready-for-shipping and packaged status, truck state.
  - Manager view: serious metrics (packages at risk, delayed, backorders, complaints, damaged,
    returned, truck status, invoice summary, pending manager actions) and playful metrics
    (Kevin-related reroutes, most dramatic incident, Dwight escalation count, Pretzel Day
    truck status, regional manager attention score, customer unhappiness warning).
- Implement `PackageListComponent` with all required columns, search, filter, sort, and
  persona-specific default filters.
- Implement `PackageDetailComponent` with all sections and persona-aware action buttons.
- Implement `StatusCardsComponent` for all lifecycle stages; clicking navigates to filtered list.
- Implement `EventStreamComponent` with auto-scroll, pause, and 100-entry limit.
- Implement `DemoControlsComponent` visible only to Michael persona.
- Wire `ApiService` for all calls with `X-Persona-Id` header injection.
- All components: keyboard navigation, ARIA labels, empty states, loading states, error messages,
  success feedback, and WCAG 2.1 AA contrast compliance.

### Phase 6: Azure Maps Delivery Map and Truck Simulation

**Goal**: Live delivery map showing trucks, customers, and routes.

- Create `TruckService`, `RouteService`, and simulation engine as in Feature 1 plan.
- Implement `MapViewComponent` and `TruckRouteViewComponent`.

### Phase 7: Event Publisher, Audit Log, and Azure Service Bus Integration

**Goal**: All meaningful events published; every write operation audited.

- Create `EventEnvelope`, `EventPublisher` abstraction, `InMemoryEventPublisher`, `ServiceBusEventPublisher`.
- Create `AuditLogger` wired into all service methods.

### Phase 8: Live Updates with Azure Web PubSub and Local WebSocket Fallback

**Goal**: Frontend receives real-time updates without polling.

- Create `RealtimeBroadcaster` abstraction with Web PubSub and WebSocket implementations.
- Implement `RealtimeService` in Angular; wire into all subscribing components.

### Phase 9: Demo Controls and Reset Scenarios

**Goal**: Trainers can reset state and trigger scripted scenarios live.

- Create `DemoService` with `reset()` and named scenario methods.
- Expose `POST /demo/reset` and `POST /demo/scenarios/{scenarioName}`.
- Wire `DemoControlsComponent` to demo endpoints; visible only to Michael persona.

### Phase 10: Tests, OpenAPI Export, Documentation, Containers, and Bicep

**Goal**: A tested, documented, containerized, deployable baseline.

- pytest suite: lifecycle, permissions, manager actions, audit, events, seed, API.
- OpenAPI export script.
- Full documentation set in `docs/`.
- Backend and frontend Dockerfiles; final `docker-compose.yml`.
- Bicep for all Azure resources.

## Complexity Tracking

No constitution violations requiring justification. All design choices are the simplest
approach that satisfies the corresponding functional requirement.

The Azure service tier (Service Bus, Web PubSub, Azure Maps) adds surface area compared to
a minimal local-only stack, but each service maps directly to an enterprise pattern that
attendees need to observe and consume during the workshop. The InMemory and WebSocket
fallbacks ensure local development remains straightforward.
