# Implementation Plan: Scranton Delivery Map and Truck Simulation

**Branch**: `003-scranton-delivery-map` | **Date**: 2026-06-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-scranton-delivery-map/spec.md`

## Summary

Implement the interactive Scranton delivery map and accelerated truck simulation for the Dunder
Mifflin Package Manager. The backend gains a deterministic simulation engine that moves three
named trucks through assigned route stops in accelerated demo time, records delivery events, and
supports Kevin hunger reroutes as via-point insertions. The frontend gains a full map view
rendering all markers, route lines, and moving truck positions with live updates via the existing
real-time channel.

All technical decisions inherit from Feature 1 (Core Package Operations). This feature extends
the existing backend simulation stub, completes the truck and route domain, and wires the map
view component that was scaffolded but not implemented in earlier features.

## Technical Context

**Language/Version**: Python 3.12 (backend) · TypeScript / Angular 18 (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Alembic, Pydantic-Settings (backend);
Angular, Tailwind CSS, Azure Maps JS SDK (frontend)
**Storage**: Azure SQL (trainer baseline) · SQL Server in Docker (local dev)
**Testing**: pytest with pytest-asyncio (backend)
**Target Platform**: Azure Container Apps (deployed) · Docker Compose (local dev)
**Project Type**: Full-stack web application — extending existing Feature 1 baseline
**Performance Goals**: Workshop demo quality. Simulation ticks at configurable rate (default:
one tick per second real time, each tick advances demo time by 5 minutes). Full route completes
in 5–10 minutes real time.
**Constraints**: Same as Feature 1. Simulation runs as a background asyncio task within the
FastAPI process. No separate worker process introduced.
**Scale/Scope**: 3 trucks, 14 customers, 3–12 stops per route. Seed data extended with food
and donut locations. Simulation state persisted in SQL so reset restores baseline.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. Workshop-First Clarity | ✅ | SimulationEngine is a plain class with a `tick()` method; TruckService methods are named for what they do |
| II. Enterprise-Translatable Design | ✅ | Route assignment, truck dispatch, delivery events, reroute audit — all map to real logistics patterns |
| III. Separation of Spec / Implementation | ✅ | This plan references spec.md; no new functional requirements added here |
| IV. API-First and Agent-Ready | ✅ | All reroute and dispatch operations exposed as standard REST endpoints; Kevin reroute callable by future agents |
| V. Auditability by Default | ✅ | Every truck location change, delivery, and reroute creates a package history and audit log entry |
| VI. Controlled State Changes | ✅ | Truck status transitions validated; package assignment validated against `ready_for_shipping` status |
| VII. Event-Driven Where It Matters | ✅ | truck-location, truck-reroute, delivery events emitted; location ticks throttled to avoid spam |
| VIII. Secure by Default | ✅ | Reroute requires authorized persona; truck dispatch requires warehouse or manager permission |
| IX. Accessible and Usable UI | ✅ | Map includes keyboard-accessible truck detail panel; all markers have ARIA labels |
| X. Demo Reliability | ✅ | Simulation reset restores all trucks to at_warehouse; POST /demo/reset covers trucks and routes |
| XI. Test the Core | ✅ | Tests for truck assignment validation, route calculation, reroute logic, delivery behavior, simulation tick |
| XII. No Hidden Workshop Dependencies | ✅ | Azure Maps key required for map rendering; key documented in .env.example with local fallback note |
| XIII. Theme Supports Learning | ✅ | Truck names (The Dundie, Pretzel Day, Big Tuna) are memorable; Kevin reroute illustrates real rerouting pattern |

**Gate result: PASS — proceed to Phase 0.**

### Spec Entity Design Decisions

Two entities named in `spec.md § Key Entities` are realized as implementation choices rather
than database tables:

- **SimulationState**: Realized as an `asyncio` background task in `backend/app/simulation/tick.py`
  with an in-memory `running: bool` flag. No database row; state does not survive process restart
  (intentional — demo reset via POST /demo/reset is the canonical way to restore state).
- **TruckDelay**: Realized as inline fields on the `Truck` model — `delay_reason`,
  `delay_duration_hours`, `delay_started_at`. A separate `TruckDelay` table would add a JOIN for
  every truck read with no benefit at this scale. The inline fields fully satisfy the spec's delay
  visibility requirement (FR-044, FR-051).

## Project Structure

### Documentation (this feature)

```text
specs/003-scranton-delivery-map/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api-trucks.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code Changes (extending Feature 1 structure)

