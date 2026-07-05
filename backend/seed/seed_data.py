"""Seed script — 12 employees, 14 customers, 3 trucks, 5 sales, 13 packages, 21 map locations."""
import json
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.models.complaint import Complaint, ComplaintPackage, ComplaintStatus
from app.models.customer import Customer
from app.models.employee import Employee, PersonaType
from app.models.invoice import Invoice
from app.models.map_location import LocationType, MapLocation
from app.models.package import Package, PackagePriority, PackageStatus
from app.models.package_history import EventSource, PackageHistory, PackageHistoryEventType
from app.models.package_line_item import PackageLineItem, ProductType
from app.models.sale import Sale
from app.models.truck import Truck, TruckStatus


def seed(session: Session) -> None:
    _seed_employees(session)
    _seed_customers(session)
    _seed_trucks(session)
    _seed_map_locations(session)
    _seed_sales_and_packages(session)
    _seed_complaints(session)
    session.commit()


def _seed_employees(session: Session) -> None:
    employees = [
        Employee(employee_id="michael-scott", name="Michael Scott", persona=PersonaType.MANAGER, title="Regional Manager", email="michael.scott@dundermifflin.com"),
        Employee(employee_id="dwight-schrute", name="Dwight Schrute", persona=PersonaType.SALES, title="Assistant (to the) Regional Manager", email="dwight.schrute@dundermifflin.com"),
        Employee(employee_id="jim-halpert", name="Jim Halpert", persona=PersonaType.SALES, title="Sales Representative", email="jim.halpert@dundermifflin.com"),
        Employee(employee_id="pam-beesly", name="Pam Beesly", persona=PersonaType.ACCOUNTING, title="Office Administrator", email="pam.beesly@dundermifflin.com"),
        Employee(employee_id="angela-martin", name="Angela Martin", persona=PersonaType.ACCOUNTING, title="Senior Accountant", email="angela.martin@dundermifflin.com"),
        Employee(employee_id="kevin-malone", name="Kevin Malone", persona=PersonaType.ACCOUNTING, title="Accountant", email="kevin.malone@dundermifflin.com"),
        Employee(employee_id="darryl-philbin", name="Darryl Philbin", persona=PersonaType.WAREHOUSE, title="Warehouse Foreman", email="darryl.philbin@dundermifflin.com"),
        Employee(employee_id="roy-anderson", name="Roy Anderson", persona=PersonaType.WAREHOUSE, title="Warehouse Associate", email="roy.anderson@dundermifflin.com"),
        Employee(employee_id="ryan-howard", name="Ryan Howard", persona=PersonaType.SALES, title="Sales Representative (Temp)", email="ryan.howard@dundermifflin.com"),
        Employee(employee_id="phyllis-vance", name="Phyllis Vance", persona=PersonaType.SALES, title="Sales Representative", email="phyllis.vance@dundermifflin.com"),
        Employee(employee_id="stanley-hudson", name="Stanley Hudson", persona=PersonaType.SALES, title="Sales Representative", email="stanley.hudson@dundermifflin.com"),
        Employee(employee_id="creed-bratton", name="Creed Bratton", persona=PersonaType.WAREHOUSE, title="Quality Assurance", email="creed.bratton@dundermifflin.com"),
    ]
    for emp in employees:
        if not session.exec(select(Employee).where(Employee.employee_id == emp.employee_id)).first():
            session.add(emp)
    session.flush()


