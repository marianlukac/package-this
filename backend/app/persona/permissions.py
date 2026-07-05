from app.models.employee import PersonaType

PERSONA_PERMISSIONS: dict[str, set[str]] = {
    PersonaType.SALES: {
        "create_sale",
        "view_sales",
        "create_package",
        "edit_package",
        "edit_package_fields",
        "delete_package",
        "cancel_package",
        "manage_line_items",
        "view_invoices",
        "create_complaint",
        "update_complaint",
        "close_complaint",
    },
    PersonaType.ACCOUNTING: {
        "view_sales",
        "view_invoices",
        "create_invoice",
        "create_complaint",
        "update_complaint",
        "close_complaint",
    },
    PersonaType.WAREHOUSE: {
        "view_sales",
        "edit_package",
        "edit_package_fields",
        "advance_lifecycle",
        "cancel_package",
        "record_delay",
        "record_damage",
        "manage_line_items",
        "view_invoices",
        "create_complaint",
        "update_complaint",
        "close_complaint",
        "assign_to_truck",
        "dispatch_truck",
    },
    PersonaType.MANAGER: {
        "create_sale",
        "view_sales",
        "create_package",
        "edit_package",
        "edit_package_fields",
        "delete_package",
        "advance_lifecycle",
        "cancel_package",
        "record_delay",
        "record_damage",
        "manage_line_items",
        "view_invoices",
        "create_invoice",
        "create_complaint",
        "update_complaint",
        "close_complaint",
        "assign_to_truck",
        "dispatch_truck",
        "approve_reroute",
        "override_priority",
        "mark_customer_unhappy",
        "approve_return",
        "approve_expensive_delivery",
        "force_truck_reassignment",
        "trigger_demo_scenario",
        "reset_demo",
        "perform_manager_action",
    },
}


def has_permission(persona: str, operation: str) -> bool:
    return operation in PERSONA_PERMISSIONS.get(persona, set())


def get_all_operations() -> set[str]:
    return set().union(*PERSONA_PERMISSIONS.values())
