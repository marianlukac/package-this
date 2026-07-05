# Research: Core Package Operations

**Phase**: 0 — Outline & Research
**Feature**: Core Package Operations
**Date**: 2026-06-19

## Decision Log

All major technical decisions for this feature were supplied explicitly in the plan prompt.
This document records each decision, its rationale, and the alternatives evaluated.

---

### D-001: Backend Language — Python 3.12

**Decision**: Python 3.12 with FastAPI.

**Rationale**: Python is the dominant language in the AI/ML workshop ecosystem. Attendees
who build agents later will almost certainly write Python. Using Python for the baseline
application ensures the workshop tech stack is consistent and attendees can read and
modify the backend without a language context switch.

**Alternatives considered**:
- Node.js/TypeScript: rejected — adds a second TypeScript runtime alongside the Angular
  frontend, which would confuse attendees about which TypeScript runtime they are in.
- Go: rejected — less familiar to the target audience; reduced ecosystem for AI/agent work.
- .NET: rejected — heavier setup; less natural for workshop persona.

---

### D-002: API Framework — FastAPI

**Decision**: FastAPI with automatic OpenAPI generation.

**Rationale**: FastAPI generates OpenAPI documentation from code, which is a first-class
workshop artifact. Pydantic-based schemas are readable, self-documenting, and familiar to
Python AI developers. The framework is simple enough that attendees can read a route handler
and understand what it does without framework expertise.

**Alternatives considered**:
- Django REST Framework: rejected — heavier; more magic; ORM conflicts with SQLModel.
- Flask: rejected — no native async; no built-in schema validation; manual OpenAPI.
- Litestar: rejected — less widespread; attendees less likely to have seen it.

---

### D-003: ORM and Models — SQLModel

**Decision**: SQLModel for database models (built on SQLAlchemy + Pydantic).

**Rationale**: SQLModel lets one class serve as both the SQLAlchemy table definition and
the Pydantic validation model. This reduces the amount of code attendees must read to
understand the data model, which aligns with Principle I (Workshop-First Clarity).

**Alternatives considered**:
- SQLAlchemy Core: rejected — more verbose; separate Pydantic schemas needed.
- Tortoise ORM: rejected — less ecosystem maturity; unfamiliar to most attendees.
- Prisma (Python): rejected — experimental; adds complexity.

---

### D-004: Database Migrations — Alembic

**Decision**: Alembic for schema migrations.

**Rationale**: Alembic is the industry-standard Python migration tool, directly integrated
with SQLAlchemy. Every enterprise Python project uses it. Workshop attendees see the
migration pattern as a learning outcome, not just a tool choice.

**Alternatives considered**:
- Yoyo Migrations: rejected — less known; not standard with SQLAlchemy.
- Manual SQL scripts: rejected — error-prone; not resettable reliably.

---

### D-005: Database — Azure SQL (trainer) + SQL Server in Docker (local)

**Decision**: Azure SQL for the shared trainer baseline; SQL Server 2022 in Docker for
local development.

**Rationale**: Azure SQL is SQL Server as a managed service — identical dialect, identical
ODBC driver, identical behavior. Using SQL Server in Docker locally means local code runs
against the exact same database engine as the trainer baseline. No dialect switching, no
"it works locally but not in Azure" problems.

**Alternatives considered**:
- PostgreSQL: evaluated — broad ecosystem, but different SQL dialect from Azure SQL; would
  require dialect-conditional code or attendees would face different behavior locally vs Azure.
- SQLite for local: rejected (explicitly) — different type system; different behavior for
  concurrent writes; inadequate for teaching enterprise database patterns.
- Azurite as SQL fallback: rejected (explicitly per plan prompt).

---

### D-006: Frontend Framework — Angular 18 with Tailwind CSS

**Decision**: Angular 18 (standalone components) with Tailwind CSS.

**Rationale**: Angular's structure is explicit and enterprise-standard. Component,
service, and routing concepts map to patterns attendees encounter in large organizations.
Tailwind provides utility classes that make WCAG-compliant styling visible in the template,
which is a teachable accessibility pattern. Angular CDK provides accessible component
primitives (focus trap, live announcer, overlay) without adding a heavy UI library.

**Alternatives considered**:
- React: rejected — less structured; more framework choices to explain; harder to enforce
  component separation as a teaching example.