def _seed_customers(session: Session) -> None:
    # 14 customers — Scranton area GPS from research.md
    customers = [
        Customer(customer_id="vance-refrigeration", name="Vance Refrigeration", address="1 Bob Vance Way", city="Scranton", lat=41.4035, lng=-75.6701),
        Customer(customer_id="lackawanna-county", name="Lackawanna County", address="200 Adams Ave", city="Scranton", lat=41.4091, lng=-75.6578),
        Customer(customer_id="poor-richard-pub", name="Poor Richard's Pub", address="456 Penn Ave", city="Scranton", lat=41.4067, lng=-75.6598),
        Customer(customer_id="scranton-business-park", name="Scranton Business Park", address="1000 Enterprise Dr", city="Scranton", lat=41.4120, lng=-75.6645),
        Customer(customer_id="coopers-seafood", name="Cooper's Seafood House", address="701 N Washington Ave", city="Scranton", lat=41.4052, lng=-75.6655),
        Customer(customer_id="steamtown-mall", name="The Steamtown Mall", address="300 Lackawanna Ave", city="Scranton", lat=41.4138, lng=-75.6680),
        Customer(customer_id="allied-steel", name="Allied Steel", address="500 Industrial Blvd", city="Scranton", lat=41.4003, lng=-75.6732),
        Customer(customer_id="carmines-italian", name="Carmine's Italian", address="400 Spruce St", city="Scranton", lat=41.4078, lng=-75.6612),
        Customer(customer_id="county-court", name="County Court", address="100 Wyoming Ave", city="Scranton", lat=41.4096, lng=-75.6570),
        Customer(customer_id="electric-city-grille", name="Electric City Grille", address="320 Penn Ave", city="Scranton", lat=41.4060, lng=-75.6640),
        Customer(customer_id="schrute-farms", name="Schrute Farms B&B", address="1 Schrute Farms Rd", city="Honesdale", state="PA", lat=41.3820, lng=-75.6440),
        Customer(customer_id="anthracite-museum", name="Anthracite Heritage Museum", address="22 Bald Mountain Rd", city="Scranton", lat=41.4100, lng=-75.6515),
        Customer(customer_id="valley-view-towers", name="Valley View Towers", address="800 Valley View Dr", city="Scranton", lat=41.4168, lng=-75.6720),
        Customer(customer_id="scranton-prep", name="Scranton Prep", address="1000 Wyoming Ave", city="Scranton", lat=41.4210, lng=-75.6550),
    ]
    for c in customers:
        if not session.exec(select(Customer).where(Customer.customer_id == c.customer_id)).first():
            session.add(c)
    session.flush()


def _seed_trucks(session: Session) -> None:
    warehouse_lat, warehouse_lng = 41.4090, -75.6624
    trucks = [
        Truck(
            truck_id="DM-TRUCK-01", truck_number=1, name="The Dundie",
            driver_name="Darryl Philbin", status=TruckStatus.AT_WAREHOUSE,
            current_lat=warehouse_lat, current_lng=warehouse_lng,
        ),
        Truck(
            truck_id="DM-TRUCK-02", truck_number=2, name="Pretzel Day",
            driver_name="Roy Anderson", status=TruckStatus.AT_WAREHOUSE,
            current_lat=warehouse_lat, current_lng=warehouse_lng,
        ),
        Truck(
            truck_id="DM-TRUCK-03", truck_number=3, name="Big Tuna",
            driver_name="Creed Bratton", status=TruckStatus.AT_WAREHOUSE,
            current_lat=warehouse_lat, current_lng=warehouse_lng,
        ),
    ]
    for t in trucks:
        existing = session.exec(select(Truck).where(Truck.truck_id == t.truck_id)).first()
        if existing:
            # Update name and driver_name if truck already exists
            existing.truck_number = t.truck_number
            existing.name = t.name
            existing.driver_name = t.driver_name
        else:
            session.add(t)
    session.flush()


