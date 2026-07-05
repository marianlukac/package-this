# Feature Specification: Persona-Based Workplace UI

**Feature Branch**: `002-persona-workplace-ui`  
**Created**: 2026-06-21  
**Status**: Draft  
**Input**: User description: "Create a functional specification for Feature 2: Persona-Based Workplace UI."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persona Switcher and Contextual Dashboard (Priority: P1)

A workshop attendee selects a persona from the persona switcher and immediately sees a dashboard tailored to that persona's workplace concerns. Switching personas changes what is emphasized, what metrics are shown, and what actions are available — without requiring a page reload or login.

**Why this priority**: The persona switcher is the entry point to the entire workshop experience. Every other persona-specific behavior depends on it. Without it, the application has no workshop narrative.

**Independent Test**: Open the application. Confirm the persona switcher is visible. Select "Michael Scott." Verify the dashboard shows manager-specific metrics including packages at risk and playful metrics. Select "Darryl Philbin." Verify the dashboard shifts to warehouse-focused content. Select "Angela Martin." Verify the dashboard shifts to invoice and accounting content. The persona name and role must be prominently visible after each switch.

**Acceptance Scenarios**:

1. **Given** no persona is selected, **When** a user opens the application, **Then** the persona switcher is the first prominent element and the user is invited to select a persona before the dashboard is populated.
2. **Given** a persona is selected, **When** the user views the dashboard, **Then** the content is filtered and organized to emphasize the concerns of that persona role.
3. **Given** Michael Scott is selected, **When** the user views the dashboard, **Then** both serious operational metrics and playful Dunder Mifflin metrics are shown.
4. **Given** a non-manager persona is selected, **When** the user attempts a manager-only action, **Then** the action is visually indicated as unavailable and the reason is clearly explained.
5. **Given** any persona is selected, **When** the user switches to a different persona, **Then** the entire UI updates to reflect the new persona's emphasis without requiring a page reload.

---

### User Story 2 - Package List with Persona-Filtered View (Priority: P1)

Any persona can navigate to the package list and see packages relevant to their role. The list is searchable and filterable. Each row shows enough context to understand the package at a glance. The active persona determines which filters are pre-applied and which columns receive visual emphasis.

**Why this priority**: The package list is the primary operational view of the system. Trainers and attendees will spend most of their demo time here, and it must work for all four persona groups.

**Independent Test**: As Jim Halpert (sales), open the package list. Verify that packages are shown with package ID, customer, salesperson, invoice creator, status, delay indicator, assigned truck, location summary, last updated time, priority, and fragile indicator. Apply a filter by status. Verify the list updates. Search by customer name. Verify results narrow. Sort by priority. Verify the order changes.

**Acceptance Scenarios**:

1. **Given** a sales persona is active, **When** viewing the package list, **Then** packages are pre-filtered to show packages from that salesperson's sales, and customer name and complaint indicators receive visual emphasis.
2. **Given** a warehouse persona is active, **When** viewing the package list, **Then** packages with status `ready_for_shipping` and `packaged` are emphasized and truck assignment column is prominent.
3. **Given** an accounting persona is active, **When** viewing the package list, **Then** invoice-related columns are emphasized and packages with terminal statuses (delivered, returned, damaged, cancelled) are surfaced.
4. **Given** the package list is displayed, **When** a user applies a filter (status, customer, salesperson, truck, delayed, exception state), **Then** the list updates to show only matching packages.
5. **Given** the package list is displayed, **When** a user types in the search field, **Then** the list filters to packages matching the search term across package ID, customer name, and contents summary.
6. **Given** the package list is displayed, **When** a user clicks a column header, **Then** the list sorts by that column and the direction toggles on repeated clicks.

---

### User Story 3 - Package Detail Page with Persona-Aware Actions (Priority: P1)

A user navigates to a package detail page and sees the full package record including sale and invoice relationship, customer, line items, status, location, truck, route, complaints, delay information, and history. The available actions on the page are determined by the active persona.

**Why this priority**: The package detail page is where all meaningful package interactions happen. It must show the complete picture while surfacing only the actions the active persona is permitted to take.

**Independent Test**: As Darryl Philbin (warehouse), navigate to a package in `packaged` status. Verify the detail page shows all required sections. Verify the lifecycle advancement button for `ready_for_shipping` is visible and functional. Switch to Jim Halpert (sales) and return to the same package. Verify the lifecycle button is absent. Attempt to advance status via the underlying system call with Jim's persona. Verify the system rejects it.

