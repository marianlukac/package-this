# MCP Integration Guide

This guide explains how future MCP servers will consume the Dunder Mifflin Package Manager API.

## Overview

The API is designed to be consumed by AI agents via MCP tools. Each MCP tool wraps one or more API endpoints and handles the `X-Persona-Id` header transparently.

## Setting up the MCP server

```python
# Example MCP tool wrapping GET /operational-summary
@tool
def get_operational_summary() -> dict:
    """Get a real-time snapshot of package operations."""
    return requests.get(
        f"{API_BASE}/operational-summary",
        headers={"X-Persona-Id": "michael-scott"}
    ).json()
```

## Key endpoints for agent tools

### Observation tools (read-only)

```
GET /operational-summary       → Current state snapshot
GET /packages                  → List with status/priority filters
GET /packages/at-risk          → Packages needing attention
GET /packages/delayed          → All delayed packages
GET /packages/{id}             → Full package detail
GET /packages/{id}/history     → Audit trail for a package
GET /trucks/{id}/current-location  → Real-time truck position
GET /trucks/{id}/current-route     → Active stops
GET /deliveries/active         → All in-flight deliveries
GET /customers/{id}/complaints → Complaints per customer
GET /events                    → Recent audit log entries
```

### Action tools (write operations)

```
POST /packages/{id}/status     → Advance lifecycle
POST /packages/{id}/delay      → Record delay
POST /manager-actions          → Execute manager decisions
POST /complaints               → Create complaint
POST /complaints/{id}/close    → Close complaint
POST /demo/reset               → Restore seed state
POST /demo/scenarios/{name}    → Run scripted scenario
```

## Persona configuration

Each MCP tool should have a configured persona appropriate to its role:

| MCP Tool | Persona |
|---|---|
| Package observer | `jim-halpert` (sales) |
| Lifecycle manager | `darryl-philbin` (warehouse) |
| Manager decision tool | `michael-scott` (manager) |
| Complaint tool | any persona |

## Event subscription for reactive agents

Agents can subscribe to Service Bus topics to react to domain events:

```
packages           → React when new packages are created
package-status     → React when package status changes
truck-location     → React to truck movements
manager-actions    → React when manager makes decisions
complaints         → React to complaint lifecycle
```

## Agent-to-agent patterns

In later workshop modules, agents will:
1. **Observe** — poll `/operational-summary` and `/packages/at-risk` for situational awareness
2. **React** — subscribe to Service Bus topics for event-driven behavior
3. **Act** — call action endpoints with appropriate persona
4. **Audit** — check `/packages/{id}/history` to verify actions took effect

## Local testing

When the backend is running locally, point the MCP server at:
```
API_BASE=http://localhost:8000
WS_URL=ws://localhost:8000/ws
```

No Azure credentials needed in local mode — the InMemoryEventPublisher simulates all events.
