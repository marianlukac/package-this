"""Tests for manager actions service (T146)."""
import pytest
from fastapi import HTTPException

from app.schemas.manager_action import ManagerActionRequest
from app.services.manager_actions_service import ManagerActionsService


@pytest.mark.asyncio
async def test_override_priority(session, michael, package, publisher):
    request = ManagerActionRequest(
        action="override_priority",
        entity_type="package",
        entity_id=package.package_id,
        reason="Customer is a VIP",
        payload={"priority": "urgent"},
        source="ui",
    )
    result = await ManagerActionsService.perform_action(session, michael, request)
    assert result.status == "applied"

    session.refresh(package)
    assert package.priority == "urgent"


@pytest.mark.asyncio
async def test_mark_customer_unhappy(session, michael, customer, publisher):
    request = ManagerActionRequest(
        action="mark_customer_unhappy",
        entity_type="customer",
        entity_id=customer.customer_id,
        reason="They called three times",
        payload={},
        source="ui",
    )
    result = await ManagerActionsService.perform_action(session, michael, request)
    assert result.status == "applied"

    session.refresh(customer)
    assert customer.is_unhappy is True


@pytest.mark.asyncio
async def test_non_manager_rejected(session, jim, package, publisher):
    """Non-manager persona must be rejected."""
    request = ManagerActionRequest(
        action="override_priority",
        entity_type="package",
        entity_id=package.package_id,
        reason="Just want to",
        payload={"priority": "urgent"},
        source="ui",
    )
    with pytest.raises(HTTPException) as exc_info:
        await ManagerActionsService.perform_action(session, jim, request)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_unknown_action_rejected(session, michael, package, publisher):
    request = ManagerActionRequest(
        action="delete_everything",
        entity_type="package",
        entity_id=package.package_id,
        reason="Test",
        payload={},
        source="ui",
    )
    with pytest.raises(HTTPException) as exc_info:
        await ManagerActionsService.perform_action(session, michael, request)
    assert exc_info.value.status_code == 422