- Vue 3: rejected — smaller enterprise footprint; fewer attendees familiar.
- Next.js: rejected — SSR complexity is unnecessary for a demo SPA; adds a deployment
  concern.

---

### D-007: Event Messaging — Azure Service Bus Topics

**Decision**: Azure Service Bus topics for the official baseline; InMemory publisher for
local development.

**Rationale**: Azure Service Bus is a first-class enterprise messaging service used in
production systems at scale. It maps directly to the Event-Driven Where It Matters principle
and is the service that workshop attendees will later subscribe to from their agents. The
8 domain topics are aligned with the functional spec's event categories and the future
MCP tools.

**Alternatives considered**:
- Azure Event Grid: evaluated — better for reactive event routing, but less granular
  subscription control for per-topic workshop exercises.
- RabbitMQ in Docker: evaluated — good local option, but adds a service attendees must
  install; does not map to Azure Service Bus for later workshop modules.
- Azure Event Hubs: rejected — optimized for high-throughput streaming; overkill for a
  workshop demo with dozens of events per session.

---

### D-008: Real-Time UI Updates — Azure Web PubSub (trainer) + WebSocket (local)

**Decision**: Azure Web PubSub for the trainer baseline; FastAPI native WebSocket endpoint
(`/ws`) for local development.

**Rationale**: Azure Web PubSub is the managed real-time service that scales to many
concurrent clients without server-side connection state. This is the pattern attendees
encounter in enterprise applications. The local WebSocket fallback requires zero additional
infrastructure and is a built-in FastAPI capability, keeping local dev simple.

**Alternatives considered**:
- Socket.IO: rejected — adds a Node.js dependency alongside Python; obscures the
  underlying WebSocket protocol.
- Server-Sent Events (SSE): evaluated — simpler, browser-native, unidirectional; sufficient
  for one-way server push but less illustrative of enterprise real-time patterns.
- Azure SignalR: evaluated — similar to Web PubSub; Web PubSub chosen for its direct
  WebSocket compatibility and simpler client SDK.

---

### D-009: Maps — Azure Maps

**Decision**: Azure Maps for routing and the delivery map view.

**Rationale**: Azure Maps is the enterprise Azure-native mapping service. It provides
route calculation via the Route API, which powers the truck simulation. The Azure Maps
JavaScript SDK integrates cleanly into Angular. Using fictional but geographically
plausible Scranton, PA coordinates keeps the theme grounded.

**Scranton reference coordinates** (fictional customers placed within ~20 miles of Scranton):
- Dunder Mifflin Office: 41.4090° N, 75.6624° W (Scranton center)
- DM Warehouse: 41.3980° N, 75.6750° W (south of office)
- Sample customer area: 41.40–41.45° N, 75.60–75.70° W

**Alternatives considered**:
- Google Maps: rejected — licensing complexity in a distributed workshop context.
- Mapbox: evaluated — good SDK; less enterprise Azure integration story.
- Leaflet with OpenStreetMap: evaluated — open source; good for general use; weaker
  integration story with Azure for the workshop's Azure-focused module.

---

### D-010: Infrastructure as Code — Bicep

**Decision**: Azure Bicep for all Azure infrastructure.

**Rationale**: Bicep is Microsoft's recommended IaC language for Azure, replacing ARM
templates. It is readable, supports Azure-native resources natively, and is the tool
attendees are most likely to encounter in enterprise Azure teams. The Bicep files serve
as a workshop artifact showing how the deployment is structured.

**Alternatives considered**:
- Terraform: evaluated — cloud-agnostic; strong community; but adds HashiCorp tooling
  that is not native to Azure and is a distraction from the Azure-focus of the workshop.
- ARM Templates: rejected — verbose; superseded by Bicep; harder for attendees to read.
- Azure Developer CLI (azd) templates: evaluated — convenient; may be used as a wrapper
  around the Bicep files in a future enhancement.

---

### D-011: Persona Validation Strategy — X-Persona-Id Header

**Decision**: Simple `X-Persona-Id` header carrying the employee slug (e.g., `michael-scott`).
FastAPI middleware resolves the employee from the database and enforces permissions server-side.

