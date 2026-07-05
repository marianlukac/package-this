# Feature Specification: Scranton Delivery Map and Truck Simulation

**Feature Branch**: `003-scranton-delivery-map`
**Created**: 2026-06-21
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Scranton Map View (Priority: P1)

A trainer or workshop attendee opens the delivery map and immediately sees Scranton, Pennsylvania with the Dunder Mifflin office and warehouse, all fourteen customer locations, three named delivery trucks at their current positions, active delivery routes, and the food and donut locations available for rerouting scenarios.

The map is the primary situational awareness view. It should be understandable at a glance without explanation — trainers use it to orient attendees to the delivery system before any interaction.

**Why this priority**: The map view is the entry point for all other interactions in this feature. Without a functioning map, no other scenario can be demonstrated.

**Independent Test**: Open the map view. Verify the Dunder Mifflin office and warehouse marker is visible. Verify fourteen customer markers are visible. Verify three truck markers are visible with names. Verify at least three food markers and three donut shop markers are visible. Verify active route lines are drawn between the warehouse and customer stops. This test delivers full value with no other user story complete.

**Acceptance Scenarios**:

1. **Given** the map view is open, **When** the page loads, **Then** the Dunder Mifflin office and warehouse marker is visible as the named central hub location
2. **Given** the map view is open, **When** the page loads, **Then** all fourteen customer markers are visible with customer names
3. **Given** the map view is open, **When** the page loads, **Then** three truck markers are visible showing "The Dundie", "Pretzel Day", and "Big Tuna"
4. **Given** trucks have active routes, **When** the map loads, **Then** route lines are drawn from the warehouse through each customer stop and back to the warehouse
5. **Given** the map view is open, **When** the page loads, **Then** food and donut location markers are visible on the Scranton map

---

### User Story 2 — Truck Assignment and Package Tracking (Priority: P1)

A warehouse user assigns a ready-for-shipping package to one of the three delivery trucks. Once the truck departs, the package location on the map tracks the truck's GPS position in real time. When the truck delivers the package to the customer, the package location becomes the customer's location.

This story covers the core logistics workflow: packages move from the warehouse to customers via trucks, and the system reflects that movement visually.

**Why this priority**: Package tracking via truck assignment is the primary business value of the map feature. Without it, the map is decorative.

**Independent Test**: Assign a ready-for-shipping package to The Dundie. Dispatch The Dundie. Open the package detail view. Verify the package location matches The Dundie's current GPS position as the truck moves. When The Dundie reaches the package's customer stop, verify the package status changes to delivered and the location becomes the customer's address. This test requires only truck assignment and package tracking; no rerouting or route detail views are needed.

**Acceptance Scenarios**:

1. **Given** a package is in `ready_for_shipping` status, **When** an authorized user assigns it to a truck, **Then** the assignment is recorded and the package appears in the truck's package list
2. **Given** a package is in `order_created`, `backorder`, or `packaged` status, **When** a user attempts to assign it to a truck, **Then** the assignment is rejected with a clear explanation
3. **Given** a package is assigned to a truck and the truck departs, **When** the truck moves, **Then** the package's current location updates to match the truck's current GPS coordinate
4. **Given** a truck arrives at a customer stop, **When** the delivery is recorded, **Then** the packages for that customer are marked delivered and their location becomes the customer location
5. **Given** a package is already assigned to one truck, **When** a user attempts to assign it to a second truck simultaneously, **Then** the second assignment is rejected
6. **Given** a package is in `ready_for_shipping` status, **When** an authorized user reassigns it to a different truck before the truck departs, **Then** the reassignment is recorded

---

### User Story 3 — Live Truck Movement Simulation (Priority: P2)

The system runs an accelerated delivery simulation where trucks depart the warehouse, move through their assigned customer stops in demo time, and return to the warehouse when their route is complete. Trainers and attendees watch trucks move on the map and see delivery events appear in the event stream as packages are dropped off.

