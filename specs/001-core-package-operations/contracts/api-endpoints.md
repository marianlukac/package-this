# API Contracts: Core Package Operations

**Date**: 2026-06-19
**Base URL**: `http://localhost:8000` (local) · `https://api.<trainer-domain>` (Azure)
**Auth header**: `X-Persona-Id: <employee-slug>` (required on all write operations)
**OpenAPI**: `GET /openapi.json` · exported as `openapi.yaml` in repo root

All responses use `application/json`. All timestamps are ISO 8601 UTC.

---

## Tag: Packages

### GET /packages
List packages, sorted by last updated descending.

**Query params**: `status`, `priority`, `customer_id`, `limit` (default 50), `offset`

**Response 200**:
```json
{
  "items": [
    {
      "package_id": "PKG-2024-001",
      "sale_id": "SALE-2024-001",
      "invoice_id": "INV-2024-001",
      "customer": { "customer_id": "lackawanna-county-schools", "name": "Lackawanna County Schools" },
      "salesperson": { "employee_id": "jim-halpert", "name": "Jim Halpert" },
      "status": "in_transit",
      "priority": "standard",
      "fragile": false,
      "contents_summary": "Case paper (10 reams), sticky notes (5 packs)",
      "current_location": "41.4012,-75.6580",
      "destination": "123 Main St, Scranton PA",
      "truck_id": "DM-TRUCK-01",
      "expected_delivery": "2026-06-19T16:00:00Z",
      "delay_reason": null,
      "created_at": "2026-06-19T09:00:00Z",
      "updated_at": "2026-06-19T14:30:00Z"
    }
  ],
  "total": 12,
  "limit": 50,
  "offset": 0
}
```

---

### GET /packages/{package_id}
Get a single package with all fields.

**Response 200**: Full package object (same shape as list item).
**Response 404**: `{ "detail": "Package not found" }`

---

### POST /packages
Create a package linked to an existing sale.
**Persona required**: sales, manager

**Request body**:
```json
{
  "sale_id": "SALE-2024-001",
  "destination": "123 Main St, Scranton PA",
  "priority": "standard",
  "contents_summary": "Case paper, sticky notes",
  "fragile": false
}
```

**Response 201**: Created package object.

---

### PATCH /packages/{package_id}
Update editable package fields (non-lifecycle). Only permitted on non-terminal packages.
**Persona required**: sales, warehouse, manager

**Request body** (all fields optional):
```json
{
  "current_location": "41.4012,-75.6580",
  "destination": "456 Elm St, Scranton PA",
  "truck_id": "DM-TRUCK-01",
  "expected_delivery": "2026-06-20T12:00:00Z",
  "priority": "urgent",
  "contents_summary": "Updated contents",
  "fragile": true
}
```

**Response 200**: Updated package object.
**Response 409**: `{ "detail": "Cannot edit a terminal package" }`

---

### DELETE /packages/{package_id}
Delete a package. Only permitted when status is `order_created`.
**Persona required**: sales, manager

**Response 204**: No content.
**Response 409**: `{ "detail": "Cannot delete a package that has progressed past order_created" }`

---

### POST /packages/{package_id}/status
Advance the package lifecycle status.
**Persona required**: warehouse, manager (sales for cancel)

**Request body**:
```json
{
  "status": "packaged",
  "reason": "All items picked and packed",
  "source": "ui",
  "correlation_id": null
}
```

**Response 200**: Updated package object.
**Response 422**: `{ "detail": "Invalid transition from in_transit to order_created" }`
**Response 409**: `{ "detail": "Package is in a terminal status" }`

---

### POST /packages/{package_id}/delay
Record a delay on a non-terminal package without changing its lifecycle status.
**Persona required**: warehouse, manager

**Request body**:
```json
{
  "delay_reason": "Road closed due to Pretzel Day crowd",
  "delay_duration_hours": 4.0,
  "source": "ui"
}
```

**Response 200**: Updated package object.

---

### GET /packages/{package_id}/history
Full history for a package in reverse-chronological order.

**Response 200**:
```json
{
  "package_id": "PKG-2024-001",
  "history": [
    {
      "event_type": "status_changed",
      "actor_name": "Darryl Philbin",
      "timestamp": "2026-06-19T14:30:00Z",
      "source": "ui",
      "entity_type": "package",
      "entity_id": "PKG-2024-001",
      "previous_value": { "status": "shipped" },
      "new_value": { "status": "in_transit" },
      "reason": "Package scanned at distribution hub",
      "correlation_id": null
    }
  ]
}
```

---

### GET /packages/at-risk
MCP-friendly: packages that are delayed, have complaints, or are approaching expected delivery.

**Response 200**: `{ "items": [...package summaries...] }`

---

### GET /packages/delayed
MCP-friendly: packages with an active delay record.

**Response 200**: `{ "items": [...package summaries...] }`

---

## Tag: Sales

### GET /sales
List all sales.
**Response 200**: `{ "items": [...], "total": N }`

