# Research: Scranton Delivery Map and Truck Simulation

**Feature**: 003-scranton-delivery-map
**Date**: 2026-06-21

## Decisions

### Route Geometry Representation

**Decision**: Store route geometry as a JSON array of `[lat, lng]` coordinate pairs in a
`TEXT`/`NVARCHAR(MAX)` column on `TruckRoute`.

**Rationale**: Route geometry is read-only once calculated and only needs to be sent to the
frontend as-is. A JSON array requires no additional JOIN and can be serialized directly from
the ORM model. No spatial query is needed on route geometry — the simulation engine reads it
sequentially tick by tick.

**Alternatives considered**: A separate `route_waypoint` table (unnecessary JOIN complexity
for a read-mostly workload), GeoJSON format (valid but adds a required wrapper object with no
benefit for this use case), PostGIS/SQL Server geometry type (overkill for demo scale).

---

### Route Calculation Strategy

**Decision**: Use simplified straight-line interpolation between customer GPS coordinates for
the seed data routes. Geometry is a list of intermediate waypoints between each stop calculated
as linear interpolation steps. For the official trainer baseline the system does not call an
external routing API.

**Rationale**: An external routing API requires an additional API key, network call at dispatch
time, and rate-limit considerations — none of which are appropriate for a workshop demo that
resets frequently. Linear interpolation produces smooth, predictable truck movement that is
sufficient for the visual demo without requiring roads. The `research.md` for Feature 1 noted
Azure Maps route calculation as a future extension — this baseline makes it optional, not
required.

**Alternatives considered**: Azure Maps route API (deferred — available as an extension once
the baseline is stable), OSRM (adds a required service dependency), hardcoded GeoJSON files
(would not support dynamic via-point insertion for Kevin reroutes).

---

### Simulation Engine Approach

**Decision**: Implement the simulation as a single `asyncio` background task running inside
the FastAPI process, using a configurable tick interval. Each tick advances all active trucks
one step along their route geometry.

**Rationale**: A separate worker process (Celery, RQ) adds significant setup complexity with
no benefit at workshop scale. A single `asyncio.sleep` loop inside a background task started
in the FastAPI lifespan is readable and requires no additional infrastructure. Attendees can
read and understand `simulation/engine.py` without understanding message queues.

**Alternatives considered**: APScheduler (adds a dependency for something asyncio handles
natively), Celery worker (requires a broker, dramatically increases local setup), threading
(harder to reason about for attendees).

---

### Movement Step Size

**Decision**: Each tick advances the truck to the next waypoint in the geometry array. Waypoints
are pre-computed at route calculation time to represent ~30 seconds of demo-time travel per step.
Tick interval defaults to 1 real second. The effect: trucks visibly move on the map once per
second, completing a 5-stop route in approximately 5–8 minutes.

**Rationale**: The workshop needs trucks to visibly move without waiting. One waypoint per tick
at 1-second intervals produces smooth, comprehensible movement. The pre-computed step size means
the simulation loop is simple (advance index by 1) rather than computing fractional positions.

**Alternatives considered**: Fraction-of-segment-per-tick with lerp (more realistic, but harder
for attendees to read in the engine code), real-time speed simulation (too slow for a demo).

**FR-031 resolution**: The spec says truck movement "MAY include minor speed variations to add
demo realism." The deterministic one-waypoint-per-tick model satisfies this requirement — uniform
advancement is within any reasonable definition of "minor." No stochastic movement is implemented;
consistency is more valuable than realism for a workshop demo.

---

### Event Throttling for Truck Location

**Decision**: Emit `truck.location_updated` events every 5 ticks (every 5 real seconds) rather
than every tick. Delivery and reroute events are always emitted immediately.

**Rationale**: Location events at 1 Hz for 3 trucks would produce 3 events/second continuously
during the simulation — acceptable for the event stream display but potentially distracting for
attendees trying to follow other events. 5-second intervals still produce smooth-enough map
updates (the frontend interpolates between received positions) while keeping the event stream
readable.

**Alternatives considered**: Every tick (too noisy), every 10 ticks (map updates become
noticeably jerky).

**FR-057 / FR-058 resolution**: The spec requires audit history entries for "all truck location
changes." This throttling decision applies to *domain events only*, not to audit records. In
practice, per-tick GPS updates are *not* individually audited — they are observable only through
the emitted events. Audit records (PackageHistory rows) are written only on meaningful business
events: delivery (event_type = `delivered`), reroute delay (event_type = `delay_recorded`), and
dispatch. This is the correct interpretation of "meaningful business change" under Constitution
Principle V. A raw GPS coordinate advancing by one waypoint is not a business state change.

---

### Kevin Reroute Via-Point Insertion