def _seed_map_locations(session: Session) -> None:
    locations = [
        # Warehouse
        MapLocation(name="Dunder Mifflin HQ", location_type=LocationType.WAREHOUSE, lat=41.4090, lng=-75.6624, description="Office and warehouse — all truck routes start and end here"),
        # 14 customers
        MapLocation(name="Vance Refrigeration", location_type=LocationType.CUSTOMER, lat=41.4035, lng=-75.6701),
        MapLocation(name="Lackawanna County", location_type=LocationType.CUSTOMER, lat=41.4091, lng=-75.6578),
        MapLocation(name="Poor Richard's Pub", location_type=LocationType.CUSTOMER, lat=41.4067, lng=-75.6598),
        MapLocation(name="Scranton Business Park", location_type=LocationType.CUSTOMER, lat=41.4120, lng=-75.6645),
        MapLocation(name="Cooper's Seafood House", location_type=LocationType.CUSTOMER, lat=41.4052, lng=-75.6655),
        MapLocation(name="The Steamtown Mall", location_type=LocationType.CUSTOMER, lat=41.4138, lng=-75.6680),
        MapLocation(name="Allied Steel", location_type=LocationType.CUSTOMER, lat=41.4003, lng=-75.6732),
        MapLocation(name="Carmine's Italian", location_type=LocationType.CUSTOMER, lat=41.4078, lng=-75.6612),
        MapLocation(name="County Court", location_type=LocationType.CUSTOMER, lat=41.4096, lng=-75.6570),
        MapLocation(name="Electric City Grille", location_type=LocationType.CUSTOMER, lat=41.4060, lng=-75.6640),
        MapLocation(name="Schrute Farms", location_type=LocationType.CUSTOMER, lat=41.3820, lng=-75.6440),
        MapLocation(name="Anthracite Heritage Museum", location_type=LocationType.CUSTOMER, lat=41.4100, lng=-75.6515),
        MapLocation(name="Valley View Towers", location_type=LocationType.CUSTOMER, lat=41.4168, lng=-75.6720),
        MapLocation(name="Scranton Prep", location_type=LocationType.CUSTOMER, lat=41.4210, lng=-75.6550),
        # 3 food
        MapLocation(name="McDonald's Airport Rd", location_type=LocationType.FOOD, lat=41.3940, lng=-75.7280, description="Available as Kevin reroute destination"),
        MapLocation(name="Wendy's Keyser Ave", location_type=LocationType.FOOD, lat=41.4180, lng=-75.6580, description="Available as Kevin reroute destination"),
        MapLocation(name="Burger King Cedar Ave", location_type=LocationType.FOOD, lat=41.4050, lng=-75.6780, description="Available as Kevin reroute destination"),
        # 3 donut
        MapLocation(name="Dunkin' Jefferson Ave", location_type=LocationType.DONUT, lat=41.4100, lng=-75.6590, description="Available as Kevin reroute destination"),
        MapLocation(name="Krispy Kreme Scranton", location_type=LocationType.DONUT, lat=41.4230, lng=-75.6660, description="Available as Kevin reroute destination"),
        MapLocation(name="Tim Hortons Moosic St", location_type=LocationType.DONUT, lat=41.3990, lng=-75.6640, description="Available as Kevin reroute destination"),
    ]
    for loc in locations:
        if not session.exec(select(MapLocation).where(MapLocation.name == loc.name)).first():
            session.add(loc)
    session.flush()


