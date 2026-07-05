# Quickstart: Events, Topics, and Live Operational Stream

**Feature**: 004-event-operational-stream | **Date**: 2026-06-22

## Workshop Scenario: Watching Events Flow

This scenario demonstrates the operational stream to workshop attendees.

### Step 1: Open the event stream

Navigate to the **Events** tab in the application. The stream is empty if the system
was just reset.

### Step 2: Trigger some events

In a second browser tab, perform a few operations:
- Create a new package.
- Advance the package to `ready_for_shipping`.
- Assign the package to a truck and dispatch it.

Switch back to the Events tab. You should see events appearing:
- `package.created` on topic `packages`
- `package.status.updated` (twice) on topic `package-status`
- `package.assigned.to.truck` on topic `package-status`
- `truck.dispatched` → `truck.route.created` on topic `truck-location`

### Step 3: Explore an event

Click any event to expand it. The full JSON payload is shown, including the actor block
and correlation ID. For the dispatch operation, all events share the same correlation ID.

### Step 4: Filter by correlation ID

Copy the correlation ID from the dispatch event. Paste it into the Correlation ID filter
field. The stream now shows only the dispatch-related events as a group.

### Step 5: Trigger a Kevin reroute

Using the manager persona, trigger a Kevin Hunger Reroute from the map view. Return to
the Events tab and observe the `truck.rerouted` event on `truck-reroute` and any
`package.delay.recorded` events on `package-status` for the affected packages.

### Step 6: Pause, act, and resume

Click Pause on the stream. Perform more operations. Click Resume. The buffered events
appear without gaps.

### Step 7: Clear the display

Click Clear. The stream display resets to empty, but the history is preserved in the
database. Refreshing the page will re-load recent events from `GET /events`.

---

## Independent Test Criteria (per spec user stories)

### US1: Live Operational Stream
- Create a package. Observe `package.created` in the stream within 3 seconds. ✓
- Click Pause, perform an operation, click Resume. Verify no events are lost. ✓
- Click Clear. Verify the display clears but `GET /events` still returns the events. ✓

### US2: Domain Event Model and Topics
- Verify `package.status.updated` event contains `previous_status`, `new_status`, `actor`,
  and `correlation_id` fields. ✓
- Verify `truck.rerouted` event is on the `truck-reroute` topic. ✓
- Attempt an invalid operation (e.g. assign an in-transit package). Verify no success event
  is published. ✓

### US3: Event Filtering
- Apply a filter for topic = `package-status`. Verify only package status events are shown. ✓
- Apply a filter for actor = `michael-scott`. Verify only Michael's events are shown. ✓
- Apply a correlation ID filter. Verify a complete group of related events is shown. ✓

### US4: Audit History
- Check `GET /packages/{id}/history` for a package that was status-changed. Verify the
  audit entry exists with actor, timestamp, previous value, and new value. ✓
- Verify the audit entry and corresponding domain event share the same correlation ID. ✓
