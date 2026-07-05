# Personas

The system uses the `X-Persona-Id` request header to identify the acting employee.

## How it works

Every API request must include the header:
```
X-Persona-Id: michael-scott
```

The `PersonaMiddleware` resolves this to an `Employee` record and attaches it to `request.state.user`. Endpoints that require specific permissions call `require_permission("operation_name")` or `require_manager()`.

## Personas and permissions

| Persona | Who | Key permissions |
|---|---|---|
| `manager` | Michael Scott | All operations including manager actions |
| `sales` | Jim, Dwight, Phyllis, Stanley, Ryan | create_sale, create_package, create_complaint |
| `accounting` | Angela, Kevin | create_invoice, view operations |
| `warehouse` | Darryl, Roy, Creed | advance_lifecycle, record_delay, manage_line_items |

## Predefined employees

| Employee ID | Name | Persona | Dashboard Role Group | Avatar Color | Cares About |
|---|---|---|---|---|---|
| `michael-scott` | Michael Scott | manager | manager | `#1e3a5f` (DM Blue) | All operations, customer happiness, and morale events |
| `dwight-schrute` | Dwight Schrute | sales | sales | `#b8860b` (Dark Gold) | Sales numbers, customer escalations, and security incidents |
| `jim-halpert` | Jim Halpert | sales | sales | `#16a34a` (Green) | My accounts, my packages, and keeping things moving |
| `phyllis-vance` | Phyllis Vance | sales | sales | `#7c3aed` (Purple) | My clients, their orders, and complaints from Bob's contacts |
| `stanley-hudson` | Stanley Hudson | sales | sales | `#ea580c` (Orange) | My sales quota, my accounts, and getting out by 5 PM |
| `angela-martin` | Angela Martin | accounting | accounting | `#4b5563` (Gray) | Invoice accuracy, exception packages, and financial discrepancies |
| `kevin-malone` | Kevin Malone | accounting | accounting | `#ca8a04` (Yellow) | Invoices, numbers (approximately), and the snack situation |
| `pam-beesly` | Pam Beesly | accounting | general | `#db2777` (Pink) | Front desk, visitor coordination, and office announcements |
| `ryan-howard` | Ryan Howard | sales | general | `#4f46e5` (Indigo) | Whatever Ryan is doing this week. Probably something with an app |
| `creed-bratton` | Creed Bratton | warehouse | general | `#475569` (Slate) | Quality checks, mysterious side projects, and staying off the radar |
| `darryl-philbin` | Darryl Philbin | warehouse | warehouse | `#0d9488` (Teal) | Truck assignments, shipping status, and warehouse readiness |
| `roy-anderson` | Roy Anderson | warehouse | warehouse | `#dc2626` (Red) | Packages ready to go, loading, and delivery handoffs |

> **Note**: The "Dashboard Role Group" column describes which dashboard view the employee sees in the UI. This is a frontend concept separate from the backend `persona` field used for API permission enforcement. Pam, Ryan, and Creed use the general dashboard view but retain their backend permissions (accounting, sales, warehouse respectively).

## How to switch personas in the UI

The persona switcher is displayed in the top navigation bar. It shows the currently active persona as a **colored initials avatar** with the employee name.

1. Click the avatar/name button in the top-right of the navigation bar
2. A dropdown panel appears showing all 12 employees as cards with:
   - Colored initials badge (using the persona's avatar color)
   - Employee name and role
   - Short description of what they care about
3. Click any employee card to switch to that persona
4. The UI immediately updates: dashboard, package list filters, visible actions, and all role-aware elements reflect the new persona
5. The selection persists in `localStorage` across page reloads

## Persona-aware UI behavior

| UI Element | How persona affects it |
|---|---|
| Dashboard | Switches between Manager, Sales, Accounting, Warehouse, or General view |
| Package list | Sales personas see their own packages pre-filtered; warehouse sees actionable packages |
| Package detail actions | Lifecycle buttons shown as disabled with explanation for non-warehouse/manager |
| Demo Controls | Visible only to Michael Scott (manager) |
| Navigation | Demo Controls nav link only shown to manager |

## Manager actions

Only `michael-scott` can call `POST /manager-actions`. The 7 supported actions are:

- `approve_reroute` — approve a truck reroute for a package
- `override_priority` — change package priority
- `mark_customer_unhappy` — flag a customer as unhappy
- `approve_return` — approve a return for in-transit or delivered package
- `approve_expensive_delivery` — authorize a non-standard delivery cost
- `force_truck_reassignment` — reassign a package to a different truck
- `trigger_demo_scenario` — run a named demo scenario