**Acceptance Scenarios**:

1. **Given** any persona is active, **When** a user opens a package detail page, **Then** the page shows: package summary, sale and invoice link, customer, line items, current status badge, current location, assigned truck, delivery route (if applicable), complaints, delay information, and package history timeline.
2. **Given** a warehouse persona is active, **When** viewing a non-terminal package, **Then** lifecycle advancement buttons and delay recording options are visible.
3. **Given** a manager persona is active, **When** viewing a package, **Then** manager action buttons (Override Priority, Approve Reroute, Approve Return, Approve Expensive Delivery, Force Truck Reassignment, Mark Customer Unhappy) are visible.
4. **Given** a sales persona is active, **When** viewing a package, **Then** complaint creation is available but lifecycle advancement buttons are absent.
5. **Given** a terminal package is open, **When** any persona views it, **Then** all lifecycle action buttons are hidden and a terminal status indicator is shown.
6. **Given** a package detail page is open, **When** an action is performed and succeeds, **Then** the history timeline updates in place without requiring a full page reload.

---

### User Story 4 - Status Cards and Navigation (Priority: P2)

The main dashboard shows package status cards grouped by lifecycle stage. Each card shows a count and visual indicator. The navigation gives access to all primary views: dashboard, packages, customers, sales and invoices, trucks and routes, event stream, and demo controls.

**Why this priority**: Status cards provide the at-a-glance operational picture that workshop trainers use to drive demo narratives. Navigation must be consistent across all views.

**Independent Test**: Open the application as Michael Scott. Verify status cards are shown for each package status with correct counts. Click a status card. Verify the package list pre-filtered to that status opens. Verify the top navigation has links to all primary views. Verify demo controls are accessible only when Michael is the active persona.

**Acceptance Scenarios**:

1. **Given** any persona is active, **When** viewing the dashboard, **Then** status cards are shown for each package lifecycle stage with a count of packages in that stage.
2. **Given** a status card is clicked, **When** the user navigates, **Then** the package list opens pre-filtered to that status.
3. **Given** Michael Scott is the active persona, **When** viewing the dashboard, **Then** a "Manager Dashboard" section shows serious operational metrics and a separate playful metrics section.
4. **Given** any persona is active, **When** navigating the application, **Then** the current section and active persona are both clearly visible in the navigation.
5. **Given** a non-manager persona is active, **When** viewing the navigation, **Then** the demo controls section is not shown.

---

### User Story 5 - Demo Controls for Trainers (Priority: P2)

Michael Scott persona has access to demo controls. From the demo controls panel, a trainer can reset the system to its baseline seed state or trigger one of several demo scenarios that create interesting package situations for demonstration purposes.

**Why this priority**: Demo reliability is a constitution requirement. Trainers need to reset state quickly and trigger specific situations for different workshop segments.

**Independent Test**: Select Michael Scott. Navigate to demo controls. Click "Reset Demo." Confirm the dialog. Verify the system returns to its baseline state and the package list reflects the seed data counts. Trigger the "Kevin Hunger Reroute" scenario. Verify a delay is recorded on at least one package. Trigger "Damaged in Transit." Verify at least one package moves to damaged status.

**Acceptance Scenarios**:

1. **Given** Michael Scott is the active persona, **When** a trainer clicks "Reset Demo" and confirms the dialog, **Then** all package, complaint, and truck data returns to the baseline seed state.
2. **Given** Michael Scott is the active persona, **When** a trainer triggers a demo scenario, **Then** the system executes the scenario and the UI reflects the resulting state changes.
3. **Given** a non-manager persona is active, **When** the trainer attempts to access demo controls, **Then** the demo controls panel is not accessible.
4. **Given** a demo scenario is running, **When** the system is applying changes, **Then** a loading indicator is shown and the controls are disabled until the scenario completes.
5. **Given** a scenario completes, **When** the result is displayed, **Then** the trainer sees a summary of what changed (which packages were affected and how).

---

### User Story 6 - Event Stream and Real-Time Awareness (Priority: P3)

Any user can view a live event stream showing recent system activity. Events appear as they happen, showing what changed, who changed it, and when. The stream makes the system's activity visible for workshop demonstration purposes.

