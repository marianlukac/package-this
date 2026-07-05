"""Tests for dual-write audit logging — AuditLog + PackageHistory (T147)."""
import pytest
from sqlmodel import select

from app.models.audit_log import AuditLog
from app.models.package import PackageStatus
from app.models.package_history import PackageHistory
from app.services.package_service import PackageService


@pytest.mark.asyncio
async def test_status_change_writes_both_logs(session, michael, package, publisher):
    """Advancing status must write to both PackageHistory and AuditLog."""
    result = await PackageService.advance_status(
        session, michael, package.package_id,
        PackageStatus.PACKAGED, "Ready to pack", "ui",
    )

    history = session.exec(
        select(PackageHistory)
        .where(PackageHistory.package_id == package.package_id)
        .order_by(PackageHistory.id.desc())
    ).first()
    assert history is not None
    assert "packaged" in (history.new_value or "")

    audit = session.exec(
        select(AuditLog)
        .where(AuditLog.entity_id == package.package_id)
        .where(AuditLog.action == "status_changed")
        .order_by(AuditLog.id.desc())
    ).first()
    assert audit is not None
    assert audit.actor_id == michael.employee_id


@pytest.mark.asyncio
async def test_create_package_writes_audit(session, michael, sale, publisher):
    """Package creation must create an AuditLog entry."""
    result = await PackageService.create_package(
        session, michael, sale.sale_id, "123 Office Park", "standard", "Test items", False,
    )

    audit = session.exec(
        select(AuditLog)
        .where(AuditLog.entity_id == result.package_id)
        .where(AuditLog.action == "create_package")
    ).first()
    assert audit is not None
    assert audit.actor_id == michael.employee_id


@pytest.mark.asyncio
async def test_delay_writes_both_logs(session, michael, package, publisher):
    """Recording a delay must write to PackageHistory and AuditLog."""
    await PackageService.record_delay(session, michael, package.package_id, "Truck breakdown", 4.0)

    history = session.exec(
        select(PackageHistory)
        .where(PackageHistory.package_id == package.package_id)
        .where(PackageHistory.event_type == "delay_recorded")
    ).first()
    assert history is not None

    audit = session.exec(
        select(AuditLog)
        .where(AuditLog.entity_id == package.package_id)
        .where(AuditLog.action == "record_delay")
    ).first()
    assert audit is not None