```text
backend/
├── app/
│   ├── models/
│   │   ├── truck.py           # EXTEND: add route, stop index, delay, GPS fields
│   │   ├── truck_route.py     # NEW: TruckRoute, RouteStop, ViaPoint
│   │   └── map_location.py    # NEW: MapLocation (warehouse, customer, food, donut)
│   ├── schemas/
│   │   ├── truck.py           # EXTEND: add route detail, location, delay schemas
│   │   └── map.py             # NEW: map marker and route geometry schemas
│   ├── services/
│   │   ├── truck_service.py   # EXTEND: assign, dispatch, deliver, reroute operations
│   │   └── route_service.py   # NEW: route calculation, stop ordering, via-point insertion
│   ├── routers/
│   │   ├── trucks.py          # EXTEND: add dispatch, reroute, current-location endpoints
│   │   ├── routes.py          # EXTEND: add route detail and progress endpoints
│   │   └── map.py             # NEW: map markers endpoint for all named locations
│   └── simulation/
│       ├── engine.py          # EXTEND: implement full tick() logic for movement and delivery
│       └── tick.py            # EXTEND: wire background task startup and stop into FastAPI lifespan
├── seed/
│   └── seed_data.py           # EXTEND: add food locations, donut locations, truck routes to seed
└── tests/
    ├── test_truck_assignment.py  # NEW
    ├── test_truck_simulation.py  # NEW
    └── test_map_endpoints.py     # NEW

frontend/
└── src/
    └── app/
        ├── components/
        │   ├── map-view/
        │   │   └── map-view.component.ts   # IMPLEMENT: full map with markers, routes, truck movement
        │   └── truck-route-view/
        │       └── truck-route-view.component.ts  # IMPLEMENT: truck detail panel
        ├── services/
        │   ├── map.service.ts    # EXTEND: truck location, route geometry, reroute API calls
        │   └── truck.service.ts  # NEW: truck state management and simulation controls
        └── models/
            ├── truck.model.ts    # EXTEND: add route, stops, delay, GPS coordinate fields
            └── map.model.ts      # NEW: MapLocation, RouteGeometry, ViaPoint types
```

## Implementation Phases

### Phase 1: Truck Domain Extension (Backend Models and Schema)

**Goal**: All truck, route, and map location data structures exist in the database.

- Extend `backend/app/models/truck.py`: add `current_lat`, `current_lng`, `current_stop_index`,
  `delay_reason`, `delay_duration_hours`, `delay_started_at` fields; add all
  truck status enum values (`loading`, `ready`, `on_route`, `rerouted`, `returning`, `completed`,
  `delayed`).
- Create `backend/app/models/truck_route.py`: `TruckRoute` (route_id, truck_id, status, geometry
  as JSON, estimated_duration_minutes, started_at, completed_at); `RouteStop` (stop_id, route_id,
  customer_id, stop_order, estimated_arrival, arrived_at, completed); `ViaPoint` (id, route_id,
  name, lat, lng, reason, inserted_at).
- Create `backend/app/models/map_location.py`: `MapLocation` (id, name, location_type as enum:
  `warehouse`/`customer`/`food`/`donut`, lat, lng, description).
- Create Alembic migration for new tables and extended truck columns.
- Extend seed data: add 3 fast food locations, 3 donut shop locations (all with fictional Scranton
  GPS coordinates); seed all three trucks with names, initial GPS at warehouse coordinate.

### Phase 2: Route Service and Truck Assignment (Backend Services)

**Goal**: Routes can be calculated and packages can be assigned to trucks.

- Create `backend/app/services/route_service.py`:
  - `calculate_route(truck_id, customer_ids)` → builds a `TruckRoute` with ordered `RouteStop`
    entries; route geometry is a list of GPS waypoints stored as JSON; calculates estimated
    duration from stop count and assumed average speed.
  - `insert_via_point(route_id, lat, lng, name, reason)` → inserts a `ViaPoint` at the current
    stop position in the route geometry.
  - `get_route_detail(route_id)` → returns route with all stops and via-points.
- Extend `backend/app/services/truck_service.py`:
  - `assign_package(truck_id, package_id, actor, source)` → validates package is in
    `ready_for_shipping`; rejects if already assigned to another truck; records history entry.
  - `dispatch_truck(truck_id, actor, source)` → validates truck has ≥1 package; changes truck
    status to `on_route`; starts route; emits `truck.dispatched` event.
  - `record_delivery(truck_id, customer_id, actor, source)` → marks packages for that customer
    on that truck as delivered; sets package location to customer GPS; creates history entries;
    emits `package.delivered` event.
  - `kevin_reroute(truck_id, location_id, reason, actor, source)` → validates truck is on_route;
    inserts via-point; records delay; updates truck status to rerouted; creates package history
    entries for all in-transit packages; emits `truck.rerouted` and `package.delayed` events.
  - `reassign_package(package_id, new_truck_id, actor, source)` → validates package is
    `ready_for_shipping` and source truck has not departed; moves assignment.

### Phase 3: Truck and Map API Endpoints (Backend Routers)

**Goal**: All truck, route, and map data is accessible via REST endpoints.

