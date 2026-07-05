"""Tests for seed data and demo reset behavior (T149)."""
import pytest
from sqlmodel import select

from app.models.complaint import Complaint
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.package import Package


def test_seed_data_has_expected_employees(session):
    """After seeding, all expected employees must be present."""
    from seed.seed_data import seed

    seed(session)
    employees = session.exec(select(Employee)).all()
    assert len(employees) >= 5
    names = {e.name for e in employees}
    assert "Michael Scott" in names
    assert "Dwight Schrute" in names
    assert "Jim Halpert" in names


def test_seed_data_has_customers(session):
    from seed.seed_data import seed
    seed(session)
    customers = session.exec(select(Customer)).all()
    assert len(customers) >= 5


def test_seed_data_has_packages_across_statuses(session):
    from seed.seed_data import seed
    seed(session)
    packages = session.exec(select(Package)).all()
    assert len(packages) >= 5
    statuses = {p.status for p in packages}
    assert len(statuses) >= 2  # spread across multiple statuses


def test_seed_data_has_complaints(session):
    from seed.seed_data import seed
    seed(session)
    complaints = session.exec(select(Complaint)).all()
    assert len(complaints) >= 1


@pytest.mark.asyncio
async def test_kevin_hunger_reroute_scenario(session, michael, publisher):
    """T029: kevin-hunger-reroute affects exactly one package and writes delay to Package + PackageHistory."""
    from seed.seed_data import seed
    from sqlmodel import select as _sel

    from app.models.package_history import PackageHistory
    from app.services.demo_service import DemoService

    seed(session)

    result = await DemoService.run_scenario(session, michael, "kevin-hunger-reroute", "test")

    assert result["status"] == "executed"
    affected = result["affected_packages"]
    assert len(affected) == 1, f"Expected 1 affected package, got {len(affected)}: {affected}"

    pkg = session.exec(select(Package).where(Package.package_id == affected[0])).one()
    assert pkg.delay_reason is not None
    assert "hungry" in pkg.delay_reason.lower(), f"Expected 'hungry' in delay_reason, got: {pkg.delay_reason!r}"

    history_entries = session.exec(
        _sel(PackageHistory)
        .where(PackageHistory.package_id == affected[0])
        .where(PackageHistory.event_type == "delay_recorded")
    ).all()
    assert len(history_entries) >= 1, "Expected at least one delay_recorded entry in PackageHistory"


@pytest.mark.asyncio
async def test_demo_reset_restores_baseline(session, publisher):
    from seed.seed_data import seed

    from app.services.demo_service import DemoService

    seed(session)
    initial_count = len(session.exec(select(Package)).all())

    DemoService.reset(session)  # reset already re-seeds internally
    after_count = len(session.exec(select(Package)).all())
    assert after_count == initial_count