This story brings the map to life and makes the system demonstrable without waiting for real-world delivery timescales.

**Why this priority**: The simulation is what makes the map useful for a workshop. However, the baseline map view (US1) and package tracking mechanics (US2) must work correctly before the simulation adds demo value.

**Independent Test**: Start the simulation with all three trucks loaded. Observe each truck moving along its route on the map. After a truck completes a customer stop, verify the package is marked delivered in the package list and a delivery history entry appears. After all stops, verify the truck returns to the warehouse and its status becomes completed. The test does not require rerouting to pass.

**Acceptance Scenarios**:

1. **Given** trucks have assigned packages and are in ready status, **When** the simulation starts, **Then** trucks begin moving along their routes in accelerated demo time
2. **Given** a truck is moving, **When** a regular simulation tick occurs, **Then** the truck's GPS coordinate is updated and the change is reflected on the map
3. **Given** a truck arrives at a customer stop, **When** the delivery is processed, **Then** all packages for that customer are marked delivered and a package history entry is created
4. **Given** a delivery event occurs, **When** the event is processed, **Then** a meaningful delivery domain event is emitted
5. **Given** a truck completes all customer stops, **When** the truck returns to the warehouse, **Then** the route is marked complete and the truck status becomes completed or at_warehouse
6. **Given** the simulation is running, **When** a trainer or attendee views the map, **Then** the current simulation state is clearly understandable (no invisible or frozen trucks)

---

### User Story 4 — Kevin Hunger Reroute (Priority: P2)

An authorized user selects a truck on the map, chooses a fast food or donut shop location, provides a hunger-related reason, and triggers a reroute. The truck's route is updated to include the food stop as a via-point, the truck is marked delayed, and affected in-transit packages receive delay notifications in their package history. The event stream shows the reroute event.

This scenario is the signature interactive demo moment — humorous but illustrating the enterprise-grade rerouting and delay propagation pattern that agents will later automate.

**Why this priority**: The reroute scenario is the key memorable demo interaction for the workshop. It connects the map, truck simulation, package history, and event stream in one visible operation.

**Independent Test**: Select The Dundie while it is on route. Choose a donut shop. Enter the reason "driver spotted fresh Krispy Kreme." Confirm the reroute. Verify the route line on the map now shows a detour to the donut shop before the next customer stop. Verify The Dundie's status is rerouted. Verify in-transit packages on The Dundie have a delay entry in their package history. Verify a reroute event appears in the event stream. No simulation restart is required.

**Acceptance Scenarios**:

1. **Given** a truck is on route, **When** an authorized user selects it and initiates a Kevin hunger reroute, **Then** the system presents a selection of available food and donut locations
2. **Given** a truck and food destination are selected with a reason, **When** the reroute is confirmed, **Then** the food location is added as a via-point to the truck's active route without removing existing customer stops
3. **Given** a reroute is confirmed, **When** the route is updated, **Then** the truck status changes to rerouted and delay information is recorded
4. **Given** a reroute is confirmed, **When** the route is updated, **Then** in-transit packages on the rerouted truck receive package history entries recording the delay
5. **Given** a reroute is confirmed, **When** the route is updated, **Then** meaningful reroute and delay domain events are emitted
6. **Given** a truck is returning to warehouse or has completed its route, **When** a user attempts to initiate a reroute, **Then** the reroute is rejected with a clear explanation
7. **Given** the user does not have rerouting permission, **When** they attempt to trigger a reroute, **Then** the action is rejected and an explanation is shown

---

### User Story 5 — Route and Delivery Detail View (Priority: P3)

A user clicks on a truck or a customer marker on the map and sees a detail panel with the truck's name, status, assigned packages, route stops with estimated delivery times, and current progress. Clicking a package in the panel opens the package detail view.

This story provides the drill-down information layer that trainers use to explain delivery operations to attendees.