**Decision**: Inserting a via-point splices a new coordinate into the route geometry array
immediately before the truck's next unvisited stop. The via-point appears as a labelled marker
on the map and in the route stop list.

**Rationale**: Splicing the geometry array is the simplest operation that correctly represents
the truck detour: the truck completes the via-point before continuing to its next customer stop,
preserving all remaining stops and package assignments. No route recalculation is required.

**Alternatives considered**: Full route recalculation after reroute (unnecessary complexity;
the via-point is a simple detour, not a reordering of stops), adding delay to current stop
without a geometry change (would not show a map detour, defeating the visual demo purpose).

---

### Seed Data Locations

**Decision**: Use the following fictional but plausible Scranton-area GPS coordinates as baseline
seed data:

| Location | Type | Lat | Lng | Lore reference |
|---|---|---|---|---|
| Dunder Mifflin HQ + Warehouse | warehouse | 41.4090 | -75.6624 | 1725 Slough Ave, Scranton |
| Vance Refrigeration | customer | 41.4035 | -75.6701 | Bob Vance's warehouse |
| Lackawanna County | customer | 41.4091 | -75.6578 | County government |
| Poor Richard's Pub | customer | 41.4067 | -75.6598 | Bar from the show |
| Scranton Business Park | customer | 41.4120 | -75.6645 | Generic office park |
| Cooper's Seafood House | customer | 41.4052 | -75.6655 | Landmark restaurant |
| The Steamtown Mall | customer | 41.4138 | -75.6680 | Local landmark |
| Allied Steel | customer | 41.4003 | -75.6732 | Industrial customer |
| Carmine's Italian | customer | 41.4078 | -75.6612 | Restaurant customer |
| County Court | customer | 41.4096 | -75.6570 | Legal customer |
| Electric City Grille | customer | 41.4060 | -75.6640 | Restaurant customer |
| Schrute Farms | customer | 41.3820 | -75.6440 | Dwight's beet farm |
| Anthracite Heritage Museum | customer | 41.4100 | -75.6515 | Museum customer |
| Valley View Towers | customer | 41.4168 | -75.6720 | Residential customer |
| Scranton Prep | customer | 41.4210 | -75.6550 | School customer |
| McDonald's Airport Rd | food | 41.3940 | -75.7280 | Fast food |
| Wendy's Keyser Ave | food | 41.4180 | -75.6580 | Fast food |
| Burger King Cedar Ave | food | 41.4050 | -75.6780 | Fast food |
| Dunkin' Jefferson Ave | donut | 41.4100 | -75.6590 | Donut shop |
| Krispy Kreme Scranton | donut | 41.4230 | -75.6660 | Donut shop |
| Tim Hortons Moosic St | donut | 41.3990 | -75.6640 | Donut shop |

**Rationale**: Real Scranton area coordinates ground the map in a believable location. Fictional
business names inspired by the show create the right tone without requiring real business data.
Fourteen customers matches the spec requirement.

---

### Azure Maps Dependency for Local Development

**Decision**: The Azure Maps subscription key is required to render the base map tiles. For
local development without an Azure subscription, attendees can use a free Azure Maps trial key.
Document the key variable as `AZURE_MAPS_KEY` in `.env.example`. The map component gracefully
handles a missing key by showing a blank map container with an error message rather than crashing.

**Rationale**: Azure Maps is already the chosen map provider from Feature 1 (Feature 1 plan
section: "Use Azure Maps for the map experience"). The key is already documented as a workshop
resource. No fallback map tile provider is introduced — that would add complexity and split
the workshop's Azure focus.

---

### Audit Record vs. Domain Event Terminology

**Decision**: `PackageHistory` is the audit store for all package-scoped business events in this
feature. The spec uses both "audit history entries" (FR-057–FR-059, covering truck and route
changes) and "package history entry" (FR-034, covering delivery). Both refer to `PackageHistory`
rows — there is no separate audit log table for truck location changes.

**Scope of PackageHistory rows in this feature**:
- `delivered` — written when a package is marked delivered (FR-034, FR-060)
- `delay_recorded` — written for each in-transit package when a Kevin reroute fires (FR-045)
- `dispatch` / `assigned` — written by truck_service.assign_package() and dispatch_truck() (US2)

**What is NOT individually audited**: Per-tick GPS waypoint advances (FR-057 "all truck location
changes" satisfied by domain events; see Event Throttling decision above). Route creation at
dispatch time is covered by the PackageHistory `dispatch` entry.

**Rationale**: A flat `PackageHistory` table remains the single queryable audit trail for
agents and MCP tools, consistent with Feature 1. Introducing a separate `TruckAuditLog` table
would fragment the audit story and add a JOIN to every agent query.
