---
description: "Task list for Persona-Based Workplace UI — Dunder Mifflin Package Manager"
---

# Tasks: Persona-Based Workplace UI

**Input**: Design documents from `specs/002-persona-workplace-ui/`
**Prerequisites**: plan.md ✅ spec.md ✅
**Baseline**: Feature 1 (Core Package Operations) fully implemented. All tasks below are
enhancements and additions that build persona differentiation on top of the existing application.

**Tests**: Not requested in spec. Tasks focus on implementation correctness verified by running
the application with each persona.

**Organization**: Phase 1 adds the foundational persona-profile data model. Phases 3–8 map to
US1–US6 in priority order. Final phase handles polish and accessibility hardening.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US6)
- Exact file paths included in every task description

---

## Phase 1: Setup (Persona Data Foundation)

**Purpose**: Introduce the PersonaProfile data structure and shared persona helpers that every
user story depends on. These are new additions not present in Feature 1.

- [X] T001 Create `frontend/src/app/models/persona-profile.ts`: TypeScript interface `PersonaProfile` with fields `employeeId: string`, `name: string`, `role: string`, `roleGroup: 'manager' | 'sales' | 'accounting' | 'warehouse' | 'general'`, `initials: string`, `themeColor: string`, `description: string` (short what-they-care-about blurb shown in switcher)
- [X] T002 [P] Create `frontend/src/app/data/persona-profiles.ts`: `PERSONA_PROFILES` constant array of `PersonaProfile` for all 12 employees — michael-scott (manager/dm-blue), dwight-schrute (sales/dm-gold), jim-halpert (sales/green), phyllis-vance (sales/purple), stanley-hudson (sales/orange), angela-martin (accounting/gray), kevin-malone (accounting/yellow), pam-beesly (general/pink), darryl-philbin (warehouse/teal), roy-anderson (warehouse/red), ryan-howard (general/indigo), creed-bratton (general/slate); include a short `description` for each persona reflecting their Dunder Mifflin concerns
- [X] T003 [P] Create `frontend/src/app/components/persona-unavailable/persona-unavailable.component.ts`: standalone Angular component that accepts `@Input() requiredRole: string` and `@Input() action: string`; renders a disabled-styled button or inline message explaining "This action requires [role]. You are currently [active persona]." Used by all action buttons to show rather than hide restricted actions

**Checkpoint**: Persona profile data and the unavailable-action component exist and can be imported.

---

## Phase 2: Foundational (PersonaService Enhancement)

**Purpose**: Extend `PersonaService` with persona-type helpers that all downstream components use
to route to the correct dashboard view and apply correct filters. Must complete before any user
story begins.

**⚠️ CRITICAL**: All user story phases depend on the updated PersonaService.

- [X] T004 Update `frontend/src/app/services/persona.service.ts`: import `PERSONA_PROFILES` from T002; add computed signals `currentPersonaProfile = computed(...)`, `isManager = computed(...)`, `isSales = computed(...)`, `isAccounting = computed(...)`, `isWarehouse = computed(...)`; add `getRoleGroup(): string` that returns the `roleGroup` for the current persona; add `canPerform(operation: string): boolean` that calls the existing employee-permissions logic from `ApiService` or derives from the current persona's role group using a local `ROLE_PERMISSIONS` map matching the backend's `PERSONA_PERMISSIONS` dict

**Checkpoint**: `PersonaService` exposes `isManager()`, `isSales()`, `isAccounting()`, `isWarehouse()`, `canPerform()` and `currentPersonaProfile` for all downstream components.

---

## Phase 3: User Story 1 — Persona Switcher and Contextual Dashboard (Priority: P1) 🎯 MVP

**Goal**: The persona switcher shows avatar, role, and description for each employee. The dashboard
renders persona-specific content — sales metrics for sales, invoice metrics for accounting, truck
readiness for warehouse, and full operational + playful metrics for Michael.

**Independent Test**: Open the application. Select Michael Scott. Verify the dashboard shows both
serious metrics (packages at risk, delayed, complaints) and playful metrics (Kevin-related reroutes,
Dwight escalation count). Switch to Angela Martin. Verify the dashboard shows invoice and financial
exception content. Switch to Darryl Philbin. Verify the dashboard shows truck and readiness content.
Confirm the persona avatar (initials + color badge) and description are visible in the switcher
after every switch.

