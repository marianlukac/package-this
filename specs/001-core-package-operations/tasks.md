---
description: "Task list for Core Package Operations — Dunder Mifflin Package Manager"
---

# Tasks: Core Package Operations

**Input**: Design documents from `specs/001-core-package-operations/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅ quickstart.md ✅

**Tests**: Included in Phase 10 as explicitly required by plan.md (not TDD — write after implementation).

**Organization**: Phases 1–2 establish shared infrastructure. Phases 3–8 correspond to user
stories in priority order (P1 → P2 → P3). Phase 9 delivers map, simulation, and real-time
features. Phase 10 completes tests, export, documentation, containers, and infrastructure.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1–US6); omitted for Setup, Foundational, and Polish phases
- Exact file paths are included in every task description

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Establish the monorepo skeleton that every subsequent phase builds on.

- [X] T001 Create monorepo directory structure: `frontend/`, `backend/`, `infra/`, `scripts/`, `docs/`, `.devcontainer/`, `.github/workflows/`
- [X] T002 [P] Write `docker-compose.yml` with three services: `sqlserver` (mcr.microsoft.com/mssql/server:2022-latest on port 1433), `backend` (port 8000), `frontend` (port 4200)
- [X] T003 [P] Write `.devcontainer/devcontainer.json` with features: Python 3.12, Node 20, Angular CLI, Azure CLI, Bicep CLI, mssql ODBC driver 18
- [X] T004 [P] Write `.github/workflows/ci.yml` with jobs: backend lint (ruff), backend tests (pytest), frontend lint (eslint)
- [X] T005 [P] Write root `README.md` covering project purpose, workshop role, quickstart (`docker compose up`), and links to `docs/`
- [X] T006 [P] Write `backend/.env.example` documenting all environment variables: `DATABASE_URL`, `EVENT_PUBLISHER`, `AZURE_SERVICE_BUS_CONNECTION_STRING`, `REALTIME_PUBLISHER`, `AZURE_WEB_PUBSUB_CONNECTION_STRING`, `AZURE_MAPS_KEY`, `SIMULATION_TICK_INTERVAL_SECONDS`, `SIMULATION_LOCATION_EVENT_EVERY_N_TICKS`, `APP_ENV`, `APP_PORT`
- [X] T007 [P] Write `frontend/.env.example` documenting: `API_BASE_URL`, `WS_URL`, `AZURE_MAPS_CLIENT_ID`
- [X] T008 [P] Write `backend/pyproject.toml` with project metadata, ruff config, and pytest config
- [X] T009 [P] Write `backend/requirements.txt` with pinned versions: fastapi, uvicorn, sqlmodel, alembic, pydantic-settings, pyodbc, azure-servicebus, azure-messaging-webpubsubservice, httpx, pytest, pytest-asyncio, ruff
- [X] T010 [P] Initialize Angular 18 project in `frontend/` using standalone components: `ng new dm-package-manager --standalone --routing --style css`
- [X] T011 [P] Install and configure Tailwind CSS in `frontend/`: `npm install tailwindcss`, write `frontend/tailwind.config.js`, update `frontend/src/styles.css` with Tailwind directives
- [X] T012 [P] Write `frontend/package.json` additions: `@azure/maps-control`, `@azure/web-pubsub-client`
- [X] T013 [P] Write `scripts/reset-seed.sh` (bash) that drops all data tables in dependency order and re-runs seed
- [X] T014 [P] Write `scripts/reset-seed.ps1` (PowerShell) equivalent of T013

**Checkpoint**: Monorepo skeleton complete — `docker compose up` starts three containers.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend infrastructure that every user story depends on.
Every service write operation requires audit logging, persona validation, and event publishing
to satisfy the constitution. These must be in place before any user story begins.

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete.

### Backend App Skeleton

- [X] T015 Create `backend/app/config.py` using `pydantic-settings`: `Settings` class loading all env vars from `backend/.env`; `get_settings()` dependency
- [X] T016 Create `backend/app/database.py`: SQLModel `engine` using `DATABASE_URL` from settings; `create_db_and_tables()` function; `get_session` FastAPI dependency yielding `Session`
- [X] T017 Create `backend/app/main.py`: FastAPI app instance; lifespan that calls `create_db_and_tables()` on startup; placeholder router mounts; OpenAPI title and tags config

### SQLModel Domain Models

- [X] T018 [P] Create `backend/app/models/employee.py`: `Employee` SQLModel table with fields from data-model.md; `Persona` string enum; `PersonaType` constants
- [X] T019 [P] Create `backend/app/models/customer.py`: `Customer` SQLModel table with all fields from data-model.md including `lat`, `lng`, `is_unhappy`
- [X] T020 [P] Create `backend/app/models/sale.py`: `Sale` SQLModel table with FK to `Employee` (salesperson) and `Customer`
- [X] T021 [P] Create `backend/app/models/invoice.py`: `Invoice` SQLModel table with FK to `Sale` (unique) and `Employee` (created_by)
- [X] T022 [P] Create `backend/app/models/package.py`: `Package` SQLModel table with all fields from data-model.md; `PackageStatus` string enum with all 10 statuses; `PackagePriority` string enum; `TERMINAL_STATUSES` constant set
- [X] T023 [P] Create `backend/app/models/package_line_item.py`: `PackageLineItem` SQLModel table; `ProductType` string enum (`paper_product`, `office_supply`)
- [X] T024 [P] Create `backend/app/models/package_history.py`: `PackageHistory` SQLModel table; `PackageHistoryEventType` string enum with all 15 event types; `EventSource` string enum (`ui`, `api`, `demo`, `agent`, `system`)
- [X] T025 [P] Create `backend/app/models/complaint.py`: `Complaint` SQLModel table; `ComplaintPackage` link table for many-to-many with `Package`; `ComplaintStatus` enum
- [X] T026 [P] Create `backend/app/models/truck.py`: `Truck` SQLModel table with simulation state fields; `TruckRoute` SQLModel table with JSON `stops` column; `TruckStatus` enum
- [X] T027 [P] Create `backend/app/models/audit_log.py`: `AuditLog` SQLModel table with all fields from data-model.md; JSON columns for `previous_value` and `new_value`
- [X] T028 Create `backend/app/models/__init__.py` exporting all models so Alembic can discover them

### Alembic Migrations and Seed Data

- [X] T029 Initialize Alembic in `backend/migrations/`: `alembic init migrations`; update `backend/migrations/env.py` to import all models from T028 and use the app engine
- [X] T030 Generate and apply initial Alembic migration: `alembic revision --autogenerate -m "initial_schema"`; verify all tables created correctly
- [X] T031 Create `backend/seed/seed_data.py`:
  - 12 employees with persona assignments from contracts/persona-model.md
  - 10 fictional Scranton-area customers with lat/lng from research.md
  - 3 trucks (DM-TRUCK-01, DM-TRUCK-02, DM-TRUCK-03) with warehouse coordinates
  - 5 sales each with auto-created invoices
  - 13 packages spread across all lifecycle statuses (2 order_created, 1 backorder, 2 packaged, 1 ready_for_shipping, 2 in_transit, 2 delivered, 1 cancelled, 1 damaged, 1 returned)
  - Package history entries for each non-order_created package reflecting its journey
  - 3 complaints (2 open, 1 closed) tied to existing sales

### Lifecycle Validator

- [X] T032 Create `backend/app/lifecycle/transitions.py`: `VALID_TRANSITIONS` dict mapping each `PackageStatus` to its list of valid next statuses; `TERMINAL_STATUSES` frozenset; `InvalidTransitionError` exception class carrying `current_status`, `target_status`, `message`
- [X] T033 Create `backend/app/lifecycle/validator.py`: `LifecycleValidator` class with `validate(current: str, target: str) -> None` that raises `InvalidTransitionError` on invalid move; `is_terminal(status: str) -> bool`

### Persona Middleware and Permissions

- [X] T034 Create `backend/app/persona/permissions.py`: `PERSONA_PERMISSIONS` dict mapping persona name to set of allowed operation strings (exact content from contracts/persona-model.md); `get_all_operations()` helper
- [X] T035 Create `backend/app/persona/middleware.py`: `PersonaMiddleware` Starlette middleware that reads `X-Persona-Id` header; resolves `Employee` from DB; sets `request.state.current_user`; returns 401 for missing header on non-GET requests; `require_permission(operation: str)` FastAPI dependency; `require_manager()` convenience dependency; 403 response includes current persona and required permission

### Audit Logger

- [X] T036 Create `backend/app/audit/logger.py`: `AuditLogger` service with `log(session, actor, source, entity_type, entity_id, action, previous_value, new_value, reason, correlation_id)` method; writes `AuditLog` record; immutable — no update or delete methods

### Event Publisher Abstraction

- [X] T037 Create `backend/app/events/envelope.py`: `EventEnvelope` Pydantic model with all 11 fields from contracts/event-envelope.md; `make_envelope(event_type, topic, actor, source, entity_type, entity_id, payload, summary, correlation_id)` factory function that auto-generates `eventId` and `occurredAt`
- [X] T038 Create `backend/app/events/publisher.py`: abstract `EventPublisher` base class with `async publish(event: EventEnvelope) -> None`; `get_publisher()` FastAPI dependency that returns correct impl based on `EVENT_PUBLISHER` setting
- [X] T039 Create `backend/app/events/inmemory.py`: `InMemoryEventPublisher(EventPublisher)` that logs event JSON to stdout with a clear prefix (`[EVENT]`); used as default for local development

### Angular Foundation

- [X] T040 Create `frontend/src/app/services/api.service.ts`: `ApiService` with `HttpClient`; base URL from environment; `getHeaders()` that injects `X-Persona-Id` from `PersonaService`; generic `get<T>`, `post<T>`, `patch<T>`, `delete<T>` methods
- [X] T041 Create `frontend/src/app/services/persona.service.ts`: `PersonaService` storing current employee selection in `BehaviorSubject<Employee | null>`; `setPersona(employee)` and `currentPersona$` observable
- [X] T042 Create `frontend/src/app/models/` with TypeScript interfaces matching all backend response shapes: `Employee`, `Customer`, `Sale`, `Invoice`, `Package`, `PackageLineItem`, `PackageHistory`, `Complaint`, `Truck`
- [X] T043 Create `frontend/src/app/app.routes.ts` with placeholder routes for all primary views; create `frontend/src/app/app.component.ts` with navigation shell and persona switcher slot
- [X] T044 Configure `frontend/src/environments/environment.ts` and `environment.prod.ts` with `apiBaseUrl`, `wsUrl`, `azureMapsClientId`

**Checkpoint**: Foundation ready — API skeleton, all models, migrations, seed data, lifecycle validator, persona middleware, audit logger, event publisher, and Angular foundation are complete.

---

## Phase 3: User Story 1 — Create a Sale with Invoice and Packages (Priority: P1) 🎯 MVP

**Goal**: A salesperson can create a sale (auto-invoiced), add packages to the sale, and add line items to each package. The frontend supports this complete create flow.

**Independent Test**: Log in as Jim Halpert (sales), create a sale for Lackawanna County Schools, add two packages each with two line items (mixing paper products and office supplies), and verify all records appear linked correctly via `GET /sales/{id}`.

### Backend — Schemas

- [X] T045 [P] [US1] Create `backend/app/schemas/sale.py`: `SaleCreate` (customer_id, notes), `SaleResponse` (all sale fields + nested invoice_id + package count)
- [X] T046 [P] [US1] Create `backend/app/schemas/invoice.py`: `InvoiceResponse` (all invoice fields + sale_id)
- [X] T047 [P] [US1] Create `backend/app/schemas/package.py`: `PackageCreate`, `PackageUpdate`, `PackageResponse` (all package fields + customer name + employee names), `PackageListItem` (summary for list views)
- [X] T048 [P] [US1] Create `backend/app/schemas/package_line_item.py`: `LineItemCreate`, `LineItemUpdate`, `LineItemResponse`
- [X] T049 [P] [US1] Create `backend/app/schemas/customer.py`: `CustomerResponse` (all customer fields)
- [X] T050 [P] [US1] Create `backend/app/schemas/employee.py`: `EmployeeResponse` (id, employee_id, name, persona)

### Backend — Services

- [X] T051 [US1] Create `backend/app/services/sale_service.py`: `SaleService` with `create_sale(session, actor, customer_id, notes, source)` that creates `Sale` + auto-creates one `Invoice` (with actor as created_by) + writes AuditLog entry + publishes `sale.created` event + returns `SaleResponse`
- [X] T052 [US1] Create `backend/app/services/package_service.py` (create operations): `create_package(session, actor, sale_id, destination, priority, contents_summary, fragile, source)` that creates `Package` in `order_created` status + creates `PackageHistory` entry (type: `package_created`) + writes AuditLog + publishes `package.created` event
- [X] T053 [US1] Add to `PackageService`: `add_line_item(session, actor, package_id, line_item_data, source)` that adds `PackageLineItem` + creates history entry (type: `line_item_added`) + writes AuditLog + publishes `package.line_item_added` event
- [X] T054 [US1] Add to `PackageService`: `update_line_item(session, actor, package_id, item_id, update_data, source)` + history entry (type: `line_item_changed`) + AuditLog
- [X] T055 [US1] Add to `PackageService`: `remove_line_item(session, actor, package_id, item_id, source)` that raises `LastLineItemError` if last item; otherwise removes + history + AuditLog
- [X] T056 [US1] Add to `PackageService`: `delete_package(session, actor, package_id, source)` that raises `PackageDeletionError` if status is not `order_created`; otherwise soft-deletes + AuditLog
- [X] T057 [US1] Add to `PackageService`: `update_fields(session, actor, package_id, update_data, source)` for editing non-lifecycle fields; raises error if terminal; creates history entry (type: `location_updated` or generic field update) + AuditLog
- [X] T058 [US1] Create `backend/app/services/customer_service.py`: `CustomerService` with `get_all(session)` and `get_by_id(session, customer_id)` (read-only)
- [X] T059 [US1] Create `backend/app/services/employee_service.py`: `EmployeeService` with `get_all(session)` and `get_by_id(session, employee_id)` (read-only)
- [X] T060 [US1] Create `backend/app/services/invoice_service.py`: `InvoiceService` with `get_by_id(session, invoice_id)` and `get_all(session)`

### Backend — Routers

- [X] T061 [US1] Create `backend/app/routers/sales.py`: `POST /sales` (require sales/manager), `GET /sales`, `GET /sales/{sale_id}`; mount in `main.py` with tag `Sales`
- [X] T062 [US1] Create `backend/app/routers/packages.py` (create/edit/delete): `POST /packages`, `PATCH /packages/{package_id}`, `DELETE /packages/{package_id}`; mount with tag `Packages`
- [X] T063 [US1] Add to packages router: `POST /packages/{package_id}/line-items`, `PUT /packages/{package_id}/line-items/{item_id}`, `DELETE /packages/{package_id}/line-items/{item_id}`
- [X] T064 [US1] Create `backend/app/routers/customers.py`: `GET /customers`, `GET /customers/{customer_id}`; mount with tag `Customers`
- [X] T065 [US1] Create `backend/app/routers/employees.py`: `GET /employees`, `GET /employees/{employee_id}`; mount with tag `Employees`
- [X] T066 [US1] Create `backend/app/routers/invoices.py`: `GET /invoices`, `GET /invoices/{invoice_id}`; mount with tag `Invoices`

### Angular — US1 Components

- [X] T067 [US1] Create `frontend/src/app/components/persona-switcher/persona-switcher.component.ts`: dropdown of all 12 employees loaded from `GET /employees`; on selection calls `PersonaService.setPersona()`; displays current persona name and role badge
- [X] T068 [US1] Create `frontend/src/app/components/sale-create/sale-create.component.ts`: form with customer dropdown (from `GET /customers`), notes field; on submit calls `POST /sales`; on success navigates to sale detail
- [X] T069 [US1] Create `frontend/src/app/components/package-create/package-create.component.ts`: form for adding a package to an existing sale; fields: destination, priority, contents summary, fragile toggle; calls `POST /packages`
- [X] T070 [US1] Create `frontend/src/app/components/line-item-manager/line-item-manager.component.ts`: displays and manages line items on a package; inline add (product name, category, quantity, unit, type, fragile), edit, and delete with last-item guard; calls line item endpoints

**Checkpoint**: US1 fully functional and testable. A salesperson can create a complete sale → invoice → packages → line items end-to-end.

---

## Phase 4: User Story 2 — View Package List and Package Detail with History (Priority: P1)

**Goal**: Any employee can see all packages with their statuses and navigate to a package detail page showing all fields and the complete history timeline.

**Independent Test**: Navigate to `/packages`, verify packages appear with status badges. Open a package that has been through several lifecycle stages and verify the history section shows all entries in reverse-chronological order with actor, timestamp, source, and changed values.

### Backend — Services

- [X] T071 [US2] Add to `PackageService`: `get_by_id(session, package_id) -> PackageResponse`; `get_all(session, filters) -> list[PackageListItem]` with optional status/priority/customer_id filters and pagination
- [X] T072 [US2] Add to `PackageService`: `get_history(session, package_id) -> list[PackageHistoryResponse]` returning all history in reverse-chronological order
- [X] T073 [US2] Create `backend/app/schemas/package_history.py`: `PackageHistoryResponse` matching the shape in contracts/api-endpoints.md
- [X] T074 [US2] Add to `SaleService`: `get_by_id(session, sale_id)` returning sale with nested invoice and package summaries; `get_all(session)` with pagination

### Backend — Routers

- [X] T075 [US2] Add to packages router: `GET /packages` (list with filters), `GET /packages/{package_id}` (full detail)
- [X] T076 [US2] Add to packages router: `GET /packages/{package_id}/history`
- [X] T077 [US2] Add to packages router: `GET /packages/at-risk` (delayed + has complaints + approaching expected delivery)
- [X] T078 [US2] Add to packages router: `GET /packages/delayed` (active delay_reason present)
- [X] T079 [US2] Add to sales router: `GET /sales/{sale_id}` with nested invoice and package list
- [X] T080 [US2] Create `backend/app/routers/events.py`: `GET /events` returning recent AuditLog entries; mount with tag `Events`

### Angular — US2 Components

- [X] T081 [US2] Create `frontend/src/app/components/status-cards/status-cards.component.ts`: displays count cards for each PackageStatus; fetches counts from `GET /packages` grouped by status; updates when real-time events arrive
- [X] T082 [US2] Create `frontend/src/app/components/dashboard/dashboard.component.ts`: page component hosting `StatusCardsComponent`; recent activity summary; quick links to package list and create sale
- [X] T083 [US2] Create `frontend/src/app/components/package-list/package-list.component.ts`: table showing `PackageListItem` fields (package_id, customer, status, priority, last_updated); status filter dropdown; sort by last_updated; pagination; row click navigates to detail
- [X] T084 [US2] Create `frontend/src/app/components/package-detail/package-detail.component.ts`: displays all `PackageResponse` fields; `LineItemManagerComponent` for viewing line items; history timeline section; action buttons section (initially empty — filled in later phases)
- [X] T085 [US2] Create `frontend/src/app/components/package-history/package-history.component.ts`: renders timeline of `PackageHistoryResponse` entries in reverse-chronological order; each entry shows event type badge, actor, timestamp, source chip, and previous/new values diff
- [X] T086 [US2] Update `frontend/src/app/app.routes.ts` with concrete routes: `/` → dashboard, `/packages` → package list, `/packages/:id` → package detail, `/sales/new` → sale create
- [X] T087 [US2] Wire `ApiService` for all US1+US2 GET calls: `getPackages(filters)`, `getPackage(id)`, `getPackageHistory(id)`, `getSales()`, `getSale(id)`, `getCustomers()`, `getEmployees()`
- [X] T088 [US2] Add empty state views to `PackageListComponent` (no packages match filter) and `PackageDetailComponent` (history empty for new package)
- [X] T089 [US2] Add accessible ARIA labels, keyboard navigation (table row Enter key, Escape to close dialogs), and visible focus rings to all US1+US2 components

**Checkpoint**: US1+US2 independently functional. Any employee can create sales, create packages with line items, and view all packages with full history.

---

## Phase 5: User Story 3 — Advance a Package Through Its Lifecycle (Priority: P2)

**Goal**: A warehouse employee can advance a package through valid lifecycle transitions and record delays. The system rejects invalid transitions and all changes are recorded in history with domain events emitted.

**Independent Test**: As Darryl Philbin (warehouse), advance a seed package step by step from `packaged` to `delivered`. Attempt a backward move and verify 409 response. Record a delay and verify status does not change.

### Backend

- [X] T090 [US3] Add to `PackageService`: `advance_status(session, actor, package_id, target_status, reason, source, correlation_id)` that: (1) if `current_status == order_created`, asserts `len(package.line_items) >= 1` and raises `MissingLineItemsError` (→ 409) before any other check; (2) dispatches permission check based on target_status — `cancelled` → assert `cancel_package`, `damaged` → assert `record_damage`, all other statuses → assert `advance_lifecycle` — raises 403 with current persona and required permission if denied; (3) calls `LifecycleValidator.validate(current_status, target_status)`, raising 409 on invalid transition; (4) updates package status; (5) creates `PackageHistory` entry (event_type: `status_changed`); (6) writes AuditLog; (7) publishes `package.status_changed` event on `package-status` topic
- [X] T091 [US3] Add to `PackageService`: `record_delay(session, actor, package_id, delay_reason, delay_duration_hours, source)` that sets delay fields on Package (replacing any existing delay); creates history entry (event_type: `delay_recorded`); writes AuditLog; publishes `package.delay_recorded` event
- [X] T092 [US3] Add to packages router: `POST /packages/{package_id}/status` with `StatusChangeRequest` body (status, reason, source, correlation_id); requires `X-Persona-Id` header (401 if absent via `PersonaMiddleware`) but NO single router-level `require_permission()` guard — permission dispatch is handled inside `PackageService.advance_status()` based on target_status (see T090); this allows sales to cancel, warehouse to damage, and warehouse/manager to advance without a single permission bottleneck
- [X] T093 [US3] Add to packages router: `POST /packages/{package_id}/delay` with `DelayRequest` body (delay_reason, delay_duration_hours, source); `require_permission("record_delay")`
- [X] T094 [US3] Create `backend/app/schemas/status_change.py`: `StatusChangeRequest`, `DelayRequest`; add `InvalidTransitionError` → 409 handler to `main.py`

### Angular

- [X] T095 [US3] Add lifecycle advancement buttons to `PackageDetailComponent`: button group showing valid next statuses for current package; only visible to warehouse and manager personas; each button triggers `POST /packages/{id}/status`; refreshes package after success
- [X] T096 [US3] Add delay recording dialog to `PackageDetailComponent`: modal with delay_reason text field and delay_duration_hours number field; submits to `POST /packages/{id}/delay`; shows current delay info if delay exists; only visible to warehouse and manager
- [X] T097 [US3] Handle 409 responses in Angular: display validation error message from `detail` field in a toast/alert component; do not navigate away

**Checkpoint**: US3 independently functional. Warehouse employees can advance packages through their lifecycle with full audit trail.

---

## Phase 6: User Story 4 — Record Operational Exceptions (Priority: P2)

**Goal**: Warehouse employees and managers can record terminal exceptions (damage, cancellation, return). Terminal packages are permanently locked from further lifecycle changes.

**Independent Test**: As Roy Anderson (warehouse), mark a seed in-transit package as damaged and verify: (1) status is `damaged`, (2) no further lifecycle actions are available, (3) history shows the damage event. As Michael, approve a return on a delivered package.

### Backend

- [X] T098 [US4] Add `damage` and `cancel` transitions to `VALID_TRANSITIONS` in `lifecycle/transitions.py`: map every non-terminal status → `cancelled` and every non-terminal status → `damaged`; verify `LifecycleValidator.validate()` already rejects these when the source status is terminal; permission enforcement for these transitions is handled inside `advance_status()` per the dispatch pattern established in T090 (no separate check needed here)
- [X] T099 [US4] Add `approve_return()` to `PackageService`: validates current status is `in_transit` or `delivered`; validates actor is manager (calls `require_manager()`); advances to `returned`; creates history entry (event_type: `returned`); publishes `package.returned` event; this is also the handler for the `approve_return` manager action

### Angular

- [X] T100 [US4] Add exception action buttons to `PackageDetailComponent`: "Mark Damaged" and "Cancel Package" buttons visible to warehouse + manager; "Approve Return" button visible to manager only; each opens a confirmation dialog with reason field; calls `POST /packages/{id}/status`
- [X] T101 [US4] Enforce terminal state UI: once a package is in a terminal status, all lifecycle action buttons are hidden; display a prominent terminal status badge; show the terminal reason from the most recent history entry

**Checkpoint**: US4 independently functional. All terminal exception paths work and are properly locked.

---

## Phase 7: User Story 5 — Manage Complaints (Priority: P2)

**Goal**: Any employee can create a complaint tied to a sale and associate it with packages. Complaints can be updated and closed. Package history reflects all complaint events.

**Independent Test**: As Pam Beesly (accounting), create a complaint on a sale and associate it with two packages. Update the complaint with new information. Close it. Verify each associated package's history shows the complaint events.

### Backend — Schemas and Services

- [X] T102 [P] [US5] Create `backend/app/schemas/complaint.py`: `ComplaintCreate` (sale_id, package_ids list, description, source), `ComplaintUpdate`, `ComplaintResponse` (all fields + linked packages list)
- [X] T103 [US5] Create `backend/app/services/complaint_service.py` with `ComplaintService`; implement `create_complaint(session, actor, sale_id, package_ids, description, source)`: creates `Complaint` + `ComplaintPackage` links + creates `PackageHistory` entry (type: `complaint_created`) on each linked package + writes AuditLog + publishes `complaint.created` event on `complaints` topic; add `MissingPackagesError` if `package_ids` references packages not belonging to the sale
- [X] T103a [US5] Add to `ComplaintService`: `update_complaint(session, actor, complaint_id, description, source)` that updates description + creates `PackageHistory` entry (type: `complaint_updated`) on each linked package + AuditLog + publishes `complaint.updated` event; raises `ComplaintClosedError` if complaint is already closed
- [X] T103b [US5] Add to `ComplaintService`: `close_complaint(session, actor, complaint_id, source)` that sets status to `closed` + creates `PackageHistory` entry (type: `complaint_updated`) on each linked package + AuditLog + publishes `complaint.closed` event; `get_by_id(session, complaint_id)`, `get_all(session, filters)`, `get_by_customer(session, customer_id)` (read-only, no side effects)

### Backend — Routers

- [X] T104 [US5] Create `backend/app/routers/complaints.py`: `POST /complaints`, `GET /complaints`, `GET /complaints/{complaint_id}`, `PATCH /complaints/{complaint_id}`, `POST /complaints/{complaint_id}/close`, `GET /customers/{customer_id}/complaints`; mount with tag `Complaints` and `Customers`
- [X] T105 [US5] Add complaint count and open complaint badge to `GET /packages/{package_id}` response schema

### Angular — US5 Components

- [X] T106 [US5] Create `frontend/src/app/components/complaint-list/complaint-list.component.ts`: displays complaints for a package or sale; shows status badge, description excerpt, package links; links to complaint detail
- [X] T107 [US5] Create `frontend/src/app/components/complaint-create/complaint-create.component.ts`: form with description field and package multi-select (packages from the same sale); submit calls `POST /complaints`; accessible multi-select with keyboard support
- [X] T108 [US5] Create `frontend/src/app/components/complaint-detail/complaint-detail.component.ts`: shows complaint detail, update form (inline), and close button; calls `PATCH /complaints/{id}` and `POST /complaints/{id}/close`
- [X] T109 [US5] Add `ComplaintListComponent` to `PackageDetailComponent`: section showing complaints linked to the package; includes a "Create Complaint" button available to all personas
- [X] T110 [US5] Wire `ApiService` for complaint endpoints: `getComplaints(filters)`, `getComplaint(id)`, `createComplaint(data)`, `updateComplaint(id, data)`, `closeComplaint(id)`, `getCustomerComplaints(customerId)`

**Checkpoint**: US5 independently functional. Complaints can be created, updated, and closed regardless of package lifecycle status.

---

## Phase 8: User Story 6 — Manager Actions and Permission Enforcement (Priority: P3)

**Goal**: Michael Scott can perform all 7 manager-only actions. Non-manager employees are rejected at the server side. All manager actions are recorded in package history. Permission enforcement is wired to all write routes.

**Independent Test**: As Michael Scott, perform each of the 7 manager actions and verify history entry is created. As Jim Halpert (sales), attempt each manager action and verify 403 response with descriptive message.

### Backend — Persona Enforcement Wire-Up

- [X] T111 [US6] Apply `require_permission()` dependency to all write routes in all existing routers: `POST /sales` → `create_sale`; `POST /packages` → `create_package`; `PATCH /packages/{id}` → `edit_package_fields`; `DELETE /packages/{id}` → `delete_package`; `POST /packages/{id}/status` → no router-level guard (service-level dispatch by target_status per T090 — see I1 fix); `POST /packages/{id}/delay` → `record_delay`; `POST/PATCH/POST /complaints/*` → no restriction (any persona)
- [X] T112 [US6] Add 403 and 401 error handlers to `backend/app/main.py` returning structured error response with `detail` field including current persona and required permission

### Backend — Manager Actions Service and Router

- [X] T113 [US6] Create `backend/app/services/manager_actions_service.py`: `ManagerActionsService` with one method per action; each method: validates actor has manager persona; executes business logic; creates `PackageHistory` entry (event_type: `manager_action_performed`) with action name, actor, timestamp, reason; writes AuditLog; publishes `manager.action_performed` event on `manager-actions` topic:
  - `approve_reroute(session, actor, package_id, reason, source)`
  - `override_priority(session, actor, package_id, new_priority, reason, source)`
  - `mark_customer_unhappy(session, actor, customer_id, reason, source)`
  - `approve_return(session, actor, package_id, reason, source)` — delegates to `PackageService.approve_return()`
  - `approve_expensive_delivery(session, actor, package_id, reason, source)`
  - `force_truck_reassignment(session, actor, package_id, new_truck_id, reason, source)`
  - `trigger_demo_scenario(session, actor, scenario_name, source)` — delegates to `DemoService`
- [X] T114 [US6] Create `backend/app/schemas/manager_action.py`: `ManagerActionRequest` (action, entity_type, entity_id, payload dict, reason, source, correlation_id); `ManagerActionResponse`
- [X] T115 [US6] Create `backend/app/routers/manager_actions.py`: `POST /manager-actions`; `require_manager()` dependency; dispatches to `ManagerActionsService`; mount with tag `ManagerActions`

### Angular — US6 Components

- [X] T116 [US6] Add manager action buttons to `PackageDetailComponent`: "Override Priority", "Approve Reroute", "Approve Return", "Approve Expensive Delivery", "Force Truck Reassignment"; each only rendered when `persona === 'manager'`; each opens a dialog with reason field
- [X] T117 [US6] Create `frontend/src/app/components/manager-action-dialog/manager-action-dialog.component.ts`: reusable modal for confirming and submitting any manager action; includes reason text field; calls `POST /manager-actions`; shows success toast or error message from 403 response
- [X] T118 [US6] Wire `ApiService.performManagerAction(request)` calling `POST /manager-actions`
- [X] T119 [US6] Add 403 error handling to `ApiService`: parse `detail` from response body and surface as a user-readable error toast (not just "Forbidden"); log persona and operation to console for workshop debugging visibility
- [X] T120 [US6] Add `mark-customer-unhappy` action to customer views (or accessible from package detail via the customer name link); visible to manager only

**Checkpoint**: US6 fully functional. All manager actions work. Non-managers are rejected server-side.

---

## Phase 9: Map, Simulation, Events, and Real-Time (Cross-Cutting)

**Purpose**: Azure Maps integration, deterministic truck simulation, Service Bus event publishing, and live UI updates. These are workshop showcase features that run on top of the complete core system.

### Truck and Route Services

- [X] T121 [P] Create `backend/app/services/truck_service.py`: `TruckService` with `get_all(session)`, `get_by_id(session, truck_id)`, `get_current_location(session, truck_id)`, `assign_to_package(session, actor, truck_id, package_id, source)`, `create_route(session, truck_id, stops)`, `complete_stop(session, truck_id, stop_index)`
- [X] T122 [P] Create `backend/app/services/route_service.py`: `RouteService` with `calculate_route(stops)` calling Azure Maps Route API; caches polyline in `TruckRoute.azure_maps_route`; falls back to straight-line interpolation if Maps key not configured

### Truck Simulation Engine

- [X] T123 Create `backend/app/simulation/engine.py`: `SimulationEngine` class; started as a background task in `main.py` lifespan; `tick()` method advances each active truck one step along its route; configurable interval from `SIMULATION_TICK_INTERVAL_SECONDS` setting
- [X] T124 Create `backend/app/simulation/tick.py`: `process_truck_tick(session, truck, publisher, realtime_broadcaster)` that: (1) advances `current_stop_index`; (2) updates `Truck.current_lat/lng` by interpolating toward next stop; (3) updates `Package.current_location` for packages assigned to this truck with `in_transit` status; (4) emits `truck-location` event every `SIMULATION_LOCATION_EVENT_EVERY_N_TICKS` ticks; (5) emits `package-location` event on same cadence; (6) emits `package.delivered` when truck completes a delivery stop and advances package to `delivered`; (7) emits `truck.returned_to_warehouse` when route is complete

### Azure Maps Frontend Integration

- [X] T125 Create `frontend/src/app/services/map.service.ts`: wraps Azure Maps JS SDK; initializes map on a given HTMLElement; `addMarker(lat, lng, icon, label)`, `updateMarkerPosition(id, lat, lng)`, `drawRoute(polyline)`, `clearRoute(id)`
- [X] T126 Create `frontend/src/app/components/map-view/map-view.component.ts`: hosts Azure Maps canvas; loads initial markers for DM office (41.4090, -75.6624), DM warehouse, all customers, all trucks; subscribes to `RealtimeService.truckLocation$` to update truck markers; shows active route polylines; themed marker icons (truck, building, donut, food) for Dunder Mifflin locations
- [X] T127 Create `frontend/src/app/components/truck-route-view/truck-route-view.component.ts`: sidebar showing selected truck's route stops, delivery status per stop, current ETA, driver name; updates on real-time events

### Truck Routers

- [X] T128 [P] Create `backend/app/routers/trucks.py`: `GET /trucks`, `GET /trucks/{truck_id}`, `GET /trucks/{truck_id}/current-location`, `GET /trucks/{truck_id}/current-route`; mount with tag `Trucks`
- [X] T129 [P] Create `backend/app/routers/routes.py`: `POST /trucks/{truck_id}/route` (create route); `GET /deliveries/active` (all in_transit packages with truck info); mount with tag `Routes`

### Service Bus Event Publisher

- [X] T130 Create `backend/app/events/service_bus.py`: `ServiceBusEventPublisher(EventPublisher)` using `azure-servicebus` SDK; reads connection string from settings; `publish(event)` sends to `event.topic` topic; handles `EVENT_PUBLISHER=service_bus` in `get_publisher()` factory

### Real-Time Broadcaster

- [X] T131 Create `backend/app/realtime/broadcaster.py`: `RealtimeBroadcaster` abstraction; `broadcast(event_type, data)` routes to Web PubSub or WebSocket based on `REALTIME_PUBLISHER` setting
- [X] T132 Create `backend/app/realtime/pubsub.py`: `WebPubSubBroadcaster` using `azure-messaging-webpubsubservice` SDK; sends to group `dm-packages` with event type as message type
- [X] T133 Create `backend/app/realtime/websocket.py`: FastAPI `WebSocket` endpoint at `GET /ws`; `WebSocketManager` maintaining set of active connections; `LocalWebSocketBroadcaster` broadcasting to all connected clients as JSON
- [X] T134 Mount WebSocket endpoint in `backend/app/main.py`; wire `RealtimeBroadcaster` into all service methods that publish events

### Angular Real-Time Service and Event Stream

- [X] T135 Create `frontend/src/app/services/realtime.service.ts`: connects to Web PubSub (production) or `WS_URL` WebSocket (local) based on `environment`; emits typed `Subject<T>` observables: `packageStatus$`, `truckLocation$`, `managerAction$`, `complaintUpdate$`, `generalEvent$`
- [X] T136 Create `frontend/src/app/components/event-stream/event-stream.component.ts`: scrolling feed of all `generalEvent$` events; each entry shows event type, summary, actor, timestamp, source chip; auto-scrolls to latest; optional pause button; max 100 entries retained
- [X] T137 Wire real-time updates into existing components: `PackageListComponent` updates status badge on `packageStatus$`; `StatusCardsComponent` updates counts; `PackageDetailComponent` appends new history entries on relevant events; `MapViewComponent` moves truck markers on `truckLocation$`

### MCP Summary Endpoints

- [X] T138 Add `GET /operational-summary` to packages router: returns packages-by-status counts, active_trucks, open_complaints, delayed_packages, at_risk_packages, as_of timestamp
- [X] T139 Add `GET /customers/{customer_id}/complaints` to customers router: delegates to `ComplaintService.get_by_customer()`

### Phase 9 Accessibility

- [X] T171 Apply ARIA labels, keyboard navigation, and focus management to all Phase 9 Angular components: `MapViewComponent` (`map-view.component.ts`) — ARIA landmarks, keyboard-accessible marker tooltips; `EventStreamComponent` (`event-stream.component.ts`) — ARIA live region (`aria-live="polite"`), keyboard pause/resume; `DemoControlsComponent` (`demo-controls.component.ts`) — button ARIA labels, confirmation dialog focus trap; consistent with the WCAG-compliant pattern established in T089

**Checkpoint**: Full-stack system with live map, truck simulation, Service Bus events, and real-time UI updates running end-to-end.

---

## Phase 10: Demo Controls, Tests, OpenAPI, Documentation, Containers, and Infrastructure

**Purpose**: Complete the workshop baseline with trainable demo scenarios, a tested core, exported API contract, full documentation, containerized deployment, and Azure Bicep infrastructure.

### Demo Service and Controls

- [X] T140 Create `backend/app/services/demo_service.py`: `DemoService` with:
  - `reset(session)`: truncates all data tables in FK-safe order, re-runs `seed_data.py`
  - `run_scenario(session, actor, scenario_name)`: dispatches to named scenario; each scenario is a sequence of service calls with a 0.5s delay between steps for visual effect; returns list of affected entity IDs
  - Scenarios: `delayed-delivery`, `damaged-in-transit`, `happy-customer`, `manager-reroute`, `complaint-and-return`
- [X] T141 Create `backend/app/routers/demo.py`: `POST /demo/reset` (`require_manager()`), `POST /demo/scenarios/{scenario_name}` (`require_manager()`); mount with tag `Demo`
- [X] T142 Create `frontend/src/app/components/demo-controls/demo-controls.component.ts`: panel visible only when persona is `manager`; "Reset Demo" button with confirmation dialog; scenario buttons ("Delayed Delivery", "Damaged In Transit", "Happy Customer", "Manager Reroute", "Complaint and Return"); each shows a loading state and success/failure result

### pytest Test Suite

Tests are NOT TDD — written after implementation to verify the core is correct before workshop delivery.

- [X] T143 [P] Create `backend/tests/conftest.py`: `TestClient` fixture using FastAPI test app; in-memory SQLite engine for tests; `seed_test_data()` fixture that creates minimal employees, customers, sale, packages in varied statuses
- [X] T144 [P] Create `backend/tests/test_lifecycle.py`: test every entry in `VALID_TRANSITIONS` is accepted; test every backward and skipped transition is rejected with `InvalidTransitionError`; test all 4 terminal statuses reject further transitions; test `is_terminal()` returns correct boolean for each status
- [X] T145 [P] Create `backend/tests/test_permissions.py`: for each operation in `PERSONA_PERMISSIONS`, test an authorized persona succeeds and all unauthorized personas receive 403; test missing `X-Persona-Id` header returns 401 on write operations
- [X] T146 [P] Create `backend/tests/test_manager_actions.py`: test each of the 7 manager actions succeeds with Michael Scott persona; test each action fails with 403 for all non-manager personas; test each action creates a `PackageHistory` entry of type `manager_action_performed`; test each action writes an `AuditLog` entry
- [X] T147 [P] Create `backend/tests/test_audit.py`: test that `SaleService.create_sale()`, `PackageService.create_package()`, `PackageService.advance_status()`, `PackageService.record_delay()`, `ComplaintService.create_complaint()`, `ComplaintService.close_complaint()` each produce an `AuditLog` entry with correct actor, entity_type, entity_id, and action; for every service write tested, also assert that a matching `PackageHistory` entry (same actor, event_type, and timestamp) was created — verifying the dual-write contract between AuditLog (system-wide) and PackageHistory (package-scoped)
- [X] T148 [P] Create `backend/tests/test_events.py`: test that each service method that should publish an event produces an `EventEnvelope` with correct eventType, topic, actor, source, entityId; use `InMemoryEventPublisher` and capture published events; test event envelope factory generates valid UUID eventId and ISO timestamp
- [X] T149 [P] Create `backend/tests/test_seed.py`: test that `seed_data.py` produces 12 employees (correct personas), 10 customers, 3 trucks, 5 sales, 13 packages (correct status distribution), 3 complaints; test that `DemoService.reset()` returns the system to this exact state
- [X] T150 [P] Create `backend/tests/test_api_packages.py`: smoke tests using `TestClient`; test `POST /packages` creates package in `order_created` status; test `POST /packages/{id}/status` advances status correctly; test invalid transition returns 409 with descriptive message; test `GET /packages/{id}/history` returns history in reverse-chronological order; test `GET /operational-summary` returns correct shape

### OpenAPI Export

- [X] T151 Write `scripts/export-openapi.sh`: starts backend with `uvicorn`, fetches `http://localhost:8000/openapi.json`, converts to YAML using `python -c "import yaml,json,sys; yaml.dump(json.load(sys.stdin), sys.stdout)"`, writes to `openapi.yaml` in repo root

### Documentation

- [X] T152 [P] Write `docs/architecture.md`: system diagram (text-based), component descriptions, data flow from sale creation to delivery, event flow diagram, persona model summary
- [X] T153 [P] Write `docs/local-setup.md`: full local setup instructions from a clean machine; references `quickstart.md` for common operations
- [X] T154 [P] Write `docs/azure-setup.md`: how to run `infra/main.bicep`; how to set backend env vars to point at shared Azure resources; how to deploy to Container Apps
- [X] T155 [P] Write `docs/persona-guide.md`: all 12 employees, their personas, what they can and cannot do, how to switch personas in the UI and via API header
- [X] T156 [P] Write `docs/seed-data.md`: describes all seeded entities (employees, customers, trucks, packages) so trainers know what state the system starts in
- [X] T157 [P] Write `docs/demo-scenarios.md`: step-by-step trainer script for each of the 5 demo scenarios; what to show attendees at each step
- [X] T158 [P] Write `docs/event-topics.md`: all 8 Service Bus topics, their event types, payload shapes, and example consumer code; mirrors contracts/event-envelope.md in trainer-friendly format
- [X] T159 [P] Write `docs/openapi-usage.md`: how to use `openapi.yaml` with tools like Postman, Bruno, and as MCP context; link to `/docs` Swagger UI
- [X] T160 [P] Write `docs/mcp-integration.md`: how future MCP servers will consume the API; which endpoints are MCP-friendly; how to set X-Persona-Id; event subscription patterns for agent-to-agent scenarios

### Containers

- [X] T161 Write `backend/Dockerfile`: multi-stage build; stage 1 installs Python deps; stage 2 copies app and runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`; runs migrations via `alembic upgrade head` as entrypoint step
- [X] T162 Write `frontend/Dockerfile`: multi-stage; stage 1 runs `ng build --configuration production`; stage 2 is nginx serving the dist folder; write `frontend/nginx.conf` with SPA fallback and gzip compression
- [X] T163 Update `docker-compose.yml` to final state: correct image references, volume mounts, env var injection from `.env` files, health checks for sqlserver and backend, depends_on ordering; verify `docker compose up` starts and seeds correctly

### Azure Bicep Infrastructure

- [X] T164 [P] Write `infra/modules/sql.bicep`: Azure SQL Server + database; configure firewall rules; output connection string reference
- [X] T165 [P] Write `infra/modules/service-bus.bicep`: Service Bus namespace (Standard tier); 8 topics (packages, package-status, package-location, truck-location, truck-reroute, manager-actions, complaints, audit-log); one subscription per topic for workshop agent consumers
- [X] T166 [P] Write `infra/modules/web-pubsub.bicep`: Azure Web PubSub instance; hub named `dm-packages`
- [X] T167 [P] Write `infra/modules/maps.bicep`: Azure Maps account (Gen2, S0 tier)
- [X] T168 [P] Write `infra/modules/container-apps.bicep`: Container Apps environment; backend container app (pulling from registry); frontend container app; environment variable references from Key Vault secrets
- [X] T169 [P] Write `infra/modules/key-vault.bicep`: Key Vault for storing SQL connection string, Service Bus connection string, Web PubSub connection string; managed identity access policies for backend container app
- [X] T170 Write `infra/main.bicep`: orchestrates all modules; outputs app URLs; write `infra/parameters/trainer.bicepparam` with trainer baseline parameter values

**Checkpoint**: All phases complete. Full system tested, documented, containerized, and deployable.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS all user story phases**
- **US1 (Phase 3)**: Depends on Foundational
- **US2 (Phase 4)**: Depends on Foundational; some tasks depend on US1 (ApiService)
- **US3 (Phase 5)**: Depends on Foundational; builds on US1+US2 backend
- **US4 (Phase 6)**: Depends on US3 (reuses status change endpoint)
- **US5 (Phase 7)**: Depends on Foundational; independent of US3/US4
- **US6 (Phase 8)**: Depends on Foundational; wire-up of all existing routes
- **Phase 9 (Map/Sim/Events)**: Depends on Foundational; can begin after US1 is complete
- **Phase 10 (Tests/Docs/Infra)**: Depends on all preceding phases

### User Story Dependencies

- **US1 (P1)**: Start after Foundational — no dependency on other stories
- **US2 (P1)**: Shares ApiService with US1; can proceed in parallel with US1 backend tasks
- **US3 (P2)**: Requires US1 backend complete (PackageService); Angular builds on US2 detail view
- **US4 (P2)**: Requires US3 (status change endpoint already exists)
- **US5 (P2)**: Requires US1 (sale and package references); independent of US3/US4
- **US6 (P3)**: Requires all US1–US5 routes to exist for permission wire-up
- **⚠️ US4 → US6 cross-phase dependency**: `approve_return` in T113 (`ManagerActionsService`) delegates to `PackageService.approve_return()` implemented in T099 (Phase 6/US4). Phase 8 T113 must not begin until T099 is merged and tested.

### Within Each Phase

- Backend schemas → services → routers (sequential)
- Angular service methods → component → template → accessibility (sequential)
- Parallel [P] tasks within a phase can run simultaneously

### Parallel Opportunities

- All Phase 1 tasks marked [P] can run simultaneously after T001
- Phase 2 SQLModel models (T018–T027) can all be written in parallel
- Phase 2 Alembic (T029) depends on T028 (models registered)
- Phase 10 test files (T143–T150) can all be written in parallel
- Phase 10 documentation files (T152–T160) can all be written in parallel
- Phase 10 Bicep modules (T164–T169) can all be written in parallel

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (**CRITICAL**)
3. Complete Phase 3: US1 — Create sale + packages + line items
4. Complete Phase 4: US2 — View packages + detail + history
5. **STOP and VALIDATE**: A salesperson can create a sale and view all packages with history
6. This MVP demonstrates the full audit trail and API-first patterns

### Incremental Delivery

1. MVP (US1+US2) → Working create and view flow
2. Add US3 → Package lifecycle advancement
3. Add US4 → Exception handling (damage, cancel, return)
4. Add US5 → Complaint management
5. Add US6 → Manager actions + permission enforcement
6. Add Phase 9 → Map, simulation, real-time events
7. Add Phase 10 → Tests, docs, containers, infrastructure

### Parallel Team Strategy

With multiple developers after Foundational is complete:
- Developer A: US1 (sale/package creation)
- Developer B: US2 (package list/detail views)
- Developer C: US5 (complaints — independent of US3/US4)
- Once US1+US2 done: Merge → add US3, US4, US6 in parallel

---

## Notes

- `[P]` = different files, no unresolved dependencies within the phase
- `[USN]` maps each task to its user story for traceability
- Every task includes a file path — sufficient context for an LLM to implement without additional input
- All write operations must: validate → write AuditLog → write PackageHistory (if package-related) → publish event → return response
- Terminal statuses: `delivered`, `cancelled`, `damaged`, `returned` — enforced by `LifecycleValidator` and `TERMINAL_STATUSES` constant
- Seed data reset command: `./scripts/reset-seed.sh` or `POST /demo/reset` (Michael persona)
- Avoid: vague task descriptions, tasks touching the same file from different stories, cross-story blocking dependencies
