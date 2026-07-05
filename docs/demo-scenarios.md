# Demo Scenarios

The system includes pre-scripted scenarios for workshop demos. Trainers can run them via the UI or API.

## Reset baseline

```bash
curl -X POST http://localhost:8000/demo/reset \
  -H "X-Persona-Id: michael-scott"
```

Or use the PowerShell script:
```powershell
.\scripts\reset-seed.ps1
```

## Available scenarios

| Scenario Name | What it does |
|---|---|
| `delayed_delivery` | Marks an in-transit package as delayed with a reason |
| `damaged_package` | Advances a package to `damaged` status |
| `reroute_required` | Emits a truck reroute event |
| `return_request` | Marks a delivered package for return |
| `complaint_escalation` | Creates a complaint on an active sale and marks customer as unhappy |

## Running via API

```bash
curl -X POST http://localhost:8000/demo/scenarios/delayed_delivery \
  -H "X-Persona-Id: michael-scott"
```

## Running via manager action

```bash
curl -X POST http://localhost:8000/manager-actions \
  -H "X-Persona-Id: michael-scott" \
  -H "Content-Type: application/json" \
  -d '{"action": "trigger_demo_scenario", "entity_id": "demo", "reason": "Workshop demo", "payload": {"scenario_name": "delayed_delivery"}, "source": "api"}'
```

---

## Event Stream

The Live Events panel in the top-right corner of the dashboard shows domain events in real time.
Use this scenario to narrate the operational event model to workshop attendees.

### Setup

Reset seed data to start with a clean event stream:

```bash
curl -X POST http://localhost:8000/demo/reset \
  -H "X-Persona-Id: michael-scott"
```

### Demo walkthrough

**Step 1: Create and advance a package**

```bash
# Advance a package status (triggers package.status.updated on topic package-status)
curl -X POST http://localhost:8000/packages/PKG-2024-001/status \
  -H "X-Persona-Id: michael-scott" \
  -H "Content-Type: application/json" \
  -d '{"status": "packaged", "reason": "All items verified"}'
```

The event stream shows:
- `package.status.updated` — topic `package-status` — actor Michael Scott

**Step 2: Dispatch a truck** (triggers a cluster of correlated events)

```bash
curl -X POST http://localhost:8000/trucks/DM-TRUCK-01/dispatch \
  -H "X-Persona-Id: darryl-philbin"
```

The event stream shows:
- `truck.route.created` — topic `truck-location`
- `package.status.updated` (one per in-transit package) — all sharing the same correlation ID

**Step 3: Observe correlated events**

Click any event in the stream to expand it. Copy the `correlation_id` from the expanded payload.
Paste it into the **Correlation ID** filter at the top of the events panel.
The stream narrows to show only the events from that single dispatch operation.

**Step 4: Expand and copy a payload**

Click ▼ on any event row to expand the full JSON payload, actor block, and correlation ID.
Click ⧉ to copy the full event JSON to the clipboard.
Paste into an agent or MCP tool to show structured event consumption.

**Step 5: Pause and resume**

Click **Pause**. Perform another operation (e.g. a package delay).
The "N queued" indicator appears. Click **Resume** — buffered events flush into the stream.
No events are lost during the pause window.

**Step 6: Filter by topic**

Use the **Filters ▼** panel. Select topic = `truck-location`.
Only truck movement events are shown. Clear the filter to restore the full stream.

**Step 7: Kevin Hunger Reroute**

```bash
curl -X POST http://localhost:8000/trucks/DM-TRUCK-01/reroute \
  -H "X-Persona-Id: michael-scott" \
  -H "Content-Type: application/json" \
  -d '{"location_id": 3, "reason": "Kevin is hungry again"}'
```

A `truck.rerouted` event appears on the `truck-reroute` topic.
All affected packages emit `package.delay.recorded` — sharing the same correlation ID.

**Step 8: Entity navigation**