- [X] T005 [P] [US1] Update `frontend/src/app/components/persona-switcher/persona-switcher.component.ts`: replace plain employee name list with cards showing: colored initials avatar (using `themeColor` from PersonaProfile), employee name, role badge, and `description` blurb; highlight the currently selected card with a border or background; load `PERSONA_PROFILES` from T002 and merge with employee list from `GET /employees`
- [X] T006 [P] [US1] Create `frontend/src/app/components/dashboard-sales/dashboard-sales.component.ts`: standalone Angular component showing sections — "My Packages" (filtered by current salesperson, sorted by last_updated), "My Customers" (customer list with complaint indicator), "Delays Affecting My Sales" (packages from my sales with delay_reason set), "Complaints on My Sales" (open complaint count with link to list); fetches data via `ApiService.getPackages({salesperson_id: currentPersonaId})` and `ApiService.getComplaints({salesperson_id: currentPersonaId})`
- [X] T007 [P] [US1] Create `frontend/src/app/components/dashboard-accounting/dashboard-accounting.component.ts`: standalone Angular component showing sections — "Invoices Overview" (total invoices, invoices by creator), "Financial Exception Packages" (packages with terminal status: returned, damaged, cancelled grouped by status with counts), "Return and Damage Impact" (count of packages in each terminal state requiring follow-up), "Recent Invoice Activity" (recent sales/invoice list); fetches data via `ApiService.getSales()` and `ApiService.getPackages({status: ['delivered','returned','damaged','cancelled']})`
- [X] T008 [P] [US1] Create `frontend/src/app/components/dashboard-warehouse/dashboard-warehouse.component.ts`: standalone Angular component showing sections — "Ready for Action" (packages in `packaged` and `ready_for_shipping` statuses as count cards), "Active Trucks" (list of all trucks with current status, route stop, and package count), "Damaged Packages" (count card + recent damaged packages), "Delivery Readiness" (packages in `ready_for_shipping` older than 24 hours as a warning list); fetches via `ApiService.getPackages({status: ['packaged','ready_for_shipping','damaged']})` and `ApiService.getTrucks()`
- [X] T009 [US1] Create `frontend/src/app/components/dashboard-manager/dashboard-manager.component.ts`: standalone Angular component with two clearly separated sections:
  **Serious Metrics** (grid of count cards): packages at risk (from `/packages/at-risk`), delayed deliveries, backorders (`order_created` + `backorder`), open complaints, damaged packages, returned packages, active trucks, pending manager actions (estimate from recent audit log);
  **Playful Metrics** (lighter visual treatment): Kevin-related reroutes (packages where salesperson is kevin-malone and delay_reason contains "hungry" or truck was rerouted), most dramatic incident (package with the most history entries), Dwight escalation count (complaints with priority high created by dwight-schrute), Pretzel Day truck status (hardcoded "All clear — no pretzel emergency" with a 🥨 unless a specific flag is set), regional manager attention score (a computed integer from open complaints + delayed + at-risk — shown with a humorous label), customer unhappiness warning (count of customers marked is_unhappy);
  fetches via `ApiService.getOperationalSummary()`, `ApiService.getPackages(...)`, `ApiService.getComplaints(...)`, and `ApiService.getCustomers()`
- [X] T010 [US1] Update `frontend/src/app/components/dashboard/dashboard.component.ts`: use `PersonaService.getRoleGroup()` to conditionally render `DashboardSalesComponent`, `DashboardAccountingComponent`, `DashboardWarehouseComponent`, or `DashboardManagerComponent`; for `roleGroup === 'general'` render a simple view with `StatusCardsComponent` and a recent packages list (no persona-specific sections); import all four sub-dashboard components as standalone
- [X] T011 [US1] Update `backend/app/routers/packages.py` `GET /operational-summary` response to include additional manager-specific fields: `backorder_count` (packages with status `backorder`), `order_created_count`, `customer_unhappy_count` (customers with `is_unhappy = true`); update the `OperationalSummary` response schema in `backend/app/schemas/` to reflect these fields