### GET /sales/{sale_id}
Get a sale with its invoice and package summaries.
**Response 200**: Sale object with nested invoice and packages array.

### POST /sales
Create a sale. Automatically creates one invoice linked to the sale.
**Persona required**: sales, manager

**Request body**:
```json
{
  "customer_id": "lackawanna-county-schools",
  "notes": "Quarterly paper order"
}
```

**Response 201**: Created sale with auto-generated invoice.

---

## Tag: Invoices

### GET /invoices
List all invoices.

### GET /invoices/{invoice_id}
Get a single invoice.

---

## Tag: Customers

### GET /customers
List all customers.

### GET /customers/{customer_id}
Get a customer.

### GET /customers/{customer_id}/complaints
MCP-friendly: all complaints for a customer across all their sales.

---

## Tag: Employees

### GET /employees
List all 12 predefined employees.

### GET /employees/{employee_id}
Get a single employee.

---

## Tag: Complaints

### GET /complaints
List complaints. Query params: `status`, `sale_id`, `package_id`.

### GET /complaints/{complaint_id}
Get a complaint with its associated packages.

### POST /complaints
Create a complaint tied to a sale.
**Persona required**: any

**Request body**:
```json
{
  "sale_id": "SALE-2024-001",
  "package_ids": ["PKG-2024-001", "PKG-2024-002"],
  "description": "Paper was damp. Michael, this is unacceptable.",
  "source": "ui"
}
```

**Response 201**: Created complaint.

### PATCH /complaints/{complaint_id}
Update an open complaint.
**Persona required**: any

**Request body**: `{ "description": "Updated description" }`

### POST /complaints/{complaint_id}/close
Close a complaint.
**Persona required**: any

---

## Tag: Trucks

### GET /trucks
List all trucks and their current status.

### GET /trucks/{truck_id}
Get a truck.

### GET /trucks/{truck_id}/current-location
MCP-friendly: current lat/lng and status.

**Response 200**:
```json
{
  "truck_id": "DM-TRUCK-01",
  "lat": 41.4012,
  "lng": -75.6580,
  "status": "in_transit",
  "current_stop": "Lackawanna County Schools",
  "last_updated": "2026-06-19T14:31:00Z"
}
```

### GET /trucks/{truck_id}/current-route
MCP-friendly: active route with stops, ETAs, and Azure Maps polyline.

---

## Tag: Events

### GET /events
List recent domain events from the audit log (last 100 by default).
Query params: `event_type`, `entity_type`, `actor_id`, `since`.

---

## Tag: ManagerActions

### POST /manager-actions
Perform a manager action.
**Persona required**: manager only

**Request body**:
```json
{
  "action": "override_priority",
  "entity_type": "package",
  "entity_id": "PKG-2024-001",
  "payload": { "priority": "urgent" },
  "reason": "Angry customer called Michael directly.",
  "source": "ui",
  "correlation_id": null
}
```

**Supported actions**: `approve_reroute`, `override_priority`, `mark_customer_unhappy`,
`approve_return`, `approve_expensive_delivery`, `force_truck_reassignment`,
`trigger_demo_scenario`

**Response 200**: `{ "action": "override_priority", "status": "applied", "entity_id": "PKG-2024-001" }`
**Response 403**: `{ "detail": "Manager persona required. Current persona: sales" }`

---

## Tag: Demo

### POST /demo/reset
Reset all data and re-run seed script.
**Persona required**: manager

**Response 200**: `{ "status": "reset_complete", "seeded_packages": 13, "seeded_employees": 12 }`

### POST /demo/scenarios/{scenarioName}
Trigger a pre-scripted demo scenario.
**Persona required**: manager

**Supported scenarios**:
- `delayed-delivery`
- `damaged-in-transit`
- `happy-customer`
- `manager-reroute`
- `complaint-and-return`

**Response 200**: `{ "scenario": "delayed-delivery", "status": "executed", "affected_packages": ["PKG-2024-003"] }`

---

## MCP-Friendly Summary Endpoints

### GET /operational-summary
Current state of all packages grouped by status, active trucks, and open complaints.

**Response 200**:
```json
{
  "packages_by_status": {
    "order_created": 2,
    "in_transit": 3,
    "delivered": 8
  },
  "active_trucks": 2,
  "open_complaints": 1,
  "delayed_packages": 1,
  "at_risk_packages": 2,
  "as_of": "2026-06-19T14:35:00Z"
}
```

### GET /deliveries/active
All packages currently in transit with truck and ETA.

---

## Error Response Shape

All errors follow:
```json
{
  "detail": "Human-readable explanation of what went wrong and what to do."
}
```

HTTP status codes used:
- 400: Invalid request body
- 401: X-Persona-Id header missing on a write operation
- 403: Persona does not have permission for this operation
- 404: Entity not found
- 409: Business rule violation (invalid transition, terminal package, last line item)
- 422: Pydantic validation failure
- 500: Unexpected server error
