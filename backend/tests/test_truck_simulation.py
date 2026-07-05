"""Tests for the truck simulation engine — ticks, delivery, reroute (T030)."""
import json

import pytest
from sqlmodel import select

from app.models.customer import Customer
from app.models.employee import Employee, PersonaType
from app.models.invoice import Invoice
from app.models.map_location import LocationType, MapLocation
from app.models.package import Package, PackagePriority, PackageStatus
from app.models.package_line_item import PackageLineItem, ProductType
from app.models.sale import Sale
from app.models.truck import Truck, TruckStatus
from app.models.truck_route import RouteStatus, RouteStop, TruckRoute
from app.services.route_service import WAREHOUSE_LAT, WAREHOUSE_LNG
from app.services.truck_service import TruckService
from app.simulation.tick import process_truck_tick

# ─── Fixtures ──────────────────────────────────────────────────────────────────

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


@pytest.fixture(name="customer_b")
def customer_b_fixture(session):
    c = Customer(
        customer_id="CUST-B01", name="Scranton Business Park",
        address="1 Lackawanna Ave", city="Scranton", state="PA",
        lat=41.410, lng=-75.663,
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


@pytest.fixture(name="truck")
def truck_fixture(session):
    t = Truck(
        truck_id="DM-TRUCK-SIM", truck_number=9, name="Test Truck",
        driver_name="Test Driver",
        status=TruckStatus.ON_ROUTE,
        current_lat=WAREHOUSE_LAT, current_lng=WAREHOUSE_LNG,
    )
    session.add(t)
    session.commit()
    session.refresh(t)
    return t


@pytest.fixture(name="route_at_customer")
def route_at_customer_fixture(session, truck, customer_b):
    """A route whose first waypoint is the customer location (so arrival fires immediately)."""
    customer_coord = [customer_b.lat, customer_b.lng]
    geometry = [customer_coord, [WAREHOUSE_LAT, WAREHOUSE_LNG]]

    route = TruckRoute(
        route_id="ROUTE-SIM-001",
        truck_id=truck.truck_id,
        status=RouteStatus.ACTIVE,
        geometry=json.dumps(geometry),
        estimated_duration_minutes=12,
        current_waypoint_index=0,
    )
    session.add(route)
    session.flush()

    stop = RouteStop(
        stop_id="ROUTE-SIM-001-STOP-01",
        route_id="ROUTE-SIM-001",
        customer_id=customer_b.customer_id,
        stop_order=1,
    )
    session.add(stop)
    session.commit()

    truck.current_route_id = "ROUTE-SIM-001"
    session.commit()
    session.refresh(truck)
    return route


@pytest.fixture(name="route_mid_journey")
def route_mid_journey_fixture(session, truck, customer_b):
    """A route with several waypoints before the customer stop."""
    mid_lat = (WAREHOUSE_LAT + customer_b.lat) / 2
    mid_lng = (WAREHOUSE_LNG + customer_b.lng) / 2
    geometry = [
        [round(mid_lat, 6), round(mid_lng, 6)],
        [round(customer_b.lat, 6), round(customer_b.lng, 6)],
        [WAREHOUSE_LAT, WAREHOUSE_LNG],
    ]

    route = TruckRoute(
        route_id="ROUTE-SIM-002",
        truck_id=truck.truck_id,
        status=RouteStatus.ACTIVE,
        geometry=json.dumps(geometry),
        estimated_duration_minutes=12,
        current_waypoint_index=0,
    )
    session.add(route)
    session.flush()

    stop = RouteStop(
        stop_id="ROUTE-SIM-002-STOP-01",
        route_id="ROUTE-SIM-002",
        customer_id=customer_b.customer_id,
        stop_order=1,
    )
    session.add(stop)
    session.commit()

    truck.current_route_id = "ROUTE-SIM-002"
    session.commit()
    session.refresh(truck)
    return route


def _make_in_transit_package(session, pkg_id, customer, truck):
    emp = session.exec(select(Employee)).first()
    if not emp:
        emp = Employee(
            employee_id="tmp-emp-sim", name="Temp", persona=PersonaType.WAREHOUSE,
            title="Warehouse", email="tmp@dm.com",
        )
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
        status=PackageStatus.IN_TRANSIT,
        priority=PackagePriority.STANDARD,
        contents_summary="Paper",
        truck_id=truck.truck_id,
    )
    session.add(pkg)
    session.add(PackageLineItem(
        package_id=pkg_id, product_name="A4", product_category="Paper",
        quantity=1, unit_description="ream", product_type=ProductType.PAPER_PRODUCT, fragile=False,
    ))
    session.commit()
    session.refresh(pkg)
    return pkg