**Why this priority**: The event stream is a workshop showcase feature. It is not required for core package operations but is valuable for demonstrating the event-driven nature of the system.

**Independent Test**: Open the event stream view. Advance a package status from another browser tab. Verify the event appears in the stream within 5 seconds. Verify each entry shows event type, summary, actor, timestamp, and source.

**Acceptance Scenarios**:

1. **Given** the event stream is open, **When** any system event occurs (status change, manager action, complaint), **Then** an entry appears in the stream within 5 seconds.
2. **Given** events appear in the stream, **When** the user reads an entry, **Then** each entry shows event type, summary, actor, timestamp, and source.
3. **Given** the stream is active, **When** more than 100 events have accumulated, **Then** older events are removed from the display to keep the stream manageable.
4. **Given** the event stream is running, **When** the user clicks pause, **Then** new events are queued but not shown until the user resumes.

---

### Edge Cases

- What happens when a persona is selected but the system has no packages in any status? Each status card shows 0 and the package list shows an empty state with a call to action.
- What happens if the system call to advance a package status returns 403 because the persona was switched mid-session? The error message shows the reason including the expected permission and the current persona.
- What happens when Michael's playful metrics reference a persona who has no packages (e.g., "Dwight escalation count" is zero)? The metric displays as 0 with an appropriate message rather than hiding the card.
- What happens if a user has the package list filtered and then switches personas? The filter is cleared and the new persona's default view is applied.
- What happens if demo controls are triggered while a simulation tick is in progress? The system either queues the scenario after the tick or provides feedback that it is temporarily unavailable.

---

## Requirements *(mandatory)*

### Functional Requirements

**Persona Switcher**

- **FR-001**: The system MUST provide a persona switcher displaying all 12 predefined Dunder Mifflin employees with name, role, visual identity, and a short description of their workplace concerns.
- **FR-002**: The active persona MUST be persistently shown throughout the UI so it is never ambiguous which persona is active.
- **FR-003**: Switching persona MUST update the dashboard emphasis, visible actions, and pre-applied filters without requiring a full page reload.
- **FR-004**: The system MUST enforce persona-based permission restrictions on all write operations at the system level, not only in the interface.
- **FR-005**: An unavailable action MUST display an explanation of why it is unavailable, including the required permission and the active persona.

**Dashboard and Navigation**

- **FR-006**: The application MUST include navigation to: main dashboard, packages, customers, sales and invoices, trucks and routes, event stream, and demo controls.
- **FR-007**: The dashboard MUST show package status cards grouped by lifecycle stage, each displaying a count of packages in that status.
- **FR-008**: Clicking a status card MUST navigate to the package list pre-filtered by that status.
- **FR-009**: The dashboard MUST show persona-appropriate content: sales metrics for sales personas, invoice and financial metrics for accounting personas, truck and readiness metrics for warehouse personas, and full operational metrics for the manager persona.
- **FR-010**: Michael Scott's dashboard MUST include a manager section with both serious operational metrics (packages at risk, delayed, backorders, complaints, damaged, returned, truck status, invoice summary, manager actions pending) and playful metrics defined as follows:
  - **Kevin-related reroutes**: packages where Kevin Malone is the salesperson and the delay reason references hunger or a truck was rerouted.
  - **Most dramatic incident**: the package with the greatest number of history entries.
  - **Dwight escalation count**: complaints raised by Dwight Schrute with high priority.
  - **Pretzel Day truck status**: always displays "All clear — no pretzel emergency" in the baseline; reserved for future demo scenario use.
  - **Regional manager attention score**: the sum of open complaints, delayed packages, and at-risk packages, shown with a humorous label.
  - **Customer unhappiness warning**: count of customers marked as unhappy.
- **FR-011**: Demo controls MUST be accessible only when Michael Scott is the active persona.

**Package List**

- **FR-012**: The package list MUST display for each package: package ID, customer, salesperson, invoice creator, status, delay indicator (when applicable), assigned truck (when applicable), current location summary, last updated time, priority, and fragile indicator.
- **FR-013**: The package list MUST support search across package ID, customer name, and contents summary.
- **FR-014**: The package list MUST support filtering by: status, customer, salesperson, invoice creator, assigned truck, delayed packages, and exception state (damaged, cancelled, returned).
- **FR-015**: The package list MUST support sorting by: last updated time, expected delivery time, and priority.
- **FR-016**: Sales personas MUST see packages from their own sales pre-filtered by default. Warehouse personas MUST see packages in actionable statuses emphasized by default.

