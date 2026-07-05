# Persona and Permission Model

**Date**: 2026-06-19

## How Personas Work

The Dunder Mifflin Package Manager uses a simplified demo-auth pattern for workshop use.
Every write operation requires the caller to identify itself via an HTTP header:

```
X-Persona-Id: <employee-slug>
```

Examples: `michael-scott`, `darryl-philbin`, `jim-halpert`

The `PersonaMiddleware` in the backend:
1. Reads the `X-Persona-Id` header.
2. Looks up the Employee record by `employee_id` slug.
3. Resolves the employee's persona (sales, accounting, warehouse, manager).
4. Sets `request.state.current_user` to the Employee object.
5. Returns `401 Unauthorized` if the header is missing on a write operation.
6. Returns `403 Forbidden` with a descriptive message if the persona lacks the required
   permission for the operation.

Read operations (GET endpoints) do not require the header, making them accessible to
agents and tools without authentication setup.

> **Enterprise note**: In a production system, this header would be replaced by a validated
> JWT claim. The server-side enforcement pattern is identical — only the token mechanism
> changes. This is documented in `docs/persona-guide.md`.

---

## Employee-to-Persona Assignments

| Employee | Slug | Persona |
|---|---|---|
| Michael Scott | michael-scott | manager |
| Dwight Schrute | dwight-schrute | sales |
| Jim Halpert | jim-halpert | sales |
| Pam Beesly | pam-beesly | accounting |
| Angela Martin | angela-martin | accounting |
| Kevin Malone | kevin-malone | accounting |
| Darryl Philbin | darryl-philbin | warehouse |
| Roy Anderson | roy-anderson | warehouse |
| Ryan Howard | ryan-howard | sales |
| Phyllis Vance | phyllis-vance | sales |
| Stanley Hudson | stanley-hudson | sales |
| Creed Bratton | creed-bratton | warehouse |

---

## Permission Matrix

| Operation | sales | accounting | warehouse | manager |
|---|---|---|---|---|
| Create sale | ✅ | ❌ | ❌ | ✅ |
| View sales | ✅ | ✅ | ✅ | ✅ |
| Create package | ✅ | ❌ | ❌ | ✅ |
| Edit package fields | ✅ | ❌ | ✅ | ✅ |
| Delete package (order_created) | ✅ | ❌ | ❌ | ✅ |
| Advance package lifecycle | ❌ | ❌ | ✅ | ✅ |
| Cancel package | ✅ | ❌ | ✅ | ✅ |
| Record delay | ❌ | ❌ | ✅ | ✅ |
| Record damage | ❌ | ❌ | ✅ | ✅ |
| View invoices | ✅ | ✅ | ✅ | ✅ |
| Create complaint | ✅ | ✅ | ✅ | ✅ |
| Update complaint | ✅ | ✅ | ✅ | ✅ |
| Close complaint | ✅ | ✅ | ✅ | ✅ |
| Approve reroute | ❌ | ❌ | ❌ | ✅ |
| Override priority | ❌ | ❌ | ❌ | ✅ |
| Mark customer unhappy | ❌ | ❌ | ❌ | ✅ |
| Approve return | ❌ | ❌ | ❌ | ✅ |
| Approve expensive delivery | ❌ | ❌ | ❌ | ✅ |
| Force truck reassignment | ❌ | ❌ | ❌ | ✅ |
| Trigger demo scenario | ❌ | ❌ | ❌ | ✅ |
| Reset demo data | ❌ | ❌ | ❌ | ✅ |

---

## Implementation Reference

**`app/persona/permissions.py`** defines:

```python
PERSONA_PERMISSIONS: dict[str, set[str]] = {
    "sales": {
        "create_sale", "view_sales", "create_package", "edit_package_fields",
        "delete_package", "cancel_package", "view_invoices",
        "create_complaint", "update_complaint", "close_complaint",
    },
    "accounting": {
        "view_sales", "view_invoices",
        "create_complaint", "update_complaint", "close_complaint",
    },
    "warehouse": {
        "view_sales", "edit_package_fields", "advance_lifecycle",
        "cancel_package", "record_delay", "record_damage", "view_invoices",
        "create_complaint", "update_complaint", "close_complaint",
    },
    "manager": {
        # All of the above, plus:
        "create_sale", "view_sales", "create_package", "edit_package_fields",
        "delete_package", "advance_lifecycle", "cancel_package",
        "record_delay", "record_damage", "view_invoices",
        "create_complaint", "update_complaint", "close_complaint",
        "approve_reroute", "override_priority", "mark_customer_unhappy",
        "approve_return", "approve_expensive_delivery", "force_truck_reassignment",
        "trigger_demo_scenario", "reset_demo",
    },
}
```

**`require_permission(operation: str)`** is a FastAPI dependency injected into route
handlers:

```python
# Usage in a router:
@router.post("/packages/{package_id}/status")
async def advance_status(
    package_id: str,
    body: StatusChangeRequest,
    _: None = Depends(require_permission("advance_lifecycle")),
    session: Session = Depends(get_session),
):
    ...
```

**`require_manager()`** is a convenience dependency for manager-only routes:

```python
@router.post("/manager-actions")
async def perform_manager_action(
    body: ManagerActionRequest,
    _: None = Depends(require_manager()),
    session: Session = Depends(get_session),
):
    ...
```

Both dependencies raise `HTTPException(status_code=403)` with a descriptive message
identifying the current persona and the required permission. No change is written to the
database on a 403 response.

---

## Agent and MCP Server Usage

When an agent or MCP server calls the API on behalf of a persona:

1. Set the `X-Persona-Id` header to the employee slug for the persona you are acting as.
2. Use `michael-scott` to exercise manager-only actions in demo scenarios.
3. The `source` field in request bodies should be set to `"agent"` to distinguish
   agent-initiated changes in the audit log and package history.
4. GET endpoints do not require a persona header and can be called without credentials.