**Why this priority**: The detail view is useful for demo narration but is not required for the simulation or rerouting to function. It enhances the experience rather than enabling it.

**Independent Test**: Click The Dundie on the map. Verify a detail panel opens showing the truck's name, status, current stop, next stop, and list of assigned packages with delivery status. Click one package in the panel. Verify the package detail view opens for that package. Close the panel and click a customer marker. Verify a panel opens showing the customer name and packages scheduled for delivery to that customer.

**Acceptance Scenarios**:

1. **Given** the map is open, **When** a user clicks a truck marker, **Then** a detail panel opens showing the truck's name, number, status, current GPS position, current stop, next stop, delay information if any, and assigned packages
2. **Given** a truck detail panel is open, **When** a user clicks a package in the panel, **Then** the package detail view opens for that package
3. **Given** the map is open, **When** a user clicks a customer marker, **Then** a panel shows the customer name and which packages are scheduled for delivery to that customer
4. **Given** a truck has an active route, **When** the user views the route detail, **Then** all stops are listed in order with estimated delivery times and current progress
5. **Given** a truck is rerouted, **When** the user views the route detail, **Then** the via-point is shown in the stop list with the delay reason

---

### Edge Cases

- What happens when a truck has no packages assigned when dispatch is requested? The system must prevent a truck from dispatching without at least one package assigned.
- What happens when a package's destination customer has no geocoded location? The package cannot be assigned to a truck route until the customer location is resolved.
- What happens if a Kevin reroute is triggered for a truck that is already delayed? The additional reroute adds to the existing delay; the delay duration accumulates.
- What happens if a Kevin reroute is triggered while the truck is between stops (in motion, not yet arrived)? The via-point is inserted before the truck's next planned stop.
- What happens when two packages for the same customer are assigned to different trucks? Each package follows its assigned truck independently; the customer may receive two separate deliveries.
- What happens if the simulation is reset while trucks are in motion? All trucks return to at_warehouse status and packages return to their pre-dispatch status.

---

## Requirements *(mandatory)*

### Functional Requirements

**Map Display**

- **FR-001**: The system MUST display a map of Scranton, Pennsylvania as the delivery map view
- **FR-002**: The map MUST show the Dunder Mifflin office and warehouse as a single named marker representing the starting and return location for all trucks
- **FR-003**: The map MUST show exactly fourteen named customer locations with plausible fictional addresses inspired by Dunder Mifflin lore
- **FR-004**: The map MUST show at least three fast food locations within the Scranton area available as Kevin reroute destinations
- **FR-005**: The map MUST show at least three donut shop locations within the Scranton area available as Kevin reroute destinations
- **FR-006**: The map MUST show three delivery truck markers at their current GPS positions
- **FR-007**: The map MUST draw active delivery routes as lines connecting the warehouse through customer stops and returning to the warehouse
- **FR-008**: The map MUST update truck positions without requiring a manual page reload
- **FR-009**: The map MUST show return-to-warehouse route geometry when a truck is in returning status

**Trucks**

- **FR-010**: The system MUST have exactly three delivery trucks: Truck 1 "The Dundie", Truck 2 "Pretzel Day", and Truck 3 "Big Tuna"
- **FR-011**: Each truck MUST have a truck ID, truck number, truck name, current GPS coordinate, current status, current route, assigned packages, current stop, next stop, and delay information
- **FR-012**: Truck status MUST be one of: at_warehouse, loading, ready, on_route, rerouted, returning, completed, delayed
- **FR-013**: All trucks MUST start every route from the Dunder Mifflin office and warehouse location
- **FR-014**: All trucks MUST return to the Dunder Mifflin office and warehouse when their route is complete

**Truck Assignment**

