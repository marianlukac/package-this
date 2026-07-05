# Architecture

## Overview

The Dunder Mifflin Package Manager is a monorepo with three runnable layers: a Python/FastAPI backend, an Angular 18 frontend, and Azure infrastructure provisioned via Bicep.

```
frontend/     Angular 18, Tailwind CSS, standalone components
backend/      Python 3.12, FastAPI, SQLModel, Alembic
infra/        Azure Bicep modules
scripts/      Dev utilities
docs/         Workshop documentation
```

## Backend

| Layer | Technology |
|---|---|
| HTTP API | FastAPI 0.115 |
| ORM / models | SQLModel 0.0.22 |
| Migrations | Alembic 1.14 |
| Config | pydantic-settings |
| Messaging | Azure Service Bus (prod) / InMemory (local) |
| Real-time | Azure Web PubSub (prod) / WebSocket at `/ws` (local) |
| Maps | Azure Maps |

### Key modules

- `app/lifecycle/` — VALID_TRANSITIONS dict, LifecycleValidator
- `app/persona/` — PersonaMiddleware, require_permission(), require_manager()
- `app/events/` — EventPublisher ABC, InMemoryEventPublisher, ServiceBusEventPublisher
- `app/realtime/` — RealtimeBroadcaster ABC, LocalWebSocketBroadcaster, WebPubSubBroadcaster
- `app/audit/` — AuditLogger (dual-write: AuditLog + PackageHistory)
- `app/simulation/` — SimulationEngine background task, process_truck_tick()
- `seed/` — Full seed dataset for demos

## Frontend

Angular 18 standalone components, lazy-loaded via app.routes.ts. Tailwind CSS for styling.

## Data flow

```
UI action → ApiService → FastAPI router → Service → DB write
                                                  → PackageHistory write (AuditLogger)
                                                  → AuditLog write (AuditLogger)
                                                  → EventPublisher.publish()
                                                  → RealtimeBroadcaster.broadcast()
```

## WebSocket

Local dev: FastAPI WebSocket endpoint at `/ws`. Frontend connects via RealtimeService. The simulation engine and service layer both call RealtimeBroadcaster which dispatches to ws_manager.broadcast() locally.

## Event topics

| Topic | Published when |
|---|---|
| `packages` | Package created, line item changes |
| `package-status` | Status changes, delay recorded |
| `package-location` | Location updated |
| `truck-location` | Truck position updates (simulation) |
| `truck-reroute` | Route changed |
| `manager-actions` | Any manager action performed |
| `complaints` | Complaint created/updated/closed |
| `audit-log` | (consumed externally; all writes go to AuditLog table) |