def _seed_sales_and_packages(session: Session) -> None:
    now = datetime.utcnow()

    # Sale 1 — Jim → Lackawanna County
    sale1 = _get_or_create_sale(session, "SALE-2024-001", "lackawanna-county", "jim-halpert", "Quarterly paper order")
    inv1 = _get_or_create_invoice(session, "INV-2024-001", sale1.sale_id, "pam-beesly")

    pkg1 = _create_package(session, "PKG-2024-001", sale1.sale_id, inv1.invoice_id, "lackawanna-county", "jim-halpert", "pam-beesly", PackageStatus.READY_FOR_SHIPPING, "Lackawanna County, 200 Adams Ave", priority=PackagePriority.URGENT)
    _add_line_item(session, pkg1.package_id, "Copy Paper", "Paper Products", 10, "case", ProductType.PAPER_PRODUCT)
    _add_line_item(session, pkg1.package_id, "Sticky Notes", "Office Supplies", 5, "pack", ProductType.OFFICE_SUPPLY)
    _add_history(session, pkg1.package_id, PackageHistoryEventType.PACKAGE_CREATED, "jim-halpert", "Jim Halpert")
    _add_history(session, pkg1.package_id, PackageHistoryEventType.STATUS_CHANGED, "darryl-philbin", "Darryl Philbin", prev={"status": "order_created"}, new={"status": "packaged"})
    _add_history(session, pkg1.package_id, PackageHistoryEventType.STATUS_CHANGED, "darryl-philbin", "Darryl Philbin", prev={"status": "packaged"}, new={"status": "ready_for_shipping"})

    pkg2 = _create_package(session, "PKG-2024-002", sale1.sale_id, inv1.invoice_id, "lackawanna-county", "jim-halpert", "pam-beesly", PackageStatus.ORDER_CREATED, "Lackawanna County, 200 Adams Ave")
    _add_history(session, pkg2.package_id, PackageHistoryEventType.PACKAGE_CREATED, "jim-halpert", "Jim Halpert")

    # Sale 2 — Dwight → Poor Richard's
    sale2 = _get_or_create_sale(session, "SALE-2024-002", "poor-richard-pub", "dwight-schrute", "Beer-drinking supplies")
    inv2 = _get_or_create_invoice(session, "INV-2024-002", sale2.sale_id, "angela-martin")

    pkg3 = _create_package(session, "PKG-2024-003", sale2.sale_id, inv2.invoice_id, "poor-richard-pub", "dwight-schrute", "angela-martin", PackageStatus.PACKAGED, "Poor Richard's Pub, 456 Penn Ave", priority=PackagePriority.STANDARD)
    _add_line_item(session, pkg3.package_id, "Printer Paper A4", "Paper Products", 20, "ream", ProductType.PAPER_PRODUCT)
    _add_history(session, pkg3.package_id, PackageHistoryEventType.PACKAGE_CREATED, "dwight-schrute", "Dwight Schrute")
    _add_history(session, pkg3.package_id, PackageHistoryEventType.STATUS_CHANGED, "darryl-philbin", "Darryl Philbin", prev={"status": "order_created"}, new={"status": "packaged"})

    pkg4 = _create_package(session, "PKG-2024-004", sale2.sale_id, inv2.invoice_id, "poor-richard-pub", "dwight-schrute", "angela-martin", PackageStatus.DELIVERED, "Poor Richard's Pub, 456 Penn Ave")
    pkg4.expected_delivery = now - timedelta(days=2)
    _add_line_item(session, pkg4.package_id, "Ballpoint Pens", "Office Supplies", 50, "box", ProductType.OFFICE_SUPPLY)
    _add_history(session, pkg4.package_id, PackageHistoryEventType.PACKAGE_CREATED, "dwight-schrute", "Dwight Schrute")
    _add_history(session, pkg4.package_id, PackageHistoryEventType.DELIVERED, "darryl-philbin", "Darryl Philbin")

    # Sale 3 — Jim → The Steamtown Mall
    sale3 = _get_or_create_sale(session, "SALE-2024-003", "steamtown-mall", "jim-halpert", "Office supply restock")
    inv3 = _get_or_create_invoice(session, "INV-2024-003", sale3.sale_id, "pam-beesly")

    pkg5 = _create_package(session, "PKG-2024-005", sale3.sale_id, inv3.invoice_id, "steamtown-mall", "jim-halpert", "pam-beesly", PackageStatus.BACKORDER, "The Steamtown Mall, 300 Lackawanna Ave")
    _add_line_item(session, pkg5.package_id, "Envelopes", "Office Supplies", 100, "box", ProductType.OFFICE_SUPPLY)
    _add_history(session, pkg5.package_id, PackageHistoryEventType.PACKAGE_CREATED, "jim-halpert", "Jim Halpert")
    _add_history(session, pkg5.package_id, PackageHistoryEventType.STATUS_CHANGED, "darryl-philbin", "Darryl Philbin", prev={"status": "order_created"}, new={"status": "backorder"}, reason="Envelope stock depleted — waiting on warehouse restock")

    pkg6 = _create_package(session, "PKG-2024-006", sale3.sale_id, inv3.invoice_id, "steamtown-mall", "jim-halpert", "pam-beesly", PackageStatus.READY_FOR_SHIPPING, "The Steamtown Mall, 300 Lackawanna Ave", fragile=True)
    _add_line_item(session, pkg6.package_id, "Framed Certificates", "Office Supplies", 5, "unit", ProductType.OFFICE_SUPPLY, fragile=True)
    _add_history(session, pkg6.package_id, PackageHistoryEventType.PACKAGE_CREATED, "jim-halpert", "Jim Halpert")
    _add_history(session, pkg6.package_id, PackageHistoryEventType.STATUS_CHANGED, "darryl-philbin", "Darryl Philbin", prev={"status": "order_created"}, new={"status": "packaged"})
    _add_history(session, pkg6.package_id, PackageHistoryEventType.STATUS_CHANGED, "darryl-philbin", "Darryl Philbin", prev={"status": "packaged"}, new={"status": "ready_for_shipping"})

    # Sale 4 — Phyllis → Scranton Business Park
    sale4 = _get_or_create_sale(session, "SALE-2024-004", "scranton-business-park", "phyllis-vance", "Monthly supplies")
    inv4 = _get_or_create_invoice(session, "INV-2024-004", sale4.sale_id, "kevin-malone")

    pkg7 = _create_package(session, "PKG-2024-007", sale4.sale_id, inv4.invoice_id, "scranton-business-park", "phyllis-vance", "kevin-malone", PackageStatus.DELIVERED, "Scranton Business Park, 1000 Enterprise Dr")
    _add_line_item(session, pkg7.package_id, "Legal Pads", "Office Supplies", 24, "pack", ProductType.OFFICE_SUPPLY)
    _add_history(session, pkg7.package_id, PackageHistoryEventType.PACKAGE_CREATED, "phyllis-vance", "Phyllis Vance")
    _add_history(session, pkg7.package_id, PackageHistoryEventType.DELIVERED, "darryl-philbin", "Darryl Philbin")

    pkg8 = _create_package(session, "PKG-2024-008", sale4.sale_id, inv4.invoice_id, "scranton-business-park", "phyllis-vance", "kevin-malone", PackageStatus.CANCELLED, "Scranton Business Park, 1000 Enterprise Dr")
    _add_line_item(session, pkg8.package_id, "Staples", "Office Supplies", 10, "box", ProductType.OFFICE_SUPPLY)
    _add_history(session, pkg8.package_id, PackageHistoryEventType.PACKAGE_CREATED, "phyllis-vance", "Phyllis Vance")
    _add_history(session, pkg8.package_id, PackageHistoryEventType.CANCELLED, "jim-halpert", "Jim Halpert", reason="Customer changed order")

    pkg9 = _create_package(session, "PKG-2024-009", sale4.sale_id, inv4.invoice_id, "scranton-business-park", "phyllis-vance", "kevin-malone", PackageStatus.DAMAGED, "Scranton Business Park, 1000 Enterprise Dr")
    pkg9.delay_reason = "Damaged during sorting"
    _add_line_item(session, pkg9.package_id, "Printer Toner", "Office Supplies", 3, "cartridge", ProductType.OFFICE_SUPPLY)
    _add_history(session, pkg9.package_id, PackageHistoryEventType.PACKAGE_CREATED, "phyllis-vance", "Phyllis Vance")
    _add_history(session, pkg9.package_id, PackageHistoryEventType.DAMAGED, "creed-bratton", "Creed Bratton", reason="Toner cartridges cracked during sort")

    # Sale 5 — Stanley → Schrute Farms
    sale5 = _get_or_create_sale(session, "SALE-2024-005", "schrute-farms", "stanley-hudson", "Beet farm office supplies")
    inv5 = _get_or_create_invoice(session, "INV-2024-005", sale5.sale_id, "angela-martin")

    pkg10 = _create_package(session, "PKG-2024-010", sale5.sale_id, inv5.invoice_id, "schrute-farms", "stanley-hudson", "angela-martin", PackageStatus.ORDER_CREATED, "Schrute Farms, 1 Schrute Farms Rd", priority=PackagePriority.NEXT_DAY)
    _add_line_item(session, pkg10.package_id, "Carbon Copy Paper", "Paper Products", 5, "pack", ProductType.PAPER_PRODUCT)
    _add_history(session, pkg10.package_id, PackageHistoryEventType.PACKAGE_CREATED, "stanley-hudson", "Stanley Hudson")

    pkg11 = _create_package(session, "PKG-2024-011", sale5.sale_id, inv5.invoice_id, "schrute-farms", "stanley-hudson", "angela-martin", PackageStatus.ORDER_CREATED, "Schrute Farms, 1 Schrute Farms Rd")
    _add_history(session, pkg11.package_id, PackageHistoryEventType.PACKAGE_CREATED, "stanley-hudson", "Stanley Hudson")

    pkg12 = _create_package(session, "PKG-2024-012", sale5.sale_id, inv5.invoice_id, "schrute-farms", "stanley-hudson", "angela-martin", PackageStatus.SHIPPED, "Schrute Farms, 1 Schrute Farms Rd")
    _add_line_item(session, pkg12.package_id, "Binder Clips", "Office Supplies", 200, "box", ProductType.OFFICE_SUPPLY)
    _add_history(session, pkg12.package_id, PackageHistoryEventType.PACKAGE_CREATED, "stanley-hudson", "Stanley Hudson")
    _add_history(session, pkg12.package_id, PackageHistoryEventType.STATUS_CHANGED, "roy-anderson", "Roy Anderson", prev={"status": "order_created"}, new={"status": "shipped"})

    pkg13 = _create_package(session, "PKG-2024-013", sale5.sale_id, inv5.invoice_id, "schrute-farms", "stanley-hudson", "angela-martin", PackageStatus.RETURNED, "Schrute Farms, 1 Schrute Farms Rd")
    _add_line_item(session, pkg13.package_id, "Desk Organizer", "Office Supplies", 1, "unit", ProductType.OFFICE_SUPPLY)
    _add_history(session, pkg13.package_id, PackageHistoryEventType.PACKAGE_CREATED, "stanley-hudson", "Stanley Hudson")
    _add_history(session, pkg13.package_id, PackageHistoryEventType.RETURNED, "michael-scott", "Michael Scott", reason="Dwight refused delivery")