- **FR-015**: A package MUST NOT be assignable to a truck unless its status is `ready_for_shipping`
- **FR-016**: A package MUST be assigned to exactly one truck at any given time
- **FR-017**: The system MUST prevent a package from being assigned to more than one truck simultaneously
- **FR-018**: Authorized personas MUST be able to reassign a package to a different truck while the package is still in `ready_for_shipping` status and the truck has not yet departed
- **FR-019**: When a package is in transit (status `in_transit` or `shipped`), the package's current location MUST reflect the assigned truck's current GPS coordinate
- **FR-020**: When a package is delivered, the package's current location MUST become the customer's location and MUST NOT continue to follow the truck

**Routes**

- **FR-021**: Routes MUST be dynamically calculated when a truck is dispatched
- **FR-022**: Each route MUST start at the Dunder Mifflin office and warehouse
- **FR-023**: Each route MUST include between three and twelve customer drop stops
- **FR-024**: Each route MUST end with a return segment to the Dunder Mifflin office and warehouse
- **FR-025**: Each route MUST include an estimated total time, current progress as a percentage or stop count, and geometry sufficient for drawing on the map
- **FR-026**: Routes MUST support optional via-points that can be inserted between existing stops for rerouting scenarios

**Truck Movement Simulation**

- **FR-027**: Truck movement MUST operate in accelerated demo time, completing a full delivery route in a workshop-practical duration
- **FR-028**: The system MUST update each truck's GPS coordinate at regular intervals as it moves along its route
- **FR-029**: The system MUST update any in-transit packages' current location each time the assigned truck's coordinate changes
- **FR-030**: The simulation state MUST be clearly visible: trainers and attendees MUST be able to determine each truck's status, current stop, and next stop without ambiguity
- **FR-031**: Truck movement MAY include minor speed variations to add demo realism, but MUST NOT produce erratic behavior that confuses the simulation state

**Delivery Behavior**

- **FR-032**: When a truck arrives at a customer stop, the system MUST mark all packages for that customer on that truck as delivered
- **FR-033**: When a package is delivered, the system MUST update the package location to the customer's location
- **FR-034**: When a package is delivered, the system MUST create a package history entry recording the delivery
- **FR-035**: When a package is delivered, the system MUST emit a meaningful delivery domain event
- **FR-036**: After completing a customer stop, the truck MUST automatically proceed to the next stop in the route
- **FR-037**: After completing all customer stops, the truck MUST begin its return to the warehouse
- **FR-038**: When the truck arrives at the warehouse, the route MUST be marked complete and the truck status MUST become completed or at_warehouse

**Kevin Hunger Reroute**

- **FR-039**: The system MUST support a Kevin hunger reroute operation that inserts a food or donut via-point into a truck's active route
- **FR-040**: Initiating a Kevin hunger reroute MUST require the user to select: a truck, a food or donut location, and a reason
- **FR-041**: A Kevin hunger reroute MUST insert the selected location as a via-point before the truck's next planned stop
- **FR-042**: A Kevin hunger reroute MUST NOT remove or reorder any existing customer stops in the route
- **FR-043**: A Kevin hunger reroute MUST NOT remove any package assignments from the truck
- **FR-044**: A Kevin hunger reroute MUST record delay information on the truck, including delay reason and estimated delay duration
- **FR-045**: A Kevin hunger reroute MUST create package history entries for all in-transit packages on the rerouted truck
- **FR-046**: A Kevin hunger reroute MUST emit a reroute domain event and a delay domain event
- **FR-047**: The Kevin hunger reroute operation MUST be available as a standard system action accessible through the same interfaces used by future agentic automation
- **FR-048**: Rerouting MUST be rejected for trucks that are in returning, completed, or at_warehouse status

**Permissions**

- **FR-049**: Rerouting MUST only be available to authorized personas
- **FR-050**: Michael Scott (manager) MUST be able to approve or force any reroute
- **FR-051**: The delay caused by a reroute MUST be clearly visible on the truck, the route detail, and in affected package records

**Map Interaction**