**Checkpoint**: US1 fully functional. Each persona sees a differentiated dashboard. Michael sees
serious operational metrics and the playful Dunder Mifflin section.

---

## Phase 4: User Story 2 — Package List with Persona-Filtered View (Priority: P1)

**Goal**: The package list applies persona-specific default filters on load and emphasizes the
columns most relevant to the active persona. All filter and sort controls function correctly.

**Independent Test**: As Jim Halpert (sales), navigate to the package list. Verify packages are
pre-filtered to show only packages from Jim's sales. Clear the filter. Verify all packages appear.
As Darryl Philbin (warehouse), verify packages in `packaged` and `ready_for_shipping` are shown
first and the truck column is visually prominent. Apply the "delayed" filter. Verify only packages
with a delay_reason are shown. Sort by priority. Verify the order changes.

- [X] T012 [US2] Update `frontend/src/app/components/package-list/package-list.component.ts`: on component init, detect `PersonaService.getRoleGroup()` and apply default filters — `sales`: `{salesperson_id: currentPersonaId}`; `warehouse`: `{status: ['packaged','ready_for_shipping','in_transit']}`; `accounting`: no default filter (show all); `manager` and `general`: no default filter; expose a "Reset to my defaults" button that re-applies the persona default filters; store active filters in component state so the filter UI reflects them; verify sort controls exist for last_updated, expected_delivery_time, and priority (FR-015) — add expected_delivery_time and priority sort options if only last_updated sort was implemented in Feature 1
- [X] T013 [P] [US2] Update `frontend/src/app/components/package-list/package-list.component.ts` column set and emphasis: first verify all 11 columns from FR-012 are present — package ID, customer, salesperson, invoice creator, status, delay indicator, assigned truck, current location summary, last updated time, priority, fragile indicator — add any missing columns; then add a complaint count badge column for sales personas; apply persona column emphasis via `[ngClass]` — warehouse: bold "Assigned Truck" and "Status"; sales: emphasize "Customer"; accounting: emphasize "Invoice Creator" and highlight terminal status rows
- [X] T014 [P] [US2] Verify search and filter controls in `frontend/src/app/components/package-list/package-list.component.ts` and `frontend/src/app/services/api.service.ts`: (1) confirm the search input field is present and calls `ApiService.getPackages({search: term})` — search must query across package ID, customer name, and contents summary (FR-013); (2) add any missing filter parameters to `getPackages()` — `invoice_creator_id`, `truck_id`, `has_delay`, `exception_state` (one of: `damaged`, `cancelled`, `returned`); (3) update `backend/app/routers/packages.py` `GET /packages` query params to accept `search`, `invoice_creator_id`, `truck_id`, `has_delay`, and `exception_state` if not already present

**Checkpoint**: US2 functional. Each persona sees relevant packages first. All 8 filter types and
3 sort options work. Persona-specific column emphasis is visible.

---

## Phase 5: User Story 3 — Package Detail with Persona-Aware Actions (Priority: P1)

**Goal**: The package detail page shows all required sections. Actions unavailable to the active
persona are shown as disabled with an explanation rather than hidden entirely.