def _seed_complaints(session: Session) -> None:
    now = datetime.utcnow()

    c1 = Complaint(complaint_id="CMP-2024-001", sale_id="SALE-2024-001", description="Paper arrived with water damage on several reams. This is unacceptable, Michael!", status=ComplaintStatus.OPEN, created_by_id="jim-halpert", source="ui")
    session.add(c1)
    session.flush()
    session.add(ComplaintPackage(complaint_id="CMP-2024-001", package_id="PKG-2024-001"))
    _add_history(session, "PKG-2024-001", PackageHistoryEventType.COMPLAINT_CREATED, "jim-halpert", "Jim Halpert", new={"complaint_id": "CMP-2024-001"})

    c2 = Complaint(complaint_id="CMP-2024-002", sale_id="SALE-2024-004", description="Wrong product delivered. We ordered legal pads, got sticky notes.", status=ComplaintStatus.OPEN, created_by_id="stanley-hudson", source="api")
    session.add(c2)
    session.flush()
    session.add(ComplaintPackage(complaint_id="CMP-2024-002", package_id="PKG-2024-007"))
    _add_history(session, "PKG-2024-007", PackageHistoryEventType.COMPLAINT_CREATED, "stanley-hudson", "Stanley Hudson", new={"complaint_id": "CMP-2024-002"})

    c3 = Complaint(complaint_id="CMP-2024-003", sale_id="SALE-2024-002", description="Late delivery. Party needed supplies on time.", status=ComplaintStatus.CLOSED, created_by_id="pam-beesly", source="ui", closed_at=now - timedelta(days=1))
    session.add(c3)
    session.flush()
    session.add(ComplaintPackage(complaint_id="CMP-2024-003", package_id="PKG-2024-004"))
    _add_history(session, "PKG-2024-004", PackageHistoryEventType.COMPLAINT_CREATED, "pam-beesly", "Pam Beesly", new={"complaint_id": "CMP-2024-003"})
    _add_history(session, "PKG-2024-004", PackageHistoryEventType.COMPLAINT_UPDATED, "michael-scott", "Michael Scott", new={"status": "closed"}, reason="Resolved with discount")


