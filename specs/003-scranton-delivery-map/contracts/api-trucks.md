# API Contract: Trucks, Routes, and Map

**Feature**: 003-scranton-delivery-map
**Date**: 2026-06-21

All endpoints require `X-Persona-Id` header. Permission requirements noted per endpoint.

---

## Trucks

### GET /trucks

List all trucks with current status and location.

**Permission**: Any authenticated persona.

**Response** `200 OK`:
```json
[
  {
    "truck_id": "DM-TRUCK-01",
    "truck_number": 1,
    "name": "The Dundie",
    "status": "on_route",
    "current_lat": 41.4078,
    "current_lng": -75.6612,
    "current_stop_index": 2,
    "delay_reason": null,
    "delay_duration_hours": null,
    "current_route_id": "ROUTE-20260621-001",
    "package_count": 3
  }
]
```

---

### GET /trucks/{truck_id}

Truck detail with assigned packages and delay info.

**Permission**: Any authenticated persona.

**Response** `200 OK`:
```json
{
  "truck_id": "DM-TRUCK-01",
  "truck_number": 1,
  "name": "The Dundie",
  "status": "on_route",
  "current_lat": 41.4078,
  "current_lng": -75.6612,
  "delay_reason": null,
  "delay_duration_hours": null,
  "delay_started_at": null,
  "current_route_id": "ROUTE-20260621-001",
  "current_stop_index": 2,
  "assigned_packages": [
    {
      "package_id": "PKG-2024-001",
      "customer_name": "Vance Refrigeration",
      "status": "in_transit",
      "stop_order": 1
    }
  ]
}
```

---

### GET /trucks/{truck_id}/current-location

GPS coordinate only. Lightweight polling endpoint.

**Permission**: Any authenticated persona.

**Response** `200 OK`:
```json
{
  "truck_id": "DM-TRUCK-01",
  "lat": 41.4078,
  "lng": -75.6612,
  "status": "on_route",
  "updated_at": "2026-06-21T14:23:45Z"
}
```

---

### GET /trucks/{truck_id}/current-route

Full route with stops, via-points, geometry, and progress.

**Permission**: Any authenticated persona.

**Response** `200 OK`:
```json
{
  "route_id": "ROUTE-20260621-001",
  "truck_id": "DM-TRUCK-01",
  "status": "active",
  "geometry": [[41.409, -75.662], [41.407, -75.661], [41.405, -75.665]],
  "estimated_duration_minutes": 42,
  "current_waypoint_index": 18,
  "started_at": "2026-06-21T14:00:00Z",
  "completed_at": null,
  "stops": [
    {
      "stop_id": "STOP-001",
      "stop_order": 1,
      "customer_id": "CUST-001",
      "customer_name": "Vance Refrigeration",
      "estimated_arrival": "2026-06-21T14:12:00Z",
      "arrived_at": "2026-06-21T14:11:47Z",
      "is_completed": true
    },
    {
      "stop_id": "STOP-002",
      "stop_order": 2,
      "customer_id": "CUST-003",
      "customer_name": "Cooper's Seafood House",
      "estimated_arrival": "2026-06-21T14:20:00Z",
      "arrived_at": null,
      "is_completed": false
    }
  ],
  "via_points": [
    {
      "id": 1,
      "name": "Dunkin' Jefferson Ave",
      "lat": 41.41,
      "lng": -75.659,
      "reason": "Driver spotted fresh Krispy Kreme — diversion approved",
      "inserted_before_stop_order": 2,
      "inserted_at": "2026-06-21T14:08:30Z"
    }
  ]
}
```

---

### POST /trucks/{truck_id}/assign

Assign a package to this truck.

**Permission**: warehouse, manager.

**Request**:
```json
{
  "package_id": "PKG-2024-001"
}
```

**Response** `200 OK`:
```json
{
  "truck_id": "DM-TRUCK-01",
  "package_id": "PKG-2024-001",
  "assigned": true
}
```

**Errors**:
- `409 Conflict` — package not in `ready_for_shipping` status
- `409 Conflict` — package already assigned to another truck
- `404 Not Found` — truck or package does not exist

---

### POST /trucks/{truck_id}/dispatch

Dispatch the truck to begin its route.

**Permission**: warehouse, manager.

**Request**: empty body or `{}`

**Response** `200 OK`:
```json
{
  "truck_id": "DM-TRUCK-01",
  "status": "on_route",
  "route_id": "ROUTE-20260621-001"
}
```

**Errors**:
- `409 Conflict` — truck has no packages assigned
- `409 Conflict` — truck is not in `ready` or `loading` status

---

### POST /trucks/{truck_id}/reroute

Trigger a Kevin hunger reroute — insert a food or donut via-point.

**Permission**: manager only (Michael Scott).

**Request**:
```json
{
  "location_id": 4,
  "reason": "Driver spotted fresh Krispy Kreme — diversion approved"
}
```

**Response** `200 OK`:
```json
{
  "truck_id": "DM-TRUCK-01",
  "status": "rerouted",
  "via_point": {
    "name": "Dunkin' Jefferson Ave",
    "lat": 41.41,
    "lng": -75.659,
    "reason": "Driver spotted fresh Krispy Kreme — diversion approved"
  },
  "affected_packages": ["PKG-2024-001", "PKG-2024-007"]
}
```

**Errors**:
- `403 Forbidden` — persona does not have reroute permission
- `409 Conflict` — truck is in `returning`, `completed`, or `at_warehouse` status
- `404 Not Found` — location_id does not reference a food or donut location

---

## Map Locations

### GET /map/locations

All named map locations.

**Permission**: Any authenticated persona.

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "name": "Dunder Mifflin HQ",
    "location_type": "warehouse",
    "lat": 41.409,
    "lng": -75.6624,
    "description": "Office and warehouse — all truck routes start and end here"
  },
  {
    "id": 2,
    "name": "Vance Refrigeration",
    "location_type": "customer",
    "lat": 41.4035,
    "lng": -75.6701,
    "description": null
  },
  {
    "id": 18,
    "name": "McDonald's Airport Rd",
    "location_type": "food",
    "lat": 41.394,
    "lng": -75.728,
    "description": "Available as Kevin reroute destination"
  }
]
```

### GET /map/markers

Consolidated marker data optimized for map rendering (same as locations but guaranteed to
include display-ready labels and type icons).

**Permission**: Any authenticated persona.

**Response**: Same shape as `GET /map/locations`.

---

## Routes

### GET /routes/{route_id}

Route detail (same shape as `GET /trucks/{id}/current-route` response).

**Permission**: Any authenticated persona.
