# Event Envelope Contract

**Date**: 2026-06-19

All domain events published to Azure Service Bus topics (and broadcast via Web PubSub or
WebSocket) use a shared `EventEnvelope` structure. Consumers must handle this envelope
regardless of topic.

---

## EventEnvelope Schema

```json
{
  "eventId": "string (UUID)",
  "eventType": "string (see Event Types below)",
  "topic": "string (Service Bus topic name)",
  "occurredAt": "string (ISO 8601 UTC)",
  "actor": "string (employee_id or 'system')",
  "source": "string (ui | api | demo | agent | system)",
  "entityType": "string (package | sale | invoice | truck | complaint | customer)",
  "entityId": "string (business identifier)",
  "correlationId": "string | null",
  "payload": "object (event-type-specific, see below)",
  "summary": "string (human-readable one-line description)"
}
```

**All fields are required except `correlationId`**, which is null when not provided by
the caller.

---

## Service Bus Topics and Their Event Types

### Topic: `packages`

| eventType | When emitted |
|---|---|
| `package.created` | Package record created |
| `package.updated` | Non-lifecycle fields updated (location, priority, etc.) |
| `package.deleted` | Package deleted (order_created only) |
| `package.line_item_added` | Line item added to package |
| `package.line_item_changed` | Line item updated |

### Topic: `package-status`

| eventType | When emitted |
|---|---|
| `package.status_changed` | Any lifecycle status change |
| `package.delivered` | Package reached delivered status |
| `package.cancelled` | Package cancelled |
| `package.damaged` | Package marked damaged |
| `package.returned` | Package marked returned |
| `package.delay_recorded` | Delay recorded (status unchanged) |

### Topic: `package-location`

| eventType | When emitted |
|---|---|
| `package.location_updated` | Package location updated (including truck position sync) |

### Topic: `truck-location`

| eventType | When emitted |
|---|---|
| `truck.location_updated` | Truck position updated during simulation tick (throttled) |

### Topic: `truck-reroute`

| eventType | When emitted |
|---|---|
| `truck.rerouted` | Truck assigned a new or modified route |
| `truck.stop_completed` | Truck completed a delivery stop |
| `truck.returned_to_warehouse` | Truck completed all stops and returned |

### Topic: `manager-actions`

| eventType | When emitted |
|---|---|
| `manager.action_performed` | Any manager action executed |

### Topic: `complaints`

| eventType | When emitted |
|---|---|
| `complaint.created` | New complaint created |
| `complaint.updated` | Complaint description updated |
| `complaint.closed` | Complaint closed |

### Topic: `audit-log`

| eventType | When emitted |
|---|---|
| `audit.entry_created` | Any meaningful write operation (mirrors AuditLog table) |

---

## Payload Shapes by Event Type

### package.status_changed

```json
{
  "package_id": "PKG-2024-001",
  "previous_status": "shipped",
  "new_status": "in_transit",
  "reason": "Package scanned at Scranton distribution hub",
  "truck_id": "DM-TRUCK-01"
}
```

### package.delay_recorded

```json
{
  "package_id": "PKG-2024-001",
  "current_status": "in_transit",
  "delay_reason": "Road closed due to Pretzel Day crowd",
  "delay_duration_hours": 4.0
}
```

### truck.location_updated

```json
{
  "truck_id": "DM-TRUCK-01",
  "lat": 41.4012,
  "lng": -75.6580,
  "current_stop_index": 2,
  "next_stop_name": "Lackawanna County Schools",
  "status": "in_transit"
}
```

### truck.rerouted

```json
{
  "truck_id": "DM-TRUCK-01",
  "reason": "Michael approved priority reroute for DM Wellness",
  "previous_route_summary": "3 stops remaining",
  "new_route_summary": "4 stops, new priority stop inserted at position 1"
}
```

### manager.action_performed

```json
{
  "action": "override_priority",
  "entity_type": "package",
  "entity_id": "PKG-2024-001",
  "payload": { "previous_priority": "standard", "new_priority": "urgent" },
  "reason": "Angry customer called Michael directly."
}
```

### complaint.created

```json
{
  "complaint_id": "CMP-2024-001",
  "sale_id": "SALE-2024-001",
  "package_ids": ["PKG-2024-001"],
  "description": "Paper was damp."
}
```

### audit.entry_created

```json
{
  "actor_name": "Jim Halpert",
  "entity_type": "package",
  "entity_id": "PKG-2024-001",
  "action": "status_changed",
  "previous_value": { "status": "packaged" },
  "new_value": { "status": "ready_for_shipping" }
}
```

---

## Full Example: package.status_changed on Topic package-status

```json
{
  "eventId": "a3f7c2b1-1234-5678-abcd-ef1234567890",
  "eventType": "package.status_changed",
  "topic": "package-status",
  "occurredAt": "2026-06-19T14:30:00Z",
  "actor": "darryl-philbin",
  "source": "ui",
  "entityType": "package",
  "entityId": "PKG-2024-001",
  "correlationId": null,
  "payload": {
    "package_id": "PKG-2024-001",
    "previous_status": "shipped",
    "new_status": "in_transit",
    "reason": "Package scanned at Scranton distribution hub",
    "truck_id": "DM-TRUCK-01"
  },
  "summary": "Package PKG-2024-001 moved from shipped to in_transit by Darryl Philbin"
}
```

---

## Consumer Notes (for Workshop Agents and MCP Servers)

- Subscribe to a specific topic to receive only the events relevant to your agent's task.
- Use `correlationId` to link related events across a workflow.
- Use `actor` and `source` to distinguish human actions (source: ui) from agent actions
  (source: agent).
- The `summary` field is LLM-friendly: use it for display or logging without parsing payload.
- All events on the `audit-log` topic mirror the AuditLog table entries and can be used
  to build a real-time event feed without polling the API.