def _get_or_create_sale(session: Session, sale_id: str, customer_id: str, salesperson_id: str, notes: str) -> Sale:
    existing = session.exec(select(Sale).where(Sale.sale_id == sale_id)).first()
    if existing:
        return existing
    sale = Sale(sale_id=sale_id, customer_id=customer_id, salesperson_id=salesperson_id, notes=notes)
    session.add(sale)
    session.flush()
    return sale


def _get_or_create_invoice(session: Session, invoice_id: str, sale_id: str, created_by_id: str) -> Invoice:
    existing = session.exec(select(Invoice).where(Invoice.invoice_id == invoice_id)).first()
    if existing:
        return existing
    invoice = Invoice(invoice_id=invoice_id, sale_id=sale_id, created_by_id=created_by_id)
    session.add(invoice)
    session.flush()
    return invoice


def _create_package(
    session: Session, package_id: str, sale_id: str, invoice_id: str,
    customer_id: str, salesperson_id: str, invoicing_employee_id: str,
    status: PackageStatus, destination: str, priority: PackagePriority = PackagePriority.STANDARD,
    fragile: bool = False, truck_id: str | None = None,
) -> Package:
    existing = session.exec(select(Package).where(Package.package_id == package_id)).first()
    if existing:
        return existing
    pkg = Package(
        package_id=package_id, sale_id=sale_id, invoice_id=invoice_id,
        customer_id=customer_id, salesperson_id=salesperson_id,
        invoicing_employee_id=invoicing_employee_id, status=status,
        destination=destination, priority=priority, fragile=fragile,
        truck_id=truck_id,
        expected_delivery=datetime.utcnow() + timedelta(days=1) if status not in ("delivered", "cancelled", "damaged", "returned") else None,
    )
    session.add(pkg)
    session.flush()
    return pkg


def _add_line_item(
    session: Session, package_id: str, product_name: str, product_category: str,
    quantity: int, unit_description: str, product_type: ProductType, fragile: bool = False,
) -> None:
    session.add(PackageLineItem(
        package_id=package_id, product_name=product_name, product_category=product_category,
        quantity=quantity, unit_description=unit_description, product_type=product_type,
        fragile=fragile,
    ))


def _add_history(
    session: Session, package_id: str, event_type: PackageHistoryEventType,
    actor_id: str, actor_name: str, prev: dict | None = None,
    new: dict | None = None, reason: str | None = None,
) -> None:
    session.add(PackageHistory(
        package_id=package_id, event_type=event_type,
        actor_id=actor_id, actor_name=actor_name,
        source=EventSource.DEMO, entity_type="package", entity_id=package_id,
        previous_value=json.dumps(prev) if prev else None,
        new_value=json.dumps(new) if new else None,
        reason=reason,
    ))
