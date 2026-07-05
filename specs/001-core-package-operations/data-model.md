# Data Model: Core Package Operations

**Phase**: 1 — Design
**Date**: 2026-06-19

All tables are defined as SQLModel models. Every table uses an integer primary key `id`.
Business identifiers (slugs, human-readable codes) are stored in a separate string field.

---

## Enumerations

### PackageStatus

```
order_created
backorder
packaged
ready_for_shipping
shipped
in_transit
delivered
cancelled
damaged
returned
```

Terminal statuses: `delivered`, `cancelled`, `damaged`, `returned`
Normal sequence: `order_created` → `backorder`? → `packaged` → `ready_for_shipping`
  → `shipped` → `in_transit` → `delivered`

### PackagePriority

```
standard
priority
urgent
```

### Persona

```
sales
accounting
warehouse
manager
```

### EventSource

```
ui
api
demo
agent
system
```

### ComplaintStatus

```
open
closed
```

### TruckStatus

```
available
in_transit
delayed
at_warehouse
```

### PackageHistoryEventType

```
package_created
line_item_added
line_item_changed
status_changed
location_updated
assigned_to_truck
truck_rerouted
delivered
returned
damaged
cancelled
complaint_created
complaint_updated
manager_action_performed
delay_recorded
```

---

## Tables

### Employee

Represents a predefined Dunder Mifflin staff member. All 12 employees are created by the
seed script. Employees are not created through the API.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | Internal key |
| employee_id | String(50) | UNIQUE, NOT NULL | Slug: "michael-scott" |
| name | String(100) | NOT NULL | Display name |
| persona | String(20) | NOT NULL | Enum: Persona |
| email | String(100) | UNIQUE, NOT NULL | Fictional DM email |
| is_active | Boolean | NOT NULL, DEFAULT true | |

---

### Customer

A business or individual that purchases from Dunder Mifflin.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| customer_id | String(50) | UNIQUE, NOT NULL | Slug |
| name | String(200) | NOT NULL | |
| address | String(300) | NOT NULL | Street address |
| city | String(100) | NOT NULL | |
| state | String(50) | NOT NULL | |
| zip | String(20) | NOT NULL | |
| contact_name | String(100) | | |
| contact_email | String(100) | | |
| is_unhappy | Boolean | NOT NULL, DEFAULT false | Set by manager action |
| lat | Float | | Delivery coordinates |
| lng | Float | | Delivery coordinates |

---

### Sale

A purchase transaction. Exactly one invoice is created when a sale is created.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| sale_id | String(50) | UNIQUE, NOT NULL | e.g. "SALE-2024-001" |
| customer_id | Integer | FK → Customer.id, NOT NULL | |
| salesperson_id | Integer | FK → Employee.id, NOT NULL | |
| notes | String(1000) | | Optional notes |
| created_at | DateTime | NOT NULL | UTC |
| updated_at | DateTime | NOT NULL | UTC |

---

### Invoice

Auto-created with every Sale. One invoice per sale.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| invoice_id | String(50) | UNIQUE, NOT NULL | e.g. "INV-2024-001" |
| sale_id | Integer | FK → Sale.id, NOT NULL, UNIQUE | One-to-one |
| created_by_id | Integer | FK → Employee.id, NOT NULL | Accounting employee |
| created_at | DateTime | NOT NULL | UTC |

---

### Package

The core entity. Tracks a collection of line items through the delivery lifecycle.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| package_id | String(50) | UNIQUE, NOT NULL | e.g. "PKG-2024-001" |
| sale_id | Integer | FK → Sale.id, NOT NULL | |
| invoice_id | Integer | FK → Invoice.id, NOT NULL | Denormalized for direct access |
| customer_id | Integer | FK → Customer.id, NOT NULL | |
| salesperson_id | Integer | FK → Employee.id, NOT NULL | |
| invoicing_employee_id | Integer | FK → Employee.id, NOT NULL | |
| status | String(30) | NOT NULL | Enum: PackageStatus |
| current_location | String(300) | | Free text or coordinates |
| destination | String(300) | NOT NULL | |
| truck_id | Integer | FK → Truck.id, NULL | Set when assigned |
| expected_delivery | DateTime | | UTC |
| priority | String(20) | NOT NULL, DEFAULT 'standard' | Enum: PackagePriority |
| contents_summary | String(500) | | Short description |
| fragile | Boolean | NOT NULL, DEFAULT false | |
| delay_reason | String(500) | | NULL when no active delay |
| delay_duration_hours | Float | | NULL when no active delay |
| delay_recorded_at | DateTime | | UTC |
| created_at | DateTime | NOT NULL | UTC |
| updated_at | DateTime | NOT NULL | UTC |

**Lifecycle enforcement**: `app/lifecycle/transitions.py` defines `VALID_TRANSITIONS`.
`LifecycleValidator.validate(current_status, target_status)` raises `InvalidTransitionError`
before any write occurs.

**Deletion rule**: Only packages in `order_created` status may be deleted.

---

### PackageLineItem

A specific product within a package.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| package_id | Integer | FK → Package.id, NOT NULL | |
| product_name | String(200) | NOT NULL | |
| product_category | String(100) | NOT NULL | |
| quantity | Integer | NOT NULL, CHECK > 0 | |
| unit_description | String(100) | NOT NULL | e.g. "reams", "boxes" |
| product_type | String(20) | NOT NULL | "paper_product" or "office_supply" |
| is_fragile | Boolean | NOT NULL, DEFAULT false | |

**Last-item protection**: `PackageService.remove_line_item()` raises `LastLineItemError`
if removal would leave the package with zero items.

---

### PackageHistory

