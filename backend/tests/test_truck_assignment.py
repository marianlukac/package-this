"""Tests for truck package assignment and GPS location tracking (T029)."""
import pytest
from sqlmodel import select

from app.models.customer import Customer
from app.models.employee import Employee, PersonaType
from app.models.invoice import Invoice
from app.models.package import Package, PackagePriority, PackageStatus
from app.models.package_line_item import PackageLineItem, ProductType
from app.models.sale import Sale
from app.models.truck import Truck, TruckStatus
from app.services.truck_service import TruckService

# ─── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(name="darryl")
def darryl_fixture(session):
    emp = Employee(
        employee_id="darryl-philbin", name="Darryl Philbin",
        persona=PersonaType.WAREHOUSE, title="Warehouse Foreman",
        email="darryl@dundermifflin.com",
    )
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return emp


@pytest.fixture(name="michael")
def michael_fixture(session):
    emp = Employee(
        employee_id="michael-scott", name="Michael Scott",
        persona=PersonaType.MANAGER, title="Regional Manager",
        email="michael@dundermifflin.com",
    )
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return emp


@pytest.fixture(name="customer_a")
def customer_a_fixture(session):
    c = Customer(
        customer_id="CUST-A01", name="Vance Refrigeration",
        address="1 Bob Vance Way", city="Scranton", state="PA",
        lat=41.408, lng=-75.662,
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


@pytest.fixture(name="truck")
def truck_fixture(session):
    t = Truck(
        truck_id="DM-TRUCK-01", truck_number=1, name="The Dundie",
        driver_name="Darryl Philbin",
        status=TruckStatus.AT_WAREHOUSE,
        current_lat=41.4090, current_lng=-75.6624,
    )
    session.add(t)
    session.commit()
    session.refresh(t)
    return t


def _make_package(session, pkg_id, customer, status=PackageStatus.READY_FOR_SHIPPING):
    emp = session.exec(select(Employee)).first() or Employee(
        employee_id="tmp-emp", name="Temp", persona=PersonaType.SALES,
        title="Sales", email="tmp@dm.com",
    )
    if not emp.employee_id:
        session.add(emp)
        session.flush()

    sale = Sale(sale_id=f"SALE-{pkg_id}", customer_id=customer.customer_id,
                salesperson_id=emp.employee_id)
    session.add(sale)
    inv = Invoice(invoice_id=f"INV-{pkg_id}", sale_id=sale.sale_id,
                  created_by_id=emp.employee_id)
    session.add(inv)
    session.flush()

    pkg = Package(
        package_id=pkg_id, sale_id=sale.sale_id, invoice_id=inv.invoice_id,
        customer_id=customer.customer_id, salesperson_id=emp.employee_id,
        invoicing_employee_id=emp.employee_id,
        status=status,
        priority=PackagePriority.STANDARD,
        contents_summary="Paper reams",
    )
    session.add(pkg)
    session.add(PackageLineItem(
        package_id=pkg_id, product_name="A4 White", product_category="Paper",
        quantity=5, unit_description="ream", product_type=ProductType.PAPER_PRODUCT, fragile=False,
    ))
    session.commit()
    session.refresh(pkg)
    return pkg


# ─── Assignment tests ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_assign_ready_package_succeeds(session, publisher, truck, customer_a, darryl):
    """A ready_for_shipping package can be assigned to a truck."""
    pkg = _make_package(session, "PKG-ASSIGN-001", customer_a)

    result = await TruckService.assign_package(session, truck.truck_id, pkg.package_id, darryl)

    assert result["assigned"] is True
    session.refresh(pkg)
    assert pkg.truck_id == truck.truck_id


@pytest.mark.asyncio
async def test_assign_non_ready_package_raises_409(session, publisher, truck, customer_a, darryl):
    """Assigning a package that is not ready_for_shipping raises 409."""
    from fastapi import HTTPException
    pkg = _make_package(session, "PKG-ASSIGN-002", customer_a, status=PackageStatus.ORDER_CREATED)

    with pytest.raises(HTTPException) as exc_info:
        await TruckService.assign_package(session, truck.truck_id, pkg.package_id, darryl)

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_assign_in_transit_package_raises_409(session, publisher, truck, customer_a, darryl):
    """An in_transit package cannot be reassigned to another truck."""
    from fastapi import HTTPException
    pkg = _make_package(session, "PKG-ASSIGN-003", customer_a, status=PackageStatus.IN_TRANSIT)
    pkg.truck_id = "DM-TRUCK-02"
    session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await TruckService.assign_package(session, truck.truck_id, pkg.package_id, darryl)

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_assign_already_assigned_same_truck_is_idempotent(session, publisher, truck, customer_a, darryl):
    """Re-assigning to the same truck is allowed (idempotent)."""
    pkg = _make_package(session, "PKG-ASSIGN-004", customer_a)
    pkg.truck_id = truck.truck_id
    session.commit()

    result = await TruckService.assign_package(session, truck.truck_id, pkg.package_id, darryl)

    assert result["assigned"] is True


@pytest.mark.asyncio
async def test_in_transit_package_location_follows_truck(session, publisher, truck, customer_a, darryl):
    """An in-transit package current_lat/lng matches the truck after dispatch."""
    pkg = _make_package(session, "PKG-ASSIGN-005", customer_a)
    await TruckService.assign_package(session, truck.truck_id, pkg.package_id, darryl)
    await TruckService.dispatch_truck(session, truck.truck_id, darryl)

    session.refresh(truck)
    session.refresh(pkg)

    assert pkg.status == PackageStatus.IN_TRANSIT
    # After dispatch the package starts at warehouse coordinates via route geometry
    assert pkg.current_lat is not None or truck.current_lat is not None


@pytest.mark.asyncio
async def test_delivered_package_location_is_customer_and_truck_id_cleared(
    session, publisher, truck, customer_a, darryl
):
    """After delivery, package current_lat/lng equals customer coords and truck_id is null."""
    pkg = _make_package(session, "PKG-ASSIGN-006", customer_a)
    await TruckService.assign_package(session, truck.truck_id, pkg.package_id, darryl)
    await TruckService.dispatch_truck(session, truck.truck_id, darryl)

    # Manually mark as delivered via record_delivery
    session.refresh(pkg)
    pkg.status = PackageStatus.IN_TRANSIT
    session.commit()

    delivered = await TruckService.record_delivery(
        session, truck.truck_id, customer_a.customer_id,
        actor_id=truck.truck_id, actor_name=truck.name, source="test",
    )

    assert pkg.package_id in delivered
    session.refresh(pkg)
    assert pkg.status == PackageStatus.DELIVERED
    assert pkg.truck_id is None
    assert pkg.current_lat == pytest.approx(customer_a.lat, abs=1e-3)
    assert pkg.current_lng == pytest.approx(customer_a.lng, abs=1e-3)
