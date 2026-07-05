# Workshop Requirements: Build Your Own Package Tracker

This document describes what attendees need to build as part of the workshop. The application you build does not have to use the same theme, technology stack, or domain as the trainer baseline. The goal is to produce a working system that agents can meaningfully operate against.

---

## What the Application Must Be

You are building a **business operations tracker** for a real-world workflow with multiple steps, multiple roles, and observable state changes. The domain is your choice: package delivery, support tickets, job applications, repair orders, loan approvals, event registrations, and so on. Pick something you can reason about naturally.

The application has three layers:

1. **A backend API** — handles data, business rules, and events.
2. **A frontend UI** — lets humans interact with the system through role-appropriate views.
3. **A data store** — persists state between requests.

---

## Functional Requirements

These are the capabilities the application must demonstrate. You do not need all edge cases; you need enough for agents to operate meaningfully.

### 1. Entities and Relationships

- The system tracks at least one **primary entity** (e.g., a package, ticket, order).
- Primary entities belong to a **parent record** (e.g., a sale, case, request).
- Primary entities have at least one **line-item or detail record** (e.g., line items, notes, attachments).
- There is at least one **secondary reference entity** (e.g., a customer, client, applicant).

### 2. Lifecycle Management

- Each primary entity moves through a defined set of **named statuses** (at least 4, e.g., created, in-progress, shipped, delivered).
- Status transitions follow **explicit rules**: not all transitions are allowed from all states.
- The system **rejects invalid transitions** with a clear error.
- Terminal states exist (e.g., delivered, cancelled, closed) from which no further transitions are allowed.

### 3. Role-Based Access

- The system defines at least **three distinct roles** (e.g., sales, warehouse, manager; or agent, supervisor, admin).
- Each role has a different set of permitted operations.
- The API enforces role permissions: requests from the wrong role are rejected.
- The UI reflects the active role: actions that are not permitted are hidden or disabled.

### 4. Operational Events

- Every significant state change publishes a **domain event** with a consistent schema.
- Events carry at minimum: an event type, the entity ID, who performed the action, and when it happened.
- Events are observable: they appear in a live feed, a log endpoint, or a stream the UI can consume.
- At least 6 distinct event types are defined and emitted.

### 5. Audit Trail

- Every status change and significant action is recorded in a **history log** attached to the entity.
- The log captures: what changed, who changed it, and when.
- History is queryable via the API.

### 6. Exception Handling

- The system supports recording **exceptions** against an entity (e.g., delays, damage, complaints, escalations).
- Exceptions have their own status or resolution flow.
- At least one exception type is defined and demonstrable.

### 7. A Privileged Role (Manager / Admin)

- One role has **elevated capabilities** that others do not: approvals, overrides, forced state changes, or resets.
- These actions are only callable by that role and are clearly labeled.
- The UI exposes a controls panel visible only to this role.

### 8. Seed Data and Reset

- The system ships with **realistic seed data**: enough records across multiple entities and statuses to tell a story.
- A reset endpoint or script restores the system to its initial seed state.
- Seed data covers all roles, all statuses, and at least one exception.

### 9. A Simulation or Automation (Stretch Goal)

- The system includes a background process that **moves entities automatically** (e.g., a truck that advances along a route, a timer that escalates overdue tickets).
- This produces continuous event output while the system runs, making it interesting for agent observation.

---

## Non-Functional Requirements

These requirements shape how the system is built, not just what it does.

### API Design

- The API follows REST conventions.
- All endpoints accept and return JSON.
- An **OpenAPI spec** is generated automatically and served at a known URL.
- The spec is accurate: request and response shapes are fully described with examples.

### Authentication and Identity

- There is no real authentication system. Instead, the caller declares who they are via a **request header** (e.g., `X-User-Id`, `X-Persona-Id`, or similar).
- The backend resolves the header to a role and enforces permissions accordingly.
- This makes the API easy to call from agents and CLI tools without an OAuth flow.

### Agent-Readiness

- The API is **fully operable by an agent** reading only the OpenAPI spec: every meaningful action is a documented endpoint, inputs are clearly described, and responses are predictable.
- Entity IDs used in path parameters are returned in list responses so an agent can discover them.
- Error responses include a human-readable message explaining what went wrong.

### Observability

- The system exposes a **real-time event feed** (WebSocket, Server-Sent Events, or a polling endpoint) that delivers events as they are published.
- Events use a **consistent envelope schema** across all event types.

### Local Development

- The full system runs locally with a single command (e.g., `docker compose up`).
- No cloud accounts are required to run the local version.
- The local stack includes a local substitute for any cloud service (e.g., an in-memory event bus instead of a managed queue).

---

## What "Done" Looks Like

At the end of the workshop, attendees should be able to demonstrate:

1. Open the UI and switch between at least three different role perspectives.
2. Create a new primary entity and walk it through at least three lifecycle stages.
3. Record an exception (delay, complaint, escalation) against an entity.
4. Perform a manager-only action (an approval, override, or reset).
5. Show the audit history for an entity.
6. Show the live event feed updating in real time as actions are taken.
7. Call the API directly with `curl` or an HTTP client as at least two different roles.
8. Show an agent reading the OpenAPI spec and performing a meaningful sequence of operations.

---

## Technology Choices

You are not required to use the same stack as the trainer baseline. The following table shows what the trainer baseline uses alongside viable alternatives.

| Layer | Trainer Baseline | Alternatives |
|---|---|---|
| Backend language | Python 3.12 | Node.js, Go, Java, C# |
| Backend framework | FastAPI | Express, Gin, Spring Boot, ASP.NET Core |
| ORM / DB access | SQLModel + Alembic | Prisma, GORM, EF Core, Drizzle |
| Database | SQL Server (Docker) | PostgreSQL, SQLite, MySQL |
| Frontend framework | Angular 18 | React, Vue, Svelte, plain HTML |
| Styling | Tailwind CSS | Bootstrap, Vanilla CSS |
| Containerization | Docker Compose | Podman Compose, bare-metal with scripts |
| Event bus (local) | In-memory | Redis Streams, local NATS, polling |
| Real-time (local) | WebSocket | SSE, long-polling |