Click the `package/PKG-2024-001` entity link on any package event.
The package detail page opens directly. Truck events link to the delivery map.

**Step 9: Clear the display**

Click **Clear**. The event stream display empties.
Open a new browser tab and call `GET /events` — the full event history is still in the database.
Clear is a UI-only action, not a data deletion.

### Acceptance check (SC-001)

Perform any write operation and watch the event panel.
Each event must appear within 3 seconds of the triggering operation completing.

---

## Delivery Map and Truck Simulation

### Overview

The Scranton delivery map shows all three DM trucks moving in accelerated demo time. Trainers
use this to narrate the full package lifecycle — from warehouse assignment through route dispatch
to delivery — and to trigger the Kevin Hunger Reroute scenario.

### Starting the simulation

**Step 1: Assign packages to a truck** (warehouse or manager persona required)

```bash
curl -X POST http://localhost:8000/trucks/DM-TRUCK-01/assign \
  -H "X-Persona-Id: darryl-philbin" \
  -H "Content-Type: application/json" \
  -d '{"package_id": "PKG-2026-AABBCCDD"}'
```

Only packages in `ready_for_shipping` status can be assigned. Assign multiple packages to the
same truck before dispatching — one stop per unique customer is created automatically.

**Step 2: Dispatch the truck** (warehouse or manager persona required)

```bash
curl -X POST http://localhost:8000/trucks/DM-TRUCK-01/dispatch \
  -H "X-Persona-Id: darryl-philbin"
```

Dispatching calculates a route from the warehouse through all assigned customer stops and back.
The truck status becomes `on_route`. Packages become `in_transit`. The simulation engine starts
moving the truck along the route geometry automatically (one waypoint per second by default).

**Step 3: Watch truck movement**

Open the **Delivery Map** view in the frontend. The truck marker moves across the map.
Package `current_lat/lng` updates with the truck in real time via the `truck.location_updated`
event (emitted every 5 ticks to avoid spam).

Check current position at any time:

```bash
curl http://localhost:8000/trucks/DM-TRUCK-01/current-location \
  -H "X-Persona-Id: michael-scott"
```

### Delivery events

When the truck arrives at a customer stop:
- Packages for that customer are marked `delivered`
- Package `current_lat/lng` snaps to the customer coordinates
- Package `truck_id` is cleared
- A `package.delivered` event is emitted
- A `truck.arrived_at_stop` event is emitted

When all stops are done, the truck returns to the warehouse and status becomes `completed`.

### Kevin Hunger Reroute scenario

**Persona required**: `michael-scott` (manager only)

The Kevin Hunger Reroute inserts a food or donut via-point into the truck's active route,
delays the truck, and records delay history for all in-transit packages.

**Via the UI**: Click a truck on the delivery map → open the route panel → click
**Kevin Hunger Reroute** (visible only for manager persona) → choose a food or donut location
→ enter a reason → confirm.

**Via the API**:

```bash
# Find available food/donut locations
curl http://localhost:8000/map/markers \
  -H "X-Persona-Id: michael-scott"

# Trigger the reroute (use a location_id of type food or donut)
curl -X POST http://localhost:8000/trucks/DM-TRUCK-01/reroute \
  -H "X-Persona-Id: michael-scott" \
  -H "Content-Type: application/json" \
  -d '{"location_id": 3, "reason": "Kevin needs a sandwich"}'
```

The response shows the via-point name and coordinates, truck status (`rerouted`), and the list
of affected package IDs. The route geometry updates immediately; the map redraws the detour
polyline when the `truck.rerouted` event arrives via the real-time stream.

### Resetting between demos

```bash
curl -X POST http://localhost:8000/demo/reset \
  -H "X-Persona-Id: michael-scott"
```

This stops the simulation, resets all trucks to `at_warehouse`, deletes active routes, and
returns the system to the seed state. Packages revert to `ready_for_shipping`.
Trainers can then reassign and redispatch for the next workshop group.
