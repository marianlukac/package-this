"""Tests for event envelope creation and publication."""
import pytest

from app.events.envelope import make_envelope
from app.models.package import PackageStatus
from app.services.package_service import PackageService


def test_make_envelope_required_fields():
    env = make_envelope(
        event_type="package.created", topic="packages",
        actor_id="jim-halpert", actor_name="Jim Halpert",
        source="ui", entity_type="package", entity_id="PKG-001",
        payload={"status": "order_created"},
        summary="Package created",
    )
    assert env.eventId
    assert env.eventType == "package.created"
    assert env.topic == "packages"
    assert env.actor.actor_id == "jim-halpert"
    assert env.actor.actor_name == "Jim Halpert"
    assert env.source == "ui"
    assert env.entityType == "package"
    assert env.entityId == "PKG-001"
    assert env.occurredAt is not None
    assert env.payload == {"status": "order_created"}
    assert env.summary == "Package created"


def test_make_envelope_unique_ids():
    e1 = make_envelope(
        event_type="a", topic="t", actor_id="actor", actor_name="Actor",
        source="ui", entity_type="pkg", entity_id="P1", payload={}, summary="s1",
    )
    e2 = make_envelope(
        event_type="a", topic="t", actor_id="actor", actor_name="Actor",
        source="ui", entity_type="pkg", entity_id="P1", payload={}, summary="s2",
    )
    assert e1.eventId != e2.eventId


@pytest.mark.asyncio
async def test_status_advance_publishes_event(session, michael, package, publisher):
    await PackageService.advance_status(
        session, michael, package.package_id, PackageStatus.PACKAGED, None, "ui",
    )
    published = publisher.published
    assert len(published) >= 1
    event = published[-1]
    assert event.topic == "package-status"
    assert "packaged" in event.payload.get("new_status", "")


@pytest.mark.asyncio
async def test_package_creation_publishes_event(session, michael, sale, publisher):
    await PackageService.create_package(
        session, michael, sale.sale_id, "Scranton, PA", "standard", "Paper reams", False,
    )
    assert any(e.topic == "packages" for e in publisher.published)
    assert any(e.eventType == "package.created" for e in publisher.published)
