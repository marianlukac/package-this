# API Contract: Events Endpoint

**Feature**: 004-event-operational-stream | **Date**: 2026-06-22

## GET /events

Returns persisted domain events, newest first.

### Query Parameters

| Parameter | Type | Description |
|---|---|---|
| `limit` | integer (default 50, max 500) | Maximum number of events to return |
| `topic` | string | Filter by topic (e.g. `package-status`, `truck-location`) |
| `event_type` | string | Filter by event type (e.g. `package.delivered`) |
| `entity_type` | string | Filter by entity type (e.g. `package`, `truck`) |
| `entity_id` | string | Filter by specific entity ID |
| `actor_id` | string | Filter by actor ID |
| `source` | string | Filter by source (`ui`, `api`, `demo`, `agent`, `system`) |
| `correlation_id` | string | Filter by correlation group |
| `since` | ISO 8601 datetime | Return only events after this timestamp |

### Response

```json
[
  {
    "event_id": "550e8400-e29b-41d4-a716-446655440000",
    "event_type": "package.status.updated",
    "topic": "package-status",
    "occurred_at": "2026-06-22T10:15:00Z",
    "actor": {
      "actor_id": "michael-scott",
      "actor_name": "Michael Scott",
      "persona": "manager",
      "actor_type": "human"
    },
    "source": "ui",
    "entity_type": "package",
    "entity_id": "PKG-2026-AABBCCDD",
    "correlation_id": "abc123",
    "payload": {
      "previous_status": "packaged",
      "new_status": "ready_for_shipping",
      "reason": null
    },
    "summary": "Package PKG-2026-AABBCCDD status changed from packaged to ready_for_shipping"
  }
]
```

### Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Invalid query parameter value |
| 401 | Missing X-Persona-Id header |
