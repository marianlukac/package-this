# Quickstart: Scranton Delivery Map and Truck Simulation

**Feature**: 003-scranton-delivery-map
**Date**: 2026-06-21

This guide covers the primary integration scenarios for the map and truck simulation feature.
Use these scenarios to validate the feature end-to-end after implementation.

---

## Scenario 1: Map Load — See All Scranton Markers

**Goal**: Verify all static markers render on load.

```
GET /map/markers
```

Expected response includes objects with `location_type` values of:
- `warehouse` (1 result — Dunder Mifflin HQ)
- `customer` (14 results)
- `food` (3 results)
- `donut` (3 results)

Open the map view in the browser. Confirm 21 markers are visible across Scranton.

---

## Scenario 2: Assign a Package to The Dundie

**Goal**: Verify package assignment is enforced on `ready_for_shipping` status.

```
# Set package to ready_for_shipping first (warehouse persona)
POST /packages/PKG-2024-001/status
X-Persona-Id: darryl-philbin
{ "status": "ready_for_shipping" }

# Assign to The Dundie
POST /trucks/DM-TRUCK-01/assign
X-Persona-Id: darryl-philbin
{ "package_id": "PKG-2024-001" }
```

Expected: 200 OK. Check `GET /trucks/DM-TRUCK-01` — package appears in assigned list.

Verify rejection with wrong status:
```
POST /trucks/DM-TRUCK-01/assign
X-Persona-Id: darryl-philbin
{ "package_id": "PKG-2024-010" }   # PKG in order_created status
```
Expected: 409 Conflict.

---

## Scenario 3: Dispatch The Dundie and Watch It Move

**Goal**: Verify the simulation moves the truck and updates positions.

```
POST /trucks/DM-TRUCK-01/dispatch
X-Persona-Id: darryl-philbin
```

Expected: 200 OK, truck status becomes `on_route`.

Poll truck location:
```
GET /trucks/DM-TRUCK-01/current-location
```

Poll 3–5 times at 2-second intervals — `lat` and `lng` values should change each time.

Check the package assigned to the truck:
```
GET /packages/PKG-2024-001
```

Confirm `current_lat` and `current_lng` match the truck's GPS coordinate.

---

## Scenario 4: Delivery at a Customer Stop

**Goal**: Verify delivery marks package delivered and freezes location at customer.

After dispatching The Dundie (Scenario 3), wait for the truck to reach its first customer stop.
The simulation will automatically call `record_delivery` when the truck arrives.

Check the package:
```
GET /packages/PKG-2024-001
```

When delivered:
- `status` → `delivered`
- `current_lat` → customer GPS lat
- `current_lng` → customer GPS lng
- `truck_id` → null (cleared)

Check package history:
```
GET /packages/PKG-2024-001/history
```

A `delivered` event entry should be present.

---

## Scenario 5: Kevin Hunger Reroute

**Goal**: Verify a reroute inserts a via-point and delays the truck.

With The Dundie dispatched and `on_route`:

```
POST /trucks/DM-TRUCK-01/reroute
X-Persona-Id: michael-scott
{
  "location_id": 4,          # ID of "Dunkin' Jefferson Ave" map location
  "reason": "Driver spotted fresh Krispy Kreme — diversion approved"
}
```

Expected: 200 OK.

Verify truck state:
```
GET /trucks/DM-TRUCK-01
```
- `status` → `rerouted`
- `delay_reason` → contains the reason string

Verify route via-point:
```
GET /trucks/DM-TRUCK-01/current-route
```
- `via_points` array contains an entry for the donut shop

Check an in-transit package:
```
GET /packages/PKG-2024-001/history
```
- A `delay_recorded` history entry for this package should be present

---

## Scenario 6: Full Route Completion

**Goal**: Verify truck returns to warehouse after all stops.

After The Dundie completes all customer stops (watch the event stream for `truck.arrived_at_stop`
events for each stop), poll:

```
GET /trucks/DM-TRUCK-01
```

- `status` → `returning` (while traveling back)
- Then `status` → `completed` or `at_warehouse`

```
GET /trucks/DM-TRUCK-01/current-route
```
- All `RouteStop.is_completed` → `true`
- `TruckRoute.completed_at` is set

---

## Scenario 7: Demo Reset Restores Truck State

**Goal**: Verify reset restores all trucks to baseline.

```
POST /demo/reset
X-Persona-Id: michael-scott
```

After reset:
```
GET /trucks
```
- All three trucks have `status: at_warehouse`
- `current_lat`/`current_lng` match warehouse coordinate
- No active route assigned

---

## Non-Manager Reroute Rejection

**Goal**: Verify persona permission enforcement.

```
POST /trucks/DM-TRUCK-01/reroute
X-Persona-Id: jim-halpert    # sales — not authorized
{ "location_id": 4, "reason": "test" }
```

Expected: 403 Forbidden.