- **FR-052**: Users MUST be able to select a truck on the map to view its name, status, current stop, next stop, assigned packages, and delay information
- **FR-053**: Users MUST be able to select a customer marker on the map to view which packages are scheduled for delivery to that customer
- **FR-054**: Users MUST be able to view route details including all stops in order with estimated delivery times
- **FR-055**: Users MUST be able to view delivery progress (which stops are complete and which are remaining)
- **FR-056**: Authorized users MUST be able to initiate a Kevin hunger reroute from the map view

**Audit and Events**

- **FR-057**: All truck location changes MUST create audit history entries with actor, timestamp, source, previous location, and new location
- **FR-058**: All package location changes MUST create audit history entries
- **FR-059**: All route changes including reroutes MUST create audit history entries
- **FR-060**: All delivery events MUST create audit history entries in the package history

---

### Key Entities

- **Truck**: Named delivery vehicle with a permanent ID and name; holds current GPS coordinate, status, assigned route, assigned packages, current stop index, next stop index, and delay information
- **TruckRoute**: The calculated path for a truck's delivery run; includes ordered list of stops, optional via-points, geometry for map rendering, estimated duration, and current progress
- **RouteStop**: A single stop in a route; references a customer location and the packages to be delivered there; tracks whether the stop has been completed
- **ViaPoint**: An optional intermediate waypoint inserted into a route, not associated with a customer delivery — used for Kevin reroute food/donut detours; includes a label, GPS coordinate, and reason
- **MapLocation**: A named geographic point — one of: warehouse, customer, fast food location, or donut shop; includes name, GPS coordinate, and location type
- **SimulationState**: The current running state of the delivery simulation — tracks which trucks are active, the accelerated time scale, and whether the simulation is running or paused
- **TruckDelay**: Delay information attached to a truck — includes delay reason, delay duration estimate, and whether the delay is active

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A trainer can open the delivery map and see all three trucks, their names, and their routes within 5 seconds of page load with no additional setup required
- **SC-002**: A workshop attendee can identify the current location of any in-transit package by viewing the map; the displayed location matches the truck's position within one simulation tick
- **SC-003**: A full delivery simulation (warehouse → all stops → return) completes for at least one truck within 10 minutes of real elapsed time at the default accelerated demo speed
- **SC-004**: A Kevin hunger reroute can be initiated, confirmed, and reflected on the map (updated route line, rerouted status) within 15 seconds of the user confirming the action
- **SC-005**: The map refreshes truck positions automatically; no manual page reload is required to see truck movement during a simulation
- **SC-006**: Every truck location change, delivery event, and reroute event creates an auditable history entry that is accessible in the package history and event stream views
- **SC-007**: A trainer can reset the simulation to the baseline seed state and have all trucks return to at_warehouse status within 30 seconds

---

## Assumptions

- All customer, fast food, and donut locations use fictional but plausible GPS coordinates within the Scranton, Pennsylvania metropolitan area
- The Dunder Mifflin office and warehouse share a single GPS coordinate and are represented as one map marker
- The simulation tick rate (speed multiplier for accelerated time) is configurable by the system; the default rate allows a full route to complete within 5–10 minutes of real time
- Route geometry uses road-following paths, not straight-line connections between stops, to make the map realistic
- The seed data includes at least three food locations and three donut shop locations as fixed points on the map
- The fourteen customer locations are fixed in seed data and treated as manageable business records (their coordinates do not change after seeding)
- A truck may have between one and twelve packages assigned before it departs; the system does not auto-assign packages to trucks
- The Kevin hunger reroute is the only named rerouting scenario built into the baseline; the operation uses the same reroute interface that future agent scenarios will call
- Delivered packages remain at the customer location unless a return is initiated through the existing return workflow (Feature 1); this feature does not modify the return flow
- The simulation does not run in the background when the application is closed; it runs as part of the application server process
- Package reassignment between trucks is only permitted while the package is in `ready_for_shipping` status and the destination truck has not yet departed