**Rationale**: Full production IAM (OAuth2, JWT, OIDC) would add significant setup
complexity that is not the focus of the Agentic AI workshop. The persona header is explicit,
visible in HTTP traces, and easy for attendees and agents to set. It demonstrates the
server-side enforcement pattern without the ceremony of a full auth system.

The middleware is named `PersonaMiddleware` and is documented as a simplified demo-auth
pattern, with a comment explaining the enterprise equivalent (JWT claim validation).

**Alternatives considered**:
- JWT tokens: evaluated — more realistic; adds token issuance, refresh, JWKS endpoint;
  distracts from workshop learning goals.
- HTTP Basic Auth: rejected — not persona-based; no natural mapping to the employee model.
- Session cookies: rejected — complicates agent consumption; agents cannot easily manage
  cookies.

---

### D-012: Truck Simulation Approach — Deterministic Tick-Based Engine

**Decision**: Background task ticking every N seconds (configurable). Each tick advances
active trucks along their routes by one waypoint step. Truck state persisted to the database.
Location events emitted at controlled intervals (not every tick).

**Rationale**: Deterministic simulation is testable and reproducible. Persisting state to
the database means the simulation survives a backend restart during a workshop. The
configurable tick interval lets trainers speed up or slow down the demo. Publishing
location events at a controlled interval (e.g., every 3 ticks) avoids flooding the event
stream with identical data, respecting Principle VII (Event-Driven Where It Matters).

**Alternatives considered**:
- Pure in-memory simulation: rejected — lost on restart; not persistent enough for
  a workshop baseline.
- Continuous streaming via WebSockets per truck: rejected — couples simulation to connection
  state; hard to scale to multiple viewer sessions.
- External simulation service: rejected — adds another deployment artifact; unnecessary
  complexity for a workshop context.

---

### D-013: Testing Strategy — pytest with Readable Test Names

**Decision**: pytest as the only test framework. Tests in flat files with descriptive
function names. No complex test factories or fixtures beyond what pytest provides natively.

**Rationale**: Workshop attendees must be able to read the tests and understand what they
verify. A test named `test_package_cannot_move_backward_in_lifecycle` communicates the
rule it enforces to a reader with no framework knowledge. Keeping tests simple maximizes
their value as documentation.

**Key test files and coverage targets**:

| File | What it tests |
|---|---|
| test_lifecycle.py | Every valid and invalid transition in VALID_TRANSITIONS |
| test_permissions.py | Every persona against every operation; authorized and rejected |
| test_manager_actions.py | All 7 manager actions; manager succeeds, non-manager rejected |
| test_audit.py | Every service write produces a correctly structured AuditLog entry |
| test_events.py | Every meaningful event produces a correctly structured EventEnvelope |
| test_seed.py | Reset produces expected counts and statuses |
| test_api_packages.py | Key endpoint smoke tests via FastAPI test client |

---

### D-014: Seed Data Design

**Decision**: Seed data designed to tell a story across the full package lifecycle.

**Employees** (all 12, with personas):

| Employee | Persona | Notes |
|---|---|---|
| Michael Scott | manager | Regional Manager; all manager actions |
| Dwight Schrute | sales | Assistant (to the) Regional Manager |
| Jim Halpert | sales | Senior salesperson |
| Pam Beesly | accounting | Office Administrator |
| Angela Martin | accounting | Head of Accounting |
| Kevin Malone | accounting | Accounting |
| Darryl Philbin | warehouse | Warehouse Foreman |
| Roy Anderson | warehouse | Warehouse |
| Ryan Howard | sales | Sales representative |
| Phyllis Vance | sales | Senior salesperson |
| Stanley Hudson | sales | Senior salesperson |
| Creed Bratton | warehouse | Quality Assurance |

**Seed packages** (spread across all lifecycle statuses):
- 2 packages in `order_created`
- 1 package in `backorder`
- 2 packages in `packaged`
- 1 package in `ready_for_shipping`
- 2 packages in `in_transit` (with active trucks)
- 2 packages in `delivered`
- 1 package in `cancelled`
- 1 package in `damaged`
- 1 package in `returned`

**Customers** (fictional Scranton-area businesses):
- Lackawanna County Schools, Scranton Business Park, Valley View Medical, Steamtown Mall,
  Scranton Times-Tribune, Electric City Fitness, Anthracite Industries, Scranton Prep,
  Cooper's Seafood House, Alfredo's Pizza Cafe
