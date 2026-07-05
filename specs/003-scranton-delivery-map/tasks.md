---
description: "Task list for Scranton Delivery Map and Truck Simulation — Dunder Mifflin Package Manager"
---

# Tasks: Scranton Delivery Map and Truck Simulation

**Input**: Design documents from `specs/003-scranton-delivery-map/`
**Prerequisites**: plan.md ✅ spec.md ✅ data-model.md ✅ contracts/ ✅ research.md ✅ quickstart.md ✅
**Baseline**: Features 1 and 2 fully implemented. All tasks below extend the existing application
with truck routing, map rendering, and delivery simulation.

**Tests**: Requested in plan.md Phase 6. Test tasks included in Polish phase.

**Organization**: Phase 1 extends the database layer. Phase 2 adds schemas and TypeScript types.
Phases 3–7 map to US1–US5 in priority order. Final phase covers tests and documentation.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Exact file paths included in every task description

---

## Phase 1: Setup (Database Layer Extension)

**Purpose**: Extend the existing database schema with all new tables and fields required by this
feature. These changes are blocking prerequisites for every user story. No application logic
depends on these tables until they are migrated and seeded.

- [X] T001 [P] Extend `backend/app/models/truck.py`: add fields `current_lat: Optional[float]`, `current_lng: Optional[float]`, `delay_reason: Optional[str]`, `delay_duration_hours: Optional[float]`, `delay_started_at: Optional[datetime]`, `current_route_id: Optional[str]`, `current_stop_index: Optional[int]`, `updated_at: datetime`; extend `TruckStatus` enum with `loading`, `ready`, `on_route`, `rerouted`, `returning`, `completed`, `delayed` values; add `current_route_id` as FK → `truck_route.route_id`
- [X] T002 [P] Create `backend/app/models/truck_route.py`: define `TruckRoute` (route_id PK, truck_id FK, status enum [`planned`/`active`/`returning`/`completed`/`cancelled`], geometry TEXT for JSON waypoints, estimated_duration_minutes, current_waypoint_index default 0, started_at nullable, completed_at nullable, created_at auto); define `RouteStop` (stop_id PK, route_id FK, customer_id FK, stop_order int, estimated_arrival nullable, arrived_at nullable, completed_at nullable, is_completed bool default False); define `ViaPoint` (id auto PK, route_id FK, name str, lat float, lng float, reason str, inserted_before_stop_order int, inserted_at auto)
- [X] T003 [P] Create `backend/app/models/map_location.py`: define `MapLocation` (id auto PK, name unique str, location_type enum [`warehouse`/`customer`/`food`/`donut`], lat float, lng float, description optional str); import in `backend/app/main.py` so SQLModel creates the table
- [X] T004 [P] Extend `backend/app/models/package.py`: add fields `truck_id: Optional[str]` as FK → `truck.truck_id`, `current_lat: Optional[float]`, `current_lng: Optional[float]`; these fields are null until a package is assigned to a truck
- [X] T005 Create Alembic migration in `backend/migrations/versions/`: generate migration for the new `truck_route`, `route_stop`, `via_point`, and `map_location` tables plus the new columns added to `truck` and `package`; ensure the migration is reversible (downgrade removes new tables and columns)
- [X] T006 Extend `backend/seed/seed_data.py`: (1) extend the three existing truck seed rows to include `current_lat=41.409`, `current_lng=-75.6624` (warehouse coordinate), `status=at_warehouse`; (2) add 21 `MapLocation` rows — 1 warehouse (Dunder Mifflin HQ, 41.409, -75.6624), 14 customers matching existing Customer coordinates, 3 food locations (McDonald's Airport Rd 41.394/-75.728, Wendy's Keyser Ave 41.418/-75.658, Burger King Cedar Ave 41.405/-75.678), 3 donut locations (Dunkin' Jefferson Ave 41.41/-75.659, Krispy Kreme Scranton 41.423/-75.666, Tim Hortons Moosic St 41.399/-75.664)

**Checkpoint**: Database schema is complete. Run `alembic upgrade head` and verify all tables exist.

---

## Phase 2: Foundational (Schemas, Services, TypeScript Types)

**Purpose**: Core shared infrastructure all user story phases depend on. Route calculation logic,
response schemas, and frontend type definitions must exist before any user story can be
implemented. T011 (RouteService) is the primary blocker.

**⚠️ CRITICAL**: All user story phases depend on T011 (RouteService) being complete.

- [X] T007 [P] Create `backend/app/schemas/map.py`: define `MapLocationResponse` (id, name, location_type, lat, lng, description)
- [X] T008 [P] Extend `backend/app/schemas/truck.py`: add `TruckListItem` (truck_id, truck_number, name, status, current_lat, current_lng, current_stop_index, delay_reason, delay_duration_hours, current_route_id, package_count); `TruckDetail` (all list fields plus `assigned_packages` list); `TruckCurrentLocation` (truck_id, lat, lng, status, updated_at); `TruckAssignRequest` (package_id); `TruckDispatchResponse` (truck_id, status, route_id); `TruckRerouteRequest` (location_id: int, reason: str); `TruckRerouteResponse` (truck_id, status, via_point dict, affected_packages list); `RouteDetailResponse` (route_id, truck_id, status, geometry, estimated_duration_minutes, current_waypoint_index, started_at, completed_at, stops list, via_points list); `RouteStopResponse` (stop_id, stop_order, customer_id, customer_name, estimated_arrival, arrived_at, is_completed); `ViaPointResponse` (id, name, lat, lng, reason, inserted_before_stop_order, inserted_at)
- [X] T009 [P] Create `frontend/src/app/models/truck.model.ts`: TypeScript interfaces `Truck` (truck_id, truck_number, name, status, current_lat, current_lng, current_stop_index, delay_reason, delay_duration_hours, current_route_id, package_count), `TruckDetail`, `TruckCurrentLocation`, `TruckRoute`, `RouteStop`, `ViaPoint`, `TruckAssignedPackage`; export `TruckStatus` as a union type of all status strings
- [X] T010 [P] Create `frontend/src/app/models/map.model.ts`: TypeScript interfaces `MapLocation` (id, name, location_type, lat, lng, description), `MapMarker` (same shape); export `LocationType` as `'warehouse' | 'customer' | 'food' | 'donut'`
- [X] T011 Create `backend/app/services/route_service.py`: implement `calculate_route(truck_id: str, customer_ids: list[str], session: Session) -> TruckRoute` — orders stops, generates geometry as list of interpolated [lat,lng] waypoints between each stop (15 waypoints per stop segment), calculates estimated_duration_minutes (8 min per stop as default), creates TruckRoute and RouteStop rows; implement `insert_via_point(route_id: str, map_location: MapLocation, reason: str, session: Session) -> ViaPoint` — inserts a ViaPoint record at the current stop position in the route's geometry JSON array; implement `get_route_detail(route_id: str, session: Session) -> TruckRoute | None`

**Checkpoint**: RouteService can calculate a route between stops and return geometry. Test manually:
`route_service.calculate_route("DM-TRUCK-01", ["CUST-001", "CUST-003"], session)`.

---

## Phase 3: User Story 1 — Scranton Map View (Priority: P1) 🎯 MVP

**Goal**: The delivery map view renders with all 21 Scranton markers (warehouse, 14 customers,
3 food, 3 donut) and the three delivery trucks. A trainer can open the map and immediately orient
attendees to the delivery area.

**Independent Test**: Open the frontend map view. Verify the Dunder Mifflin warehouse marker
is visible. Verify 14 customer markers appear. Verify 3 food and 3 donut markers appear. Verify
3 truck markers appear with name labels. All this works without any simulation running.

- [X] T012 [P] [US1] Create `backend/app/routers/map.py`: implement `GET /map/locations` (returns all MapLocation rows as list of MapLocationResponse); implement `GET /map/markers` (same data, alias for frontend convenience); add the router to `backend/app/main.py` with prefix `/map` and tag `Map`
- [X] T013 [P] [US1] Extend `frontend/src/app/services/map.service.ts`: add `getMapMarkers(): Observable<MapMarker[]>` calling `GET /map/markers`; add `getMapLocations(): Observable<MapLocation[]>` calling `GET /map/locations`; add `getTrucks(): Observable<Truck[]>` calling `GET /trucks`
- [X] T014 [US1] Implement `frontend/src/app/components/map-view/map-view.component.ts` — full map view: initialize Azure Maps SDK with Scranton center (41.41, -75.663) at zoom 13; call `mapService.getMapMarkers()` on init and render each location as a typed marker (warehouse: office icon or distinct color, customer: person/building icon, food: 🍔 emoji/icon, donut: 🍩 emoji/icon); call `mapService.getTrucks()` on init and render each truck as a labeled marker showing truck name; attach click handlers to truck markers (emit selected truck ID); attach click handlers to customer markers (emit selected customer ID); display a loading state while markers are fetching; show an error message if Azure Maps key is missing or map fails to load; **accessibility**: every marker must have an `aria-label` containing location name and type (e.g. "The Dundie — truck", "Vance Refrigeration — customer"); the map container must have `role="application"` and a visible focus ring; truck and customer click handlers must also be keyboard-triggerable (Enter/Space on focused marker)

**Checkpoint**: US1 complete. All 21 static location markers and 3 truck markers visible on map load.

---

## Phase 4: User Story 2 — Truck Assignment and Package Tracking (Priority: P1)

**Goal**: A warehouse user can assign a ready-for-shipping package to a truck and dispatch it.
While the truck is active, the package's location tracks the truck's GPS coordinate. When
delivered, the package location freezes at the customer address.

**Independent Test**: Assign PKG-2024-001 (ready_for_shipping) to DM-TRUCK-01 via
`POST /trucks/DM-TRUCK-01/assign`. Dispatch DM-TRUCK-01 via `POST /trucks/DM-TRUCK-01/dispatch`.
Verify GET /packages/PKG-2024-001 shows current_lat/lng matching truck. Verify rejection when
assigning a non-ready_for_shipping package. Verify rejection of dual assignment.

- [X] T015 [US2] Extend `backend/app/services/truck_service.py`: implement `assign_package(truck_id, package_id, actor, source, session)` — validates package status is `ready_for_shipping`, validates package not already assigned to a truck, sets package.truck_id = truck_id, creates PackageHistory entry; implement `reassign_package(package_id, new_truck_id, actor, source, session)` — validates same conditions, clears old assignment, sets new; implement `dispatch_truck(truck_id, actor, source, session)` — validates truck has ≥1 assigned package, validates truck status allows dispatch, calls `route_service.calculate_route()` with assigned packages' customer_ids, updates truck status to `on_route`, sets `started_at`, emits `truck.dispatched` event
- [X] T016 [US2] Extend `backend/app/routers/trucks.py`: add `GET /trucks` → list all trucks as `list[TruckListItem]`; add `GET /trucks/{truck_id}` → `TruckDetail` with assigned packages; add `GET /trucks/{truck_id}/current-location` → `TruckCurrentLocation`; add `POST /trucks/{truck_id}/assign` → call truck_service.assign_package(), require warehouse or manager persona; add `POST /trucks/{truck_id}/dispatch` → call truck_service.dispatch_truck(), require warehouse or manager persona; add `GET /routes/{route_id}` to `backend/app/routers/routes.py` → call route_service.get_route_detail()
- [X] T017 [P] [US2] Extend `frontend/src/app/services/map.service.ts`: add `getTruckLocation(truckId: string): Observable<TruckCurrentLocation>`, `assignPackage(truckId: string, packageId: string): Observable<any>`, `dispatchTruck(truckId: string): Observable<any>`, `getTruckRoute(truckId: string): Observable<TruckRoute>`; create `frontend/src/app/services/truck.service.ts` as a signal-based service holding `trucks = signal<Truck[]>([])`, `selectedTruck = signal<Truck | null>(null)`, methods `refreshTrucks()`, `selectTruck(id)`, `clearSelection()`
- [X] T018 [US2] Extend `frontend/src/app/components/map-view/map-view.component.ts`: fetch active route geometries for all on_route/rerouted trucks and draw polylines on the map; when a truck marker is selected, draw its route polyline prominently; subscribe to `RealtimeService` events for `truck.location_updated` and update the truck marker position on the map; on package detail view (if package has truck_id), show truck assignment with link to map view

**Checkpoint**: US2 complete. Package assignment API enforced, dispatch creates route, package
location tracks truck in real time when truck.location_updated events arrive.

---

## Phase 5: User Story 3 — Live Truck Movement Simulation (Priority: P2)

**Goal**: The simulation engine moves trucks along their routes in accelerated demo time.
Delivery events fire automatically when trucks arrive at customer stops. Trucks return to the
warehouse when all stops are complete.

**Independent Test**: Dispatch DM-TRUCK-01 with packages. Start the application. Observe
DM-TRUCK-01's GPS coordinate changing on GET /trucks/DM-TRUCK-01/current-location every
few seconds. Wait until the truck reaches its first customer stop — verify the package is
marked delivered and a history entry exists. Wait for all stops — verify truck status becomes
returning then completed.

- [X] T019 [US3] Implement `backend/app/services/truck_service.py` `record_delivery(truck_id, customer_id, actor, source, session)` method: query all packages where truck_id == truck_id and customer_id == customer_id and status is in_transit; for each package: advance status to `delivered`, set current_lat/lng = customer.lat/lng, set truck_id = null, create PackageHistory entry with event_type = `delivered`, emit `package.delivered` event via EventPublisher
- [X] T020 [US3] Implement full `backend/app/simulation/engine.py` `tick(session)` async method: for each truck with status `on_route` or `rerouted` (1) advance `current_waypoint_index` by 1 in `TruckRoute.geometry`; (2) update truck `current_lat/lng` to the new waypoint; (3) if the waypoint index crosses a RouteStop's geometry segment: mark RouteStop.arrived_at, call `record_delivery()` for that stop's customer, mark RouteStop.is_completed = True, advance `current_stop_index`; (4) if all RouteStops are completed: update truck status to `returning`, begin return-to-warehouse geometry segment; (5) if returning and reached final waypoint (warehouse): update truck status to `completed`, set route.completed_at; (6) emit `truck.location_updated` event every 5 ticks (use a counter per truck); update truck.updated_at on every tick
- [X] T021 [US3] Implement `backend/app/simulation/tick.py`: start an asyncio background task in the FastAPI `lifespan` context manager (startup); run `engine.tick(session)` on a configurable interval (env var `SIMULATION_TICK_SECONDS`, default `1`); expose a module-level `pause()` and `resume()` function so `POST /demo/reset` can stop the simulation, reset state, and restart it; extend the reset handler in `backend/app/main.py` or `backend/app/services/demo_service.py` to call `tick.pause()`, reset all trucks to `at_warehouse` status and warehouse GPS, delete active TruckRoutes, then call `tick.resume()`
- [X] T022 [US3] Extend `frontend/src/app/components/map-view/map-view.component.ts`: subscribe to `RealtimeService.events$` filtering for `package.delivered` events; when a delivered event arrives, refresh the package marker to the customer location and remove it from the in-transit truck's package list in the UI

**Checkpoint**: US3 complete. Dispatch a truck, watch it move on the map, see delivery events
in the event stream, verify truck returns to warehouse after all stops.

---

## Phase 6: User Story 4 — Kevin Hunger Reroute (Priority: P2)

**Goal**: Authorized users can insert a food or donut via-point into a truck's active route.
The route updates on the map, the truck is marked delayed, and affected packages get history
entries. The reroute endpoint is also the hook for future agentic automation.

**Independent Test**: With DM-TRUCK-01 on_route, call `POST /trucks/DM-TRUCK-01/reroute` as
michael-scott with a valid donut location_id. Verify truck status becomes rerouted, delay_reason
is set, affected packages have delay_recorded history entries, and truck.rerouted event fired.
Verify 403 for non-manager and 409 for returning/completed truck.

- [X] T023 [US4] Extend `backend/app/services/truck_service.py` with `kevin_reroute(truck_id, location_id, reason, actor, source, session)`: (1) fetch truck; validate status is `on_route` or `rerouted`; (2) fetch MapLocation by location_id; validate type is `food` or `donut`; (3) call `route_service.insert_via_point(route_id, map_location, reason, session)` to splice the location into route geometry before current next stop; (4) update truck: status = `rerouted`, delay_reason = reason, delay_started_at = now, delay_duration_hours = 0.5 (estimated); (5) query all packages on this truck with status `in_transit` or `shipped`; for each: create PackageHistory entry with event_type = `delay_recorded`, reason = reason; (6) emit `truck.rerouted` event and `package.delayed` event for each affected package; (7) return list of affected package_ids
- [X] T024 [US4] Extend `backend/app/routers/trucks.py`: add `POST /trucks/{truck_id}/reroute` endpoint that requires manager persona (`require_manager()`), reads `TruckRerouteRequest` body, calls `truck_service.kevin_reroute()`, returns `TruckRerouteResponse`; add `GET /trucks/{truck_id}/current-route` endpoint that calls `route_service.get_route_detail()` and returns `RouteDetailResponse`
- [X] T025 [US4] Create `frontend/src/app/components/truck-route-view/truck-route-view.component.ts`: standalone Angular component that accepts `@Input() truckId: string`; fetches truck detail from `GET /trucks/{id}` and route from `GET /trucks/{id}/current-route`; renders: truck name + status badge, current stop label, next stop label, delay info panel (shown when delay_reason is set), list of assigned packages; includes a "Kevin Reroute" button visible only when `persona.isManager()` — clicking opens an inline selector listing all `food` and `donut` map locations from `GET /map/markers`, a reason text input, and a confirm button that calls `mapService.kevinReroute(truckId, {location_id, reason})`; add `kevinReroute(truckId, payload)` method to `frontend/src/app/services/map.service.ts` calling `POST /trucks/{id}/reroute`; **accessibility**: the panel must be closeable with Escape key; the Kevin Reroute button must have `aria-label="Kevin Reroute — manager only"`; the food/donut selector must be keyboard-navigable with arrow keys; the panel must have `role="dialog"` and `aria-labelledby` pointing to the truck name heading
- [X] T026 [US4] Extend `frontend/src/app/components/map-view/map-view.component.ts`: wire truck marker click to open `TruckRouteViewComponent` as a side panel (slide-in panel or positioned overlay); subscribe to `RealtimeService.events$` filtering for `truck.rerouted` events — when received, re-fetch the truck's route via `getTruckRoute()` and redraw the route polyline on the map to include the via-point detour; add a via-point marker (donut/food icon) to the map for each ViaPoint in the refreshed route

**Checkpoint**: US4 complete. Kevin reroute works end-to-end: map shows detour, truck status
rerouted, packages have history, events emitted.

---

## Phase 7: User Story 5 — Route and Delivery Detail View (Priority: P3)

**Goal**: Clicking a truck on the map shows a detailed stop list with estimated arrivals and
per-stop package assignments. Clicking a customer shows which deliveries are scheduled for them.

**Independent Test**: Click The Dundie on the map. Verify the detail panel shows the full stop
list in order with estimated arrival times and completion status. Click one package in the panel.
Verify the package detail view opens. Click a customer marker. Verify a panel shows which
packages are scheduled for that customer across all active routes.

- [X] T027 [US5] Extend `frontend/src/app/components/truck-route-view/truck-route-view.component.ts`: extend the route display to show the full `RouteDetailResponse.stops` list in stop_order with estimated_arrival formatted as a relative time ("~12 min"), is_completed shown as a checkmark badge, arrived_at shown when present; for each stop, show the packages assigned to that customer with their current status; add via-points inline in the stop list (shown between the relevant stops with the food/donut icon and reason); clicking a package in the stop list navigates to `/packages/{package_id}` via Angular Router
- [X] T028 [US5] Extend `frontend/src/app/components/map-view/map-view.component.ts`: add customer marker click handler that opens an inline tooltip or small panel showing customer name and a list of packages currently scheduled for that customer (queried from `TruckService.trucks()` computed from assigned packages on active routes); the panel must close when the user clicks elsewhere on the map

**Checkpoint**: US5 complete. Full route detail visible in panel, package navigation works,
customer tooltip shows scheduled deliveries.

---

## Phase 8: Polish, Tests, and Documentation

**Purpose**: Automated tests covering core business rules and a documentation update for trainers.

- [X] T029 [P] Add pytest tests in `backend/tests/test_truck_assignment.py`: (1) verify assigning a package with status `ready_for_shipping` succeeds and package.truck_id is set; (2) verify assigning a package with any other status raises 409; (3) verify assigning a package already assigned to a different truck raises 409; (4) verify in-transit package current_lat/lng equals assigned truck current_lat/lng after a tick; (5) verify delivered package current_lat/lng equals customer lat/lng and truck_id is null after delivery
- [X] T030 [P] Add pytest tests in `backend/tests/test_truck_simulation.py`: (1) verify `engine.tick()` advances truck current_waypoint_index by 1; (2) verify delivery fires (package status = delivered) when truck waypoint crosses a RouteStop segment; (3) verify truck status becomes `returning` after all RouteStops are completed; (4) verify `truck_service.kevin_reroute()` inserts a ViaPoint and sets truck status to `rerouted`; (5) verify `kevin_reroute()` raises 409 when truck status is `returning` or `completed`; (6) verify `kevin_reroute()` raises 404 when location_id references a `customer` or `warehouse` location (not food/donut)
- [X] T031 [P] Add pytest tests in `backend/tests/test_map_endpoints.py`: (1) verify `GET /map/markers` returns at least one marker of each type: warehouse, customer, food, donut; (2) verify `GET /trucks` returns exactly 3 trucks with names "The Dundie", "Pretzel Day", "Big Tuna"; (3) verify `GET /trucks/{id}/current-location` returns lat and lng fields for a known truck_id; (4) verify `GET /trucks/{id}/reroute` returns 403 for a non-manager persona and 409 for a truck not on_route; **note**: SC-001 (5-second page load) and SC-004 (15-second reroute round-trip) are workshop-observed criteria; no automated latency assertion is required at this stage
- [X] T032 Update `docs/demo-scenarios.md`: add section "Delivery Map and Truck Simulation" — explain how to start a simulation (assign packages, dispatch trucks), how to watch truck movement on the map, and how to trigger the Kevin Hunger Reroute scenario including which persona is required; keep the existing scenario list above the new section

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately; T001–T004 can all run in parallel [P]
- **Foundational (Phase 2)**: Depends on T001–T005; T007–T010 can run in parallel; T011 depends on T002 and T003 — **BLOCKS all user story phases**
- **US1 (Phase 3)**: Depends on T011 (RouteService) and T007–T010; T012–T013 can run in parallel [P]; T014 depends on T013
- **US2 (Phase 4)**: Depends on T011; T017 can run in parallel [P]; T015 → T016 → T018 are sequential
- **US3 (Phase 5)**: Depends on US2 (T015–T018); T019–T021 are sequential; T022 can overlap T021 [P]
- **US4 (Phase 6)**: Depends on US2 (T015–T016); T023 → T024 → T025 → T026 are sequential
- **US5 (Phase 7)**: Depends on US4 (T025 must exist for extension); T027 → T028 are sequential
- **Polish (Phase 8)**: Depends on all preceding phases; T029–T031 can run in parallel [P]; T032 can run any time

### User Story Dependencies

- **US1 (P1)**: Requires Foundational complete; T012 and T013 are independent of each other [P]
- **US2 (P1)**: Requires Foundational; independent of US1 (different backend files)
- **US3 (P2)**: Requires US2 complete (uses truck dispatch and record_delivery)
- **US4 (P2)**: Requires US2 complete (uses truck status and route); independent of US3
- **US5 (P3)**: Requires US4 complete (extends TruckRouteViewComponent from US4)

### Parallel Opportunities

- Phase 1: T001, T002, T003, T004 all parallel
- Phase 2: T007, T008, T009, T010 all parallel; T011 sequential after T002/T003
- Phase 3: T012 and T013 parallel; T014 after T013
- Phase 4: T017 parallel with T015/T016
- Phase 8: T029, T030, T031 all parallel

---

## Implementation Strategy

### MVP First (US1 Only — Map View Without Simulation)

1. Complete Phase 1: Setup (T001–T006)
2. Complete Phase 2: Foundational (T007–T011)
3. Complete Phase 3: US1 (T012–T014)
4. **STOP and VALIDATE**: Open the map view, verify all 21 location markers and 3 truck markers
5. This MVP gives trainers a working map to show attendees before any simulation runs

### Incremental Delivery

1. Setup + Foundational → All models and types ready
2. US1 → Static map view (markers visible, trucks visible)
3. US2 → Truck assignment API + dynamic truck markers on map (no movement yet)
4. US3 → Simulation running — trucks move, deliveries fire automatically
5. US4 → Kevin reroute interactive demo moment
6. US5 → Route detail drill-down for trainer narration
7. Polish → Tests and documentation

---

## Notes

- `[P]` = different files, no unresolved dependencies within the phase
- `[USN]` maps each task to its user story for traceability
- Features 1 and 2 built the full application shell; all paths reference existing files or new files added alongside them
- The simulation tick (T020–T021) runs in the FastAPI process as a background asyncio task — no additional infrastructure required
- Route geometry is stored as JSON in TEXT column (research.md decision) — no spatial SQL queries needed
- Kevin reroute (T023–T024) uses the same endpoint interface that future agent demos will call — no special agent integration work required; the API contract is already agent-ready
- The `delay_duration_hours` for a Kevin reroute defaults to 0.5h (30 min) in the baseline; trainers can vary the reason text; this is a demo simplification documented in research.md