**Package Detail**

- **FR-017**: The package detail page MUST show: package summary, sale and invoice relationship, customer, line items, current status, current location, assigned truck, delivery route (when applicable), complaints, delay information, and package history.
- **FR-018**: The package detail page MUST show action buttons appropriate to the active persona. Actions must not be shown to personas who cannot perform them.
- **FR-019**: The package history section MUST show all history entries in reverse-chronological order, each with event type, actor, timestamp, source, and previous/new values where applicable.
- **FR-020**: Terminal package status MUST be prominently indicated. All lifecycle action buttons MUST be hidden for terminal packages.

**Demo Mode**

- **FR-021**: The demo controls panel MUST support resetting the system to the baseline seed state, with a confirmation step before execution.
- **FR-022**: The demo controls MUST support triggering named scenarios: delayed delivery, damaged package, Kevin hunger reroute, complaint escalation, and return request.
- **FR-023**: Each demo scenario MUST display a summary of affected entities after completion.

**Accessibility and Usability**

- **FR-024**: The UI MUST provide clear empty states for views with no data and loading states for all async operations.
- **FR-025**: The UI MUST provide error feedback when a system operation fails, including human-readable explanation.
- **FR-026**: The UI MUST provide success feedback when a write operation completes.
- **FR-027**: The UI MUST be responsive and usable on standard desktop and tablet viewports.
- **FR-028**: The UI MUST meet WCAG 2.1 AA contrast requirements for all text and interactive elements.
- **FR-029**: All interactive elements MUST be navigable via keyboard.

### Key Entities

- **Persona**: One of 12 predefined employees; has a name, role group (manager, sales, accounting, warehouse, reception, qa), avatar representation, and a description of their workplace concerns. Determines which operations are permitted and which dashboard view is presented.
- **Dashboard View**: The persona-specific arrangement of metrics, status cards, and quick links shown on the main dashboard. There are four distinct dashboard views: manager, sales, accounting, and warehouse (reception and QA personas use a general-purpose view).
- **Status Card**: A count card representing one package lifecycle status. Clicking navigates to the filtered package list.
- **Demo Scenario**: A named, reproducible sequence of system operations that creates a specific package situation for demonstration. Each scenario has a name, description, and a list of affected entities it produces.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time workshop attendee can identify the active persona and understand their role within 10 seconds of opening the application.
- **SC-002**: A trainer can switch between all 12 personas and verify the dashboard changes within 60 seconds total.
- **SC-003**: A trainer can reset the system to baseline seed state in under 30 seconds including confirmation.
- **SC-004**: When a persona attempts an unauthorized action, the explanation of why it is unavailable must be understandable without needing to read any documentation.
- **SC-005**: The package list must render with all columns and filters functional for 100+ packages within 2 seconds of navigation.
- **SC-006**: Events in the event stream must appear within 5 seconds of the originating system action.
- **SC-007**: All views must remain fully readable and functional on viewports 768px wide and above.
- **SC-008**: 100% of write operations that require a specific persona permission must be rejected at the system level when the active persona does not have that permission.

---

## Assumptions

- The 12 predefined employees from Feature 1 are already in the system; this feature does not add new employees.
- Persona selection is stored locally in the user's browser for the duration of their session; it is not a server-side authentication mechanism.
- Pam Beesly (reception) and Ryan Howard (temp) and Creed Bratton (QA) use a general-purpose dashboard view; they are not assigned to a named functional group with a distinct dashboard layout. Their permission sets are defined in the system but their dashboard does not have a separate specialized layout.
- The playful manager metrics are derived from existing package, complaint, and audit data using naming conventions (e.g., packages associated with Kevin Malone as salesperson count toward "Kevin-related" metrics); they do not require separate data storage.
- Visual identity for each persona (avatar) is represented by initials or a colored badge using the persona's name; photographs are not required.
- The demo controls panel is a dedicated section within the navigation visible only to the manager persona; it is not a separate application mode.
- Real-time event updates use the same event infrastructure defined in Feature 1; this feature consumes those events for UI display purposes only.