Immutable audit trail for all meaningful events on a package. Never updated or deleted.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| package_id | Integer | FK → Package.id, NOT NULL | |
| actor_id | Integer | FK → Employee.id, NULL | NULL for system events |
| actor_name | String(100) | NOT NULL | Denormalized for immutability |
| timestamp | DateTime | NOT NULL | UTC |
| source | String(20) | NOT NULL | Enum: EventSource |
| event_type | String(50) | NOT NULL | Enum: PackageHistoryEventType |
| entity_type | String(50) | NOT NULL | e.g. "package", "line_item" |
| entity_id | String(50) | NOT NULL | |
| previous_value | JSON | | NULL if not applicable |
| new_value | JSON | | NULL if not applicable |
| reason | String(500) | | NULL if not applicable |
| correlation_id | String(100) | | NULL if not applicable |

**Immutability**: No UPDATE or DELETE operations are permitted on this table. The service
layer enforces this; the table does not have cascading deletes.

---

### Complaint

A record of a customer concern tied to a sale.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| complaint_id | String(50) | UNIQUE, NOT NULL | e.g. "CMP-2024-001" |
| sale_id | Integer | FK → Sale.id, NOT NULL | |
| status | String(20) | NOT NULL, DEFAULT 'open' | Enum: ComplaintStatus |
| description | String(2000) | NOT NULL | |
| created_by_id | Integer | FK → Employee.id, NOT NULL | |
| created_at | DateTime | NOT NULL | UTC |
| updated_at | DateTime | NOT NULL | UTC |

---

### ComplaintPackage (Junction)

Many-to-many between Complaint and Package.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| complaint_id | Integer | FK → Complaint.id, NOT NULL | PK (composite) |
| package_id | Integer | FK → Package.id, NOT NULL | PK (composite) |

---

### Truck

Represents a Dunder Mifflin delivery truck in the simulation.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| truck_id | String(50) | UNIQUE, NOT NULL | e.g. "DM-TRUCK-01" |
| name | String(100) | NOT NULL | e.g. "Big Brown Beauty" |
| driver_name | String(100) | | |
| status | String(20) | NOT NULL | Enum: TruckStatus |
| current_lat | Float | NOT NULL | Scranton area |
| current_lng | Float | NOT NULL | |
| home_lat | Float | NOT NULL | Warehouse coordinates |
| home_lng | Float | NOT NULL | |
| current_route_id | Integer | FK → TruckRoute.id, NULL | |
| current_stop_index | Integer | NOT NULL, DEFAULT 0 | |
| delay_state | JSON | | NULL when not delayed |
| last_tick_at | DateTime | | UTC |

---

### TruckRoute

A route assigned to a truck for a delivery run.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| truck_id | Integer | FK → Truck.id, NOT NULL | |
| stops | JSON | NOT NULL | List of stop objects (see below) |
| azure_maps_route | JSON | | Cached polyline from Azure Maps |
| created_at | DateTime | NOT NULL | UTC |
| started_at | DateTime | | UTC |
| completed_at | DateTime | | UTC |

**Stop object schema** (each element in `stops` JSON array):
```json
{
  "sequence": 1,
  "name": "Lackawanna County Schools",
  "address": "123 Main St, Scranton PA",
  "lat": 41.4090,
  "lng": -75.6624,
  "package_id": "PKG-2024-007",
  "delivered_at": null
}
```

---

### AuditLog

System-wide immutable audit log for all meaningful write operations.
Distinct from PackageHistory: covers all entities, not just packages.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | Integer | PK, auto | |
| actor_id | Integer | FK → Employee.id, NULL | NULL for system operations |
| actor_name | String(100) | NOT NULL | Denormalized |
| timestamp | DateTime | NOT NULL | UTC |
| source | String(20) | NOT NULL | Enum: EventSource |
| entity_type | String(50) | NOT NULL | e.g. "package", "sale" |
| entity_id | String(50) | NOT NULL | Business ID |
| action | String(100) | NOT NULL | e.g. "status_changed" |
| previous_value | JSON | | NULL if not applicable |
| new_value | JSON | | NULL if not applicable |
| reason | String(500) | | NULL if not applicable |
| correlation_id | String(100) | | NULL if not applicable |

**Immutability**: No UPDATE or DELETE operations are permitted on this table.

---

## Lifecycle State Machine

```
VALID_TRANSITIONS = {
    "order_created":      ["backorder", "packaged", "cancelled", "damaged"],
    "backorder":          ["packaged", "cancelled", "damaged"],
    "packaged":           ["ready_for_shipping", "cancelled", "damaged"],
    "ready_for_shipping": ["shipped", "cancelled", "damaged"],
    "shipped":            ["in_transit", "cancelled", "damaged"],
    "in_transit":         ["delivered", "returned", "cancelled", "damaged"],
    "delivered":          ["returned"],   # requires manager approval
    "cancelled":          [],             # terminal
    "damaged":            [],             # terminal
    "returned":           [],             # terminal
}
```

`LifecycleValidator.validate(current: str, target: str)` raises `InvalidTransitionError`
if `target` is not in `VALID_TRANSITIONS[current]`.

`InvalidTransitionError` carries: `current_status`, `target_status`, `message`.

The validator is called as the first step in any status-change operation, before any
database write, history entry, or event emission.

---

## Entity Relationships (summary)

```
Customer ──────────────────────────────────── Sale ──── Invoice
                                               │
                          ┌────────────────────┤
                          │                    │
                       Package ─── PackageLineItem
                          │
                          ├─── PackageHistory (immutable)
                          │
                          ├─── ComplaintPackage ─── Complaint ─── Sale
                          │
                          └─── Truck ─── TruckRoute

AuditLog (covers all entities, not just Package)
```