**Independent Test**: As Darryl Philbin (warehouse), open a package in `packaged` status. Verify
all 12 required sections are visible. Confirm the "Ready for Shipping" advancement button is
enabled. Switch to Jim Halpert (sales) on the same package. Verify lifecycle buttons are now
shown as disabled with an explanation ("This action requires warehouse or manager role. You are
currently Jim Halpert / Sales."). Open a terminal package as any persona. Verify all lifecycle
buttons are absent and a terminal status badge is prominent.

- [X] T015 [US3] Audit `frontend/src/app/components/package-detail/package-detail.component.ts` against all 12 required sections from spec FR-017: package summary, sale+invoice link, customer, line items, current status, current location, assigned truck, delivery route (if applicable), complaints, delay information, package history; add any missing sections; ensure each section has a clear heading and an empty state when data is not applicable
- [X] T016 [US3] Update action buttons in `frontend/src/app/components/package-detail/package-detail.component.ts`: replace any `*ngIf="canAdvance"` patterns with a visible-but-disabled pattern using `PersonaUnavailableComponent` from T003; warehouse lifecycle buttons → disabled with explanation for non-warehouse/non-manager personas; manager action buttons → disabled with explanation for non-manager personas; cancellation and damage buttons → disabled with explanation for non-warehouse/non-manager personas; terminal packages → all lifecycle buttons hidden (terminal state is a hard hide, not a soft disable)
- [X] T017 [P] [US3] Verify `frontend/src/app/components/package-history/package-history.component.ts` renders all 15 event types listed in spec FR-019 with correct icon or badge per event type; add any missing event type renderings; ensure previous_value / new_value diff is shown as `"old → new"` for `status_changed`, `priority_changed`, and `location_updated` events; ensure `manager_action_performed` entries show the action name prominently

**Checkpoint**: US3 functional. All sections present on package detail. Restricted actions visible
as disabled with explanations. History covers all 15 event types.

---

## Phase 6: User Story 4 — Status Cards and Navigation (Priority: P2)

**Goal**: Status cards cover all lifecycle stages, clicking a card navigates to the filtered list,
and navigation consistently shows the active persona. Demo controls are hidden from non-managers.

**Independent Test**: As Michael Scott, verify all 10 package statuses have a status card
(including terminal statuses). Click the "Damaged" card. Verify the package list opens filtered
to damaged packages. Verify the top navigation shows Michael's name and avatar. Switch to Roy
Anderson. Verify "Demo Controls" is absent from the navigation. Verify Roy's avatar appears.

- [X] T018 [P] [US4] Audit `frontend/src/app/components/status-cards/status-cards.component.ts`: ensure all 10 package statuses have a card (order_created, backorder, packaged, ready_for_shipping, in_transit, delivered, cancelled, damaged, returned, and the operational state "delayed" as a derived count); clicking each card must emit a filter event or navigate to `/packages?status=[status]`; terminal status cards (cancelled, damaged, returned) should have a visually distinct styling (muted or red-tinted) to indicate they are end states
- [X] T019 [US4] Update `frontend/src/app/app.component.ts` navigation bar: add links for all required views — Dashboard, Packages, Customers, Sales & Invoices, Trucks & Routes, Event Stream; add the `PersonaSwitcherComponent` inline in the nav bar (compact mode showing only initials avatar + name); show "Demo Controls" link only when `PersonaService.isManager()` is true; ensure the currently active route link is highlighted

**Checkpoint**: US4 functional. All 10 status cards present. Navigation complete with all
required views. Demo controls hidden for non-managers.

---

## Phase 7: User Story 5 — Demo Controls for Trainers (Priority: P2)

**Goal**: Demo controls support all 5 named scenarios with descriptive labels, loading states,
result summaries, and a confirmation-guarded reset. Visible only to Michael.

**Independent Test**: Select Michael Scott. Navigate to Demo Controls. Click "Reset Demo" and
confirm. Verify the system resets and the package list reflects baseline counts. Click "Kevin's
Hunger Reroute." Verify a loading indicator appears. After completion, verify a result summary
shows which package was affected and that the package shows a delay reason referencing hunger.

- [X] T020 [US5] Update `frontend/src/app/components/demo-controls/demo-controls.component.ts`: add all 5 scenario buttons with labels and one-line descriptions — "Delayed Delivery" (A package gets stuck in transit with a delay reason), "Damaged in Transit" (A package is marked damaged en route), "Kevin's Hunger Reroute" (Kevin redirects the truck for a snack detour, causing a delay), "Complaint Escalation" (An angry customer creates a complaint on an in-transit package), "Return Request" (A delivered package is marked for return by manager approval); each button must show a loading spinner and disable all controls while executing; show the result summary in an inline panel below the buttons after completion — this panel serves as the FR-026 success feedback signal for demo operations; the summary must name which package(s) were affected and what changed
- [X] T021 [P] [US5] Add `kevin-hunger-reroute` scenario to `backend/app/services/demo_service.py` `run_scenario()` dispatcher: scenario selects a package assigned to kevin-malone (salesperson), records a delay on it with `delay_reason="Truck rerouted — driver hungry"` and `delay_duration_hours=1`, publishes a `package.delay_recorded` event, returns affected package_id; map scenario name `"kevin-hunger-reroute"` in the router's `POST /demo/scenarios/{scenario_name}` dispatch

**Checkpoint**: US5 functional. All 5 named scenarios work, each with loading state and result
summary. Kevin scenario creates a delay with the correct reason string.

---

## Phase 8: User Story 6 — Event Stream (Priority: P3)

**Goal**: The event stream shows all required fields per entry, auto-scrolls to latest, enforces
the 100-entry cap, and exposes a keyboard-accessible pause button with an ARIA live region.

**Independent Test**: Open the Event Stream view. In another tab advance a package status. Verify
the event appears in the stream within 5 seconds showing event type badge, summary, actor, timestamp,
and source chip. Click "Pause." Advance another package status. Verify the new event does not
appear. Click "Resume." Verify queued events appear.

- [X] T022 [P] [US6] Audit `frontend/src/app/components/event-stream/event-stream.component.ts`: ensure each entry renders event type (badge), summary text, actor name, ISO timestamp formatted as relative time (e.g., "2 min ago"), and source chip (`ui` / `api` / `demo` / `agent` / `system`); add Pause/Resume toggle button; when paused, accumulate events in a buffer and display them all on Resume; maintain a max of 100 entries in the display list (drop oldest)
- [X] T023 [P] [US6] Add ARIA support to `frontend/src/app/components/event-stream/event-stream.component.ts`: wrap the stream list in a `<div role="log" aria-live="polite" aria-label="Event stream">` region; the Pause button must be `aria-pressed="true/false"` toggling with keyboard focus; add auto-scroll behavior (implementation choice beyond the spec) — suspend auto-scroll when the user manually scrolls up, detected via scroll position comparison, and resume when the user scrolls back to the bottom; document this behavior in an inline comment as a UX enhancement not derived from the spec

**Checkpoint**: US6 functional. Event stream shows all required fields, pauses/resumes, respects
the 100-entry limit, and meets ARIA requirements.

---

## Phase 9: Polish and Accessibility Hardening

**Purpose**: Cross-cutting quality improvements affecting all user stories.

- [X] T024 [P] Audit all Tailwind CSS color usage in `frontend/src/styles.css` and all component templates against WCAG 2.1 AA contrast ratios (4.5:1 for normal text, 3:1 for large text): check dm-blue (#1e3a5f) and dm-gold (#c9a227) against white and against each other; check all persona theme colors from T002 against white badge text; fix any failing combination by adjusting the shade or adding a text shadow
- [X] T025 [P] Add loading skeleton states to `frontend/src/app/components/dashboard/dashboard.component.ts`, `frontend/src/app/components/package-list/package-list.component.ts`, and `frontend/src/app/components/package-detail/package-detail.component.ts`: while any async data call is in-flight, show a skeleton placeholder (gray animated bars) rather than a blank area; use Angular's `isLoading` signal pattern already established in the app
- [X] T026 [P] Add persona-appropriate empty states and keyboard navigation to the new dashboard sub-components (T006, T007, T008, T009): (1) empty states — sales: "No packages for your sales yet — create a sale to get started"; accounting: "All invoices clear — no exception packages"; warehouse: "All packages are moving — nothing to action right now"; manager: "Operations running smoothly — Michael approves"; (2) keyboard navigation audit (FR-029, constitution Principle IX) — verify all interactive elements (status card links, package row links, complaint links, action buttons) in each sub-dashboard are reachable via Tab and activated via Enter/Space; add `tabindex="0"` and `(keydown.enter)` handlers to any non-native-interactive elements; (3) error feedback (FR-025) — verify each sub-dashboard shows a human-readable error banner if its API calls fail, e.g., "Could not load your packages. Please try again."
- [X] T027 Update `docs/persona-guide.md`: add a column to the persona table for "Avatar Color" and "Cares About" (the description blurb from T002); update the "How to switch personas in the UI" section to describe the new avatar-based switcher; keep the existing permission table and API header instructions
- [X] T028 [P] Add pytest test to `backend/tests/test_api_packages.py`: verify `GET /operational-summary` response includes new fields `backorder_count` (int), `order_created_count` (int), and `customer_unhappy_count` (int) added in T011; assert all three fields are present and non-negative in the seed-data state
- [X] T029 [P] Add pytest test to `backend/tests/test_seed.py`: verify `POST /demo/scenarios/kevin-hunger-reroute` (with michael-scott persona) returns HTTP 200, affects exactly one package, and that package has `delay_reason` containing "hungry"; assert the delay was written to both `Package` and `PackageHistory` tables

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2, T004)**: Depends on T001–T003; **BLOCKS all user story phases**
- **US1 (Phase 3)**: Depends on Foundational — T005–T010 can run in parallel after T004; T010 and T011 depend on T005–T009 being complete
- **US2 (Phase 4)**: Depends on T004; T012–T014 can run after Foundational
- **US3 (Phase 5)**: Depends on T004; T015–T017 can run after Foundational
- **US4 (Phase 6)**: Depends on T004; T018–T019 can run after Foundational; T019 depends on T005 (persona switcher avatar)
- **US5 (Phase 7)**: Depends on T004; T021 (backend) can run immediately; T020 (frontend) depends on T021
- **US6 (Phase 8)**: Depends on T004; fully independent of other user stories
- **Polish (Phase 9)**: Depends on all preceding phases; T028 depends on T011; T029 depends on T021

### User Story Dependencies

- **US1 (P1)**: Must finish T004 first; T005–T009 are independent of each other [P]; T010 depends on T005–T009
- **US2 (P1)**: Independent of US1 after T004; T012 depends on T004; T013–T014 can run with T012 [P]
- **US3 (P1)**: Independent of US1/US2 after T004; T015–T017 can run in parallel [P] within the story
- **US4 (P2)**: T018 independent; T019 depends on T005 (avatar in nav bar)
- **US5 (P2)**: T021 (backend) independent; T020 depends on T021
- **US6 (P3)**: Fully independent; T022–T023 can run in parallel [P]

### Within Each Phase

- Foundational (T004) must finish before user story phases begin
- Within each user story, [P] tasks can run simultaneously
- T010 (dashboard router) depends on T005–T009 (sub-dashboard components) all being present

### Parallel Opportunities

- T001–T003 (Setup) can all run in parallel
- US1 sub-dashboard components T005–T009 can all run in parallel
- US2 tasks T012–T014 can run in parallel
- US3 tasks T015–T017 can run in parallel
- US4 tasks T018–T019 can run in parallel (T019 waits on T005)
- US5 backend T021 can run concurrently with any frontend task
- US6 tasks T022–T023 can run in parallel
- Polish tasks T024–T027 can all run in parallel
- T028 and T029 can run in parallel with each other after T011 and T021 respectively

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup (T001–T003)
2. Complete Phase 2: Foundational (T004) — **CRITICAL**
3. Complete Phase 3: US1 — Persona switcher avatar + contextual dashboards
4. Complete Phase 4: US2 — Persona-filtered package list
5. **STOP and VALIDATE**: Each persona sees differentiated dashboard and package list
6. This MVP demonstrates the full persona experience to a workshop attendee

### Incremental Delivery

1. Setup + Foundational → PersonaService ready with role helpers
2. US1 → Persona switcher + contextual dashboards (biggest visible change)
3. US2 → Package list persona defaults (immediate operational value)
4. US3 → Package detail action explanations (correctness)
5. US4 → Status cards + navigation cleanup (polish)
6. US5 → Demo controls scenarios (trainer workflow)
7. US6 → Event stream refinements (workshop showcase)
8. Polish → Accessibility + empty states

---

## Notes

- `[P]` = different files, no unresolved dependencies within the phase
- `[USN]` maps each task to its user story for traceability
- Feature 1 built the full application; all file paths reference existing files to be updated or new files to be added alongside them
- The "PersonaUnavailable" pattern (T003, T016) implements FR-005: show why an action is unavailable rather than silently hiding it — this is a deliberate UX choice that helps workshop attendees understand the permission model
- Playful manager metrics (T009) are derived entirely from existing data — no new database fields required; the humorous labels are frontend-only presentation
- Backend task T011 (operational-summary additions) and T021 (kevin scenario) are the only backend changes in this feature; all other work is frontend-only
- All write operations continue to enforce permissions server-side; this feature only changes what is *displayed* to non-permitted personas, not what the system accepts
