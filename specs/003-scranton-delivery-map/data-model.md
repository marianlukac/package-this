# Data Model: Scranton Delivery Map and Truck Simulation

**Feature**: 003-scranton-delivery-map
**Date**: 2026-06-21

## Entity Relationship Summary

```
Truck ─── TruckRoute ─── RouteStop ─── Customer
                    └─── ViaPoint ─── MapLocation (food/donut)
MapLocation (warehouse/customer/food/donut) — static reference data
Package.truck_id → Truck (when assigned)
Package.current_lat/lng ← Truck.current_lat/lng (while in transit)
```

---

## Truck (extended)

Extends the existing `Truck` model from Feature 1 with simulation and routing fields.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| truck_id | String | PK, immutable | e.g., `DM-TRUCK-01` |
| truck_number | Integer | NOT NULL | 1, 2, 3 |
| name | String | NOT NULL | "The Dundie", "Pretzel Day", "Big Tuna" |
| status | Enum | NOT NULL | `at_warehouse` \| `loading` \| `ready` \| `on_route` \| `rerouted` \| `returning` \| `completed` \| `delayed` |
| current_lat | Float | nullable | GPS latitude; null when at warehouse and not dispatched |
| current_lng | Float | nullable | GPS longitude |
| delay_reason | String | nullable | Set on Kevin reroute or other delays |
| delay_duration_hours | Float | nullable | Estimated delay duration |
| delay_started_at | DateTime | nullable | When the delay was first recorded |
| current_route_id | String | FK → TruckRoute, nullable | Active route; null when at warehouse |
| current_stop_index | Integer | nullable | Index of the stop currently being served or traveling to |
| updated_at | DateTime | auto | Updated on every tick position change |

**Validation rules**:
- Status transitions: `at_warehouse` → `loading` → `ready` → `on_route` → [`rerouted` ↔ `on_route`] → `returning` → `completed` → `at_warehouse`
- `delayed` is a flag status that overlaps with `on_route` or `rerouted`
- `current_lat`/`current_lng` MUST be set whenever status is not `at_warehouse` or `completed`

---

## TruckRoute

One route per truck dispatch. A truck may have many historical routes; only one is active.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| route_id | String | PK | e.g., `ROUTE-20260621-001` |
| truck_id | String | FK → Truck, NOT NULL | Which truck runs this route |
| status | Enum | NOT NULL | `planned` \| `active` \| `returning` \| `completed` \| `cancelled` |
| geometry | Text (JSON) | NOT NULL | Array of `[lat, lng]` waypoints covering all stops |
| estimated_duration_minutes | Integer | NOT NULL | Calculated at route creation |
| current_waypoint_index | Integer | default 0 | Simulation engine advances this each tick |
| started_at | DateTime | nullable | Set when truck is dispatched |
| completed_at | DateTime | nullable | Set when truck returns to warehouse |
| created_at | DateTime | auto | |

---

## RouteStop

One row per customer stop in the route. Ordered by `stop_order`.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| stop_id | String | PK | |
| route_id | String | FK → TruckRoute, NOT NULL | |
| customer_id | String | FK → Customer, NOT NULL | |
| stop_order | Integer | NOT NULL | 1-based ordering of stops |
| estimated_arrival | DateTime | nullable | Calculated when route is created |
| arrived_at | DateTime | nullable | Set when truck reaches this stop |
| completed_at | DateTime | nullable | Set when all packages delivered at this stop |
| is_completed | Boolean | default False | |

---

## ViaPoint

Optional intermediate points inserted into an active route (Kevin reroutes, detours).

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| route_id | String | FK → TruckRoute, NOT NULL | |
| name | String | NOT NULL | e.g., "Dunkin' Jefferson Ave" |
| lat | Float | NOT NULL | |
| lng | Float | NOT NULL | |
| reason | String | NOT NULL | e.g., "Driver hungry — detour approved" |
| inserted_before_stop_order | Integer | NOT NULL | Inserted before this stop number |
| inserted_at | DateTime | auto | |

---

## MapLocation

Static reference data for named points on the Scranton map.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| name | String | NOT NULL, unique | e.g., "Dunkin' Jefferson Ave" |
| location_type | Enum | NOT NULL | `warehouse` \| `customer` \| `food` \| `donut` |
| lat | Float | NOT NULL | |
| lng | Float | NOT NULL | |
| description | String | nullable | Optional label shown in tooltip |

**Seed data**: 1 warehouse, 14 customers (references Customer records by coordinate),
3 food, 3 donut = 21 map location records total.

---

## Package (extended)

Adds truck assignment and live GPS tracking fields to the existing Package model.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| truck_id | String | FK → Truck, nullable | Assigned truck; null until assigned |
| current_lat | Float | nullable | Live position; tracks truck when in transit |
| current_lng | Float | nullable | Live position |

**Rules (enforced in service layer)**:
- `truck_id` can only be set when `status == ready_for_shipping`
- When `status in (in_transit, shipped)`: `current_lat/lng` = assigned truck's `current_lat/lng`
- When `status == delivered`: `current_lat/lng` = customer's GPS coordinate (frozen)
- When `status` is terminal (delivered/returned/damaged/cancelled): `truck_id` is cleared

---

## Domain Events (new for this feature)

| Event type | Topic | Payload key fields |
|---|---|---|
| `truck.dispatched` | truck-location | truck_id, route_id |
| `truck.location_updated` | truck-location | truck_id, lat, lng, stop_index |
| `truck.arrived_at_stop` | truck-location | truck_id, customer_id, stop_order |
| `truck.rerouted` | truck-reroute | truck_id, via_point_name, reason, delay_hours |
| `truck.returned` | truck-location | truck_id, route_id |
| `package.delivered` | package-status | package_id, customer_id, truck_id |
| `package.delayed` | package-status | package_id, truck_id, delay_reason |
