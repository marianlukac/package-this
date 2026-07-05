# Event Topics

All domain events use a shared `EventEnvelope` schema and are published to Azure Service Bus topics (production) or logged to stdout (local development).

## Envelope Schema

```json
{
  "eventId": "uuid-v4",
  "eventType": "package.status_changed",
  "topic": "package-status",
  "occurredAt": "2026-06-20T14:30:00Z",
  "actor": "darryl-philbin",
  "source": "ui",
  "entityType": "package",
  "entityId": "PKG-2026-AABBCCDD",
  "correlationId": "optional-uuid",
  "payload": { ... },
  "summary": "Package PKG-2026-AABBCCDD moved from packaged to shipped by Darryl Philbin"
}
```

## Topics

### `packages`
Events related to package lifecycle creation and line items.

| eventType | Trigger |
|---|---|
| `package.created` | New package created via POST /packages |
| `package.line_item_added` | Line item added |

### `package-status`
Status and delay changes.

| eventType | Trigger |
|---|---|
| `package.status_changed` | Any lifecycle advance |
| `package.delivered` | Package reaches delivered |
| `package.cancelled` | Package cancelled |
| `package.damaged` | Package marked damaged |
| `package.returned` | Package marked returned |
| `package.delay_recorded` | Delay recorded |

### `package-location`
Location updates from simulation.

| eventType | Trigger |
|---|---|
| `package.location_updated` | Package moves with truck |

### `truck-location`
Truck movement from simulation engine.

| eventType | Trigger |
|---|---|
| `truck.location_updated` | Simulation tick with position change |
| `truck.route_complete` | Truck finished all stops |

### `truck-reroute`
Route changes.

| eventType | Trigger |
|---|---|
| `truck.rerouted` | Manager approves reroute |

### `manager-actions`
All manager action executions.

| eventType | Trigger |
|---|---|
| `manager.action_performed` | Any POST /manager-actions call |

### `complaints`
Complaint lifecycle.

| eventType | Trigger |
|---|---|
| `complaint.created` | POST /complaints |
| `complaint.updated` | PATCH /complaints/{id} |
| `complaint.closed` | POST /complaints/{id}/close |

### `audit-log`
System-wide audit trail (consumed externally; stored in AuditLog table internally).

## Local development

In local mode (`EVENT_PUBLISHER=inmemory`), events are printed to stdout:
```
[EVENT] package-status/package.status_changed | PKG-2026-AABBCCDD | Package moved from packaged to shipped by Darryl Philbin
```

## Agent consumer example

```python
from azure.servicebus import ServiceBusClient
import json

with ServiceBusClient.from_connection_string(conn_str) as client:
    with client.get_subscription_receiver("package-status", "my-agent") as receiver:
        for msg in receiver:
            event = json.loads(str(msg))
            print(f"Event: {event['eventType']} on {event['entityId']}")
            receiver.complete_message(msg)
```