# ─── Tick advancement ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_tick_advances_waypoint_index(session, publisher, truck, route_mid_journey):
    """process_truck_tick increments current_waypoint_index by 1."""
    initial_idx = route_mid_journey.current_waypoint_index

    await process_truck_tick(session, truck, tick_number=1, location_event_every_n_ticks=5)

    session.refresh(route_mid_journey)
    assert route_mid_journey.current_waypoint_index == initial_idx + 1


@pytest.mark.asyncio
async def test_tick_updates_truck_coordinates(session, publisher, truck, route_mid_journey):
    """After a tick the truck lat/lng changes to the next waypoint."""
    original_lat = truck.current_lat
    original_lng = truck.current_lng

    await process_truck_tick(session, truck, tick_number=1, location_event_every_n_ticks=5)

    session.refresh(truck)
    geometry = json.loads(route_mid_journey.geometry)
    expected_lat, expected_lng = geometry[0]
    assert truck.current_lat == pytest.approx(expected_lat, abs=1e-5)
    assert truck.current_lng == pytest.approx(expected_lng, abs=1e-5)


# ─── Delivery on arrival ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delivery_fires_when_truck_arrives_at_customer(
    session, publisher, truck, customer_b, route_at_customer
):
    """Package is marked delivered when the tick moves truck to a customer waypoint."""
    pkg = _make_in_transit_package(session, "PKG-SIM-DELIV-01", customer_b, truck)

    await process_truck_tick(session, truck, tick_number=1, location_event_every_n_ticks=5)

    session.refresh(pkg)
    assert pkg.status == PackageStatus.DELIVERED
    assert pkg.truck_id is None


@pytest.mark.asyncio
async def test_truck_status_becomes_returning_after_all_stops(
    session, publisher, truck, customer_b, route_at_customer
):
    """After all stops are completed truck transitions to RETURNING."""
    _make_in_transit_package(session, "PKG-SIM-RET-01", customer_b, truck)

    await process_truck_tick(session, truck, tick_number=1, location_event_every_n_ticks=5)

    session.refresh(truck)
    assert truck.status == TruckStatus.RETURNING


# ─── Kevin reroute ─────────────────────────────────────────────────────────────

@pytest.fixture(name="donut_location")
def donut_location_fixture(session):
    loc = MapLocation(
        name="Dunkin Jefferson Ave",
        location_type=LocationType.DONUT,
        lat=41.410, lng=-75.659,
        description="Kevin's favorite",
    )
    session.add(loc)
    session.commit()
    session.refresh(loc)
    return loc


@pytest.fixture(name="customer_location")
def customer_location_fixture(session):
    loc = MapLocation(
        name="Vance Refrigeration",
        location_type=LocationType.CUSTOMER,
        lat=41.408, lng=-75.662,
    )
    session.add(loc)
    session.commit()
    session.refresh(loc)
    return loc


@pytest.mark.asyncio
async def test_kevin_reroute_inserts_via_point_and_sets_status_rerouted(
    session, publisher, truck, customer_b, route_at_customer, donut_location, michael
):
    """kevin_reroute() inserts a ViaPoint and sets truck status to REROUTED."""
    from app.models.truck_route import ViaPoint

    result = await TruckService.kevin_reroute(
        session, truck.truck_id, donut_location.id, "Kevin is hungry", michael
    )

    session.refresh(truck)
    assert truck.status == TruckStatus.REROUTED
    assert truck.delay_reason == "Kevin is hungry"
    assert result["truck_id"] == truck.truck_id

    via_points = session.exec(
        select(ViaPoint).where(ViaPoint.route_id == truck.current_route_id)
    ).all()
    assert len(via_points) == 1
    assert via_points[0].name == donut_location.name


@pytest.mark.asyncio
async def test_kevin_reroute_raises_409_when_truck_returning(
    session, publisher, truck, donut_location, michael, route_at_customer
):
    """kevin_reroute() raises 409 when truck status is RETURNING."""
    from fastapi import HTTPException

    truck.status = TruckStatus.RETURNING
    session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await TruckService.kevin_reroute(
            session, truck.truck_id, donut_location.id, "Too late", michael
        )

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_kevin_reroute_raises_409_when_truck_completed(
    session, publisher, truck, donut_location, michael, route_at_customer
):
    """kevin_reroute() raises 409 when truck status is COMPLETED."""
    from fastapi import HTTPException

    truck.status = TruckStatus.COMPLETED
    session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await TruckService.kevin_reroute(
            session, truck.truck_id, donut_location.id, "Too late", michael
        )

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_kevin_reroute_raises_404_for_non_food_location(
    session, publisher, truck, customer_location, michael, route_at_customer
):
    """kevin_reroute() raises 404 when location_type is customer or warehouse."""
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await TruckService.kevin_reroute(
            session, truck.truck_id, customer_location.id, "Wrong type", michael
        )

    assert exc_info.value.status_code == 404
