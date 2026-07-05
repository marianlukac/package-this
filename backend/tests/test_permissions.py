"""Tests for persona permission validation (T145)."""

from app.models.employee import PersonaType
from app.persona.permissions import PERSONA_PERMISSIONS, get_all_operations, has_permission


def test_manager_has_all_permissions():
    """Michael can do everything."""
    all_ops = get_all_operations()
    for op in all_ops:
        assert has_permission(PersonaType.MANAGER, op), f"Manager missing: {op}"


def test_sales_can_create_sale():
    assert has_permission(PersonaType.SALES, "create_sale")


def test_sales_can_cancel_package():
    assert has_permission(PersonaType.SALES, "cancel_package")


def test_warehouse_can_advance_lifecycle():
    assert has_permission(PersonaType.WAREHOUSE, "advance_lifecycle")


def test_warehouse_cannot_perform_manager_actions():
    assert not has_permission(PersonaType.WAREHOUSE, "perform_manager_action")


def test_accounting_can_create_invoice():
    assert has_permission(PersonaType.ACCOUNTING, "create_invoice")


def test_unknown_operation_returns_false():
    assert not has_permission(PersonaType.SALES, "fly_to_the_moon")


def test_all_personas_defined():
    expected_personas = {
        PersonaType.MANAGER, PersonaType.SALES, PersonaType.ACCOUNTING, PersonaType.WAREHOUSE,
    }
    assert expected_personas.issubset(set(PERSONA_PERMISSIONS.keys()))