- Extend `backend/app/routers/trucks.py`:
  - `GET /trucks` — list all trucks with status, GPS, current stop, next stop
  - `GET /trucks/{truck_id}` — truck detail with assigned packages and delay info
  - `GET /trucks/{truck_id}/current-location` — GPS coordinate only (polling-friendly)
  - `GET /trucks/{truck_id}/current-route` — full route with stops and via-points
  - `POST /trucks/{truck_id}/assign` — assign a package to this truck
  - `POST /trucks/{truck_id}/dispatch` — dispatch the truck
  - `POST /trucks/{truck_id}/reroute` — Kevin hunger reroute (requires authorized persona)
- Create `backend/app/routers/map.py`:
  - `GET /map/locations` — all named map locations (warehouse, customers, food, donut)
  - `GET /map/markers` — stable alias for `GET /map/locations`; identical response shape;
    exists as a semantically named endpoint for agents and MCP tools
- Extend `backend/app/routers/routes.py`:
  - `GET /routes/{route_id}` — route detail with geometry, stops, via-points, progress

### Phase 4: Simulation Engine (Backend)

**Goal**: Trucks move in accelerated time along their routes.

- Implement `backend/app/simulation/engine.py` `tick()` method:
  - For each truck with status `on_route` or `rerouted`: advance position along route geometry
    by one tick's worth of movement (configurable meters-per-tick or segment-per-tick).
  - When a truck reaches the next via-point: log the stop, resume movement.
  - When a truck reaches a customer stop: call `truck_service.record_delivery()` for that
    customer's packages; advance to next stop.
  - When a truck completes all stops: begin return segment; update status to `returning`.
  - When a truck completes return: update status to `completed` / `at_warehouse`.
  - Emit `truck.location_updated` event every N ticks (configurable, default: every 5 ticks)
    to avoid event spam.
- Implement `backend/app/simulation/tick.py`:
  - Start simulation as an `asyncio` background task during FastAPI lifespan startup.
  - Configurable tick interval (default: 1 second real time).
  - Simulation can be paused and resumed via a flag (for demo reset scenarios).
  - Extend `POST /demo/reset` to pause simulation, reset all trucks to seed state, resume.

### Phase 5: Map View Component (Frontend)

**Goal**: The Angular map view renders all Scranton markers and moving trucks.

- Implement `frontend/src/app/components/map-view/map-view.component.ts`:
  - Initialize Azure Maps with Scranton center coordinate and appropriate zoom level.
  - Fetch all map locations from `GET /map/markers` on load; render typed markers
    (warehouse: building icon, customer: person icon, food: burger icon, donut: 🍩 icon).
  - Fetch all trucks from `GET /trucks` on load; render truck markers with name labels.
  - Fetch active routes; render route geometry as polylines on the map.
  - Subscribe to real-time `truck.location_updated` events; update truck marker positions.
  - Subscribe to real-time `truck.rerouted` events; refresh route geometry.
  - Subscribe to real-time `package.delivered` events; update customer marker state.
  - On truck marker click: open `TruckRouteViewComponent` panel.
  - On customer marker click: show customer name and scheduled packages in a tooltip.
- Implement `frontend/src/app/components/truck-route-view/truck-route-view.component.ts`:
  - Truck name, status badge, current stop, next stop, delay information if present.
  - Ordered list of route stops with estimated arrival and completion status.
  - Package list for each stop.
  - "Kevin Reroute" button (visible only to authorized personas) that opens a food/donut
    selection panel and submits to `POST /trucks/{id}/reroute`.
- Extend `frontend/src/app/services/map.service.ts`:
  - `getMapMarkers()`, `getTrucks()`, `getTruckLocation(id)`, `getTruckRoute(id)`,
    `assignPackage(truckId, packageId)`, `dispatchTruck(truckId)`, `kevinReroute(truckId, payload)`.
- Create `frontend/src/app/models/truck.model.ts` and `map.model.ts` with full TypeScript types.

### Phase 6: Tests

**Goal**: Core truck simulation logic is covered by automated tests.

- `backend/tests/test_truck_assignment.py`:
  - Verify a package in `ready_for_shipping` can be assigned to a truck.
  - Verify a package in any other status cannot be assigned.
  - Verify a package cannot be assigned to two trucks simultaneously.
  - Verify package location tracks truck GPS coordinate when in transit.
  - Verify package location becomes customer location upon delivery.
- `backend/tests/test_truck_simulation.py`:
  - Verify `tick()` advances truck position along route geometry.
  - Verify delivery is recorded when truck reaches a customer stop.
  - Verify truck returns to warehouse after all stops.
  - Verify Kevin reroute inserts via-point and sets rerouted status.
  - Verify reroute is rejected for returning/completed trucks.
- `backend/tests/test_map_endpoints.py`:
  - Verify `GET /map/markers` returns warehouse, customer, food, and donut markers.
  - Verify `GET /trucks` returns all three trucks with correct names.
  - Verify `GET /trucks/{id}/current-location` returns GPS coordinate.
